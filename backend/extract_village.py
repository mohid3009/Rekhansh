"""Extract 10-30 real parcels for ONE pilot village + contiguity/area report.

Streams the gz file, keeps only features of the target village_giscode, and
writes the village subset to backend/data/pilot_village_real.geojson.
Checks: polygon validity, contiguity (queen), real surveyed areas, bbox span.
"""
import gzip
import json
import sys

import shapely
from shapely.geometry import shape

GIS = sys.argv[1] if len(sys.argv) > 1 else "RVM1501271500010190910000"  # Bond Gavhan
MAXN = int(sys.argv[2]) if len(sys.argv) > 2 else 30
PATH = "backend/data/nanded.geojson.gz"
OUT = "backend/data/pilot_village_real.geojson"

kept = []
with gzip.open(PATH, "rt", encoding="utf-8") as fh:
    header = fh.readline()  # {"type":"FeatureCollection","features":[
    for line in fh:
        line = line.strip().rstrip(",").rstrip("]")
        if not line.startswith('{"type":"Feature"'):
            if line.startswith("]"):
                break
            continue
        try:
            feat = json.loads(line)
        except json.JSONDecodeError:
            continue
        p = feat.get("properties", {})
        if p.get("village_giscode") != GIS:
            continue
        if p.get("geom_kind") != "polygon":
            continue
        try:
            g = shape(feat["geometry"])
        except Exception:
            continue
        if g.geom_type != "Polygon" or g.area <= 0:
            continue
        kept.append(feat)
        if len(kept) >= MAXN:
            pass  # keep scanning to count total, but cap stored

print(f"village parcels with polygon geometry: {len(kept)} (capped store {MAXN})")
vil = kept[0]["properties"]["village"]
tal = kept[0]["properties"]["taluka"]
print(f"village={vil} taluka={tal} district=Nanded")
store = kept[:MAXN]
geoms = [shape(f["geometry"]) for f in store]
print("survey_nos:", [f["properties"]["survey_no"] for f in store])
areas_ha = [f["properties"].get("area_hectares") for f in store]
print("recorded area_hectares:", areas_ha)
# validity + contiguity
print("all valid:", all(g.is_valid for g in geoms))
n_touch = sum(1 for i in range(len(geoms)) for j in range(i + 1, len(geoms))
              if geoms[i].touches(geoms[j]) or geoms[i].intersects(geoms[j]))
print(f"touching/intersecting pairs: {n_touch}")
xs = [c[0] for g in geoms for c in g.exterior.coords]
ys = [c[1] for g in geoms for c in g.exterior.coords]
print(f"bbox: lon [{min(xs):.5f},{max(xs):.5f}] lat [{min(ys):.5f},{max(ys):.5f}]")
print(f"span: {(max(xs)-min(xs))*105000:.0f}m x {(max(ys)-min(ys))*110600:.0f}m")
ctr = (sum(xs) / len(xs), sum(ys) / len(ys))
print(f"centroid: {ctr[1]:.5f},{ctr[0]:.5f}")
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump({"type": "FeatureCollection", "features": store}, fh)
print(f"wrote {OUT} ({len(store)} features)")
