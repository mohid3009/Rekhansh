"""Save 3x3 z19 chips for the 3 candidates; report per-tile variance and
save PNGs for visual inspection. Also retry z19 center tile with backoff."""
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

def fetch(z, x, y, tries=5):
    for a in range(tries):
        try:
            r = requests.get(T.format(z=z, x=x, y=y), timeout=45, headers=UA)
            if r.status_code == 200 and len(r.content) > 1200:
                im = np.asarray(Image.open(io.BytesIO(r.content)).convert("RGB"))
                if im.std() >= 6:
                    return im
        except Exception as e:
            print("   retry", a, type(e).__name__)
        time.sleep(1.0 * (a + 1))
    return None

for name, (lat, lon) in CANDS.items():
    x0, y0 = tile(19, lat, lon)
    canvas = np.zeros((768, 768, 3), np.uint8)
    print(f"==== {name} center19=({x0},{y0})")
    for j in range(3):
        row = []
        for i in range(3):
            im = fetch(19, x0 + i - 1, y0 + j - 1)
            if im is None:
                row.append("BLANK")
            else:
                canvas[j*256:(j+1)*256, i*256:(i+1)*256] = im
                row.append(f"std={im.std():.1f} mean={im.mean():.0f}")
        print("   ", row)
    Image.fromarray(canvas).save(f"tmp_chip_{name}_z19.png")
    print("    saved tmp_chip_%s_z19.png blankfrac=%.2f" % (
        name, (canvas.std(axis=-1) < 6).mean()))
