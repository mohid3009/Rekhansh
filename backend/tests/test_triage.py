"""Triage rule tests — PRD Module 07 (state machine) + config-driven
thresholds (US-0.2: change config, outcomes change)."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import TriageConfig, load_triage_config
from app.pipeline.triage import triage_parcel
from shapely.geometry import Polygon, mapping as gmap

LAT, LON = 19.910, 73.900


def sq(size_m=80.0, lon=LON, lat=LAT):
    dlon = size_m / (111_320.0 * 0.94)
    dlat = size_m / 110_540.0
    return gmap(Polygon([(lon - dlon, lat - dlat), (lon + dlon, lat - dlat),
                         (lon + dlon, lat + dlat), (lon - dlon, lat + dlat)]))


def base_parcel(state="UNVERIFIED"):
    return {"id": "P1", "survey_number": "1/1",
            "current_geometry": sq(), "verification_status": state}


def match(mtype="ONE_TO_ONE", conf=0.9):
    return {"match_type": mtype, "match_confidence": conf,
            "field_polygon_ids": ["A1"]}


def evidence(**over):
    ev = {"id": "E1", "parcel_id": "P1", "area_diff_ha": 0.01, "area_diff_pct": 1.0,
          "boundary_displacement_m": 0.2, "iou": 0.95, "support_ratio_pct": 98.0,
          "occlusion_fraction": 0.1, "topology_status": "PASS", "topology_issues": [],
          "uncertainty_score": 0.15, "evidence_quality": "GOOD", "ai_confidence": 0.9,
          "computed_at": "2026-01-01T00:00:00+00:00"}
    ev.update(over)
    return ev


CFG = load_triage_config()


def test_all_pass_is_cleared():
    d = triage_parcel(base_parcel(), match(), evidence(), CFG)
    assert d["state"] == "CLEARED"
    assert d["reason_codes"] == ["CLEAR_BOUNDARY"]


def test_no_match_is_insufficient():
    d = triage_parcel(base_parcel(), match("NO_MATCH", 0.0),
                      evidence(ai_confidence=0.0, support_ratio_pct=0.0,
                               uncertainty_score=0.7, evidence_quality="POOR",
                               iou=0.0), CFG)
    assert d["state"] == "INSUFFICIENT_EVIDENCE"
    assert "NO_MATCHING_FIELD" in d["reason_codes"]


def test_low_confidence_is_insufficient_even_if_metrics_pass():
    d = triage_parcel(base_parcel(), match(conf=0.9),
                      evidence(ai_confidence=0.3), CFG)
    assert d["state"] == "INSUFFICIENT_EVIDENCE"
    assert "LOW_AI_CONFIDENCE" in d["reason_codes"]


def test_high_occlusion_is_insufficient():
    d = triage_parcel(base_parcel(), match(), evidence(occlusion_fraction=0.55), CFG)
    assert d["state"] == "INSUFFICIENT_EVIDENCE"
    assert "OCCLUSION_EXCEEDS_LIMIT" in d["reason_codes"]


def test_poor_quality_is_insufficient():
    d = triage_parcel(base_parcel(), match(),
                      evidence(evidence_quality="POOR", uncertainty_score=0.8), CFG)
    assert d["state"] == "INSUFFICIENT_EVIDENCE"
    assert "IMAGERY_QUALITY_POOR" in d["reason_codes"]


def test_area_diff_flags():
    d = triage_parcel(base_parcel(), match(), evidence(area_diff_pct=5.0), CFG)
    assert d["state"] == "FLAGGED"
    assert "AREA_DIFF_EXCEEDS_TOLERANCE" in d["reason_codes"]


def test_displacement_flags():
    d = triage_parcel(base_parcel(), match(),
                      evidence(boundary_displacement_m=0.9), CFG)
    assert d["state"] == "FLAGGED"
    assert "BOUNDARY_DISPLACEMENT_EXCEEDS_TOLERANCE" in d["reason_codes"]


def test_low_support_flags():
    d = triage_parcel(base_parcel(), match(), evidence(support_ratio_pct=60.0), CFG)
    assert d["state"] == "FLAGGED"
    assert "LOW_SUPPORT_RATIO" in d["reason_codes"]


def test_topology_fail_flags():
    d = triage_parcel(base_parcel(), match(),
                      evidence(topology_status="FAIL",
                               topology_issues=["NEIGHBOR_OVERLAP_EXCEEDS_TOLERANCE:2/9(3.0%)"]),
                      CFG)
    assert d["state"] == "FLAGGED"
    assert "NEIGHBOR_OVERLAP_EXCEEDS_TOLERANCE" in d["reason_codes"]


def test_split_and_merge_flag():
    d = triage_parcel(base_parcel(), match("SPLIT"), evidence(), CFG)
    assert d["state"] == "FLAGGED" and "SPLIT_DETECTED" in d["reason_codes"]
    d = triage_parcel(base_parcel(), match("MERGE"), evidence(), CFG)
    assert d["state"] == "FLAGGED" and "MERGE_DETECTED" in d["reason_codes"]


def test_insufficient_dominates_flagged():
    """PRD order: insufficient rules evaluated first."""
    d = triage_parcel(base_parcel(), match("NO_MATCH", 0.0),
                      evidence(ai_confidence=0.0, area_diff_pct=50.0,
                               uncertainty_score=0.9, evidence_quality="POOR",
                               support_ratio_pct=0.0), CFG)
    assert d["state"] == "INSUFFICIENT_EVIDENCE"


def test_thresholds_are_config_driven_not_hardcoded():
    """Tighten MAX_AREA_DIFF_PCT in config -> a 2% diff that was CLEARED becomes FLAGGED."""
    strict = TriageConfig()
    strict.clear.MAX_AREA_DIFF_PCT = 1.0
    d = triage_parcel(base_parcel(), match(), evidence(area_diff_pct=2.0), strict)
    assert d["state"] == "FLAGGED" and "AREA_DIFF_EXCEEDS_TOLERANCE" in d["reason_codes"]
    d = triage_parcel(base_parcel(), match(), evidence(area_diff_pct=2.0), CFG)
    assert d["state"] == "CLEARED"          # default 3.0% allows 2%


def test_invalid_geometry_forces_insufficient():
    bow = {"type": "Polygon", "coordinates": [[
        [LON, LAT], [LON + 0.001, LAT + 0.001], [LON + 0.001, LAT], [LON, LAT + 0.001],
        [LON, LAT]]]}
    p = base_parcel()
    p["current_geometry"] = bow
    d = triage_parcel(p, match(), evidence(), CFG)
    assert d["state"] == "INSUFFICIENT_EVIDENCE"
    assert "GEOMETRY_INVALID" in d["reason_codes"]
