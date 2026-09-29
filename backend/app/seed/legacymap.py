"""Renders the mock cadastral layer as a 'scanned paper map' PNG in the
distorted scan frame produced by Module 02 (labels, fills, title block).
The *georeferencing* of that scan is the recorded geometry itself — see
georeference.run_georeferencing.
"""
from __future__ import annotations

import random

from PIL import Image, ImageDraw, ImageFont

from ..config import DATA_DIR


def render_scan(georef, survey_numbers: list[str], village_name: str,
                village_id: str) -> str:
    w, h = georef.paper_size_px
    rng = random.Random(len(survey_numbers) * 31 + w)
    # paper texture
    bg = Image.new("RGB", (w, h), (238, 231, 213))
    px = bg.load()
    for y in range(0, h, 3):
        for x in range(0, w, 3):
            n = rng.randint(-8, 6)
            px[x, y] = (max(0, min(255, 238 + n)),
                        max(0, min(255, 231 + n)),
                        max(0, min(255, 213 + n)))
    draw = ImageDraw.Draw(bg, "RGBA")

    fills = [(214, 196, 152, 200), (206, 188, 146, 200), (199, 182, 143, 200),
             (210, 192, 149, 200)]
    for ring, num in zip(georef.scan_pixels, survey_numbers):
        pts = [(p[0], p[1]) for p in ring]
        draw.polygon(pts, fill=fills[hash(num) % len(fills)],
                     outline=(60, 48, 32))
        cx = sum(p[0] for p in pts) / len(pts)
        cy = sum(p[1] for p in pts) / len(pts)
        draw.text((cx - 16, cy - 6), num, fill=(40, 30, 18))

    draw.rectangle([2, 2, w - 3, h - 3], outline=(70, 55, 35), width=3)
    draw.rectangle([8, 8, 320, 64], fill=(245, 240, 226, 235), outline=(70, 55, 35))
    draw.text((18, 14), f"Record of Rights — {village_name}", fill=(35, 28, 18))
    draw.text((18, 34), "(mock cadastral survey sheet, generated for prototype)",
              fill=(90, 75, 55))
    out_dir = DATA_DIR / "legacy"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{village_id}_scan.png"
    bg.save(path)
    return f"legacy/{village_id}_scan.png"
