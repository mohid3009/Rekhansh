"""KPI dashboard computations (US-7.x). Null (shown as '—') when no data."""
from __future__ import annotations

import math
from typing import Any

from .. import db
from ..config import load_triage_config


def _pct(a: float, b: float) -> float | None:
    return round(100.0 * a / b, 1) if b > 0 else None


def compute_kpis() -> dict[str, Any]:
    cfg = load_triage_config()
    threshold = cfg.kpi.FALSE_CLEAR_ERROR_M
    decisions = {d["parcel_id"]: d for d in db.select("triage_decisions")}
    vers = db.select("rtk_verifications")

    # false-clear: audited while CLEARED, surveyor found it wrong
    audited_clear = [v for v in vers
                     if v.get("triage_state_at_audit") == "CLEARED"]
    wrong_clear = [v for v in audited_clear
                   if v["surveyor_decision"] != "ACCEPT"
                   or v["observed_error_m"] > threshold]
    false_clear_rate = _pct(len(wrong_clear), len(audited_clear))

    # PRD definition: % cleared without full RTK = CLEARED count / total parcel
    # count × 100 — the share of the village cleared without RTK fieldwork.
    cleared_count = sum(1 for d in decisions.values() if d["state"] == "CLEARED")
    total_parcels = len(db.select("parcels")) or len(decisions)
    cleared_without_rtk = _pct(cleared_count, total_parcels)

    # boundary RMSE vs RTK-corrected ground truth, across ALL RTK-verified
    # parcels (PRD definition); ACCEPT/REJECT verifications contribute 0 m.
    errs = [float(v.get("observed_error_m") or 0.0) for v in vers]
    boundary_rmse_m = round(math.sqrt(sum(e * e for e in errs) / len(errs)), 3) if errs else None

    # area error vs corrected geometry
    area_errs = []
    from ..geo import polygon_area_ha
    from ..pipeline.versions import versions_for
    for v in vers:
        if not v.get("corrected_geometry"):
            continue
        vs = versions_for(v["parcel_id"])
        pre = next((x for x in vs if x["surveyor_action"] != "CORRECT"), None) or vs[0]
        rec, corr = pre["geometry"], v["corrected_geometry"]
        a_corr = polygon_area_ha(corr)
        if a_corr > 0:
            area_errs.append(abs(polygon_area_ha(rec) - a_corr) / a_corr * 100.0)
    area_error_pct = round(sum(area_errs) / len(area_errs), 3) if area_errs else None
    n_corrected = len(area_errs)

    # false-flag: audited while FLAGGED, surveyor confirmed it was already correct
    audited_flagged = [v for v in vers
                       if v.get("triage_state_at_audit") == "FLAGGED"]
    false_flag = [v for v in audited_flagged if v["surveyor_decision"] == "ACCEPT"]
    false_flag_rate = _pct(len(false_flag), len(audited_flagged))

    # processing time per parcel from the latest completed run
    runs = sorted(db.select("pipeline_runs"), key=lambda r: r["started_at"])
    time_per_parcel_ms = None
    for run in reversed(runs):
        if run.get("finished_at") and run.get("steps"):
            total = sum(s.get("ms", 0) for s in run["steps"])
            n = run.get("parcel_count") or len(decisions) or 1
            time_per_parcel_ms = round(total / n, 1)
            break

    return {
        "false_clear_rate_pct": false_clear_rate,
        "cleared_without_full_rtk_pct": cleared_without_rtk,
        "boundary_rmse_m": boundary_rmse_m,
        "area_error_pct": area_error_pct,
        "false_flag_rate_pct": false_flag_rate,
        "processing_time_per_parcel_ms": time_per_parcel_ms,
        "sample_sizes": {"audited_cleared": len(audited_clear),
                         "audited_flagged": len(audited_flagged),
                         "corrected": n_corrected},
    }
