"""Module 06 — reconciliation engine: every formula in the PRD table, in the
local projected CRS, driven by config thresholds.

Observed area = area of the union of matched AI polygons.
Support ratio = % of recorded perimeter within `SUPPORT_BUFFER_M` of the
detected features. Occlusion is *measured on the real orthomosaic pixels* of
the parcel (shadow + canopy), with a config-driven fallback only when no
imagery exists. Uncertainty uses the PRD's weighted-sum recipe; the RMSE
normaliser (GEOREF_RMSE_NORM_M) is a config extension, since the PRD does not
define how to normalise a metre value into 0..1.
"""
from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
from shapely.geometry import shape
from shapely.ops import transform as sh_transform, unary_union

from ..config import TriageConfig
from ..geo import (asbd_projected, geom_of, make_transformer,
                   neighbor_overlap_pct, sanitize_poly, support_ratio_pct)


def measure_occlusion(img, affine, geom_wgs84, cfg) -> float | None:
    """Fraction of the parcel where imagery hides boundaries (shadow/canopy)."""
    if img is None or affine is None:
        return None
    h, w = img.shape[:2]
    ring = np.array(shape(geom_wgs84).exterior.coords)
    cols, rows = affine.lonlat_to_px(ring[:, 0], ring[:, 1])
    c0, c1 = int(np.clip(cols.min(), 0, w - 1)), int(np.clip(cols.max(), 0, w - 1))
    r0, r1 = int(np.clip(rows.min(), 0, h - 1)), int(np.clip(rows.max(), 0, h - 1))
    if c1 - c0 < 2 or r1 - r0 < 2:
        return None
    import cv2
    mask = np.zeros((r1 - r0 + 1, c1 - c0 + 1), dtype=np.uint8)
    pts = np.array(np.column_stack([cols - c0, rows - r0]), dtype=np.int32)
    cv2.fillPoly(mask, [pts], 1)
    patch = img[r0:r1 + 1, c0:c1 + 1].astype(np.float64)
    if patch.ndim != 3:
        return None
    rr, gg, bb = patch[..., 0], patch[..., 1], patch[..., 2]
    bright = (rr + gg + bb) / 3.0
    exg = 2 * gg - rr - bb
    sel = mask.astype(bool)
    if int(sel.sum()) < 16:
        return None
    shadow_frac = float((bright[sel] < cfg.occlusion.SHADOW_V_MAX).mean())
    dense_frac = float((exg[sel] > cfg.occlusion.DENSE_EXG_MIN).mean())
    return float(min(1.0, cfg.occlusion.SCALE * (shadow_frac + 0.5 * dense_frac)))


def compute_evidence(
    parcel: dict,
    match: dict,
    ai_by_id: dict[str, dict],
    all_parcels: list[dict],
    cfg: TriageConfig,
    georef_rmse_m: float,
    img=None,
    affine=None,
    rng: np.random.Generator | None = None,
) -> dict:
    """Build an EvidenceReport row for one parcel (PRD Module 06).

    `parcel["current_geometry"]` = latest ParcelVersion geometry (the record
    the surveyor is triaging right now).
    """
    recorded = parcel["current_geometry"]
    matched = [ai_by_id[i] for i in match["field_polygon_ids"] if i in ai_by_id]
    b, t = cfg.boundary, cfg.topology

    g_rec = geom_of(recorded)
    fwd = make_transformer(g_rec.centroid.x, g_rec.centroid.y)
    proj = lambda g: sanitize_poly(sh_transform(  # noqa: E731
        lambda x, y, z=None: fwd.transform(x, y), shape(g)))

    g_rec_p = proj(recorded)
    recorded_area_ha = abs(g_rec_p.area) / 10_000.0

    observed_geoms = [proj(a["geometry"]) for a in matched]
    obs_union = unary_union(observed_geoms) if observed_geoms else None
    observed_area_ha = abs(obs_union.area) / 10_000.0 if obs_union is not None else 0.0

    # PRD: area_diff_ha = |recorded − observed| (absolute difference)
    area_diff_ha = round(abs(recorded_area_ha - observed_area_ha), 4)
    area_diff_pct = (round(abs(area_diff_ha) / recorded_area_ha * 100.0, 3)
                     if recorded_area_ha > 0 else 100.0)

    if obs_union is not None and obs_union.area > 0:
        inter = g_rec_p.intersection(obs_union).area
        union = g_rec_p.union(obs_union).area
        iou_val = float(inter / union) if union > 0 else 0.0
        disp = asbd_projected(g_rec_p, obs_union, b.SAMPLE_INTERVAL_M)
    else:
        iou_val = 0.0
        if ai_by_id:   # nearest poly anywhere as displacement fallback
            nearest = min(ai_by_id.values(),
                          key=lambda a: g_rec_p.distance(proj(a["geometry"])))
            disp = asbd_projected(g_rec_p, proj(nearest["geometry"]),
                                  b.SAMPLE_INTERVAL_M)
        else:
            disp = float(np.hypot(g_rec_p.bounds[2] - g_rec_p.bounds[0],
                                  g_rec_p.bounds[3] - g_rec_p.bounds[1]) / 2.0)

    feat_lines = [shape(a["geometry"]).exterior.__geo_interface__ for a in matched]
    support = (support_ratio_pct(recorded, feat_lines, fwd, b.SUPPORT_BUFFER_M)
               if matched else 0.0)

    occ = measure_occlusion(img, affine, recorded, cfg)
    if occ is None:
        r = rng if rng is not None else np.random.default_rng(0)
        occ = float(np.clip(r.normal(cfg.occlusion.FALLBACK_MEAN,
                                     cfg.occlusion.FALLBACK_SD), 0.0, 1.0))

    issues: list[str] = []
    for other in all_parcels:
        if other["id"] == parcel["id"]:
            continue
        pct = neighbor_overlap_pct(recorded, other["current_geometry"], fwd)
        if pct > t.MAX_NEIGHBOR_OVERLAP_PCT:
            issues.append(f"NEIGHBOR_OVERLAP_EXCEEDS_TOLERANCE:{other['survey_number']}"
                          f"({pct:.1f}%)")
    topology_status = "FAIL" if issues else "PASS"

    conf = float(np.mean([a["confidence"] for a in matched])) if matched else 0.0
    u = cfg.uncertainty
    norm_rmse = min(1.0, max(0.0, georef_rmse_m / u.GEOREF_RMSE_NORM_M))
    uncertainty = round(float(np.clip(
        u.W_AI_CONFIDENCE * (1.0 - conf)
        + u.W_GEOREF_RMSE * norm_rmse
        + u.W_OCCLUSION * float(occ)
        + u.W_SUPPORT * (1.0 - support / 100.0), 0.0, 1.0)), 4)
    q = cfg.quality
    quality = ("GOOD" if uncertainty <= q.GOOD_MAX_UNCERTAINTY
               else "MODERATE" if uncertainty <= q.MODERATE_MAX_UNCERTAINTY
               else "POOR")

    return {
        "id": f"EVD-{parcel['id']}",
        "parcel_id": parcel["id"],
        "area_diff_ha": area_diff_ha,
        "area_diff_pct": area_diff_pct,
        "boundary_displacement_m": round(float(disp), 3),
        "iou": round(iou_val, 4),
        "support_ratio_pct": round(float(support), 3),
        "occlusion_fraction": round(float(occ), 4),
        "topology_status": topology_status,
        "topology_issues": issues,
        "uncertainty_score": uncertainty,
        "evidence_quality": quality,
        "ai_confidence": round(conf, 3),
        "computed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
