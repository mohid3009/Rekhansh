"""Pydantic models — PRD Data Model, verbatim plus Village/pipeline-log extras."""
from __future__ import annotations

from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class Village(BaseModel):
    id: str
    name: str
    district: str
    state: str
    lat: float
    lon: float
    source: Literal["MOCK", "IMPORTED"]
    notes: str = ""


class Parcel(BaseModel):
    id: str
    village_id: str
    survey_number: str                 # e.g. "142/3"
    recorded_area_ha: float
    recorded_geometry: dict            # GeoJSON Polygon, WGS84
    ror_owner_name: str                # MOCK ONLY — see Assumptions
    source: Literal["MOCK", "IMPORTED"]
    created_at: datetime


class ControlPoint(BaseModel):
    pixel_x: float
    pixel_y: float
    lat: float
    lon: float


class LegacyMap(BaseModel):
    id: str
    village_id: str
    raster_path: str
    control_points: list[ControlPoint]
    affine_transform: list[float]      # 6-parameter affine
    rmse_m: float


class RTKPoint(BaseModel):
    point_id: str
    lat: float
    lon: float
    elevation_m: float
    horizontal_accuracy_m: float
    vertical_accuracy_m: float
    captured_at: datetime


class AerialSurvey(BaseModel):
    id: str
    village_id: str
    orthomosaic_path: str
    dsm_path: Optional[str] = None
    resolution_cm_per_px: float
    capture_date: date
    checkpoints: list[RTKPoint] = Field(default_factory=list)


class AIFieldPolygon(BaseModel):
    id: str
    survey_id: str
    geometry: dict                     # GeoJSON Polygon
    confidence: float                  # 0-1
    detected_features: list[Literal["BOUNDARY", "BUND", "FENCE", "ROAD",
                                    "IRRIGATION_CHANNEL"]] = Field(default_factory=list)
    source: Literal["CV_MODEL", "SYNTHETIC_FALLBACK"]


class MatchResult(BaseModel):
    id: str
    parcel_id: str
    field_polygon_ids: list[str]
    match_type: Literal["ONE_TO_ONE", "SPLIT", "MERGE", "NO_MATCH"]
    match_confidence: float


class EvidenceReport(BaseModel):
    id: str
    parcel_id: str
    area_diff_ha: float
    area_diff_pct: float
    boundary_displacement_m: float
    iou: float
    support_ratio_pct: float
    occlusion_fraction: float
    topology_status: Literal["PASS", "FAIL"]
    topology_issues: list[str] = Field(default_factory=list)
    uncertainty_score: float           # 0 (best) – 1 (worst)
    evidence_quality: Literal["GOOD", "MODERATE", "POOR"]
    computed_at: datetime


class TriageDecision(BaseModel):
    id: str
    parcel_id: str
    state: Literal["CLEARED", "FLAGGED", "INSUFFICIENT_EVIDENCE"]
    reason_codes: list[str]
    evidence_report_id: str
    computed_at: datetime


class RTKVerification(BaseModel):
    id: str
    parcel_id: str
    checkpoints: list[RTKPoint] = Field(default_factory=list)
    observed_error_m: float
    corrected_geometry: Optional[dict] = None
    surveyor_decision: Literal["ACCEPT", "CORRECT", "REJECT"]
    surveyor_notes: str
    verified_by: str
    verified_at: datetime


class ParcelVersion(BaseModel):
    id: str
    parcel_id: str
    version_number: int
    geometry: dict
    area_ha: float
    verification_status: Literal["UNVERIFIED", "CONFIRMED", "CORRECTED", "ESCALATED"]
    evidence_report_id: Optional[str] = None
    surveyor_action: Optional[Literal["ACCEPT", "CORRECT", "REJECT"]] = None
    timestamp: datetime
    previous_version_id: Optional[str] = None
    previous_version_hash: Optional[str] = None
    record_hash: str
