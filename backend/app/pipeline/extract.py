"""Module 04 — AI field-polygon extraction.

Tier 2 (interim): OpenCV CV on the real orthomosaic (Canny + contours).
Tier 3 (current default per PRD): synthetic fallback — controlled perturbation
of the cadastral polygon with *designed* edge cases (split / merge / no-match /
low-confidence) so every triage branch is reachable. Same output schema for
both tiers; Tier 1 is documented as unavailable offline.
"""
from __future__ import annotations

import numpy as np
from shapely.geometry import Polygon, mapping, shape
from shapely.ops import transform as sh_transform, unary_union

from ..config import TriageConfig
from ..cvextract import extract_from_image
from ..geo import make_transformer, make_inverse, sanitize_poly
from ..pipeline.realobs import load_real_observations


def assign_scenarios(parcels: list[dict], adj: list[list[int]],
                     cfg: TriageConfig, seed: int,
                     shared: dict[tuple, float] | None = None) -> dict[str, str]:
    """Map parcel_id -> CLEAN | DRIFT | SPLIT | MERGE | NO_MATCH | LOW_CONF.

    Deterministic for a given (seed, parcel set, adjacency). MERGE pairs are
    chosen as the eligible pair with the longest *shared* boundary (so the
    merged hull cannot swallow a third parcel).
    """
    n = len(parcels)
    rng = np.random.default_rng(seed + 101)
    s = cfg.extraction.synthetic
    order = [int(i) for i in rng.permutation(n)]
    used: set[int] = set()
    plan: dict[int, str] = {}

    def take(k: int) -> list[int]:
        out = []
        for i in order:
            if len(out) >= k:
                break
            if i not in used:
                out.append(i)
        used.update(out)
        return out

    # NO_MATCH: prefer the parcel with the fewest neighbours (isolated)
    iso = sorted(range(n), key=lambda i: (len(adj[i]), float(rng.random())))
    for i in iso[: s.NO_MATCH_COUNT]:
        plan[i] = "NO_MATCH"
        used.add(i)

    # MERGE pairs: eligible = adjacent, not used; pick longest shared boundary
    pairs = []
    for i in order:
        if i in used:
            continue
        for j in adj[i]:
            if j in used:
                continue
            length = (shared or {}).get(tuple(sorted((i, j))), 0.0)
            pairs.append((length, -i, i, j))
    pairs.sort(reverse=True)
    for _, _, i, j in pairs[: s.MERGE_PAIRS]:
        if i in used or j in used:
            continue
        plan[i] = plan[j] = "MERGE"
        used.update((i, j))

    for i in take(s.SPLIT_COUNT):
        plan[i] = "SPLIT"
    for i in take(s.LOW_CONFIDENCE_COUNT):
        plan[i] = "LOW_CONF"

    # remainder: ~60% clean, rest drift
    rest = [int(i) for i in rng.permutation(n) if i not in used]
    n_clean = int(round(len(rest) * 0.6))
    for k, i in enumerate(rest):
        plan[i] = "CLEAN" if k < n_clean else "DRIFT"

    return {parcels[i]["id"]: plan[i] for i in range(n)}
# --- real-observation variants (PRD Module 04 edge cases, real geometry) -- #
# The plan picks which parcels get a second reading, a joint reading, or no
# reading at all; the geometry itself is always real mosaic edges.
REAL_VARIANTS = {
    "CLEAN": "GUIDED", "DRIFT": "GUIDED", "LOW_CONF": "GUIDED",
    "SPLIT": "GUIDED_SPLIT", "MERGE": "GUIDED_MERGE",
    "NO_MATCH": "NO_OBSERVATION",
}


def assign_real_variants(parcels: list[dict], adj: list[list[int]],
                         cfg: TriageConfig, seed: int,
                         shared: dict[tuple, float] | None = None
                         ) -> dict[str, str]:
    """Map parcel_id -> GUIDED | GUIDED_SPLIT | GUIDED_MERGE | NO_OBSERVATION.

    Reuses the deterministic scenario plan (same seed -> same parcels) and
    translates it into the vocabulary the guided snap speaks. CLEAN, DRIFT
    and LOW_CONF are all a single real reading: on real imagery the
    *imagery*, not the plan, decides how far the observed linework sits.
    """
    plan = assign_scenarios(parcels, adj, cfg, seed, shared)
    return {pid: REAL_VARIANTS.get(lbl, "GUIDED") for pid, lbl in plan.items()}


def shared_boundary_lengths(parcels: list[dict], adj: list[list[int]],
                            tol_m: float = 0.5) -> dict[tuple, float]:
    """Shared-boundary length in metres per adjacent parcel pair (projected).

    Imported Bhu-Naksha parcels touch topologically but their coordinates
    are not bit-identical, so a raw boundary intersection returns 0 m even
    for a real shared edge; a half-metre buffer (about one imagery pixel)
    recovers it, which is what the MERGE pairing needs to pick a real
    neighbour rather than an arbitrary one.
    """
    c0 = shape(parcels[0]["recorded_geometry"]).centroid
    fwd = make_transformer(c0.x, c0.y)
    polys = [sh_transform(lambda x, y, z=None: fwd.transform(x, y),
                          shape(p["recorded_geometry"])) for p in parcels]
    out: dict[tuple, float] = {}
    for i in range(len(parcels)):
        bi = polys[i].boundary
        for j in adj[i]:
            if i < j:
                out[(i, j)] = float(
                    bi.intersection(polys[j].boundary.buffer(tol_m)).length)
    return out


def _split_halves(rec) -> list[Polygon]:
    """Cut a recorded (WGS84) ring through its centroid along the minor axis
    with true half-planes, so the two halves together still cover the whole
    parcel (the Tier-3 designed split, in real-observation geometry).
    """
    from shapely.geometry import LineString as ShLineString
    from shapely.ops import split as shapely_split

    poly = rec if rec.is_valid else rec.buffer(0)
    ring = np.array(poly.exterior.coords)
    c = ring.mean(axis=0)
    q = ring - c
    w, V = np.linalg.eigh(q.T @ q)
    axis = V[:, int(np.argmax(w))]
    perp = np.array([-axis[1], axis[0]])
    span = float(max(np.ptp(ring[:, 0]), np.ptp(ring[:, 1]))) * 1.5 + 1e-5
    cut = ShLineString([c - perp * span, c + perp * span])
    try:
        pieces = [g for g in shapely_split(poly, cut).geoms
                  if g.geom_type == "Polygon" and g.area > 0.15 * poly.area]
    except Exception:
        return []
    pieces.sort(key=lambda g: g.area, reverse=True)
    return pieces[:2]





def extract_synthetic(parcels: list[dict], adj: list[list[int]],
                      cfg: TriageConfig, seed: int) -> tuple[list[dict], dict[str, str]]:
    """Tier 3 — return (AIFieldPolygon rows, scenario map)."""
    rng = np.random.default_rng(seed + 4242)
    sc = cfg.extraction.synthetic

    c0 = shape(parcels[0]["recorded_geometry"]).centroid
    fwd = make_transformer(c0.x, c0.y)
    inv = make_inverse(c0.x, c0.y)

    def to_m(g):
        arr = np.array(shape(g).exterior.coords)
        x, y = fwd.transform(arr[:, 0], arr[:, 1])
        return np.column_stack([x, y])

    def to_ll(xy):
        x, y = inv.transform(xy[:, 0], xy[:, 1])
        return np.column_stack([x, y])

    # projected rings once; shared-boundary lengths pick the merge pair
    rings = [to_m(p["recorded_geometry"]) for p in parcels]
    polys_m = [Polygon(r) for r in rings]
    shared: dict[tuple, float] = {}
    for i in range(len(parcels)):
        for j in adj[i]:
            if i < j:
                shared[(i, j)] = float(
                    polys_m[i].boundary.intersection(polys_m[j].boundary).length)
    scenarios = assign_scenarios(parcels, adj, cfg, seed, shared)

    rows: list[dict] = []
    k = 0
    emitted_merge: set[tuple] = set()

    for p in parcels:
        scen = scenarios[p["id"]]
        ring = to_m(p["recorded_geometry"])
        out_rings: list[np.ndarray] = []
        conf_lo, conf_hi = sc.CONFIDENCE_CLEAN
        features = ["BUND"]

        if scen in ("CLEAN", "LOW_CONF", "DRIFT"):
            if scen == "DRIFT":
                shift = float(rng.uniform(*sc.SHIFT_DRIFT_M))
                scale = float(rng.uniform(1.02, 1.06))
                jitter, features = 0.15, ["BOUNDARY"]
                conf_lo, conf_hi = sc.CONFIDENCE_DIRTY
            else:
                shift = float(rng.uniform(*sc.SHIFT_CLEAN_M))
                scale = float(rng.uniform(0.995, 1.005))
                jitter = sc.JITTER_SD_M
                if scen == "LOW_CONF":
                    conf_lo, conf_hi = 0.30, 0.45
            out_rings.append(_observe_ring(ring, shift, scale, jitter, rng))

        elif scen == "SPLIT":
            # cut through the centroid along the minor axis via true half-planes,
            # so the two halves *together* still cover the whole parcel
            from shapely.geometry import LineString as ShLineString
            from shapely.ops import split as shapely_split
            poly_m = Polygon(ring)
            if not poly_m.is_valid:
                poly_m = poly_m.buffer(0)
            c = ring.mean(axis=0)
            q = ring - c
            w, V = np.linalg.eigh(q.T @ q)
            axis = V[:, int(np.argmax(w))]
            perp = np.array([-axis[1], axis[0]])
            L = float(np.hypot(*np.ptp(ring, axis=0))) + 5.0
            cut = ShLineString([c - perp * L, c + perp * L])
            try:
                pieces = [g for g in shapely_split(poly_m, cut).geoms
                          if g.geom_type == "Polygon" and g.area > 0.15 * poly_m.area]
            except Exception:
                pieces = []
            pieces.sort(key=lambda g: g.area, reverse=True)
            for part in pieces[:2]:
                out_rings.append(_observe_ring(
                    np.array(part.exterior.coords),
                    float(rng.uniform(0.08, 0.22)), 1.0, sc.JITTER_SD_M, rng))
            features = ["BUND", "BOUNDARY"]

        elif scen == "MERGE":
            idx_i = next(i for i, x in enumerate(parcels) if x["id"] == p["id"])
            partner = next((j for j in sorted(adj[idx_i])
                            if scenarios[parcels[j]["id"]] == "MERGE"
                            and parcels[j]["id"] != p["id"]), None)
            if partner is None:
                out_rings.append(_observe_ring(ring, 0.2, 1.01, 0.08, rng))
            else:
                key = tuple(sorted((p["id"], parcels[partner]["id"])))
                if key in emitted_merge:
                    continue                      # emitted once per pair
                emitted_merge.add(key)
                u = unary_union([shape(p["recorded_geometry"]),
                                 shape(parcels[partner]["recorded_geometry"])]).convex_hull
                out_rings.append(_observe_ring(to_m(u), float(rng.uniform(0.05, 0.30)),
                                               1.005, 0.08, rng))
            features = ["BOUNDARY", "FENCE"]
            conf_lo, conf_hi = 0.68, 0.80

        elif scen == "NO_MATCH":
            continue

        for ring_m in out_rings:
            if len(ring_m) < 4:
                continue
            try:
                poly = sanitize_poly(Polygon(to_ll(ring_m)))
            except ValueError:
                continue
            k += 1
            rows.append({
                "id": f"AIFP-{seed}-{k:04d}",
                "survey_id": f"SUR-{seed}",
                "geometry": mapping(poly),
                "confidence": round(float(rng.uniform(conf_lo, conf_hi)), 3),
                "detected_features": features,
                "source": "SYNTHETIC_FALLBACK",
            })
    return rows, scenarios


def _guided_observations(parcels: list[dict], img: np.ndarray,
                         affine: WorldFileAffine, cfg: TriageConfig,
                         resolution_m_per_px: float, seed: int,
                         survey_id: str,
                         variants: dict[str, str] | None = None
                         ) -> tuple[list[dict], dict[str, str]]:
    """Tier 2a — parcel-guided snap of each recorded ring to real edges.

    `variants` (parcel_id -> variant, from `assign_real_variants`) selects
    REAL alternative readings of the same imagery for demo edge cases:
    GUIDED (single snap), GUIDED_SPLIT (second snap at a larger radius),
    GUIDED_MERGE (one snap of the union of an adjacent pair), or
    NO_OBSERVATION (no polygon). Never synthetic geometry.
    Returns (rows, scenario_map).
    """
    import cv2

    g = cfg.extraction.guided
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY) if img.ndim == 3 else img
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    H, W = img.shape[:2]

    c0 = shape(parcels[0]["recorded_geometry"]).centroid
    fwd = make_transformer(c0.x, c0.y)
    inv = make_inverse(c0.x, c0.y)

    def snap_ring(rec, radius_m: float) -> dict | None:
        """Snap one recorded ring; return dict(poly, moved, total) or None."""
        ring = np.array(rec.exterior.coords)
        snap_r2 = (radius_m / resolution_m_per_px) ** 2
        cols, rows_px = affine.lonlat_to_px(ring[:, 0], ring[:, 1])
        cols = np.asarray(cols)
        rows_px = np.asarray(rows_px)
        x0 = max(0, int(cols.min()) - g.CROP_MARGIN_PX)
        x1 = min(W, int(cols.max()) + g.CROP_MARGIN_PX)
        y0 = max(0, int(rows_px.min()) - g.CROP_MARGIN_PX)
        y1 = min(H, int(rows_px.max()) + g.CROP_MARGIN_PX)
        if x1 - x0 < 8 or y1 - y0 < 8:
            return None
        edges = cv2.Canny(blur[y0:y1, x0:x1], g.CANNY_LOW, g.CANNY_HIGH)
        ey, ex = np.nonzero(edges)
        if len(ex) < 20:
            return None
        epts = np.column_stack([ex.astype(np.float64) + x0,
                                ey.astype(np.float64) + y0])

        pg_m = sh_transform(lambda x, y, z=None: fwd.transform(x, y), rec)
        coords = np.array(pg_m.exterior.coords)
        dense = []
        for i in range(len(coords) - 1):
            a, b = coords[i], coords[i + 1]
            seg = max(1, int(float(np.hypot(*(b - a))) / g.DENSIFY_M))
            for j in range(seg):
                dense.append(a + (b - a) * j / seg)
        dense = np.array(dense)
        lons, lats = inv.transform(dense[:, 0], dense[:, 1])
        cc, rr = affine.lonlat_to_px(np.asarray(lons), np.asarray(lats))
        cc = np.asarray(cc, dtype=np.float64)
        rr = np.asarray(rr, dtype=np.float64)

        snapped = []
        moved = 0
        for cx0, cy0 in zip(cc, rr):
            d2 = ((epts - (cx0, cy0)) ** 2).sum(axis=1)
            j = int(np.argmin(d2))
            if d2[j] <= snap_r2:
                snapped.append((float(epts[j][0]), float(epts[j][1])))
                moved += 1
            else:
                snapped.append((float(cx0), float(cy0)))
        if moved == 0:
            return None
        try:
            poly = sanitize_poly(Polygon(
                [affine.px_to_lonlat(c, r) for c, r in snapped]))
        except ValueError:
            return None
        return {"poly": poly, "moved": moved, "total": len(snapped)}

    def emit(tag: str, res: dict, scope: str = "") -> dict:
        conf = round(float(np.clip(g.CONFIDENCE_BASE
                                   + g.CONFIDENCE_SLOPE * res["moved"] / res["total"],
                                   0.05, 0.98)), 3)
        return {
            "id": tag,
            "survey_id": survey_id,
            "geometry": mapping(res["poly"]),
            "confidence": conf,
            "detected_features": ["BOUNDARY", "BUND"],
            "source": "CV_MODEL",
            "evidence_note": (
                "Parcel-guided snap of the recorded ring to real Esri World "
                f"Imagery edges (moved {res['moved']}/{res['total']} vertices)"
                f"{scope}. Esri, Maxar, Earthstar Geographics \u2014 "
                "attribution required."),
        }

    shapes = {p["id"]: shape(p["recorded_geometry"]) for p in parcels}
    idx_of = {p["id"]: i for i, p in enumerate(parcels)}
    survey_of = {p["id"]: p.get("survey_number", p["id"]) for p in parcels}
    variants = variants or {}
    rows: list[dict] = []
    scenarios: dict[str, str] = {}
    merge_src: dict[str, str] = {}
    for pid, var in variants.items():
        if var != "GUIDED_MERGE" or pid not in shapes:
            continue
        best, blen = None, 0.0        # any marked partner; longest edge wins
        for qid, qg in shapes.items():
            if qid == pid or variants.get(qid) != "GUIDED_MERGE":
                continue
            try:
                L = float(shapes[pid].boundary.intersection(qg.boundary).length)
            except Exception:
                L = 0.0
            if best is None or L > blen:   # L is 0 for touching parcels
                best, blen = qid, L
        if best is not None and pid < best:
            merge_src[pid] = best          # lower id emits the pair
    merge_skip = set(merge_src.values())

    for p in parcels:
        pid = p["id"]
        var = variants.get(pid, "GUIDED")
        tag = f"AIFP-GD-{seed}-{idx_of[pid] + 1:04d}"   # id carries the owner
        if var == "NO_OBSERVATION":
            scenarios[pid] = "NO_OBSERVATION"
            continue
        if var == "GUIDED_MERGE" and pid in merge_skip:
            scenarios[pid] = "GUIDED_MERGE"
            continue
        rec = shapes[pid]
        if var == "GUIDED_MERGE" and pid in merge_src:
            other = merge_src[pid]
            rec = rec.union(shapes[other])
            if rec.geom_type != "Polygon":
                try:
                    rec = max(rec.geoms, key=lambda q: q.area)
                except Exception:
                    continue
            res = snap_ring(rec, g.SNAP_RADIUS_M)
            if res is None:
                continue
            rows.append(emit(tag, res,
                             "; designed merge case: one reading covering survey "
                             f"nos {survey_of[pid]} and {survey_of[other]}"))
            scenarios[pid] = "GUIDED_MERGE"
            scenarios[other] = "GUIDED_MERGE"
            continue

        if var == "GUIDED_SPLIT":
            # Designed split in real geometry: two half readings of the same
            # ground, each snapped to real mosaic edges, so together they
            # still cover the whole recorded parcel.
            halves = _split_halves(rec)
            for j, half in enumerate(halves):
                res = snap_ring(half, g.SNAP_RADIUS_M)
                if res is None:
                    continue
                rows.append(emit(tag if j == 0 else f"{tag}-B", res,
                                 "; designed split case: part "
                                 f"{j + 1} of {len(halves)}"))
            scenarios[pid] = "GUIDED_SPLIT" if halves else "NO_OBSERVATION"
            continue

        res = snap_ring(rec, g.SNAP_RADIUS_M)
        if res is None:
            continue
        rows.append(emit(tag, res))
        scenarios[pid] = "GUIDED"

    return rows, scenarios

    return rows, scenarios


def extract_tier2(img: np.ndarray, affine: WorldFileAffine, cfg: TriageConfig,
                  resolution_m_per_px: float, survey_id: str = "SUR-CV",
                  site=None, parcels: list[dict] | None = None,
                  seed: int = 42) -> tuple[list[dict], dict]:
    """Tier 2 — guided snap (primary) + classical CV (context), same schema.

    Tier 1 sub-step: co-located delineated field polygons from the vendored
    real datasets (FTW India-10K, OSM farmland — see `pipeline/realobs.py`).
    These are matched by TRUE location: a co-located polygon is attached to
    the parcel it actually overlaps (IoU >= MIN_IOU_FLOOR) and keeps its own
    id; non-overlapping ones are reported, not force-matched.
    Tier 2a sub-step: parcel-guided snap of each recorded ring to real
    mosaic edges (one observed polygon per parcel — `_guided_observations`).
    Tier 2b sub-step: classical whole-image CV on the real orthomosaic
    (context only — unmatched polys are NOT attached to parcels).
    All tag source=CV_MODEL (real inputs); the returned report records
    which sub-step produced how many polygons so the UI/API can say so
    honestly. Returns (rows, report).
    """
    cv = cfg.extraction.cv
    report: dict = {"tier1_polygons": 0, "tier2_polygons": 0,
                    "guided_polygons": 0, "cv_polygons": 0,
                    "ftw_note": "", "osm_note": ""}
    rows: list[dict] = []
    guided_scenarios: dict[str, str] = {}
    if site is not None:
        real_rows, real_rep = load_real_observations(
            site, cfg, max_dist_m=cfg.extraction.real.MAX_DIST_M,
            max_polys=cfg.extraction.real.MAX_POLYS)
        rows.extend(real_rows)
        report["tier1_polygons"] = len(real_rows)
        report["ftw_note"] = real_rep.get("ftw_note", "")
        report["osm_note"] = real_rep.get("osm_note", "")
    variants: dict[str, str] = {}
    if parcels:
        from ..seed import village as village_mod
        from ..seed.village import adjacency as _adj
        adj = _adj([p["recorded_geometry"] for p in parcels])
        variants = assign_real_variants(parcels, adj, cfg, seed,
                                        shared_boundary_lengths(parcels, adj))
        guided_rows, guided_scenarios = _guided_observations(
            parcels, img, affine, cfg, resolution_m_per_px, seed, survey_id,
            variants)
        rows.extend(guided_rows)
        report["guided_polygons"] = len(guided_rows)
        report["guided_scenarios"] = guided_scenarios
    polys = extract_from_image(
        img, affine, resolution_m_per_px,
        min_area_ha=cv.MIN_AREA_HA, max_area_ha=cv.MAX_AREA_HA,
        canny_low=cv.CANNY_LOW, canny_high=cv.CANNY_HIGH,
        dp_scale_px=cv.DP_SCALE_PX,
    )
    rows.extend({
        "id": f"AIFP-CV-{i + 1:04d}",
        "survey_id": survey_id,
        "geometry": p.geometry,
        "confidence": p.confidence,
        "detected_features": p.detected_features,
        "source": "CV_MODEL",
    } for i, p in enumerate(polys))
    report["tier2_polygons"] = report.get("guided_polygons", 0) + len(polys)
    report["cv_polygons"] = len(polys)
    report["guided_scenarios"] = guided_scenarios
    return rows, report


def _observe_ring(ring_xy: np.ndarray, shift_m: float, scale: float,
                  jitter_sd: float, rng: np.random.Generator) -> np.ndarray:
    """translate + dilate + jitter a ring in local metres (the 'observed' truth)."""
    c = ring_xy.mean(axis=0)
    p = (ring_xy - c) * scale + c
    ang = rng.uniform(0, 2 * np.pi)
    p = p + np.array([np.cos(ang), np.sin(ang)]) * shift_m
    p = p + rng.normal(0, jitter_sd, size=p.shape)
    return p
