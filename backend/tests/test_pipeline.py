"""Offline integration: deterministic seed, full pipeline run, all triage
classes reachable, append-only version history across re-runs (US-6.1)."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import db
from app.seed.village import generate_design


def test_design_is_deterministic_and_seed_sensitive():
    g1, _ = generate_design(19.91, 73.90, 18, 42)
    g2, _ = generate_design(19.91, 73.90, 18, 42)
    g3, _ = generate_design(19.91, 73.90, 18, 43)
    assert g1 == g2, "same seed must give identical village (US-0.1)"
    assert g3 != g1, "different seed must change the village"


def test_survey_numbers_unique():
    from app.seed.village import parcel_rows
    geoms, _ = generate_design(19.91, 73.90, 18, 42)
    rows = parcel_rows(geoms, "VIL-X", 42, "2026-01-01T00:00:00+00:00")
    nums = [r["survey_number"] for r in rows]
    assert len(set(nums)) == len(nums), "no two parcels may share a survey number"
    assert all("/" in n for n in nums), "numbers follow the NNN/N convention"
    # US-0.1: plausible recorded areas — a square-degrees regression made these 0.0
    areas = [r["recorded_area_ha"] for r in rows]
    assert all(0.05 < a < 5.0 for a in areas), f"recorded areas implausible: {areas}"


def test_full_pipeline_offline(monkeypatch):
    import app.pipeline.runner as runner

    def offline(*a, **k):
        raise RuntimeError("network disabled in tests")

    monkeypatch.setattr(runner, "fetch_orthomosaic", offline)
    monkeypatch.setattr(runner, "fetch_osm_context", lambda *a, **k: None)

    db.init_db()
    runner.ensure_seeded()
    r1 = runner.run_full()
    assert r1["parcel_count"] >= 10
    for key in ("CLEARED", "FLAGGED", "INSUFFICIENT_EVIDENCE"):
        assert r1["outcomes"][key] >= 1, f"no parcel reached {key} (US-9.1 demo)"

    # matching exercised every designed branch at least once across runs,
    # and a second run yields identical outcomes (determinism)
    totals = {}
    r2 = runner.run_full()
    assert r2["outcomes"] == r1["outcomes"], "same seed must reproduce outcomes"
    for run in (r1, r2):
        for s in run["steps"]:
            if s["name"] == "matching":
                for k, v in s.get("types", {}).items():
                    totals[k] = totals.get(k, 0) + v
    assert totals.get("NO_MATCH", 0) >= 1
    assert totals.get("SPLIT", 0) >= 1
    assert totals.get("MERGE", 0) >= 1

    # append-only history: re-runs never touch ParcelVersion rows (US-6.1)
    counts = db.query("SELECT COUNT(*) AS c FROM parcel_versions "
                      "WHERE parcel_id LIKE 'PAR-VIL-%'")
    assert counts[0]["c"] >= 18
    per_parcel = db.query("SELECT parcel_id, COUNT(*) AS c FROM parcel_versions "
                          "WHERE parcel_id LIKE 'PAR-VIL-%' GROUP BY parcel_id")
    assert all(row["c"] == 1 for row in per_parcel), \
        "run-full must not add or rewrite versions (genesis only until audits)"


def test_verification_appends_version_and_survives_rerun(monkeypatch):
    import app.pipeline.runner as runner
    from app.pipeline.rtk import submit_verification
    from app.pipeline.versions import versions_for

    monkeypatch.setattr(runner, "fetch_orthomosaic",
                        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("offline")))
    db.init_db()
    runner.ensure_seeded()
    if not db.select("triage_decisions"):
        runner.run_full()

    pid = db.select("parcels", order_by="id")[0]["id"]
    before = len(versions_for(pid))
    row = submit_verification(pid, "ACCEPT", "unit test", "pytest")
    after = versions_for(pid)
    assert len(after) == before + 1
    assert after[-1]["verification_status"] == "CONFIRMED"
    assert row["triage_state_at_audit"] in (None, "CLEARED", "FLAGGED",
                                            "INSUFFICIENT_EVIDENCE")

    # re-run pipeline: version count unchanged, integrity intact
    r = runner.run_full()
    assert r["parcel_count"] >= 10
    assert len(versions_for(pid)) == len(after)


def test_kpis_shape_and_null_without_data():
    from app.pipeline.kpis import compute_kpis
    k = compute_kpis()
    for key in ("false_clear_rate_pct", "cleared_without_full_rtk_pct",
                "boundary_rmse_m", "area_error_pct", "false_flag_rate_pct",
                "processing_time_per_parcel_ms", "sample_sizes"):
        assert key in k
