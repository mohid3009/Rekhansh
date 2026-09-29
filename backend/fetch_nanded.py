"""Download Nanded cadastral GeoJSON (real Bhu-Naksha, ODbL-1.0) and find a
compact 10-30 parcel village cluster for the pilot."""
import gzip
import json
import math
import os
from collections import defaultdict

import requests

BASE = "https://huggingface.co/datasets/Ashutosh99/maharashtra-cadastral-tier-a/resolve/main"
OUT = "backend/data/nanded.geojson.gz"

os.makedirs("backend/data", exist_ok=True)
if not os.path.exists(OUT):
    print("downloading nanded.geojson.gz (~34MB)...", flush=True)
    r = requests.get(f"{BASE}/nanded.geojson.gz", timeout=300, stream=True)
    print("status", r.status_code)
    r.raise_for_status()
    with open(OUT, "wb") as fh:
        for chunk in r.iter_content(chunk_size=1 << 20):
            if chunk:
                fh.write(chunk)
    print("saved", os.path.getsize(OUT))
else:
    print("cached", os.path.getsize(OUT))

print("reading features...", flush=True)
with gzip.open(OUT, "rt", encoding="utf-8") as fh:
    fc = json.load(fh)
feats = fc["features"]
print("total features", len(feats))
print("sample props", json.dumps(feats[0]["properties"], ensure_ascii=False)[:600])
print("sample geom type", feats[0]["geometry"]["type"] if feats[0].get("geometry") else None)

# filter polygon geometries only
polys = [f for f in feats if f.get("geometry") and f["geometry"]["type"] in ("Polygon", "MultiPolygon")]
print("polygon features", len(polys))
# group by village
by_vil = defaultdict(list)
for f in polys:
    p = f["properties"]
    key = (p.get("taluka"), p.get("village"), p.get("village_giscode"))
    by_vil[key].append(f)
print("villages with polygons", len(by_vil))
# stats on village sizes
sizes = sorted(((len(v), k) for k, v in by_vil.items()), reverse=True)
print("top 15 villages by polygon count:")
for n, k in sizes[:15]:
    print(f"  n={n} taluka={k[0]} village={k[1]} gis={k[2]}")

# for villages with 10-60 polygons, compute compactness (bbox span)
cands = []
for n, k in sizes:
    if 10 <= n <= 60:
        feats_v = by_vil[k]
        lons, lats = [], []
        for f in feats_v:
            g = f["geometry"]
            coords = g["coordinates"][0] if g["type"] == "Polygon" else g["coordinates"][0][0]
            for lon, lat in coords:
                lons.append(lon)
                lats.append(lat)
        lat0 = sum(lats) / len(lats)
        span_x = (max(lons) - min(lons)) * 111320.0 * math.cos(math.radians(lat0))
        span_y = (max(lats) - min(lats)) * 110540.0
        span = max(span_x, span_y)
        cands.append((span, n, k))
cands.sort()
print("most compact 10-60 parcel villages (span m):")
for span, n, k in cands[:15]:
    print(f"  span={span:.0f}m n={n} taluka={k[0]} village={k[1]} gis={k[2]}")
