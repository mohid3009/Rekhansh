"""One-off: fetch Esri mosaic for Bond Gavhan + check real parcels vs imagery
overlap, CV polygon count, and per-parcel IoU sanity."""
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
from app.raster import WorldFileAffine  # noqa: E402

LAT, LON, Z, N = 19.88471, 78.08788, 19, 10
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
        for attempt in range(3):
            try:
                r = requests.get(url, timeout=40, headers=UA)
                if r.status_code == 200 and len(r.content) > 1200:
                    im = Image.open(__import__("io").BytesIO(r.content))
                    im = im.convert("RGB")
                    if np.asarray(im).std() >= 6:
                        canvas.paste(im, (i * 256, j * 256))
                        got += 1
                        break
            except Exception as e:
                print("tile err", i, j, e)
            time.sleep(0.6)
    print(f"row {j}: got={got}")
canvas.save("tmp_chips/bond_gavhan_z19.png")
print("saved tmp_chips/bond_gavhan_z19.png, got", got)

img = np.asarray(canvas)
aff = tile_affine(Z, x0, y0, img.shape[1], img.shape[0])
print("res m/px", round(aff.resolution_m_per_px(LAT), 3))
print("bounds", aff.bounds_wgs84(img.shape[1], img.shape[0]))

feats = json.load(open("backend/data/pilot_village_real.geojson"))["features"]


def px(lon, lat):
    return aff.lonlat_to_px(lon, lat)


H, W = img.shape[:2]
inside = 0
for f in feats:
    g = shape(f["geometry"])
    cx, cy = g.centroid.x, g.centroid.y
    c, r = px(cx, cy)
    ok = 0 <= c < W and 0 <= r < H
    inside += ok
    print(f"  survey={f['properties']['survey_no']} centroid_px="
          f"({c:.0f},{r:.0f}) inside={ok}")
print(f"centroids inside image: {inside} / {len(feats)}")

res = aff.resolution_m_per_px(LAT)
polys = extract_from_image(img, aff, res, min_area_ha=0.10, max_area_ha=15.0)
print("CV polygons:", len(polys))
for p in polys[:15]:
    g = shape(p.geometry)
    print(f"  conf={p.confidence} area_ha={g.area * 0:.3f} feat={p.detected_features}")
