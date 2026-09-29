"""One-off: span report for all 10-30 parcel villages + check Fieldscapes/FTW
overlap with Bond Gavhan (do real ML boundaries cover our pilot?)."""
import gzip
import json
import math
from collections import defaultdict

import pyarrow.parquet as pq
from shapely.geometry import shape

GZ = "backend/data/nanded.geojson.gz"
print("loading nanded geojson ...")
with gzip.open(GZ, "rt", encoding="utf-8") as fh:
    feats = json.load(fh)["features"]
print("total", len(feats))
polys = [f for f in feats if f["properties"].get("geom_kind") == "polygon"]
per = defaultdict(list)
for f in polys:
    p = f["properties"]
    per[(p.get("taluka"), p.get("village"), p.get("village_giscode"))].append(f)

print("=== villages with 10-30 polygon parcels, sorted by span ===")
rows = []
for key, items in per.items():
    if not 10 <= len(items) <= 30:
        continue
    lons = [c[0] for f in items for c in f["geometry"]["coordinates"][0]]
    lats = [c[1] for f in items for c in f["geometry"]["coordinates"][0]]
    lat0 = sum(lats) / len(lats)
    span = max((max(lons) - min(lons)) * 111320.0 * math.cos(math.radians(lat0)),
               (max(lats) - min(lats)) * 110540.0)
    areas = [float(f["properties"].get("area_hectares") or 0) for f in items]
    rows.append((span, len(items), key, sum(lons) / len(lons),
                 sum(lats) / len(lats), min(areas), max(areas)))
rows.sort()
for span, n, (tal, vil, gis), lon, lat, a0, a1 in rows:
    print(f"  span={span:5.0f}m n={n:2d} {tal}/{vil} @ {lat:.5f},{lon:.5f} "
          f"area {a0:.2f}-{a1:.2f} gis={gis}")

# Bond Gavhan bbox for overlap checks
BG = [f for f in polys
      if f["properties"].get("village_giscode") == "RVM1501271500010190910000"]
lons = [c[0] for f in BG for c in f["geometry"]["coordinates"][0]]
lats = [c[1] for f in BG for c in f["geometry"]["coordinates"][0]]
BG_BBOX = (min(lons), min(lats), max(lons), max(lats))
print("Bond Gavhan bbox:", [round(v, 5) for v in BG_BBOX])

# Fieldscapes india 10k near Bond Gavhan?
t = pq.read_table("backend/data/india_fields_2016.parquet",
                  columns=["id", "area", "geometry"])
wl = t.column("geometry").to_pylist()
near, total = 0, len(wl)
for w in wl:
    try:
        g = shape({"type": "Polygon", "coordinates": None}) if False else None
        import shapely
        g = shapely.from_wkb(w)
        b = g.bounds  # minx, miny, maxx, maxy
        if (b[2] >= BG_BBOX[0] and b[0] <= BG_BBOX[2]
                and b[3] >= BG_BBOX[1] and b[1] <= BG_BBOX[3]):
            near += 1
    except Exception:
        pass
print(f"Fieldscapes polygons intersecting Bond Gavhan bbox: {near} / {total}")

# where are Fieldscapes polygons concentrated? sample centroids
import random
random.seed(1)
idx = random.sample(range(total), min(total, 3000))
import shapely
cxs, cys = [], []
for i in idx:
    g = shapely.from_wkb(wl[i])
    c = g.centroid
    cxs.append(c.x)
    cys.append(c.y)
print("Fieldscapes sample lon range", round(min(cxs), 2), round(max(cxs), 2),
      "lat range", round(min(cys), 2), round(max(cys), 2))
# any within 50km of Bond Gavhan?
n50 = sum(1 for x, y in zip(cxs, cys)
          if abs(x - 78.09) * 105 < 50 and abs(y - 19.88) * 110.5 < 50)
print("Fieldscapes sample within ~50km of Bond Gavhan:", n50, "/ 3000")
