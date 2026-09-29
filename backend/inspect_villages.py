"""Inspect candidate pilot villages: parcel details, areas, centroid, compactness."""
import gzip
import json
import math

from shapely.geometry import shape

with gzip.open("backend/data/nanded.geojson.gz", "rt", encoding="utf-8") as fh:
    fc = json.load(fh)
feats = fc["features"]

TARGETS = [
    ("RVM1507271500070197380000", "Tarbujapur?", "Mudkhed"),
    ("RVM1506271500060196880000", "Satarpur?", "Nanded"),
    ("RVM1512271500120201220000", "Babhulgaon?", "Naigaon"),
    ("RVM1505271500050195980000", "Lahan Tanda?", "Ardhapur"),
]

for gis, guess, tal in TARGETS:
    vil = [f for f in feats
           if f["properties"].get("village_giscode") == gis
           and f.get("geometry") and f["geometry"]["type"] in ("Polygon", "MultiPolygon")]
    print(f"===== {guess} taluka={tal} gis={gis} n_poly={vil}")
    if not vil:
        continue
    vil = vil
    print("  village name:", vil[0]["properties"].get("village"))
    geoms = [shape(f["geometry"]) for f in vil]
    # areas via local projection
    import pyproj
    lon0 = sum(g.centroid.x for g in geoms) / len(geoms)
    lat0 = sum(g.centroid.y for g in geoms) / len(geoms)
    zone = int((lon0 + 180) / 6) + 1
    crs = f"EPSG:{32600 + zone}" if lat0 >= 0 else f"EPSG:{32700 + zone}"
    tr = pyproj.Transformer.from_crs("EPSG:4326", crs, always_xy=True).transform
    from shapely.ops import transform as sht
    areas = [sht(tr, g).area / 1e4 for g in geoms]
    print(f"  centroid {lat0:.5f},{lon0:.5f} UTM zone {zone}")
    print("  areas ha:", sorted(round(a, 3) for a in areas))
    sns = sorted({f["properties"].get("survey_no") for f in vil})
    print(f"  distinct survey_no={len(sns)} sample={sns[:15]}")
    kinds = {}
    for f in vil:
        kinds[f["geometry"]["type"]] = kinds.get(f["geometry"]["type"], 0) + 1
    print("  geom types:", kinds)
    lons = [g.centroid.x for g in geoms]
    lats = [g.centroid.y for g in geoms]
    sx = (max(lons) - min(lons)) * 111320.0 * math.cos(math.radians(lat0))
    sy = (max(lats) - min(lats)) * 110540.0
    print(f"  centroid-bbox span {sx:.0f}m x {sy:.0f}m")
