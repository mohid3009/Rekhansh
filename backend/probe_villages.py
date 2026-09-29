"""Download Esri World Imagery chips for each candidate village centroid and
report field-structure signal: bare/bund fraction, canopy, shadow, zoom-19
resolution, and Tile 1 variance (blank-tile guard)."""
import io
import math
import sys

import numpy as np
import requests
from PIL import Image

UA = {"User-Agent": "RuralLandResurveyTriage/0.1 (research prototype)"}
T = "https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"

CANDS = {
    "bond_gavhan": (19.88471, 78.08788),
    "shekapur": (19.86020, 77.90044),
    "rodgi": (19.31179, 77.41937),
}

def tile(z, lat, lon):
    n = 2 ** z
    xf = (lon + 180.0) / 360.0 * n
    yf = (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2.0 * n
    return int(xf), int(yf)

def fetch(z, x, y):
    r = requests.get(T.format(z=z, x=x, y=y), timeout=40, headers=UA)
    assert r.status_code == 200 and len(r.content) > 1200, f"tile {x}/{y} failed"
    return np.asarray(Image.open(io.BytesIO(r.content)).convert("RGB"))

for name, (lat, lon) in CANDS.items():
    x0, y0 = tile(19, lat, lon)
    print(f"==== {name} @ {lat:.5f},{lon:.5f} tile19=({x0},{y0})")
    for z in (18, 19):
        # scale tile coords to zoom z
        xz, yz = (x0 * 2 ** (z - 19), y0 * 2 ** (z - 19)) if z <= 19 else (None, None)
        img = fetch(z, xz, yz)
        f = img.astype(float)
        R, G, B = f[..., 0], f[..., 1], f[..., 2]
        mx, mn = f.max(axis=-1), f.min(axis=-1)
        ExG = 2 * G - R - B
        bare = ((mx - mn < 28) & (R > 110) & (R < 200)).mean()   # bunds/paths/soil
        canopy = (ExG > 65).mean()
        shadow = (mx < 42).mean()
        res_m = 156543.03 * math.cos(math.radians(lat)) / 2 ** z
        # 4-quadrant contrast: structured fields => quadrants differ
        h, w = R.shape
        qs = [R[:h//2, :w//2].mean(), R[:h//2, w//2:].mean(),
              R[h//2:, :w//2].mean(), R[h//2:, w//2:].mean()]
        print(f"  z{z}: res={res_m:.2f}m/px bare={bare:.2f} canopy={canopy:.3f} "
              f"shadow={shadow:.3f} std={f.std():.1f} quadR={[round(q) for q in qs]}")
