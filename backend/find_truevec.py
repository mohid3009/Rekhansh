"""Find villages with TRUE vectorized polygons (geom_kind == 'polygon' + non-rectangular)."""
import gzip
import json
import math
from collections import defaultdict

import numpy as np

with gzip.open("backend/data/nanded.geojson.gz", "rt", encoding="utf-8") as fh:
    fc = json.load(fh)
feats = fc["features"]

vec = [f for f in feats if f["properties"].get("geom_kind") == "polygon"
       and f.get("geometry") and f["geometry"]["type"] == "Polygon"]
print("geom_kind=polygon features:", len(vec))


def is_rect(coords, tol=1e-9):
    if len(coords) != 5:
        return False
    xs = [c[0] for c in coords[:4]]
    ys = [c[1] for c in coords[:4]]
    return len(set(round(x, 9) for x in xs)) == 2 and len(set(round(y, 9) for y in ys)) == 2


n_rect = sum(1 for f in vec if is_rect(f["geometry"]["coordinates"][0]))
print("of which axis-aligned rectangles:", n_rect)

truevec = [f for f in vec if not is_rect(f["geometry"]["coordinates"][0])]
print("true vectorized (non-rect) polygons:", len(truevec))

by_vil = defaultdict(list)
for f in truevec:
    p = f["properties"]
    by_vil[(p.get("taluka"), p.get("village"), p.get("village_giscode"))].append(f)
print("villages with true polygons:", len(by_vil))
sizes = sorted(((len(v), k) for k, v in by_vil.items()), reverse=True)
print("top 20 by true-polygon count:")
for n, k in sizes[:20]:
    print(f"  n={n} taluka={k[0]} village={k[1]} gis={k[2]}")

cands = []
for n, k in sizes:
    if 8 <= n <= 80:
        lons, lats = [], []
        for f in by_vil[k]:
            for lon, lat in f["geometry"]["coordinates"][0]:
                lons.append(lon)
                lats.append(lat)
        lat0 = sum(lats) / len(lats)
        span = max((max(lons) - min(lons)) * 111320.0 * math.cos(math.radians(lat0)),
                   (max(lats) - min(lats)) * 110540.0)
        cands.append((span, n, k))
cands.sort()
print("most compact 8-80 true-polygon villages:")
for span, n, k in cands[:20]:
    print(f"  span={span:.0f}m n={n} taluka={k[0]} village={k[1]} gis={k[2]}")
