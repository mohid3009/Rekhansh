"""Download real Nanded cadastral GeoJSON (Bhu-Naksha via HF, Tier A, ODbL-1.0)
and select ONE village with >=12 real polygon parcels in a compact cluster.

Writes backend/data/real_parcels.json for the village seeder to consume.
"""
import gzip
import io
import json
import math
import urllib.request
from collections import defaultdict

BASE = ("https://huggingface.co/datasets/Ashutosh99/"
        "maharashtra-cadastral-tier-a/resolve/main")
OUT = "backend/data/real_parcels.json"


def bounds_of(geom):
    xs, ys = [], []
    if geom["type"] == "Polygon":
        rings = geom["coordinates"]
    elif geom["type"] == "MultiPolygon":
        rings = [r for poly in geom["coordinates"] for r in poly]
    else:
        return None
    for ring in rings:
        for x, y in ring:
            xs.append(x)
            ys.append(y)
    return (min(xs), min(ys), max(xs), max(ys)) if xs else None


def main():
    print("downloading nanded.geojson.gz ...", flush=True)
    req = urllib.request.Request(BASE + "/nanded.geojson.gz",
                                 headers={"User-Agent": "sih-demo/1.0"})
    raw = urllib.request.urlopen(req, timeout=300).read()
    print("bytes:", len(raw), flush=True)
    fc = json.loads(gzip.decompress(raw).decode("utf-8"))
    feats = fc["features"]
    print("total features:", len(feats), flush=True)

    per_village = defaultdict(list)
    for f in feats:
        p = f["properties"]
        if p.get("geom_kind") != "polygon":
            continue
        g = f["geometry"]
        if not g or g["type"] not in ("Polygon", "MultiPolygon"):
            continue
        b = bounds_of(g)
        if not b:
            continue
        key = (p.get("district"), p.get("taluka"),
               p.get("village"), p.get("village_giscode"))
        per_village[key].append((f, b))

    print("villages with polygon geometry:", len(per_village), flush=True)

    # candidate villages: >=10 parcels, compact (all centroids within ~1.2km box)
    cands = []
    for key, items in per_village.items():
        if len(items) < 10:
            continue
        cx = [(b[0] + b[2]) / 2 for _, b in items]
        cy = [(b[1] + b[3]) / 2 for _, b in items]
        lat0 = sum(cy) / len(cy)
        dx = (max(cx) - min(cx)) * 111320.0 * math.cos(math.radians(lat0))
        dy = (max(cy) - min(cy)) * 110540.0
        span = max(dx, dy)
        if span <= 1200:
            cands.append((len(items), int(span), key))
    cands.sort(reverse=True)
    print("compact candidates (>=10 parcels, span<=1200m):", len(cands))
    for n, span, key in cands[:20]:
        print("  n=%d span=%dm %s / %s / %s (%s)" % (n, span, *key))

    if not cands:
        raise SystemExit("no compact village found")

    n, span, key = cands[0]
    items = per_village[key]
    # keep parcels closest to the village centroid for a tight pilot cluster
    cx = [(b[0] + b[2]) / 2 for _, b in items]
    cy = [(b[1] + b[3]) / 2 for _, b in items]
    lon0, lat0 = sum(cx) / len(cx), sum(cy) / len(cy)
    items.sort(key=lambda t: ((t[1][0] + t[1][2]) / 2 - lon0) ** 2
               + ((t[1][1] + t[1][3]) / 2 - lat0) ** 2)
    keep = items[:min(24, len(items))]
    feats_out = [f for f, _ in keep]
    lon = sum((b[0] + b[2]) / 2 for _, b in keep) / len(keep)
    lat = sum((b[1] + b[3]) / 2 for _, b in keep) / len(keep)
    out = {
        "district": key[0], "taluka": key[1], "village": key[2],
        "village_giscode": key[3], "lon": lon, "lat": lat,
        "source": "https://mahabhunakasha.mahabhumi.gov.in/ via "
                  "huggingface.co/datasets/Ashutosh99/"
                  "maharashtra-cadastral-tier-a (Tier A, ODbL-1.0)",
        "licence": "ODbL-1.0",
        "features": feats_out,
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh)
    import os
    print("wrote", OUT, os.path.getsize(OUT), "bytes:",
          len(feats_out), "parcels @", round(lon, 5), round(lat, 5), flush=True)


main()
