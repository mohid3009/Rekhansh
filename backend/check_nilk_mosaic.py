"""One-off: fetch z18 mosaic for Nilkanthwadi + CV extraction check."""
import io
import json
import math
import sys
import time

import numpy as np
import requests
from PIL import Image
from shapely.geometry import shape

sys.path.insert(0, "backend")
from app.raster import tile_affine  # noqa: E402
from app.cvextract import extract_from_image  # noqa: E402

LAT, LON, Z, N = 19.29672, 77.43605, 18, 8
T = ("https://services.arcgisonline.com/ArcGIS/rest/services/"
     "World_Imagery/MapServer/tile/{z}/{y}/{x}")
UA = {"User-Agent": "RuralLandResurveyTriage/0.1 (research prototype)"}

nn = 2 ** Z
xf = (LON + 180.0) / 360.0 * nn
yf = (1 - math.asinh(math.tan(math.radians(LAT))) / math.pi) / 2.0 * nn
x0, y0 = int(xf) - N // 2, int(yf) - N // 2
print("tile range x", x0, "y", y0, "z", Z, "tiles", N)

canvas = Image.new("RGB", (N * 256, N * 256))
got = 0
for j in range(N):
    for i in range(N):
        url = T.format(z=Z, x=x0 + i, y=y0 + j)
        ok = False
        for attempt in range(3):
            try:
                r = requests.get(url, timeout=40, headers=UA)
                if r.status_code == 200 and len(r.content) > 1200:
                    im = Image.open(io.BytesIO(r.content)).convert("RGB")
                    if np.asarray(im).std() >= 6:
                        canvas.paste(im, (i * 256, j * 256))
                        got += 1
                        ok = True
                        break
            except Exception as e:
                print("tile err", i, j, e)
            time.sleep(0.5)
        if not ok:
            print(f"tile {i},{j} BLANK/failed")
    print(f"row {j}: got={got}")
canvas.save("tmp_chips/nilk_z18_mosaic.png")
print("saved, got", got, "/", N * N)

img = np.asarray(canvas)
aff = tile_affine(Z, x0, y0, img.shape[1], img.shape[0])
print("res m/px", round(aff.resolution_m_per_px(LAT), 3))
print("bounds", aff.bounds_wgs84(img.shape[1], img.shape[0]))

import gzip
with gzip.open("backend/data/nanded.geojson.gz", "rt",
               encoding="utf-8") as fh:
    feats = [f for f in json.load(fh)["features"]
             if f["properties"].get("village_giscode")
             == "RVM1504271500040195420000"
             and f["properties"].get("geom_kind") == "polygon"]
print("parcels:", len(feats))
H, W = img.shape[:2]
inside = 0
for f in feats:
    g = shape(f["geometry"])
    c, r = aff.lonlat_to_px(g.centroid.x, g.centroid.y)
    ok = 0 <= c < W and 0 <= r < H
    inside += ok
    print(f"  survey={f['properties']['survey_no']} px=({c:.0f},{r:.0f}) "
          f"inside={ok}")
print(f"inside: {inside}/{len(feats)}")

res = aff.resolution_m_per_px(LAT)
polys = extract_from_image(img, aff, res, min_area_ha=0.10, max_area_ha=15.0)
print("CV polygons:", len(polys))
for p in polys[:20]:
    g = shape(p.geometry)
    from app.geo import polygon_area_ha
    print(f"  conf={p.confidence} area_ha="
          f"{polygon_area_ha(p.geometry):.2f} feat={p.detected_features}")
