"""Render candidate village polygons over Esri tiles to eyeball alignment."""
import gzip
import io
import json
import math

import requests
from PIL import Image, ImageDraw

OUT = "backend/data/nanded.geojson.gz"
with gzip.open(OUT, "rt", encoding="utf-8") as fh:
    feats = json.load(fh)["features"]

TARGETS = {
    "tarbujapur": "RVM1507271500070197380000",
    "satarpur": "RVM1506271500060196880000",
    "nilkathwadi": "RVM1504271500040195420000",
}

UA = {"User-Agent": "RuralLandResurveyTriage/0.1 (research prototype)"}


def tile_xy(lat, lon, z):
    n = 2 ** z
    x = (lon + 180.0) / 360.0 * n
    y = (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2.0 * n
    return x, y


Z = 17
for name, gis in TARGETS.items():
    fs = [f for f in feats if f["properties"].get("village_giscode") == gis
          and f.get("geometry") and f["geometry"]["type"] == "Polygon"]
    lons = [c[0] for f in fs for c in f["geometry"]["coordinates"][0]]
    lats = [c[1] for f in fs for c in f["geometry"]["coordinates"][0]]
    lat0, lon0 = sum(lats) / len(lats), sum(lons) / len(lons)
    fx, fy = tile_xy(lat0, lon0, Z)
    # 3x3 tiles at z17 (~1.1km across), canvas 768
    cx, cy = int(fx), int(fy)
    canvas = Image.new("RGB", (768, 768), (0, 0, 0))
    ox, oy = cx - 1, cy - 1
    for j in range(3):
        for i in range(3):
            url = f"https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{Z}/{oy + j}/{ox + i}"
            try:
                r = requests.get(url, timeout=40, headers=UA)
                im = Image.open(io.BytesIO(r.content)).convert("RGB")
                canvas.paste(im, (i * 256, j * 256))
            except Exception as e:
                print(name, "tile fail", e)
    d = ImageDraw.Draw(canvas)

    def px(lat, lon):
        x, y = tile_xy(lat, lon, Z)
        return ((x - ox) * 256, (y - oy) * 256)

    for f in fs:
        ring = f["geometry"]["coordinates"][0]
        pts = [px(lat, lon) for lon, lat in ring]
        d.polygon(pts, outline=(255, 30, 30), width=2)
        cxp, cyp = sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)
        d.text((cxp - 4, cyp - 6), f["properties"].get("survey_no", "?"), fill=(255, 255, 0))
    canvas.save(f"tmp_chips/real_{name}_z17.png")
    print("saved tmp_chips/real_%s_z17.png n=%d" % (name, len(fs)))
