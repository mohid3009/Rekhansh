"""One-off: Nilkanthwadi (Hatnoor dam backwater) + Chowfuli detail + imagery look."""
import gzip
import io
import json
import math

import numpy as np
import requests
from PIL import Image

UA = {"User-Agent": "RuralLandResurveyTriage/0.1 (research prototype)"}
TILE = "https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"


def load():
    with gzip.open("backend/data/nanded.geojson.gz", "rt", encoding="utf-8") as fh:
        return json.load(fh)["features"]


def chip(lat, lon, z, n, tag):
    nn = 2 ** z
    xf = (lon + 180.0) / 360.0 * nn
    yf = (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2.0 * nn
    x0, y0 = int(xf) - n // 2, int(yf) - n // 2
    canvas = Image.new("RGB", (n * 256, n * 256))
    for j in range(n):
        for i in range(n):
            r = requests.get(TILE.format(z=z, x=x0 + j, y=y0 + i), timeout=40, headers=UA)
            if r.status_code == 200 and len(r.content) > 1200:
                canvas.paste(Image.open(io.BytesIO(r.content)).convert("RGB"), (j * 256, i * 256))
    a = np.asarray(canvas).astype(float)
    print(tag, "mean_rgb", a.reshape(-1, 3).mean(axis=0).round(1),
          "std", round(float(a.std()), 1))
    canvas.save(f"tmp_{tag}.png")
    return canvas


feats = load()
for gis, z, n in [("RVM1504271500040195420000", 17, 5),   # Nilkanthwadi
                  ("RVM1501271500010190920000", 17, 5)]:  # Chowfuli
    v = [x for x in feats if x["properties"].get("village_giscode") == gis
         and x.get("geometry") and x["properties"].get("geom_kind") == "polygon"]
    p0 = v[0]["properties"]
    lons = [c[0] for f in v for c in f["geometry"]["coordinates"][0]]
    lats = [c[1] for f in v for c in f["geometry"]["coordinates"][0]]
    clat, clon = sum(lats) / len(lats), sum(lons) / len(lons)
    print(f"--- {p0['taluka'].encode('ascii','ignore').decode()}/"
          f"{gis} n={len(v)} centroid={clat:.5f},{clon:.5f}")
    for f in v:
        p = f["properties"]
        g = f["geometry"]["coordinates"][0]
        xs = [c[0] for c in g]
        ys = [c[1] for c in g]
        w = (max(xs) - min(xs)) * 111320.0 * math.cos(math.radians(clat))
        h = (max(ys) - min(ys)) * 110540.0
        print(f"  survey={p['survey_no']:>4} area={p['area_hectares']:6.2f}ha "
              f"extent={w:5.0f}x{h:5.0f}m vpts={len(xs)-1}")
    chip(clat, clon, z, n, f"chk_{gis[-6:]}_z{z}")
