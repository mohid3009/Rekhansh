"""Run Tier-2 CV extraction on the vendored REAL orthomosaic and report."""
from __future__ import annotations

import json
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parent
sys.path.insert(0, str(BACKEND))

from app.config import load_triage_config  # noqa: E402
from app.pipeline.extract import extract_tier2  # noqa: E402
from app.raster import WorldFileAffine, load_png  # noqa: E402

img = load_png(BACKEND / "data" / "imagery" / "VIL-PILOT_ortho.png")
aff = WorldFileAffine.read_world_file(
    BACKEND / "data" / "imagery" / "VIL-PILOT_ortho.pgw")
prov = json.loads((BACKEND / "data" / "imagery" / "VIL-PILOT_ortho.json")
                  .read_text(encoding="utf-8"))
cfg = load_triage_config()
res_m = aff.resolution_m_per_px(19.8847)
print(f"img {img.shape} res {res_m:.3f} m/px  provider={prov['provider']}")
polys = extract_tier2(img, aff, cfg, res_m)
import numpy as np
from shapely.geometry import shape
areas = sorted([abs(shape(p["geometry"]).area) * (111320 * 0.94) ** 2 / 1e4
                for p in polys])
print(f"CV polygons: {len(polys)}")
print("areas_ha sample:", [round(a, 2) for a in areas[:10]],
      "..." if len(areas) > 10 else "")
print("conf sample:", [p["confidence"] for p in polys[:10]])
from collections import Counter
print("features:", Counter(tuple(p["detected_features"]) for p in polys))
