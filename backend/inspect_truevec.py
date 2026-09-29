"""Detail-inspect compact true-polygon villages for pilot suitability."""
import gzip
import json
import math

from shapely.geometry import shape
from shapely.ops import transform as sht
import pyproj

with gzip.open("backend/data/nanded.geojson.gz", "rt", encoding="utf-8") as fh:
    fc = json.load(fh)
feats = fc["features"]

TARGETS = [
    "RVM1504271500040195420000",  # Nilakathwadi 10
    "RVM1504271500040194760000",  # Khairgaon 23
    "RVM1504271500040194140000",  # Wakoda 36
    "RVM1501271500010190920000",  # Chaufuli 29
    "RVM1502271500020191650000",  # Raipurtanda 18
    "RVM1501271500010190310000",  # Keroli 19
    "RVM1504271500040193890000",  # Manula 50
]

for gis in TARGETS:
    vil = [f for f in feats if f["properties"].get("village_giscode") == gis
           and f.get("geometry") and f["geometry"]["type"] == "Polygon"]
    p0 = vil[0]["properties"]
    print(f"===== {p0.get('village')} taluka={p0.get('taluka')} n={len(vil)}")
    geoms = [shape(f["geometry"]) for f in vil]
    lon0 = sum(g.centroid.x for g in geoms) / len(geoms)
    lat0 = sum(g.centroid.y for g in geoms) / len(geoms)
    zone = int((lon0 + 180) / 6) + 1
    tr = pyproj.Transformer.from_crs("EPSG:4326", f"EPSG:{32600 + zone}", always_xy=True).transform
    areas = sorted(sht(tr, g).area / 1e4 for g in geoms)
    nring = sorted(len(g.exterior.coords) for g in geoms)
    sns = sorted({f["properties"].get("survey_no") for f in vil})
    print(f"  centroid {lat0:.5f},{lon0:.5f}")
    print(f"  areas ha min/med/max {areas[0]:.2f}/{areas[len(areas)//2]:.2f}/{areas[-1]:.2f}")
    print(f"  ring verts min/med/max {nring[0]}/{nring[len(nring)//2]}/{nring[-1]}")
    print(f"  distinct survey_no={len(sns)} total={len(vil)} sample={sns[:12]}")
    lons = [g.centroid.x for g in geoms]
    lats = [g.centroid.y for g in geoms]
    sx = (max(lons) - min(lons)) * 111320.0 * math.cos(math.radians(lat0))
    sy = (max(lats) - min(lats)) * 110540.0
    print(f"  span {sx:.0f}m x {sy:.0f}m")
