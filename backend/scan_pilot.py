"""Pick pilot village cluster: extract parcels of chosen village, check contiguity."""
import gzip
import io
import json
import math

import requests
from PIL import Image
from shapely.geometry import shape

PATH = "backend/data/nanded.geojson.gz"
TARGET_GIS = "RVM1501271500010190910000"  # Mahur / bond gavhan, 30 polygons

print("extracting village parcels ...")
parcels = []
with gzip.open(PATH, "rt", encoding="utf-8") as fh:
    # stream-decode: features are large; parse incrementally via raw decode chunks
    # Simpler: read whole text (may be ~200MB). Use iterative json? fallback: load all.
    text = fh.read()
print("decompressed chars:", len(text))
fc = json.loads(text)
del text
print("features:", len(fc["features"]))
for f in fc["features"]:
    p = f["properties"]
    if p.get("village_giscode") == TARGET_GIS and p.get("geom_kind") == "polygon":
        parcels.append(f)
print("village parcels:", len(parcels))
areas = [p["properties"].get("area_hectares") for p in parcels]
print("area_ha min/med/max:",
      round(min(a for a in areas if a), 3),
      round(float(sorted(a for a in areas if a)[len(areas)//2]), 3),
      round(max(a for a in areas if a), 3))
geoms = [shape(f["geometry"]) for f in parcels]
print("valid:", sum(g.is_valid for g in geoms),
      "types:", {g.geom_type for g in geoms})
xs = [g.centroid.x for g in geoms]; ys = [g.centroid.y for g in geoms]
print("centroid: %.5f, %.5f" % (sum(xs)/len(xs), sum(ys)/len(ys)))
print("lon range %.5f..%.5f lat range %.5f..%.5f" % (min(xs), max(xs), min(ys), max(ys)))
print("survey_nos:", [p["properties"].get("survey_no") for p in parcels][:35])
# check contiguity: how many touch at least one other
n_touch = 0
for i, gi in enumerate(geoms):
    for j, gj in enumerate(geoms):
        if i != j and gi.touches(gj):
            n_touch += 1
            break
print("parcels touching >=1 other:", n_touch, "/", len(geoms))
json.dump([{"properties": p["properties"],
            "geometry": p["geometry"]} for p in parcels],
          open("backend/data/pilot_village_raw.json", "w", encoding="utf-8"),
          ensure_ascii=False)
print("saved backend/data/pilot_village_raw.json")

# quick imagery check at centroid
lat = sum(ys)/len(ys); lon = sum(xs)/len(xs)
print("fetching imagery chip at %.5f, %.5f" % (lat, lon))
z = 18
nn = 2 ** z
xt = int((lon + 180.0) / 360.0 * nn)
yt = int((1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2.0 * nn)
im = Image.new("RGB", (512, 512))
for j in range(2):
    for i in range(2):
        url = ("https://services.arcgisonline.com/ArcGIS/rest/services/"
               f"World_Imagery/MapServer/tile/{z}/{yt-1+j}/{xt-1+i}")
        r = requests.get(url, timeout=40,
                         headers={"User-Agent": "RuralLandResurveyTriage/0.1"})
        print("tile", i, j, r.status_code, len(r.content))
        t = Image.open(io.BytesIO(r.content)).convert("RGB")
        im.paste(t, (i*256, j*256))
im.save("tmp_chips/nanded_pilot.png")
print("saved tmp_chips/nanded_pilot.png")
