"""Match CV Tier-2 polygons to REAL Bhu-Naksha parcels and report."""
from __future__ import annotations

import json
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parent
sys.path.insert(0, str(BACKEND))

from app.config import load_triage_config  # noqa: E402
from app.pipeline import matching  # noqa: E402
from app.pipeline.extract import extract_tier2  # noqa: E402
from app.raster import WorldFileAffine, load_png  # noqa: E402
from app.seed import village as village_mod  # noqa: E402

VILLAGE_ID = "VIL-PILOT"
site_lat = 19.88471

img = load_png(BACKEND / "data" / "imagery" / "VIL-PILOT_ortho.png")
aff = WorldFileAffine.read_world_file(
    BACKEND / "data" / "imagery" / "VIL-PILOT_ortho.pgw")
cfg = load_triage_config()
res_m = aff.resolution_m_per_px(site_lat)
polys = extract_tier2(img, aff, cfg, res_m)
print(f"CV polygons: {len(polys)}")

real = village_mod.real_design(VILLAGE_ID)
design, _layout, parcel_meta = real
parcels = village_mod.parcel_rows(
    design, VILLAGE_ID, 42, "2026-09-27T00:00:00+00:00", parcel_meta)
print(f"parcels: {len(parcels)}")

matches = matching.match_parcels(parcels, polys, cfg)
from collections import Counter
print("match types:", Counter(m["match_type"] for m in matches))
shown = 0
for m in matches:
    if m["match_type"] != "NO_MATCH" and shown < 15:
        print(f"  {m['parcel_id']} -> {m['match_type']} "
              f"conf={m['match_confidence']} polys={m['field_polygon_ids']}")
        shown += 1
