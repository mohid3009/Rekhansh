"""Overlay REAL parcels (red) + CV polygons (cyan) on the REAL orthomosaic."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

BACKEND = Path(__file__).resolve().parent
sys.path.insert(0, str(BACKEND))

from app.config import load_triage_config  # noqa: E402
from app.pipeline.extract import extract_tier2  # noqa: E402
from app.raster import WorldFileAffine, load_png  # noqa: E402
from app.seed import village as village_mod  # noqa: E402
from shapely.geometry import shape  # noqa: E402

VILLAGE_ID = "VIL-PILOT"
img = load_png(BACKEND / "data" / "imagery" / "VIL-PILOT_ortho.png")
aff = WorldFileAffine.read_world_file(
    BACKEND / "data" / "imagery" / "VIL-PILOT_ortho.pgw")
cfg = load_triage_config()
polys = extract_tier2(img, aff, cfg, aff.resolution_m_per_px(19.8847))
print(f"CV: {len(polys)}")

real = village_mod.real_design(VILLAGE_ID)
design, _layout, parcel_meta = real
rec_ha = {m["survey_number"]: m["recorded_area_ha"] for m in parcel_meta}
print("recorded ha all:", sorted(rec_ha.values()))


def to_px(geom) -> list[tuple[float, float]]:
    ring = shape(geom).exterior.coords
    out = []
    for lon, lat in ring:
        c, r = aff.lonlat_to_px(lon, lat)
        out.append((c, r))
    return out


base = Image.fromarray(img).convert("RGB")
ov = Image.new("RGBA", base.size, (0, 0, 0, 0))
d = ImageDraw.Draw(ov, "RGBA")
for g in design:
    pts = to_px(g)
    d.polygon(pts, outline=(255, 30, 30, 255), width=4)
for p in polys:
    pts = to_px(p["geometry"])
    d.polygon(pts, outline=(0, 220, 255, 255), width=2)
combo = Image.alpha_composite(base.convert("RGBA"), ov).convert("RGB")
combo.save("tmp_real_overlay_full.png")

# zoom crop around parcel bounding box
allx = [c for g in design for c, r in to_px(g)]
ally = [r for g in design for c, r in to_px(g)]
x0, x1 = max(0, int(min(allx)) - 80), min(base.size[0], int(max(allx)) + 80)
y0, y1 = max(0, int(min(ally)) - 80), min(base.size[1], int(max(ally)) + 80)
print(f"crop x[{x0},{x1}] y[{y0},{y1}]")
combo.crop((x0, y0, x1, y1)).save("tmp_real_overlay_crop.png")
combo.crop((x0, y0, x1, y1)).resize((1152, 768)).save("tmp_real_overlay_small.png")
print("saved overlays")
