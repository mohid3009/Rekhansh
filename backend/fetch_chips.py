"""Fetch Esri World Imagery chips for Wakoda + fallback candidate centroids."""
import io
import math
import os
import time

import requests
from PIL import Image

UA = {"User-Agent": "RuralLandResurveyTriage/0.1 (research prototype; SIH demo)"}
T = "https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"

CANDS = {
    "wakoda": (19.53525, 77.66380),
    "chaufuli": (19.88661, 78.09688),
    "khairgaon": (19.32330, 77.41995),
}

os.makedirs("tmp_chips", exist_ok=True)


def tile_xy(lat, lon, z):
    nn = 2 ** z
    xf = (lon + 180.0) / 360.0 * nn
    yf = (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2.0 * nn
    return xf, yf


for name, (lat, lon) in CANDS.items():
    for z in (18, 19):
        xf, yf = tile_xy(lat, lon, z)
        xi, yi = int(xf), int(yf)
        fn = f"tmp_chips/esri_{name}_z{z}.jpg"
        if os.path.exists(fn):
            print(name, z, "cached", os.path.getsize(fn))
            continue
        url = T.format(z=z, x=xi, y=yi)
        try:
            r = requests.get(url, timeout=40, headers=UA)
            print(name, z, r.status_code, len(r.content))
            if r.status_code == 200 and len(r.content) > 1200:
                open(fn, "wb").write(r.content)
        except Exception as e:
            print(name, z, "ERR", e)
        time.sleep(0.5)
