"""Module 07 — deterministic triage. Evaluate in PRD order; thresholds come
from config, never from code constants.

INSUFFICIENT_EVIDENCE (any): no match / low AI confidence / high occlusion /
poor imagery / invalid geometry.
FLAGGED (any): area diff / boundary displacement / support ratio / topology /
split / merge.
CLEARED: none of the above -> CLEAR_BOUNDARY.
"""
from __future__ import annotations

from datetime import datetime, timezone

from ..config import TriageConfig
from ..geo import geom_of

REASON_CODES = [
    "NO_MATCHING_FIELD", "LOW_AI_CONFIDENCE", "OCCLUSION_EXCEEDS_LIMIT",
    "IMAGERY_QUALITY_POOR", "GEOMETRY_INVALID", "AREA_DIFF_EXCEEDS_TOLERANCE",
    "BOUNDARY_DISPLACEMENT_EXCEEDS_TOLERANCE", "LOW_SUPPORT_RATIO",
    "NEIGHBOR_OVERLAP_EXCEEDS_TOLERANCE", "SPLIT_DETECTED", "MERGE_DETECTED",
    "CLEAR_BOUNDARY",
]


def triage_parcel(parcel: dict, match: dict, evidence: dict,
                  cfg: TriageConfig) -> dict:
    """Return a TriageDecision row for one parcel."""
    insufficient: list[str] = []
    flagged: list[str] = []
    ins, clr = cfg.insufficient, cfg.clear

    # --- INSUFFICIENT_EVIDENCE rules -------------------------------------- #
    if match["match_type"] == "NO_MATCH":
        insufficient.append("NO_MATCHING_FIELD")
    if evidence["ai_confidence"] < ins.MIN_AI_CONFIDENCE:
        insufficient.append("LOW_AI_CONFIDENCE")
    if evidence["occlusion_fraction"] > ins.MAX_OCCLUSION_FRAC:
        insufficient.append("OCCLUSION_EXCEEDS_LIMIT")
    if evidence["evidence_quality"] == "POOR":
        insufficient.append("IMAGERY_QUALITY_POOR")
    try:
        if not geom_of(parcel["current_geometry"]).is_valid:
            insufficient.append("GEOMETRY_INVALID")
    except Exception:
        insufficient.append("GEOMETRY_INVALID")

    if insufficient:
        state = "INSUFFICIENT_EVIDENCE"
        reasons = insufficient
    else:
        # --- FLAGGED rules ------------------------------------------------ #
        if evidence["area_diff_pct"] > clr.MAX_AREA_DIFF_PCT:
            flagged.append("AREA_DIFF_EXCEEDS_TOLERANCE")
        if evidence["boundary_displacement_m"] > clr.MAX_BOUNDARY_DISPLACEMENT_M:
            flagged.append("BOUNDARY_DISPLACEMENT_EXCEEDS_TOLERANCE")
        if evidence["support_ratio_pct"] < clr.MIN_SUPPORT_RATIO_PCT:
            flagged.append("LOW_SUPPORT_RATIO")
        if evidence["topology_status"] == "FAIL":
            flagged.extend(iss.split(":")[0] for iss in evidence["topology_issues"])
        if match["match_type"] == "SPLIT":
            flagged.append("SPLIT_DETECTED")
        if match["match_type"] == "MERGE":
            flagged.append("MERGE_DETECTED")
        if flagged:
            state = "FLAGGED"
            reasons = list(dict.fromkeys(flagged))
        else:
            state = "CLEARED"
            reasons = ["CLEAR_BOUNDARY"]

    return {
        "id": f"TRI-{parcel['id']}",
        "parcel_id": parcel["id"],
        "state": state,
        "reason_codes": reasons,
        "evidence_report_id": evidence["id"],
        "computed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
