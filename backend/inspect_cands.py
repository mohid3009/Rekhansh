"""Deep-inspect 3 candidate villages: areas, gaps/overlaps, survey nos, cluster pick."""
import gzip
import json
import math

OUT = "backend/data/nanded.geojson.gz"

with gzip.open(OUT, "rt", encoding="utf-8") as fh:
    feats = json.load(fh)["features"]

TARGETS = {
    "TARBUJAPUR": "RVM1507271500070197380000",
    "SATARPUR": "RVM1506271500060196880000",
    "NILKATHWADI": "RVM1504271500040195420000",
}

by_gis = {}
for f in feats:
    g = f.get("geometry")
    if g and g["type"] == "Polygon":
        by_gis.setdefault(f["properties"].get("village_giscode"), []).append(f)

from shapely.geometry import shape
from shapely.ops import transform as sh_transform
from shapely import affinity


def proj(g, lon0, lat0):
    import pyproj
    t = pyproj.Transformer.from_crs("EPSG:4326", f"+proj=aeqd +lon_0={lon0} +lat_0={lat0} +units=m", always_xy=True)
    return sh_transform(lambda x, y, z=None: t.transform(x, y), shape(g))


for name, gis in TARGETS.items():
    fs = by_gis[gis]
    print("=" * 70)
    print(name, gis, "n=", len(fs), "village=", fs[0]["properties"].get("village"),
          "taluka=", fs[0]["properties"].get("taluka"))
    sns = [f["properties"].get("survey_no") for f in fs]
    print("survey_nos:", sns)
    areas = [f["properties"].get("area_hectares") for f in fs]
    print("declared areas ha:", areas)
    lons = [c[0] for f in fs for c in f["geometry"]["coordinates"][0]]
    lats = [c[1] for f in fs for c in f["geometry"]["coordinates"][0]]
    lon0, lat0 = sum(lons) / len(lons), sum(lats) / len(lats)
    print("centroid: %.6f, %.6f" % (lat0, lon0))
    pp = [proj(f["geometry"], lon0, lat0) for f in fs]
    ga = [p.area / 10000.0 for p in pp]
    print("geom areas ha: min=%.3f med=%.3f max=%.3f" % (min(ga), sorted(ga)[len(ga) // 2], max(ga)))
    # pairwise overlaps/gaps
    big_ov = 0
    for i in range(len(pp)):
        for j in range(i + 1, len(pp)):
            if pp[i].intersects(pp[j]):
                ov = pp[i].intersection(pp[j]).area
                frac = ov / min(pp[i].area, pp[j].area)
                if frac > 0.02:
                    big_ov += 1
    print("pairs overlapping >2%% of smaller:", big_ov)
    # union coverage vs bbox
    from shapely.ops import unary_union
    u = unary_union(pp)
    print("union type:", u.geom_type, "union area ha: %.2f" % (u.area / 10000))
    bb = u.bounds
    print("union bbox span m: %.0f x %.0f" % (bb[2] - bb[0], bb[3] - bb[1]))
    # adjacency: neighbours within 8m
    adj = 0
    for i in range(len(pp)):
        for j in range(i + 1, len(pp)):
            if pp[i].buffer(8.0).intersects(pp[j]):
                adj += 1
    print("adjacent pairs (8m):", adj)
