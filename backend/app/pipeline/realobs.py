"""Real observation sources: co-located FTW-2016 fields + OSM farmland.

Primary: Fields-of-the-World India-10K ML set (vendored
`backend/data/india_fields_2016.parquet`, 10,013 manually delineated crop
fields, CC-BY-4.0, Wang/Waldner/Lobell via Zenodo 7315090), consumed at
their TRUE locations. Secondary: OSM farmland polygons around the pilot
extent (ODbL). Both return AIFieldPolygon rows with per-polygon
`evidence_note` provenance (dataset, licence, delineation method).

Co-location gate: polygons farther than MAX_DIST_M from the pilot centre
are NOT returned as observations (a field 28 km away cannot evidence a
parcel here); the report states the nearest real-field distance so the
pipeline/UI can say so honestly instead of silently matching nothing.
"""
from __future__ import annotations

import json

from shapely.geometry import Point, mapping, shape
from shapely.ops import transform as sh_transform

from ..config import DATA_DIR, TriageConfig
from ..geo import make_transformer, sanitize_poly

FTW_PARQUET = DATA_DIR / "india_fields_2016.parquet"
OSM_FARMLAND = DATA_DIR / "context" / "osm_farmland.geojson"

FTW_NOTE = ("FTW India-10K ML (source.coop/ftw india-10k-ml, CC-BY-4.0; "
            "Wang, Waldner & Lobell 2022, Zenodo 7315090; manually "
            "delineated crop fields on Airbus SPOT imagery)")
OSM_NOTE = "OSM farmland polygons (OpenStreetMap contributors, ODbL-1.0)"


def load_real_observations(site, cfg: TriageConfig,
                           max_dist_m: float = 2_000.0,
                           max_polys: int = 60) -> tuple[list[dict], dict]:
    """Co-located real field polygons as AIFieldPolygon rows + report dict."""
    _ = cfg
    fwd = make_transformer(site.lon, site.lat)

    def to_m(g):
        return sh_transform(lambda x, y, z=None: fwd.transform(x, y), g)

    site_pt = to_m(Point(site.lon, site.lat))
    rows: list[dict] = []
    report: dict = {"tier1_polygons": 0, "ftw_note": "", "osm_note": "",
                    "max_dist_m": max_dist_m}

    if FTW_PARQUET.exists():
        import pyarrow.parquet as pq
        import shapely

        t = pq.read_table(str(FTW_PARQUET), columns=["id", "area", "geometry"])
        ids = t.column("id").to_pylist()
        areas = t.column("area").to_pylist()
        near: list[tuple[float, object, float, str]] = []
        for fid, a, w in zip(ids, areas, t.column("geometry").to_pylist()):
            try:
                g = shapely.from_wkb(w)
                d = to_m(g).distance(site_pt)
            except Exception:
                continue
            near.append((d, g, float(a or 0.0), str(fid)))
        near.sort(key=lambda r: r[0])
        n_in = sum(1 for d, _, _, _ in near if d <= max_dist_m)
        report["ftw_note"] = (
            f"FTW India-10K ({t.num_rows} fields): nearest "
            f"{near[0][0] / 1000:.1f} km from pilot; {n_in} within "
            f"{max_dist_m / 1000:.0f} km" if near else "FTW India-10K: empty")
        k = 0
        for d, g, a, fid in near:
            if d > max_dist_m or len(rows) >= max_polys:
                break
            try:
                poly = sanitize_poly(g)
            except ValueError:
                continue
            k += 1
            rows.append({
                "id": f"AIFP-FTW-{k:04d}",
                "survey_id": "SUR-FTW-10K",
                "geometry": mapping(poly),
                "confidence": 0.90,
                "detected_features": ["BOUNDARY"],
                "source": "CV_MODEL",
                "evidence_note": (
                    f"{FTW_NOTE}; field {fid} ({a / 10000:.2f} ha) "
                    f"{d / 1000:.1f} km from pilot"),
            })
    else:
        report["ftw_note"] = "FTW India-10K parquet not vendored"

    if OSM_FARMLAND.exists():
        doc = json.loads(OSM_FARMLAND.read_text(encoding="utf-8"))
        feats = doc.get("features", doc.get("elements", []))
        geoms = []
        for f in feats:
            try:
                g = shape(f.get("geometry", f))
                if g.geom_type == "Polygon" and g.is_valid:
                    geoms.append(g)
            except Exception:
                continue
        near = []
        for g in geoms:
            try:
                near.append((to_m(g).distance(site_pt), g))
            except Exception:
                continue
        near.sort(key=lambda r: r[0])
        report["osm_note"] = (
            f"OSM farmland ({len(feats)} features): nearest "
            f"{near[0][0] / 1000:.1f} km from pilot" if near
            else f"OSM farmland ({len(feats)} features): no polygons")
        k = 0
        for d, g in near:
            if d > max_dist_m or len(rows) >= max_polys:
                break
            try:
                poly = sanitize_poly(g)
            except ValueError:
                continue
            k += 1
            rows.append({
                "id": f"AIFP-OSM-{k:04d}",
                "survey_id": "SUR-OSM",
                "geometry": mapping(poly),
                "confidence": 0.70,
                "detected_features": ["BOUNDARY"],
                "source": "CV_MODEL",
                "evidence_note": (
                    f"{OSM_NOTE} {d / 1000:.1f} km from pilot"),
            })
    else:
        report["osm_note"] = "osm_farmland.geojson not vendored"

    report["tier1_polygons"] = len(rows)
    report["real_polygons"] = len(rows)
    return rows, report


