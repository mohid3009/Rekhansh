"""Unit tests for the reconciliation formulas (PRD Module 06), triage rules
(Module 07), hash chain (Module 09) and config-driven thresholds (US-0.2).

Run: python -m pytest backend/tests -q
"""
import math
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import load_triage_config
from app.geo import (asbd_projected, boundary_displacement_m, iou, make_transformer,
                     neighbor_overlap_pct, polygon_area_ha, sanitize_poly,
                     support_ratio_pct, utm_epsg)
from app.hashchain import canonical_json, compute_record_hash, verify_chain
from app.pipeline.triage import triage_parcel
from shapely.geometry import LineString, Polygon, mapping, shape

LAT, LON = 19.910, 73.900


def square(lon, lat, size_m):
    """Axis-aligned square polygon (WGS84) centred on lon/lat, size in metres."""
    dlon = size_m / (111_320.0 * math.cos(math.radians(lat)))
    dlat = size_m / 110_540.0
    return mapping(Polygon([
        (lon - dlon / 2, lat - dlat / 2), (lon + dlon / 2, lat - dlat / 2),
        (lon + dlon / 2, lat + dlat / 2), (lon - dlon / 2, lat + dlat / 2)]))


@pytest.fixture
def fwd():
    return make_transformer(LON, LAT)


# --------------------------------------------------------------------------- #
# geometry / projection
# --------------------------------------------------------------------------- #
def test_utm_zone_for_site():
    assert utm_epsg(73.9, 19.91) == "EPSG:32643"


def test_area_of_100m_square_is_one_hectare(fwd):
    assert polygon_area_ha(square(LON, LAT, 100.0), fwd) == pytest.approx(1.0, rel=0.01)


def test_iou_identical_is_one(fwd):
    g = square(LON, LAT, 100)
    assert iou(g, g, fwd) == pytest.approx(1.0)


def test_iou_disjoint_is_zero(fwd):
    a = square(LON, LAT, 100)
    b = square(LON + 0.01, LAT, 100)
    assert iou(a, b, fwd) == pytest.approx(0.0, abs=1e-9)


def test_iou_half_shifted(fwd):
    """Shift a square by half its width -> IoU = 1/3 (classic 2-D result)."""
    a = square(LON, LAT, 100)
    b = square(LON + 0.00045, LAT, 100)   # ~45 m east at this latitude
    val = iou(a, b, fwd)
    assert val == pytest.approx(1 / 3, abs=0.05)


def test_asbd_zero_for_identical(fwd):
    g = square(LON, LAT, 100)
    assert boundary_displacement_m(g, g, fwd, 0.5) == pytest.approx(0.0, abs=1e-6)


def test_asbd_shift_meters(fwd):
    """ASBD per PRD: mean of vertex-to-opposite-ring distances *both ways*.

    For a pure translation by d of a rectangle, side vertices are collinear
    with the other ring (distance 0) while top/bottom vertices are d away,
    so the PRD-defined ASBD of a translation is d/2 (verified here)."""
    from shapely.affinity import translate
    a = shape(square(LON, LAT, 100))
    dlat = 0.8 / 110_540.0
    b = translate(a, yoff=dlat)
    val = boundary_displacement_m(mapping(a), mapping(b), fwd, 0.5)
    assert val == pytest.approx(0.4, abs=0.03)


def test_asbd_projected_direct(fwd):
    from shapely.ops import transform as sh_transform
    a = shape(square(LON, LAT, 100))
    ga = sh_transform(lambda x, y, z=None: fwd.transform(x, y), a)
    gb = type(ga)([(x + 1.5, y) for x, y in ga.exterior.coords])
    val = asbd_projected(ga, gb, 0.5)
    assert val == pytest.approx(0.75, abs=0.03)   # translation d -> d/2 (see above)


def test_support_ratio_full_and_none(fwd):
    g = square(LON, LAT, 100)
    ring = shape(g).exterior.__geo_interface__
    assert support_ratio_pct(g, [ring], fwd, 1.0) == pytest.approx(100.0, abs=1.0)
    assert support_ratio_pct(g, [], fwd, 1.0) == pytest.approx(0.0)


def test_support_ratio_far_line_is_zero(fwd):
    g = square(LON, LAT, 100)
    far = LineString([(LON + 0.01, LAT), (LON + 0.011, LAT)]).__geo_interface__
    assert support_ratio_pct(g, [far], fwd, 1.0) == pytest.approx(0.0)


def test_neighbor_overlap_pct(fwd):
    a = square(LON, LAT, 100)
    b = square(LON + 0.0005, LAT, 100)     # overlaps ~half? -> between 0 and 100
    val = neighbor_overlap_pct(a, b, fwd)
    assert 0 < val <= 100


def test_sanitize_poly_fixes_bowtie():
    bow = Polygon([(0, 0), (2, 2), (2, 0), (0, 2)])
    assert not bow.is_valid
    fixed = sanitize_poly(bow)
    assert fixed.is_valid and fixed.geom_type == "Polygon"


# --------------------------------------------------------------------------- #
# regressions: units and geometry-type handling
# --------------------------------------------------------------------------- #
def test_polygon_area_ha_self_projects_when_no_transformer():
    """Calling without a projector must NOT compute square degrees (this bug
    rounded every recorded_area_ha in the seed to 0.0)."""
    g = square(LON, LAT, 100.0)
    assert polygon_area_ha(g) == pytest.approx(1.0, rel=0.01)
    assert polygon_area_ha(g, make_transformer(LON, LAT)) == pytest.approx(1.0, rel=0.01)


def test_asbd_multipolygon_union_is_boundary_scale(fwd):
    """A SPLIT match yields a MultiPolygon union of two jittered halves; ASBD
    must stay at boundary scale, not collapse to a bbox-sized fallback."""
    from shapely.affinity import translate
    from shapely.geometry import LineString
    from shapely.ops import split as sh_split, unary_union

    gp = sh_transform_fwd(shape(square(LON, LAT, 100.0)), fwd)
    xmin, ymin, xmax, ymax = gp.bounds
    halves = sh_split(gp, LineString([(xmin + 50.0, ymin - 1), (xmin + 50.0, ymax + 1)]))
    parts = [translate(g, xoff=off) for g, off in
             zip(sorted(halves.geoms, key=lambda p: p.bounds[0]), (-1.5, 1.5))]
    union = unary_union(parts)
    assert union.geom_type == "MultiPolygon", "halves must be disjoint after jitter"
    val = asbd_projected(gp, union, 0.5)
    assert 0.0 < val < 10.0, f"ASBD blew up to {val} for a MultiPolygon union"


def sh_transform_fwd(g, fwd):
    from shapely.ops import transform as _t
    return _t(lambda x, y, z=None: fwd.transform(x, y), g)


def test_occlusion_is_measured_from_imagery_pixels():
    """measure_occlusion must read the orthomosaic pixels (a truncated body
    made it always return None, silently falling back to random sampling)."""
    import numpy as np
    from app.config import load_triage_config
    from app.pipeline.reconcile import measure_occlusion
    from app.raster import WorldFileAffine

    cfg = load_triage_config()
    n_px, m_per_px = 100, 1.0
    m_per_deg_lon = 111_320.0 * np.cos(np.radians(LAT))
    m_per_deg_lat = 110_540.0
    aff = WorldFileAffine(A=1.0 / m_per_deg_lon, B=0.0, C=LON - n_px * m_per_px / 2 / m_per_deg_lon,
                          D=0.0, E=-1.0 / m_per_deg_lat, F=LAT + n_px * m_per_px / 2 / m_per_deg_lat)
    bright = np.full((n_px, n_px, 3), 180, dtype=np.uint8)      # bare soil: no shadow/canopy
    dark = np.full((n_px, n_px, 3), 30, dtype=np.uint8)         # fully shadowed
    assert measure_occlusion(bright, aff, square(LON, LAT, 90.0), cfg) == pytest.approx(0.0, abs=0.05)
    assert measure_occlusion(dark, aff, square(LON, LAT, 90.0), cfg) == pytest.approx(1.0, abs=0.05)
