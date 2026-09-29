"""Tier 2 — classical CV field-boundary extraction (PRD Module 04).

Canny edge detection -> contour extraction -> Douglas-Peucker simplification on
the orthomosaic, with feature tagging (boundary / bund / fence / road /
irrigation channel) from line geometry and spectral cues. Same output schema as
Tier 3's synthetic fallback, so downstream modules don't care which tier ran.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import cv2
import numpy as np
from shapely.geometry import Polygon, mapping

from .raster import WorldFileAffine


@dataclass
class ExtractedPolygon:
    """Tier-agnostic output — maps directly onto the AIFieldPolygon model."""

    geometry: dict                     # GeoJSON Polygon, WGS84
    confidence: float                  # 0-1
    detected_features: list[str] = field(default_factory=list)
    source: str = "CV_MODEL"


def _gray(img: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY) if img.ndim == 3 else img


def spectral_features(img: np.ndarray, contour_pts: np.ndarray) -> list[str]:
    """Tag detected features from spectral cues inside the contour."""
    if img.ndim != 3:
        return ["BOUNDARY"]
    x, y, w, h = cv2.boundingRect(contour_pts)
    patch = img[y:y + h, x:x + w].astype(np.float64)
    r, g, b = patch[..., 0], patch[..., 1], patch[..., 2]
    exg = 2 * g - r - b
    bright = (r + g + b) / 3.0
    tags: list[str] = []
    if float(np.mean(bright)) < 55:
        tags.append("IRRIGATION_CHANNEL")     # dark, water-like patch
    if float((exg < 12).mean()) > 0.55 and float(np.mean(bright)) > 80:
        tags.append("BUND")                   # bare-soil lineation between crops
    if float((exg < 20).mean()) > 0.6:
        tags.append("BOUNDARY")
    if h > 0 and w > 0 and max(w, h) / max(1, min(w, h)) > 6:
        tags.append("ROAD")                   # long thin corridor
    return tags or ["BOUNDARY"]


def extract_from_image(
    img: np.ndarray,
    affine: WorldFileAffine,
    resolution_m_per_px: float,
    min_area_ha: float,
    max_area_ha: float,
    canny_low: int = 40,
    canny_high: int = 110,
    dp_scale_px: float = 2.0,
) -> list[ExtractedPolygon]:
    """Canny -> contours -> Douglas-Peucker, filtered to plausible parcel sizes.

    `affine` maps orthomosaic pixel coordinates to WGS84 lon/lat, so returned
    polygons are already georeferenced.
    """
    gray = _gray(img)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, canny_low, canny_high)
    edges = cv2.dilate(edges, np.ones((3, 3), np.uint8), iterations=1)
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    px2m2 = resolution_m_per_px ** 2
    min_px = max(24.0, min_area_ha * 10_000.0 / px2m2)
    max_px = max(40.0, max_area_ha * 10_000.0 / px2m2)

    candidates: list[tuple[float, Polygon, np.ndarray]] = []
    for cnt in sorted(contours, key=cv2.contourArea, reverse=True):
        area_px = float(cv2.contourArea(cnt))
        if area_px < min_px or area_px > max_px:
            continue
        approx = cv2.approxPolyDP(cnt, dp_scale_px, True)
        if len(approx) < 4:
            continue
        ring = [affine.px_to_lonlat(float(p[0][0]), float(p[0][1])) for p in approx]
        poly = Polygon(ring)
        if not poly.is_valid or poly.is_empty:
            continue
        candidates.append((area_px, poly, approx))

    # containment de-dup: keep the largest polygon in any nested group
    kept: list[tuple[float, Polygon, np.ndarray]] = []
    for area_px, poly, approx in candidates:
        if any(poly.within(k[1]) for k in kept):
            continue
        kept = [k for k in kept if not k[1].within(poly)]
        kept.append((area_px, poly, approx))

    out: list[ExtractedPolygon] = []
    for area_px, poly, approx in kept:
        hull_area = max(float(cv2.contourArea(cv2.convexHull(approx))), 1.0)
        solidity = area_px / hull_area
        area_score = min(1.0, area_px / max_px * 6.0)
        confidence = float(np.clip(0.30 + 0.45 * solidity + 0.25 * area_score, 0.05, 0.98))
        out.append(ExtractedPolygon(
            geometry=mapping(poly),
            confidence=round(confidence, 3),
            detected_features=spectral_features(img, approx),
            source="CV_MODEL",
        ))
    return out
