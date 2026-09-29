"""Geometry helpers for the reconciliation engine (PRD Module 06).

All area/distance math runs in a projected CRS (local UTM zone); geometries are
stored in WGS84 (EPSG:4326) GeoJSON and reprojected in/out for computation.
"""
from __future__ import annotations

import math
from typing import Iterable, Sequence

from pyproj import CRS, Transformer
from shapely.geometry import LineString, MultiLineString, Point, Polygon, mapping, shape
from shapely.ops import transform as shapely_transform, unary_union
from shapely import segmentize

WGS84 = "EPSG:4326"


def utm_epsg(lon: float, lat: float) -> str:
    """Local UTM zone EPSG code for a WGS84 point."""
    zone = int(math.floor((lon + 180.0) / 6.0)) + 1
    return f"EPSG:{32600 + zone if lat >= 0 else 32700 + zone}"


def make_transformer(lon: float, lat: float) -> Transformer:
    return Transformer.from_crs(CRS.from_epsg(4326), CRS.from_user_input(utm_epsg(lon, lat)), always_xy=True)


def make_inverse(lon: float, lat: float) -> Transformer:
    """UTM (local zone for the point) -> WGS84."""
    return Transformer.from_crs(CRS.from_user_input(utm_epsg(lon, lat)),
                                CRS.from_epsg(4326), always_xy=True)


def project_geojson(geojson: dict, fwd: Transformer) -> dict:
    return mapping(shapely_transform(lambda x, y, z=None: fwd.transform(x, y), shape(geojson)))


def unproject_geojson(geojson: dict, inv: Transformer) -> dict:
    return mapping(shapely_transform(lambda x, y, z=None: inv.transform(x, y), shape(geojson)))


def geom_of(geojson: dict) -> Polygon:
    g = shape(geojson)
    if not isinstance(g, Polygon):
        raise TypeError(f"expected Polygon, got {g.geom_type}")
    return g


def sanitize_poly(g):
    """Coerce any shapely geometry to a single valid Polygon.

    Self-intersecting rings (e.g. cut halves) -> buffer(0); if that collapses
    to lines/points/multipolygons -> largest part or convex hull. Never returns
    an invalid polygon.
    """
    from shapely.geometry import MultiPolygon
    if g.is_empty:
        raise ValueError("empty geometry")
    if isinstance(g, Polygon) and g.is_valid:
        return g
    fixed = g.buffer(0)
    if isinstance(fixed, Polygon) and fixed.is_valid and not fixed.is_empty:
        return fixed
    if isinstance(fixed, MultiPolygon):
        parts = sorted(fixed.geoms, key=lambda p: p.area, reverse=True)
        if parts and parts[0].is_valid and parts[0].area > 0:
            return parts[0]
    hull = g.convex_hull
    if isinstance(hull, Polygon) and hull.is_valid and hull.area > 0:
        return hull
    raise ValueError("geometry could not be coerced to a valid polygon")


def polygon_area_ha(geojson: dict, fwd: Transformer | None = None) -> float:
    """Area in hectares, computed in the local UTM zone.

    When no transformer is supplied the geometry projects itself around its own
    centroid — calling sites must never accidentally compute an area in square
    degrees (that bug rounded every recorded area to 0.0 ha).
    """
    g = geom_of(geojson)
    if fwd is None:
        c = g.centroid
        fwd = make_transformer(c.x, c.y)
    g = shapely_transform(lambda x, y, z=None: fwd.transform(x, y), g)
    return abs(g.area) / 10_000.0


def is_valid_polygon(geojson: dict) -> tuple[bool, list[str]]:
    try:
        g = geom_of(geojson)
    except Exception:
        return False, ["GEOMETRY_INVALID"]
    if g.is_empty or not g.is_valid or not g.is_simple:
        return False, ["GEOMETRY_INVALID"]
    return True, []


def iou(a: dict, b: dict, fwd: Transformer) -> float:
    ga = shapely_transform(lambda x, y, z=None: fwd.transform(x, y), geom_of(a))
    gb = shapely_transform(lambda x, y, z=None: fwd.transform(x, y), geom_of(b))
    inter = ga.intersection(gb).area
    union = ga.union(gb).area
    return float(inter / union) if union > 0 else 0.0


def overlap_fraction(parcel: dict, other: dict, fwd: Transformer) -> float:
    ga = shapely_transform(lambda x, y, z=None: fwd.transform(x, y), geom_of(parcel))
    gb = shapely_transform(lambda x, y, z=None: fwd.transform(x, y), geom_of(other))
    if ga.area <= 0:
        return 0.0
    return float(ga.intersection(gb).area / ga.area)


def union_geojson(polys: Sequence[dict]) -> dict | None:
    geoms = [geom_of(p) for p in polys]
    if not geoms:
        return None
    u = unary_union(geoms)
    return mapping(u) if not u.is_empty else None


def boundary_displacement_m(a: dict, b: dict, fwd: Transformer, sample_interval_m: float) -> float:
    """ASBD for two WGS84 polygon dicts: project, then call asbd_projected."""
    ga = shapely_transform(lambda x, y, z=None: fwd.transform(x, y), geom_of(a))
    gb = shapely_transform(lambda x, y, z=None: fwd.transform(x, y), geom_of(b))
    return asbd_projected(ga, gb, sample_interval_m)


def _segmentized_boundary_lines(g, sample_interval_m: float) -> list[LineString]:
    """Densified exterior-ring linework of a Polygon or MultiPolygon."""
    if g.geom_type == "Polygon":
        parts = [g]
    elif g.geom_type == "MultiPolygon":
        parts = list(g.geoms)
    else:
        return []
    lines = []
    for p in parts:
        if p.is_empty or p.exterior is None:
            continue
        lines.append(segmentize(LineString(p.exterior.coords), sample_interval_m))
    return lines


def asbd_projected(ga, gb, sample_interval_m: float) -> float:
    """Average Symmetric Boundary Distance between two *projected* polygons:
    densify both boundaries to a vertex every `sample_interval_m`, then mean of
    the per-vertex nearest-point distances in both directions.

    MultiPolygon inputs (e.g. the union of a SPLIT's AI polygons) are handled
    through their boundary linework — a bbox fallback here produced meaningless
    ~90 m displacements for parcels whose IoU was 0.99.
    """
    if not ga.is_valid:
        ga = ga.buffer(0)
    if not gb.is_valid:
        gb = gb.buffer(0)
    if ga.is_empty or gb.is_empty:
        # degenerate input: coarse bound so triage never crashes
        return float(max(abs(ga.bounds[2] - ga.bounds[0]) if not ga.is_empty else 0.0,
                         abs(gb.bounds[3] - gb.bounds[1]) if not gb.is_empty else 0.0))
    lines_a = _segmentized_boundary_lines(ga, sample_interval_m)
    lines_b = _segmentized_boundary_lines(gb, sample_interval_m)
    if not lines_a or not lines_b:
        return float(max(abs(ga.bounds[2] - ga.bounds[0]),
                         abs(gb.bounds[3] - gb.bounds[1])))
    line_a = unary_union(lines_a)
    line_b = unary_union(lines_b)
    dists: list[float] = []
    for seg in lines_a:
        dists += [Point(x, y).distance(line_b) for x, y in seg.coords]
    for seg in lines_b:
        dists += [Point(x, y).distance(line_a) for x, y in seg.coords]
    return float(sum(dists) / len(dists)) if dists else 0.0


def support_ratio_pct(parcel: dict, feature_lines: Iterable[dict], fwd: Transformer, buffer_m: float) -> float:
    """% of the cadastral polygon's perimeter length falling inside a `buffer_m`
    buffer around the AI-detected boundary features."""
    gp = shapely_transform(lambda x, y, z=None: fwd.transform(x, y), geom_of(parcel))
    perimeter = LineString(gp.exterior.coords)
    if perimeter.length <= 0:
        return 0.0
    lines: list[LineString] = []
    for feat in feature_lines:
        try:
            g = shapely_transform(lambda x, y, z=None: fwd.transform(x, y), shape(feat))
            if g.is_empty:
                continue
            if isinstance(g, LineString):
                lines.append(g)
            elif isinstance(g, MultiLineString):
                lines.extend(list(g.geoms))
            elif g.geom_type == "Polygon":
                lines.append(LineString(g.exterior.coords))
            elif g.geom_type == "MultiPolygon":
                lines.append(LineString(list(g.geoms)[0].exterior.coords))
        except Exception:
            continue
    if not lines:
        return 0.0
    support = unary_union(lines).buffer(buffer_m)
    supported_len = perimeter.intersection(support).length
    return float(100.0 * supported_len / perimeter.length)


def neighbor_overlap_pct(parcel: dict, neighbor: dict, fwd: Transformer) -> float:
    """Overlap area as a percentage of the parcel's own area."""
    return 100.0 * overlap_fraction(parcel, neighbor, fwd)


def centroid_of(geojson: dict) -> tuple[float, float]:
    c = geom_of(geojson).centroid
    return float(c.y), float(c.x)
