"""One-off: survey compactness of the 10-30-parcel polygon villages."""
import gzip
import json
import math

SRC = "backend/data/nanded.geojson.gz"


def load():
    with gzip.open(SRC, "rt", encoding="utf-8") as fh:
        return json.load(fh)["features"]


feats = load()
by_v: dict[str, list] = {}
for x in feats:
    p = x.get("properties", {})
    if x.get("geometry") and p.get("geom_kind") == "polygon":
        by_v.setdefault(p.get("village_giscode"), []).append(x)

print("villages10-30 detail:")
for gis in ["RVM1504271500040195420000", "RVM1504271500040194210000",
            "RVM1504271500040194790000", "RVM1502271500020191650000",
            "RVM1501271500010190310000", "RVM1501271500010191220000",
            "RVM1504271500040194760000", "RVM1502271500020192240000",
            "RVM1501271500010191180000", "RVM1504271500040194770000",
            "RVM1505271500040194770000", "RVM1504271500040195450000",
            "RVM1503271500030193510000", "RVM1501271500010190320000",
            "RVM1501271500010190920000", "RVM1501271500010190910000"]:
    v = by_v[gis]
    p0 = v[0]["properties"]
    lons = [c[0] for f in v for c in f["geometry"]["coordinates"][0]]
    lats = [c[1] for f in v for c in f["geometry"]["coordinates"][0]]
    lat0 = sum(lats) / len(lats)
    span_m = max((max(lons) - min(lons)) * 111320.0 * math.cos(math.radians(lat0)),
                 (max(lats) - min(lats)) * 110540.0)
    gaps = 0
    for f in v:
        xs = [c[0] for c in f["geometry"]["coordinates"][0]]
        ys = [c[1] for c in f["geometry"]["coordinates"][0]]
        gaps += len(xs) - 1
    areas = sorted(f["properties"].get("area_hectares") or 0 for f in v)
    print(f"n={len(v):3d} {p0.get('district')}/{p0.get('taluka')}/"
          f"{p0.get('village')} span={span_m:6.0f}m vpts={gaps:4d} "
          f"areaMed={areas[len(areas)//2]:.2f}ha max={areas[-1]:.2f}ha gis={gis}")
