"""Module 02 — Legacy map georeferencing (distort-then-recover, per PRD).

Demo-mode approach (a PRD assumption): rasterise the mock cadastral layer,
apply a deliberate distortion (rotation + scale drift + measurement noise),
then run the actual georeferencing algorithm — a least-squares 6-parameter
affine fit from ground control points — to recover it. The recovered RMSE
becomes a real, non-fabricated number that feeds the uncertainty score.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
from pyproj import Transformer
from shapely.geometry import Polygon, mapping

from ..geo import make_transformer, make_inverse


@dataclass
class GeorefResult:
    control_points: list[dict]            # {pixel_x, pixel_y, lat, lon}
    affine: list[float]                   # 6 params: pixel->WGS84 lon/lat (A,B,C,D,E,F)
    rmse_m: float
    distortion: dict                      # what we applied (for provenance/UI)
    recorded: list[dict]                  # georeferenced parcel geometries (same order)
    scan_pixels: list                     # per-parcel paper-frame rings
    paper_size_px: tuple[int, int]
    origin_px: tuple[float, float]        # paper offset of the paper frame origin

    def pixel_to_lonlat(self, px: float, py: float) -> tuple[float, float]:
        a = np.array(self.affine)
        return (float(a[0] * px + a[1] * py + a[2]),
                float(a[3] * px + a[4] * py + a[5]))


def fit_affine(cps: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Least-squares 6-parameter affine (pixel_x, pixel_y) -> (lon, lat).

    Returns (params (A,B,C,D,E,F), per-CP residuals in degrees).
    """
    x, y = cps[:, 0], cps[:, 1]
    lon, lat = cps[:, 2], cps[:, 3]
    M = np.column_stack([x, y, np.ones_like(x)])
    c_lon, *_ = np.linalg.lstsq(M, lon, rcond=None)
    c_lat, *_ = np.linalg.lstsq(M, lat, rcond=None)
    params = np.array([c_lon[0], c_lon[1], c_lon[2], c_lat[0], c_lat[1], c_lat[2]])
    resid = np.column_stack([M @ c_lon - lon, M @ c_lat - lat])
    return params, resid


def apply_affine(params, px, py):
    lon = params[0] * px + params[1] * py + params[2]
    lat = params[3] * px + params[4] * py + params[5]
    return lon, lat



def run_georeferencing(
    design_geoms: list[dict],
    site_lat: float,
    site_lon: float,
    rotation_deg: float,
    scale_pct: float,
    noise_m: float,
    cp_grid: int,
    rng: np.random.Generator,
) -> GeorefResult:
    """Design WGS84 polygons -> distorted 'scan' -> recovered affine + RMSE."""
    fwd = make_transformer(site_lon, site_lat)
    inv = make_inverse(site_lon, site_lat)

    def to_m(g: dict) -> np.ndarray:
        pts = np.array(Polygon(g["coordinates"][0]).exterior.coords)
        lon, lat = fwd.transform(pts[:, 0], pts[:, 1])
        return np.column_stack([lon, lat])

    rings_m = [to_m(g) for g in design_geoms]
    all_xy = np.vstack(rings_m)
    cx, cy = float(all_xy[:, 0].mean()), float(all_xy[:, 1].mean())
    span = float(max(all_xy[:, 0].max() - all_xy[:, 0].min(),
                     all_xy[:, 1].max() - all_xy[:, 1].min(), 1.0))

    px_per_m = 2400.0 / span                       # fit block into a ~2400 px paper
    theta = math.radians(rotation_deg)
    R = np.array([[math.cos(theta), -math.sin(theta)], [math.sin(theta), math.cos(theta)]])
    s = (1.0 + scale_pct / 100.0) * px_per_m

    def to_paper(xy: np.ndarray) -> np.ndarray:
        return (xy - np.array([cx, cy])) @ R.T * s

    paper_rings = [to_paper(r) for r in rings_m]
    xs = np.concatenate([r[:, 0] for r in paper_rings])
    ys = np.concatenate([r[:, 1] for r in paper_rings])
    pad = 120.0
    origin = np.array([float(xs.min() - pad), float(ys.min() - pad)])
    size = (int(xs.max() - xs.min() + 2 * pad), int(ys.max() - ys.min() + 2 * pad))
    paper_rings = [r - origin for r in paper_rings]

    # ground control points: known lat/lon <-> measured scan pixel
    gx = np.linspace(all_xy[:, 0].min(), all_xy[:, 0].max(), cp_grid)
    gy = np.linspace(all_xy[:, 1].min(), all_xy[:, 1].max(), cp_grid)
    cps = []
    for X in gx:
        for Y in gy:
            true_lon, true_lat = inv.transform(float(X), float(Y))
            paper = to_paper(np.array([[X, Y]]))[0] - origin
            err = rng.normal(0.0, noise_m, size=2)   # scan-reading error, metres
            paper_obs = paper + err * s
            cps.append([float(paper_obs[0]), float(paper_obs[1]),
                        float(true_lon), float(true_lat)])   # [px, py, lon, lat]
    cps_arr = np.array(cps)

    params, resid_deg = fit_affine(cps_arr)
    m_per_deg_lat = 110_540.0
    m_per_deg_lon = 111_320.0 * math.cos(math.radians(site_lat))
    res_m = np.column_stack([resid_deg[:, 0] * m_per_deg_lon, resid_deg[:, 1] * m_per_deg_lat])
    rmse_m = float(np.sqrt((res_m ** 2).sum(axis=1).mean()))

    recorded = []
    for ring in paper_rings:
        lon, lat = apply_affine(params, ring[:, 0], ring[:, 1])
        poly = Polygon(np.column_stack([lon, lat]))
        if not poly.is_valid:
            poly = poly.buffer(0)
        recorded.append(mapping(poly))

    return GeorefResult(
        control_points=[{"pixel_x": c[0], "pixel_y": c[1], "lat": c[3], "lon": c[2]}
                        for c in cps],
        affine=list(map(float, params)),
        rmse_m=rmse_m,
        distortion={"rotation_deg": rotation_deg, "scale_pct": scale_pct,
                    "noise_m": noise_m, "cp_grid": cp_grid},
        recorded=recorded,
        scan_pixels=[r.tolist() for r in paper_rings],
        paper_size_px=size,
        origin_px=(float(origin[0]), float(origin[1])),
    )
