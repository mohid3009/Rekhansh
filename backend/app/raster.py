"""Raster / world-file utilities.

The orthomosaic and the legacy map are stored as PNG + ESRI world file
(6-parameter affine: pixel -> WGS84 lon/lat), matching the PRD's
"PNG + world file" imagery input. This module owns:
  * reading/writing world files and pixel<->lonlat conversion
  * computing WGS84 bounds for Leaflet ImageOverlay
  * affine fitting for legacy-map georeferencing is in pipeline/georeference.py
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image


@dataclass
class WorldFileAffine:
    """ESRI world file: 6 parameters for pixel (col,row) -> lon/lat (EPSG:4326).

    lon = A*col + B*row + C
    lat = D*col + E*row + F
    """

    A: float
    B: float
    C: float
    D: float
    E: float
    F: float

    def px_to_lonlat(self, col: float, row: float) -> tuple[float, float]:
        return (self.A * col + self.B * row + self.C,
                self.D * col + self.E * row + self.F)

    def lonlat_to_px(self, lon: float, lat: float) -> tuple[float, float]:
        det = self.A * self.E - self.B * self.D
        if abs(det) < 1e-18:
            raise ValueError("degenerate affine")
        dx, dy = lon - self.C, lat - self.F
        col = (dx * self.E - dy * self.B) / det
        row = (self.A * dy - self.D * dx) / det
        return col, row

    def resolution_m_per_px(self, lat: float) -> float:
        """Ground resolution in metres per pixel at a given latitude (north-up raster)."""
        m_lon = abs(self.A) * 111_320.0 * math.cos(math.radians(lat))
        m_lat = abs(self.E) * 110_540.0
        return math.hypot(m_lon, m_lat) / math.sqrt(2.0) if abs(self.B) + abs(self.D) > 0 \
            else (m_lon + m_lat) / 2.0

    def bounds_wgs84(self, width: int, height: int) -> list[list[float]]:
        """[[south,west],[north,east]] for a Leaflet image overlay."""
        corners = [self.px_to_lonlat(c, r)
                   for c, r in ((0, 0), (width - 1, 0), (0, height - 1), (width - 1, height - 1))]
        lons = [c[0] for c in corners]
        lats = [c[1] for c in corners]
        return [[min(lats), min(lons)], [max(lats), max(lons)]]

    # ---------------- persistence ---------------- #
    def write_world_file(self, path: str | Path) -> None:
        """ESRI .pgw/.wld order: A, D, B, E, C, F."""
        Path(path).write_text(
            f"{self.A:.12f}\n{self.D:.12f}\n{self.B:.12f}\n"
            f"{self.E:.12f}\n{self.C:.12f}\n{self.F:.12f}\n",
            encoding="utf-8",
        )

    @classmethod
    def read_world_file(cls, path: str | Path) -> "WorldFileAffine":
        vals = [float(v) for v in Path(path).read_text(encoding="utf-8").split() if v.strip()]
        a, d, b, e, c, f = vals[:6]
        return cls(A=a, B=b, C=c, D=d, E=e, F=f)

    @classmethod
    def from_topleft(cls, west: float, north: float, m_per_deg_lon: float,
                     m_per_deg_lat: float) -> "WorldFileAffine":
        """Affine anchored at the *centre* of the top-left pixel (world-file
        convention) for a north-up raster."""
        return cls(
            A=1.0 / m_per_deg_lon, B=0.0, C=west,
            D=0.0, E=-1.0 / m_per_deg_lat, F=north,
        )

    def to_dict(self) -> dict:
        return {"A": self.A, "B": self.B, "C": self.C, "D": self.D, "E": self.E, "F": self.F}

    @classmethod
    def from_dict(cls, d: dict) -> "WorldFileAffine":
        return cls(A=d["A"], B=d["B"], C=d["C"], D=d["D"], E=d["E"], F=d["F"])


def load_png(path: str | Path) -> np.ndarray:
    return np.asarray(Image.open(path).convert("RGB"))


def save_png(arr: np.ndarray, path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(arr.astype("uint8")).save(path)


def write_provenance(path: str | Path, payload: dict) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(payload, indent=2), encoding="utf-8")


# --------------------------------------------------------------------------- #
# XYZ tile (Web Mercator) math — used to stitch raster tiles into an orthomosaic
# --------------------------------------------------------------------------- #
def tile_lon(z: int, x: float) -> float:
    return x / (2 ** z) * 360.0 - 180.0


def tile_lat(z: int, y: float) -> float:
    n = math.pi - 2.0 * math.pi * y / (2 ** z)
    return math.degrees(math.atan(math.sinh(n)))


def tile_affine(z: int, x0: int, y0: int, width_px: int, height_px: int) -> WorldFileAffine:
    """North-up world-file affine for a mosaic whose top-left tile is (x0, y0)
    at zoom z (standard XYZ scheme, Google/ESRI tiling). Pixel coordinates are
    mosaic-local; the anchor is the centre of the top-left pixel (world-file
    convention)."""
    deg_per_px = 360.0 / (2 ** z * 256.0)
    lon_c = tile_lon(z, x0 + 0.5 / 256.0)
    lat_top = tile_lat(z, y0 + 0.5 / 256.0)
    lat_next = tile_lat(z, y0 + 1.5 / 256.0)
    return WorldFileAffine(A=deg_per_px, B=0.0, C=lon_c,
                           D=0.0, E=-(lat_top - lat_next), F=lat_top)
