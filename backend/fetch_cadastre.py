"""One-off: download Nanded cadastral GeoJSON, index polygon villages, score each
for pilot suitability (compact 10-30 parcel cluster). Streams the gzip in
chunks; parses features incrementally to avoid loading 35MB JSON at once."""
import gzip
import json
import math
import sys
from collections import defaultdict

import numpy as np
import requests

URL = ("https://huggingface.co/datasets/Ashutosh99/maharashtra-cadastral-tier-a"
       "/resolve/main/nanded.geojson.gz")
OUT = "backend/data/nanded.geojson.gz"

# --- download with progress ---
r = requests.get(URL, stream=True, timeout=120)
r.raise_for_status()
total = int(r.headers.get("content-length", "0"))
got = 0
with open(OUT, "wb") as fh:
    for chunk in r.iter_content(chunk_size=1 << 20):
        fh.write(chunk)
        got += len(chunk)
        print(f"\rdownload {got/1e6:.1f} / {total/1e6:.1f} MB", end="", flush=True)
print("\ndownloaded", got, "bytes")


def feats(path):
    """Yield (props, ring) for polygon features using incremental decode."""
    dec = json.JSONDecoder()
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        buf = fh.read()
    print("decompressed chars:", len(buf))
    # find features array; decode object by object via raw_decode on each
    # '{"type":"Feature"' occurrence
    idx = 0
    n = 0
    while True:
        i = buf.find('{"type":"Feature"', idx)
        if i < 0:
            break
        try:
            obj, end = dec.raw_decode(buf, i)
        except json.JSONDecodeError:
            idx = i + 1
            continue
        idx = end
        n += 1
        if n % 50000 == 0:
            print("parsed", n)
        try:
            g = obj.get("geometry") or {}
            if g.get("type") != "Polygon":
                continue
            coords = g.get("coordinates") or []
            if not coords or not coords[0]:
                continue
            yield obj.get("properties") or {}, coords[0]
        except Exception:
            continue
    print("total features parsed:", n)


villages = defaultdict(list)   # giscode -> list of (area_ha, cx, cy, survey_no)
for props, ring in feats(OUT):
    if props.get("geom_kind") != "polygon" or not props.get("has_geometry"):
        continue
    try:
        xs = [p[0] for p in ring]
        ys = [p[1] for p in ring]
    except Exception:
        continue
    if len(xs) < 4:
        continue
    cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
    # shoelace in degrees -> approx m2
    s = 0.0
    for k in range(len(xs) - 1):
        s += xs[k] * ys[k + 1] - xs[k + 1] * ys[k]
    area_m2 = abs(s) / 2 * 111320.0 * math.cos(math.radians(cy)) * 110540.0
    villages[props.get("village_giscode", "?")].append(
        (area_m2 / 10000.0, cx, cy, str(props.get("survey_no", "?")),
         props.get("village", "?"), props.get("taluka", "?")))

print("polygon villages:", len(villages))
rows = []
for code, plist in villages.items():
    n = len(plist)
    if n < 8 or n > 60:
        continue
    areas = np.array([p[0] for p in plist])
    cxs = np.array([p[1] for p in plist])
    cys = np.array([p[2] for p in plist])
    span = max((cxs.max() - cxs.min()) * 111320.0 * math.cos(math.radians(cys.mean())),
               (cys.max() - cys.min()) * 110540.0)
    med = float(np.median(areas))
    # compactness: fraction of parcels within 300m of village centroid
    dx = (cxs - cxs.mean()) * 111320.0 * math.cos(math.radians(cys.mean()))
    dy = (cys - cys.mean()) * 110540.0
    core = int(((dx * dx + dy * dy) <= 300.0 ** 2).sum())
    rows.append((core, n, round(med, 2), int(span), code,
                 plist[0][4], plist[0][5]))
rows.sort(reverse=True)
print("villages 8-60 parcels:", len(rows))
for core, n, med, span, code, vname, taluka in rows[:25]:
    print(f"core={core} n={n} medHa={med} span={span}m {taluka}/{vname} {code}")
