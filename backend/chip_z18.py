"""Compare candidate villages at z18 (real Esri max zoom here) with 3x3 chips:
per-tile variance + quadrant contrast + saved PNGs for visual check."""
import io
import math
import time

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

def fetch(z, x, y, tries=4):
    for a in range(tries):
        try:
            r = requests.get(T.format(z=z, x=x, y=y), timeout=45, headers=UA)
            if r.status_code == 200 and len(r.content) > 1200:
                return np.asarray(Image.open(io.BytesIO(r.content)).convert("RGB"))
        except Exception:
            pass
        time.sleep(1.0 * (a + 1))
    return None

for name, (lat, lon) in CANDS.items():
    x0, y0 = tile(18, lat, lon)
    canvas = np.zeros((768, 768, 3), np.uint8)
    print(f"==== {name} center18=({x0},{y0})")
    ok = 0
    for j in range(3):
        row = []
        for i in range(3):
            im = fetch(18, x0 + i - 1, y0 + j - 1)
            if im is None:
                row.append("FAIL")
            else:
                canvas[j*256:(j+1)*256, i*256:(i+1)*256] = im
                ok += 1
                row.append(f"std={im.std():.1f}")
        print("   ", row)
    Image.fromarray(canvas).save(f"tmp_chip_{name}_z18.png")
    f = canvas.astype(float)
    R, G, B = f[..., 0], f[..., 1], f[..., 2]
    ExG = 2 * G - R - B
    print(f"    tiles_ok={ok}/9 std={f.std():.1f} canopy={(ExG > 65).mean():.3f} "
          f"shadow={(f.max(axis=-1) < 42).mean():.3f}")
