"""Configuration loading: YAML -> validated pydantic models (US-0.2).

Triage thresholds live in `config/triage.yaml`; site/seed parameters live in
`config/site.yaml`. Nothing in the pipeline hardcodes a threshold.
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import BaseModel, Field

BACKEND_DIR = Path(__file__).resolve().parents[1]
CONFIG_DIR = Path(os.environ.get("TRIAGE_CONFIG_DIR", BACKEND_DIR / "config"))
DATA_DIR = Path(os.environ.get("DATA_DIR", BACKEND_DIR / "data"))


class MatchCfg(BaseModel):
    MIN_IOU_ONE_TO_ONE: float = 0.30
    MIN_IOU_FLOOR: float = 0.05
    SPLIT_COMBINED_IOU: float = 0.50
    MERGE_MIN_OVERLAP_FRAC: float = 0.30


class ClearCfg(BaseModel):
    MAX_AREA_DIFF_PCT: float = 3.0
    MAX_BOUNDARY_DISPLACEMENT_M: float = 0.50
    MIN_SUPPORT_RATIO_PCT: float = 90.0


class InsufficientCfg(BaseModel):
    MIN_AI_CONFIDENCE: float = 0.50
    MAX_OCCLUSION_FRAC: float = 0.40


class BoundaryCfg(BaseModel):
    SUPPORT_BUFFER_M: float = 1.0
    SAMPLE_INTERVAL_M: float = 0.5


class TopologyCfg(BaseModel):
    MAX_NEIGHBOR_OVERLAP_PCT: float = 2.0


class UncertaintyCfg(BaseModel):
    W_AI_CONFIDENCE: float = 0.35
    W_GEOREF_RMSE: float = 0.15
    W_OCCLUSION: float = 0.30
    W_SUPPORT: float = 0.20
    GEOREF_RMSE_NORM_M: float = 10.0


class QualityCfg(BaseModel):
    GOOD_MAX_UNCERTAINTY: float = 0.25
    MODERATE_MAX_UNCERTAINTY: float = 0.50


class OcclusionCfg(BaseModel):
    SHADOW_V_MAX: float = 42.0
    DENSE_EXG_MIN: float = 65.0
    SCALE: float = 1.0
    FALLBACK_MEAN: float = 0.12
    FALLBACK_SD: float = 0.08


class KpiCfg(BaseModel):
    FALSE_CLEAR_ERROR_M: float = 0.5


class SyntheticCfg(BaseModel):
    DEFAULT_TIER: str = "SYNTHETIC_FALLBACK"
    SHIFT_CLEAN_M: list[float] = Field(default_factory=lambda: [0.10, 0.30])
    SHIFT_DRIFT_M: list[float] = Field(default_factory=lambda: [0.70, 1.60])
    CONFIDENCE_CLEAN: list[float] = Field(default_factory=lambda: [0.82, 0.95])
    CONFIDENCE_DIRTY: list[float] = Field(default_factory=lambda: [0.55, 0.75])
    JITTER_SD_M: float = 0.06
    SPLIT_COUNT: int = 2
    MERGE_PAIRS: int = 1
    NO_MATCH_COUNT: int = 1
    LOW_CONFIDENCE_COUNT: int = 1


class CvCfg(BaseModel):
    CANNY_LOW: int = 30
    CANNY_HIGH: int = 90
    DP_SCALE_PX: float = 3.0
    MIN_AREA_HA: float = 0.30
    MAX_AREA_HA: float = 15.00


class RealObsCfg(BaseModel):
    MAX_DIST_M: float = 2000.0
    MAX_POLYS: int = 60


class GuidedCfg(BaseModel):
    # Search radius for the real-boundary reading, calibrated on the pilot
    # mosaic (30 real Bond Gavhan parcels, Esri z18, 0.56 m/px):
    #   <= 2 m -> the snap stops moving the record: 30/30 parcels clear and
    #             the metrics lose all discriminating power;
    #    8 m   -> 0/30 clear: every parcel flags on support alone, because
    #             vertices jump onto unrelated texture;
    #    4 m   -> 5/30 clear, support p50 86%, ASBD p50 0.40 m: real
    #             sub-metre displacement is measured and both outcomes
    #             (clear / flag) stay reachable.
    SNAP_RADIUS_M: float = 4.0
    CROP_MARGIN_PX: int = 40
    DENSIFY_M: float = 5.0
    CANNY_LOW: int = 30
    CANNY_HIGH: int = 90
    CONFIDENCE_BASE: float = 0.55
    CONFIDENCE_SLOPE: float = 0.35


class ExtractionCfg(BaseModel):
    synthetic: SyntheticCfg = Field(default_factory=SyntheticCfg)
    cv: CvCfg = Field(default_factory=CvCfg)
    real: RealObsCfg = Field(default_factory=RealObsCfg)
    guided: GuidedCfg = Field(default_factory=GuidedCfg)


class GeorefCfg(BaseModel):
    SCAN_ROTATION_DEG: float = 3.5
    SCAN_SCALE_PCT: float = 4.0
    SCAN_NOISE_M: float = 1.2
    CONTROL_POINT_GRID: int = 6


class TriageConfig(BaseModel):
    match: MatchCfg = Field(default_factory=MatchCfg)
    clear: ClearCfg = Field(default_factory=ClearCfg)
    insufficient: InsufficientCfg = Field(default_factory=InsufficientCfg)
    boundary: BoundaryCfg = Field(default_factory=BoundaryCfg)
    topology: TopologyCfg = Field(default_factory=TopologyCfg)
    uncertainty: UncertaintyCfg = Field(default_factory=UncertaintyCfg)
    quality: QualityCfg = Field(default_factory=QualityCfg)
    occlusion: OcclusionCfg = Field(default_factory=OcclusionCfg)
    kpi: KpiCfg = Field(default_factory=KpiCfg)
    extraction: ExtractionCfg = Field(default_factory=ExtractionCfg)
    georeferencing: GeorefCfg = Field(default_factory=GeorefCfg)


class SiteCfg(BaseModel):
    name: str = "Pilot village"
    taluka: str = ""
    district: str = ""
    state: str = ""
    country: str = "India"
    lat: float = 20.0
    lon: float = 73.7
    zoom: int = 19
    tiles: int = 5
    elevation_m: float = 700.0          # approx, for demo RTK elevations only
    tile_url: str = ("https://services.arcgisonline.com/ArcGIS/rest/services/"
                     "World_Imagery/MapServer/tile/{z}/{y}/{x}")
    attribution: str = "Esri, Maxar, Earthstar Geographics"
    seed: int = 42
    parcel_count: int = 18


def _load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


@lru_cache(maxsize=4)
def load_triage_config(path: str | None = None) -> TriageConfig:
    p = Path(path) if path else CONFIG_DIR / "triage.yaml"
    return TriageConfig.model_validate(_load_yaml(p))


@lru_cache(maxsize=4)
def load_site_config(path: str | None = None) -> SiteCfg:
    p = Path(path) if path else CONFIG_DIR / "site.yaml"
    return SiteCfg.model_validate(_load_yaml(p))
