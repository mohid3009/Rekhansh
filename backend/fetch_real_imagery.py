"""Fetch REAL Esri World Imagery for the pilot site, centred on the REAL
Bhu-Naksha parcel extent (not the site.yaml point).

Usage:  python backend/fetch_real_imagery.py [zoom] [pad_tiles]
"""
from __future__ import annotations

import io
import json
import math
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import requests
from PIL import Image

BACKEND = Path(__file__).resolve().parent
sys.path.insert(0, str(BACKEND))

from app.config import load_site_config  # noqa: E402
from app.raster import tile_affine, save_png  # noqa: E402

UA = {"User-Agent": "RuralLandResurveyTriage/0.1 (research prototype)"}
VILLAGE_ID = "VIL-PILOT"


def lonlat_to_tile(lat: float, lon: float, z: int) -> tuple[float, float]:
    nn = 2 ** z
    xf = (lon + 180.0) / 360.0 * nn
    yf = (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2.0 * nn
    return xf, yf


def main() -> None:
    z = int(sys.argv[1]) if len(sys.argv) > 1 else 18
    pad = int(sys.argv[2]) if len(sys.argv) > 2 else 1

    site = load_site_config()
    feats = json.loads((BACKEND / "data" / "pilot_village_real.geojson")
                       .read_text(encoding="utf-8"))["features"]
    lons = [c[0] for f in feats for c in f["geometry"]["coordinates"][0]]
    lats = [c[1] for f in feats for c in f["geometry"]["coordinates"][0]]
    lon0, lon1 = min(lons), max(lons)
    lat0, lat1 = min(lats), max(lats)
    print(f"parcels span lon [{lon0:.5f},{lon1:.5f}] lat [{lat0:.5f},{lat1:.5f}]")

    # tile range covering the extent + pad tiles margin
    x0f, y0f = lonlat_to_tile(lat1, lon0, z)   # NW corner
    x1f, y1f = lonlat_to_tile(lat0, lon1, z)   # SE corner
    tx0, ty0 = int(math.floor(x0f)) - pad, int(math.floor(y0f)) - pad
    tx1, ty1 = int(math.floor(x1f)) + pad, int(math.floor(y1f)) + pad
    nx, ny = tx1 - tx0 + 1, ty1 - ty0 + 1
    print(f"zoom {z}: tiles x[{tx0},{tx1}] y[{ty0},{ty1}] = {nx}x{ny} "
          f"({nx * ny} tiles)")

    canvas = Image.new("RGB", (nx * 256, ny * 256), (0, 0, 0))
    got = 0
    for j in range(ny):
        for i in range(nx):
            url = site.tile_url.format(z=z, x=tx0 + i, y=ty0 + j)
            for attempt in range(3):
                try:
                    r = requests.get(url, timeout=40, headers=UA)
                    if r.status_code == 200 and len(r.content) > 1200:
                        im = Image.open(io.BytesIO(r.content)).convert("RGB")
                        if np.asarray(im).std() >= 6:
                            canvas.paste(im, (i * 256, j * 256))
                            got += 1
                            break
                    time.sleep(0.6 * (attempt + 1))
                except Exception:
                    time.sleep(0.8 * (attempt + 1))
            else:
                print(f"  MISS tile x={tx0 + i} y={ty0 + j}")
            time.sleep(0.15)
    print(f"retrieved {got}/{nx * ny} tiles")
    if got == 0:
        raise SystemExit("no tiles retrieved")

    img = np.asarray(canvas)
    aff = tile_affine(z, tx0, ty0, img.shape[1], img.shape[0])
    out = BACKEND / "data" / "imagery"
    out.mkdir(parents=True, exist_ok=True)
    save_png(img, out / f"{VILLAGE_ID}_ortho.png")
    aff.write_world_file(out / f"{VILLAGE_ID}_ortho.pgw")
    res_cm = round(aff.resolution_m_per_px((lat0 + lat1) / 2) * 100, 3)
    prov = {
        "provider": "Esri World Imagery (ArcGIS Online)",
        "tile_url_template": site.tile_url,
        "attribution": site.attribution,
        "licence_note": "Esri basemap tiles — attribution required; not survey-grade.",
        "zoom": z, "tiles": [nx, ny], "tiles_retrieved": got,
        "tile_range": {"x0": tx0, "y0": ty0},
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generated_by_this_project": False,
        "note": "Externally sourced imagery (PRD Module 03 'pre-existing data'). "
                "Acquisition date not published by provider; capture_date records "
                "the retrieval date. Mosaic extent centred on the real Bhu-Naksha "
                "parcel extent of Bond Gavhan village, Mahur taluka, Nanded.",
        "resolution_cm_per_px": res_cm,
        "bounds_wgs84": aff.bounds_wgs84(img.shape[1], img.shape[0]),
    }
    (out / f"{VILLAGE_ID}_ortho.json").write_text(json.dumps(prov, indent=2))
    print(f"saved {img.shape[1]}x{img.shape[0]} px, {res_cm} cm/px")


if __name__ == "__main__":
    main()
