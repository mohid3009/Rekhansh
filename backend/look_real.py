"""Quick look: real Nilkanthwadi parcels over the fresh orthomosaic."""
import json
import sys

sys.path.insert(0, "backend")
from app.seed.fetch_imagery import load_cached
from app.raster import WorldFileAffine

pack = load_cached("VIL-PILOT")
img, aff = pack["image"], pack["affine"]
print("img", img.shape, "res_cm", pack["resolution_cm_per_px"])
print("bounds", pack["bounds"])

d = json.load(open("backend/data/real_parcels.json"))
print("parcels:", len(d["features"]))

import numpy as np
from PIL import Image

h, w, _ = img.shape
thumb = Image.fromarray(img).resize((w // 2, h // 2))
tp = np.asarray(thumb)
print("mean rgb", tp.mean(axis=(0, 1)).round(1), "std", tp.std().round(1))
Image.fromarray(img).save("backend/data/imagery/VIL-PILOT_ortho_full.png")
thumb.save("backend/data/imagery/VIL-PILOT_ortho_thumb.png")

# per-parcel pixel footprint check
import shapely.ops as ops
from shapely.geometry import shape


def to_px(lon, lat):
    return aff.lonlat_to_px(lon, lat)


inside = 0
for f in d["features"]:
    g = shape(f["geometry"])
    minx, miny, maxx, maxy = g.bounds
    x0, y0 = to_px(minx, maxy)
    x1, y1 = to_px(maxx, miny)
    cx = (x0 + x1) / 2
    cy = (y0 + y1) / 2
    ok = 0 <= cx < w and 0 <= cy < h
    inside += ok
    print(" survey=%s area_ha=%s centroid_px=(%.0f,%.0f) inside=%s"
          % (f["properties"]["survey_no"],
             f["properties"]["area_hectares"], cx, cy, ok))
print("centroids inside image:", inside, "/", len(d["features"]))
