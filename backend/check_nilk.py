"""One-off: nilkanthwadi detail — sizes, contiguity, Esri z18/z19 tile check."""
import gzip
import io
import json
import math

import numpy as np
import requests
from PIL import Image
from shapely.geometry import shape

GZ = "backend/data/nanded.geojson.gz"
GIS = "RVM1504271500040195420000"
with gzip.open(GZ, "rt", encoding="utf-8") as fh:
    feats = [f for f in json.load(fh)["features"]
             if f["properties"].get("village_giscode") == GIS
             and f["properties"].get("geom_kind") == "polygon"]
print("n:", len(feats))
for f in feats:
    g = shape(f["geometry"])
    print(f"  survey={f['properties']['survey_no']} "
          f"decl={f['properties']['area_hectares']} geom_ha="
          f"{g.area * (111320 * math.cos(math.radians(19.3))) * 110540 / 1e4:.2f} "
          f"valid={g.is_valid} nvert={len(g.exterior.coords)} "
          f"ctr={g.centroid.y:.5f},{g.centroid.x:.5f}")
geoms = [shape(f["geometry"]) for f in feats]
n_touch = sum(1 for i in range(len(geoms)) for j in range(i + 1, len(geoms))
              if geoms[i].touches(geoms[j]) or geoms[i].overlaps(geoms[j]))
print("touching/overlapping pairs:", n_touch)
lons = [c[0] for g in geoms for c in g.exterior.coords]
lats = [c[1] for g in geoms for c in g.exterior.coords]
print("bbox lon", round(min(lons), 5), round(max(lons), 5),
      "lat", round(min(lats), 5), round(max(lats), 5))
cx, cy = sum(lons) / len(lons), sum(lats) / len(lats)
print("centroid", round(cy, 5), round(cx, 5))

UA = {"User-Agent": "RuralLandResurveyTriage/0.1"}
T = ("https://services.arcgisonline.com/ArcGIS/rest/services/"
     "World_Imagery/MapServer/tile/{z}/{y}/{x}")
for z in (18, 19):
    nn = 2 ** z
    xf = (cx + 180.0) / 360.0 * nn
    yf = (1 - math.asinh(math.tan(math.radians(cy))) / math.pi) / 2.0 * nn
    xi, yi = int(xf), int(yf)
    r = requests.get(T.format(z=z, x=xi, y=yi), timeout=30, headers=UA)
    im = Image.open(io.BytesIO(r.content)).convert("RGB")
    a = np.asarray(im)
    print(f"z{z} tile {xi}/{yi}: {r.status_code} {len(r.content)}b std="
          f"{a.std():.1f} mean={a.mean(axis=(0, 1)).round(0)}")
    im.save(f"tmp_chips/nilkanthwadi_z{z}.png")
print("saved tmp_chips/nilkanthwadi_z{z}.png")
