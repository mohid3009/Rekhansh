"""REST API (PRD Appendix A). Every route from the appendix plus extras the
user stories need (list detail, evidence, export, meta)."""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .. import db
from ..config import load_site_config, load_triage_config, CONFIG_DIR
from ..pipeline.kpis import compute_kpis
from ..pipeline.rtk import submit_verification, verifications_for
from ..pipeline.runner import run_full, VILLAGE_ID
from ..pipeline.versions import chain_integrity, versions_for

router = APIRouter()

REASON_COPY = {
    "NO_MATCHING_FIELD": "No AI-detected field boundary matches this record (best IoU below floor).",
    "LOW_AI_CONFIDENCE": "AI confidence is below the configured minimum.",
    "OCCLUSION_EXCEEDS_LIMIT": "More of the parcel is hidden by shadow/canopy than allowed.",
    "IMAGERY_QUALITY_POOR": "Combined evidence uncertainty is POOR — the imagery cannot support a decision.",
    "GEOMETRY_INVALID": "The recorded geometry is invalid (self-intersecting or degenerate).",
    "AREA_DIFF_EXCEEDS_TOLERANCE": "Recorded vs observed area difference is above the allowed %.",
    "BOUNDARY_DISPLACEMENT_EXCEEDS_TOLERANCE": "Boundary displacement (ASBD) is above the allowed metres.",
    "LOW_SUPPORT_RATIO": "Too little of the recorded perimeter is supported by detected features.",
    "NEIGHBOR_OVERLAP_EXCEEDS_TOLERANCE": "Overlaps a neighbouring parcel beyond the topology tolerance.",
    "SPLIT_DETECTED": "The record is covered by multiple AI polygons (likely a split).",
    "MERGE_DETECTED": "One AI polygon covers several records (likely a merge).",
    "CLEAR_BOUNDARY": "All clearance tests passed on good-quality evidence.",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _requires_pipeline() -> None:
    if not db.select("triage_decisions"):
        raise HTTPException(503, "Pipeline has not produced triage state yet — "
                                 "POST /api/pipeline/run-full")


# --------------------------------------------------------------------------- #
# villages
# --------------------------------------------------------------------------- #
@router.get("/villages")
def list_villages():
    return db.select("villages")


@router.get("/villages/{vid}/summary")
def village_summary(vid: str):
    village = db.select_one("villages", id=vid)
    if not village:
        raise HTTPException(404, "village not found")
    _requires_pipeline()
    decisions = db.select("triage_decisions")
    parcels = db.select("parcels", village_id=vid)
    meta = db.select_one("village_meta", village_id=vid) or {}
    survey = db.select_one("aerial_surveys", village_id=vid) or {}
    legacy = db.select_one("legacy_maps", village_id=vid) or {}
    runs = sorted(db.select("pipeline_runs"), key=lambda r: r["started_at"])
    counts = {s: sum(1 for d in decisions if d["state"] == s)
              for s in ("CLEARED", "FLAGGED", "INSUFFICIENT_EVIDENCE")}
    latest = next((r for r in reversed(runs) if r.get("finished_at")), None)
    return {
        "village": village,
        "parcel_count": len(parcels),
        "counts": counts,
        "seed_examples": meta.get("seed_examples") or {},
        "survey": {k: survey.get(k) for k in
                   ("id", "orthomosaic_path", "dsm_path", "resolution_cm_per_px",
                    "capture_date", "bounds", "provenance")},
        "legacy": {k: legacy.get(k) for k in
                   ("id", "raster_path", "rmse_m", "affine_transform", "applied_distortion")},
        "latest_run": ({"run_id": latest["id"], "tier": latest["tier"],
                        "finished_at": latest["finished_at"], "steps": latest["steps"],
                        "ok": latest["ok"]} if latest else None),
    }


@router.get("/villages/{vid}/parcels")
def village_parcels(vid: str):
    village = db.select_one("villages", id=vid)
    if not village:
        raise HTTPException(404, "village not found")
    _requires_pipeline()
    from ..pipeline.versions import latest_version
    decisions = {d["parcel_id"]: d for d in db.select("triage_decisions")}
    matches = {m["parcel_id"]: m for m in db.select("match_results")}
    out = []
    for p in db.select("parcels", village_id=vid, order_by="survey_number"):
        lv = latest_version(p["id"])
        d = decisions.get(p["id"])
        m = matches.get(p["id"])
        out.append({
            "id": p["id"], "survey_number": p["survey_number"],
            "ror_owner_name": p["ror_owner_name"], "source": p["source"],
            "recorded_area_ha": p["recorded_area_ha"],
            "current_area_ha": lv["area_ha"],
            "geometry": lv["geometry"],
            "triage_state": d["state"] if d else None,
            "reason_codes": d["reason_codes"] if d else [],
            "match_type": m["match_type"] if m else None,
            "match_confidence": m["match_confidence"] if m else None,
            "verification_status": lv["verification_status"],
            "version_number": lv["version_number"],
        })
    return out


# --------------------------------------------------------------------------- #
# parcel detail / comparison
# --------------------------------------------------------------------------- #
def _get_parcel(pid: str) -> dict:
    p = db.select_one("parcels", id=pid)
    if not p:
        raise HTTPException(404, "parcel not found")
    return p


@router.get("/parcels/{pid}")
def parcel_detail(pid: str):
    p = _get_parcel(pid)
    _requires_pipeline()
    from ..pipeline.versions import latest_version
    lv = latest_version(pid)
    d = db.select_one("triage_decisions", parcel_id=pid)
    m = db.select_one("match_results", parcel_id=pid)
    ev = (db.select_one("evidence_reports", id=d["evidence_report_id"])
          if d else None)
    vers = versions_for(pid)
    vs = verifications_for(pid)
    return {
        "parcel": {**p, "current_geometry": lv["geometry"],
                   "current_area_ha": lv["area_ha"],
                   "verification_status": lv["verification_status"]},
        "triage": d, "match": m, "evidence": ev,
        "version_count": len(vers),
        "latest_version": lv,
        "verifications": [{k: v[k] for k in
                           ("id", "surveyor_decision", "surveyor_notes",
                            "verified_by", "verified_at", "observed_error_m",
                            "triage_state_at_audit")}
                          for v in vs],
    }


@router.get("/parcels/{pid}/comparison")
def parcel_comparison(pid: str):
    """Everything Screen 2 needs to draw the comparison map (US-2.1)."""
    p = _get_parcel(pid)
    _requires_pipeline()
    from ..pipeline.versions import latest_version
    from ..geo import geom_of, make_transformer, overlap_fraction
    lv = latest_version(pid)
    m = db.select_one("match_results", parcel_id=pid) or {}
    ai_ids = m.get("field_polygon_ids") or []
    ai = [a for a in db.select("ai_field_polygons") if a["id"] in ai_ids]
    survey = db.select_one("aerial_surveys", village_id=p["village_id"]) or {}
    legacy = db.select_one("legacy_maps", village_id=p["village_id"]) or {}
    g = geom_of(lv["geometry"])
    fwd = make_transformer(g.centroid.x, g.centroid.y)
    neighbours = []
    for o in db.select("parcels", village_id=p["village_id"]):
        if o["id"] == pid:
            continue
        ov = db.select_one("parcel_versions", parcel_id=o["id"],
                           order_by="version_number DESC")
        if not ov:
            continue
        pct = overlap_fraction(lv["geometry"], ov["geometry"], fwd)
        if pct > 0.005:
            neighbours.append({"id": o["id"], "survey_number": o["survey_number"],
                               "overlap_pct": round(pct * 100, 2),
                               "geometry": ov["geometry"]})
    return {
        "parcel_id": pid,
        "recorded_geometry": lv["geometry"],
        "recorded_area_ha": lv["area_ha"],
        "ai_polygons": [{"id": a["id"], "geometry": a["geometry"],
                         "confidence": a["confidence"],
                         "detected_features": a["detected_features"],
                         "source": a["source"],
                         "evidence_note": a.get("evidence_note")} for a in ai],
        "neighbour_overlaps": neighbours,
        "match": m,
        "orthomosaic": {"url": f"/static/{survey.get('orthomosaic_path')}",
                        "bounds": survey.get("bounds"),
                        "resolution_cm_per_px": survey.get("resolution_cm_per_px"),
                        "provenance": survey.get("provenance")},
        "legacy_scan": {"url": f"/static/{legacy.get('raster_path')}",
                        "rmse_m": legacy.get("rmse_m"),
                        "affine_transform": legacy.get("affine_transform"),
                        "applied_distortion": legacy.get("applied_distortion")},
        "control_points": legacy.get("control_points"),
    }


# --------------------------------------------------------------------------- #
# evidence / versions / export
# --------------------------------------------------------------------------- #
@router.get("/parcels/{pid}/evidence")
def parcel_evidence(pid: str):
    """Evidence panel payload (US-3.1): metrics, thresholds, plain language."""
    _get_parcel(pid)
    _requires_pipeline()
    d = db.select_one("triage_decisions", parcel_id=pid)
    if not d:
        raise HTTPException(404, "no triage decision")
    ev = db.select_one("evidence_reports", id=d["evidence_report_id"])
    m = db.select_one("match_results", parcel_id=pid)
    cfg = load_triage_config()
    thresholds = {"clear": cfg.clear.model_dump(), "match": cfg.match.model_dump(),
                  "insufficient": cfg.insufficient.model_dump(),
                  "topology": cfg.topology.model_dump(),
                  "quality": cfg.quality.model_dump(),
                  "uncertainty": cfg.uncertainty.model_dump()}
    return {
        "decision": d,
        "evidence": ev,
        "match": m,
        "thresholds": thresholds,
        "reasons": [{"code": c, "copy": REASON_COPY.get(c, c)} for c in d["reason_codes"]],
        "checks": [
            {"name": "area_diff_pct", "value": ev["area_diff_pct"],
             "rule": f"<= {cfg.clear.MAX_AREA_DIFF_PCT}%",
             "pass": ev["area_diff_pct"] <= cfg.clear.MAX_AREA_DIFF_PCT},
            {"name": "boundary_displacement_m", "value": ev["boundary_displacement_m"],
             "rule": f"<= {cfg.clear.MAX_BOUNDARY_DISPLACEMENT_M} m",
             "pass": ev["boundary_displacement_m"] <= cfg.clear.MAX_BOUNDARY_DISPLACEMENT_M},
            {"name": "support_ratio_pct", "value": ev["support_ratio_pct"],
             "rule": f">= {cfg.clear.MIN_SUPPORT_RATIO_PCT}%",
             "pass": ev["support_ratio_pct"] >= cfg.clear.MIN_SUPPORT_RATIO_PCT},
            {"name": "occlusion_fraction", "value": ev["occlusion_fraction"],
             "rule": f"<= {cfg.insufficient.MAX_OCCLUSION_FRAC}",
             "pass": ev["occlusion_fraction"] <= cfg.insufficient.MAX_OCCLUSION_FRAC},
            {"name": "ai_confidence", "value": ev["ai_confidence"],
             "rule": f">= {cfg.insufficient.MIN_AI_CONFIDENCE}",
             "pass": ev["ai_confidence"] >= cfg.insufficient.MIN_AI_CONFIDENCE},
            {"name": "uncertainty_score", "value": ev["uncertainty_score"],
             "rule": f"GOOD <= {cfg.quality.GOOD_MAX_UNCERTAINTY}; "
                     f"POOR > {cfg.quality.MODERATE_MAX_UNCERTAINTY}",
             "pass": ev["evidence_quality"] != "POOR"},
            {"name": "topology_status", "value": ev["topology_status"],
             "rule": f"neighbor overlap <= {cfg.topology.MAX_NEIGHBOR_OVERLAP_PCT}%",
             "pass": ev["topology_status"] == "PASS"},
        ],
    }


@router.get("/parcels/{pid}/versions")
def parcel_versions(pid: str):
    _get_parcel(pid)
    vers = versions_for(pid)
    return {"versions": vers, "integrity": chain_integrity(pid)}


@router.get("/parcels/{pid}/export")
def parcel_export(pid: str):
    """US-5.2 — complete parcel evidence + version history as one JSON."""
    _get_parcel(pid)
    d = db.select_one("triage_decisions", parcel_id=pid)
    ev = (db.select_one("evidence_reports", id=d["evidence_report_id"])
          if d else None)
    m = db.select_one("match_results", parcel_id=pid)
    p = db.select_one("parcels", id=pid)
    vs = verifications_for(pid)
    vers = versions_for(pid)
    return {
        "exported_at": _now(),
        "parcel": p,
        "match": m,
        "evidence": ev,
        "triage": d,
        "rtk_verifications": vs,
        "versions": vers,
        "chain_integrity": chain_integrity(pid),
    }


# --------------------------------------------------------------------------- #
# verification / pipeline / kpis / meta
# --------------------------------------------------------------------------- #
class VerifyIn(BaseModel):
    decision: str                          # ACCEPT | CORRECT | REJECT
    notes: str = ""
    verified_by: str = "field-surveyor-1"
    corrected_geometry: dict | None = None
    checkpoints: list[dict] = Field(default_factory=list)


@router.post("/parcels/{pid}/rtk-verification")
def post_verification(pid: str, body: VerifyIn):
    _get_parcel(pid)
    _requires_pipeline()
    try:
        row = submit_verification(pid, body.decision, body.notes, body.verified_by,
                                  body.corrected_geometry, body.checkpoints)
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    return {"ok": True, "verification": row,
            "versions": versions_for(pid),
            "integrity": chain_integrity(pid)}


@router.post("/pipeline/run-full")
def post_run_full():
    result = run_full()
    result["kpis"] = compute_kpis()
    return result


@router.get("/kpis")
def get_kpis():
    return compute_kpis()


@router.get("/meta")
def get_meta():
    """Session/meta payload: village, thresholds, reason copy, banners, run."""
    site = load_site_config()
    cfg = load_triage_config()
    village = db.select_one("villages", id=VILLAGE_ID)
    meta = db.select_one("village_meta", village_id=VILLAGE_ID) or {}
    runs = sorted(db.select("pipeline_runs"), key=lambda r: r["started_at"])
    latest = next((r for r in reversed(runs) if r.get("finished_at")), None)
    return {
        "app": {"name": "Rural Land Resurvey Triage", "mode": "PROTOTYPE",
                "data_classification": (
                    "PROTOTYPE DATA — real Bhu-Naksha cadastral parcels + real Esri "
                    "imagery; owner names, legacy scan and RTK traces simulated; "
                    "no Record of Rights data is shown"),
                "reason_codes": REASON_COPY},
        "site": site.model_dump(),
        "thresholds": {"clear": cfg.clear.model_dump(), "match": cfg.match.model_dump(),
                       "insufficient": cfg.insufficient.model_dump(),
                       "boundary": cfg.boundary.model_dump(),
                       "topology": cfg.topology.model_dump(),
                       "quality": cfg.quality.model_dump(),
                       "uncertainty": cfg.uncertainty.model_dump(),
                       "kpi": cfg.kpi.model_dump(),
                       "georeferencing": cfg.georeferencing.model_dump(),
                       "active_tier": cfg.extraction.synthetic.DEFAULT_TIER},
        "config_files": {"triage": str(CONFIG_DIR / "triage.yaml"),
                         "site": str(CONFIG_DIR / "site.yaml")},
        "village": village,
        "seed_examples": meta.get("seed_examples") or {},
        "has_triage": bool(db.select("triage_decisions")),
        "latest_run": ({"run_id": latest["id"], "tier": latest["tier"],
                        "finished_at": latest["finished_at"], "steps": latest["steps"]}
                       if latest else None),
    }
