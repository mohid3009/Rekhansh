"""One-off: build pilot village from REAL Nanded cadastral data.

Strategy (keeps the demo's cluster coherence requirement from the design
review): for each candidate village, rank its REAL parcels by distance to the
village centroid and take the 18 most central ones -> compact, contiguous,
real-geometry pilot cluster. Prints compactness/size stats + saves
backend/data/pilot_village_real.geojson (real) and regenerates
backend/data/pilot_village_raw.json (the 30-row scouting extract format is
replaced by the adopted-village extract).
"""
import gzip
import json
import math

PATH = "backend/data/nanded.geojson.gz"

TARGETS = [
    "RVM1501271500010190910000",  # Mahur / bond gavhan (30 parcels)
    "RVM1501271500010190320000",  # Mahur / shekapur (29)
    "RVM1501271500010190920000",  # Mahur / choufuli (29)
    "RVM1503271500030193510000",  # Himayatnagar / pahunmari (27)
    "RVM1504271500040195450000",  # Hadgaon / mandva (26)
    "RVM1505271500040194770000",  # Ardhapur / rodgi (25)
]


def ring_area_m2(ring, lat0):
    s = 0.0
    kx = 111320.0 * math.cos(math.radians(lat0))
    ky = 110540.0
    for (x1, y1), (x2, y2) in zip(ring, ring[1:]):
        s += (x1 * kx) * (y2 * ky) - (x2 * kx) * (y1 * ky)
    return abs(s) / 2.0


print("loading features ...", flush=True)
with gzip.open(PATH, "rt", encoding="utf-8") as fh:
    fc = json.load(fh)
print("features:", len(fc["features"]), flush=True)

by_village: dict[str, list] = {}
for ft in fc["features"]:
    p = ft.get("properties", {}) or {}
    g = ft.get("geometry") or {}
    if g.get("type") != "Polygon" or p.get("geom_kind") != "polygon":
        continue
    if p.get("village_giscode") in TARGETS:
        by_village.setdefault(p["village_giscode"], []).append(ft)

for gis, feats in by_village.items():
    p0 = feats[0]["properties"]
    print(f"\n=== {p0['taluka']} / {p0['village']} gis={gis}: "
          f"{len(feats)} polygon parcels ===")
    # centroid of village bbox
    xs = [c[0] for ft in feats for r in ft["geometry"]["coordinates"]
          for c in r]
    ys = [c[1] for ft in feats for r in ft["geometry"]["coordinates"]
          for c in r]
    cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
    kx = 111320.0 * math.cos(math.radians(cy))
    # rank parcels by centroid distance to village centroid
    scored = []
    for ft in feats:
        ring = ft["geometry"]["coordinates"][0]
        px = sum(c[0] for c in ring) / len(ring)
        py = sum(c[1] for c in ring) / len(ring)
        d = math.hypot((px - cx) * kx, (py - cy) * 110540.0)
        scored.append((d, ft))
    scored.sort(key=lambda t: t[0])
    for take in (18,):
        sel = [ft for _, ft in scored[:take]]
        sx = [c[0] for ft in sel for r in ft["geometry"]["coordinates"]
              for c in r]
        sy = [c[1] for ft in sel for r in ft["geometry"]["coordinates"]
              for c in r]
        lat0 = sum(sy) / len(sy)
        span = max((max(sy) - min(sy)) * 110540.0,
                   (max(sx) - min(sx)) * 111320.0
                   * math.cos(math.radians(lat0)))
        areas = [ring_area_m2(ft["geometry"]["coordinates"][0], lat0)
                 for ft in sel]
        srt = sorted(areas)
        print(f"  central-{take}: span={int(span)}m "
              f"med={int(srt[len(srt)//2])}m2 "
              f"min={int(srt[0])} max={int(srt[-1])} "
              f"centroid=({sum(sy)/len(sy):.5f},{sum(sx)/len(sx):.5f})")
        print(f"  surveys: {[ft['properties']['survey_no'] for ft in sel]}")


