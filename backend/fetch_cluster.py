"""Refetch pilot parcels: Tarbujapur (Mudkhed taluka) - 10-20 PARCELS.

Current Nilkanthwadi bundle covers the whole village bbox (~1.5km wide with
VILLAGE CENTROID MISMATCH: imagery was fetched at site.yaml lat/lon which was
just the old Shinde Nashik location; the 25 tiles at z18 cover ~770m but the
Nilkanthwadi parcels spread wider. This script:
  1. Loads nanded.geojson.gz, takes Tarbujapur parcels.
  2. Picks a compact cluster of 10-16 SMALL parcels (<=6 ha declared, small geom
     areas) closest together (greedy nearest-neighbour growth).
  3. Writes backend/data/real_parcels.json.
  4. Prints the cluster centroid -> caller updates backend/config/site.yaml.
"""
import gzip
import json
import math

GZ = "backend/data/nanded.geojson.gz"
OUT = "backend/data/real_parcels.json"
GIS = "RVM1507271500070197380000"  # Tarbujapur, Mudkhed taluka
TARGET = 14  # aim for ~14 parcels (10-20 band, imagery-tight)


def ring_area_ha(coords, lat0):
    s = 0.0
    m_lon = 111320.0 * math.cos(math.radians(lat0))
    for i in range(len(coords) - 1):
        x0, y0 = coords[i][0] * m_lon, coords[i][1] * 110540.0
        x1, y1 = coords[i + 1][0] * m_lon, coords[i + 1][1] * 110540.0
        s += x0 * y1 - x1 * y0
    return abs(s) / 2 / 10000.0


with gzip.open(GZ, "rt", encoding="utf-8") as fh:
    feats = json.load(fh)["features"]

vil = [f for f in feats
       if f["properties"].get("village_giscode") == GIS
       and f.get("geometry") and f["geometry"]["type"] == "Polygon"]
print("Tarbujapur polygon parcels:", len(vil))

lat_all = sum(c[1] for f in vil for c in f["geometry"]["coordinates"][0])
lat_all /= sum(len(f["geometry"]["coordinates"][0]) for f in vil)

# candidate small parcels: declared area 0.3..6 ha AND geom area <= 8 ha
cands = []
for f in vil:
    p = f["properties"]
    try:
        decl = float(p.get("area_hectares") or 0)
    except (TypeError, ValueError):
        decl = 0
    ga = ring_area_ha(f["geometry"]["coordinates"][0], lat_all)
    if 0.3 <= decl <= 6.0 and ga <= 8.0:
        cx = sum(c[0] for c in f["geometry"]["coordinates"][0])
        cx /= len(f["geometry"]["coordinates"][0])
        cy = sum(c[1] for f in f["geometry"]["coordinates"][0] for _ in [0]) \
            if False else sum(c[1] for c in f["geometry"]["coordinates"][0])
        cy /= len(f["geometry"]["coordinates"][0])
        cands.append((f, cx, cy, decl, ga))
print("small-parcel candidates:", len(cands))
for f, cx, cy, decl, ga in sorted(cands, key=lambda t: t[3]):
    print("  survey=%s decl=%.2f geom=%.2f @ %.5f,%.5f"
          % (f["properties"].get("survey_no"), decl, ga, cy, cx))


def mdist(a, b, lat0):
    return math.hypot((a[0] - b[0]) * 111320.0 * math.cos(math.radians(lat0)),
                      (a[1] - b[1]) * 110540.0)


# greedy growth: start from the pair with min distance, add nearest each step
best = None
for s in range(len(cands)):
    chosen, rest = [s], [i for i in range(len(cands)) if i != s]
    while len(chosen) < TARGET and rest:
        last = cands[chosen[-1]]
        nxt = min(rest, key=lambda i: mdist((cands[i][1], cands[i][2]),
                                            (last[1], last[2]), lat_all))
        chosen.append(nxt)
        rest.remove(nxt)
    pts = [(cands[i][1], cands[i][2]) for i in chosen]
    span = max(max(p[0] for p in pts) - min(p[0] for p in pts),
               max(p[1] for p in pts) - min(p[1] for p in pts)) * 110540.0
    if best is None or span < best[0]:
        best = (span, chosen)
span, chosen = best
keep = [cands[i][0] for i in chosen]
print("cluster: n=%d span=%.0fm" % (len(keep), span))

lon = sum(cands[i][1] for i in chosen) / len(chosen)
lat = sum(cands[i][2] for i in chosen) / len(chosen)
print("cluster centroid: %.5f, %.5f" % (lat, lon))
print("survey_nos:", sorted(f["properties"].get("survey_no") for f in keep))
out = {
    "district": "Nanded", "taluka": "Mudkhed",
    "village": keep[0]["properties"].get("village"),
    "village_giscode": GIS, "lon": lon, "lat": lat,
    "source": ("https://mahabhunakasha.mahabhumi.gov.in/ via "
               "huggingface.co/datasets/Ashutosh99/"
               "maharashtra-cadastral-tier-a (Tier A, ODbL-1.0)"),
    "licence": "ODbL-1.0",
    "features": keep,
}
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(out, fh)
import os
print("wrote", OUT, os.path.getsize(OUT), "bytes")
