"""Module 05 — polygon matching (IoU-based; split/merge/topology-aware).

Classification order (PRD rules, with two documented interpretations for
unspecified bands):

1. NO_MATCH floor: best IoU < MIN_IOU_FLOOR  -> NO_MATCH
2. MERGE: one AI polygon covers >=2 parcels each above MERGE_MIN_OVERLAP_FRAC
   of that parcel's own area (checked before one-to-one, since a merged
   polygon is a one-to-one-looking candidate for both parcels)
3. SPLIT: >=2 AI polygons overlap the parcel, combined IoU >= SPLIT_COMBINED_IOU,
   and *no single polygon explains the parcel on its own* — read as
   max_iou < 0.9 * combined (the PRD's "clears the one-to-one threshold" can't
   mean IoU >= MIN_IOU_ONE_TO_ONE numerically, because two halves of one parcel
   each reach ~0.5).
4. ONE_TO_ONE: exactly one polygon at or above MIN_IOU_ONE_TO_ONE that no other
   parcel matches better. The unspecified band MIN_IOU_FLOOR <= best < 
   MIN_IOU_ONE_TO_ONE is treated as a *weak* ONE_TO_ONE (match_confidence
   carries the low IoU; triage then fails it on the clearance metrics rather
   than calling it NO_MATCH).
"""
from __future__ import annotations

import numpy as np

from ..config import TriageConfig
from ..geo import geom_of, iou, make_transformer, overlap_fraction, sanitize_poly
from shapely.ops import transform as sh_transform, unary_union
from shapely.geometry import shape


def match_parcels(parcels: list[dict], ai_polys: list[dict],
                  cfg: TriageConfig, restrict: dict | None = None,
                  no_observation: set[str] | None = None) -> list[dict]:
    """Return MatchResult rows (one per parcel).

    `restrict`: optional {ai_polygon_id: parcel_id | [parcel_ids]}
    pinning guided observations to the parcel(s) they were derived from
    (merge-emitter polygons cover their pair), so context polygons can
    never hijack the match. Unrestricted polys match freely.

    `no_observation`: parcel ids the extraction tier emitted no polygon
    for (the designed NO_OBSERVATION case). They stay unmatched, so
    unrelated CV context cannot be presented as evidence -> NO_MATCH.
    """
    if not parcels:
        return []
    c = geom_of(parcels[0]["recorded_geometry"]).centroid
    fwd = make_transformer(c.x, c.y)
    m = cfg.match
    no_obs = set(no_observation or ())

    def proj(g):
        return sh_transform(lambda x, y, z=None: fwd.transform(x, y), shape(g))

    p_geom = {p["id"]: sanitize_poly(proj(p["recorded_geometry"]))
              for p in parcels if p["id"] not in no_obs}
    a_geom = {}
    for a in ai_polys:
        try:
            a_geom[a["id"]] = sanitize_poly(proj(a["geometry"]))
        except ValueError:
            continue

    iou_map: dict[tuple[str, str], float] = {}
    frac_map: dict[tuple[str, str], float] = {}
    restrict = restrict or {}
    for pid, pg in p_geom.items():
        for aid, ag in a_geom.items():
            if aid in restrict:
                allowed = restrict[aid]
                if isinstance(allowed, str):
                    allowed = [allowed]
                if pid not in allowed:
                    continue                  # guided poly: its parcel(s) only
            inter = pg.intersection(ag).area
            union = pg.union(ag).area
            iou_map[(pid, aid)] = inter / union if union > 0 else 0.0
            frac_map[(pid, aid)] = inter / pg.area if pg.area > 0 else 0.0

    # ---- step A: MERGE polys (cover >=2 parcels) -------------------------- #
    merge_polys: dict[str, list[str]] = {}
    for aid in a_geom:
        cover = [pid for pid in p_geom
                 if (pid, aid) in frac_map
                 and frac_map[(pid, aid)] >= m.MERGE_MIN_OVERLAP_FRAC]
        if len(cover) >= 2:
            merge_polys[aid] = cover

    assigned: dict[str, dict] = {}
    used_polys: set[str] = set()
    for aid, cover in merge_polys.items():
        for pid in cover:
            assigned[pid] = {
                "field_polygon_ids": [aid],
                "match_type": "MERGE",
                "match_confidence": round(float(np.mean(
                    [iou_map[(pid, aid)] for pid in cover])), 3),
            }
        used_polys.add(aid)

    # ---- step B: splits --------------------------------------------------- #
    free_polys = [a for a in a_geom if a not in used_polys]
    for p in parcels:
        pid = p["id"]
        if pid in assigned:
            continue
        # A parcel with readings of its own (owner-restricted) is explained
        # by them; free context polygons only fill in where it has none.
        owned = [a for a in free_polys
                 if a in restrict
                 and pid in (restrict[a] if isinstance(restrict[a], list)
                             else [restrict[a]])]
        pool = owned or free_polys
        cands = sorted([a for a in pool
                        if (pid, a) in iou_map
                        and iou_map[(pid, a)] >= m.MIN_IOU_FLOOR],
                       key=lambda a: -iou_map[(pid, a)])
        if len(cands) >= 2:
            union = unary_union([a_geom[a] for a in cands])
            combined = (p_geom[pid].intersection(union).area /
                        p_geom[pid].union(union).area)
            best = iou_map[(pid, cands[0])]
            if combined >= m.SPLIT_COMBINED_IOU and best < 0.9 * combined:
                assigned[pid] = {
                    "field_polygon_ids": cands[:4],
                    "match_type": "SPLIT",
                    "match_confidence": round(float(combined), 3),
                }
                used_polys.update(cands[:4])
                continue

    # ---- step C: greedy one-to-one by descending IoU ---------------------- #
    pairs = sorted(
        ((iou_map[(pid, a)], pid, a) for pid in p_geom for a in a_geom
         if (pid, a) in iou_map
         and pid not in assigned and a not in used_polys
         and iou_map[(pid, a)] >= m.MIN_IOU_FLOOR),
        key=lambda t: -t[0])
    for best_iou, pid, aid in pairs:
        if pid in assigned or aid in used_polys:
            continue
        assigned[pid] = {
            "field_polygon_ids": [aid],
            "match_type": "ONE_TO_ONE",
            "match_confidence": round(float(best_iou), 3),
        }
        used_polys.add(aid)

    # ---- remaining: NO_MATCH --------------------------------------------- #
    rows = []
    for p in parcels:
        pid = p["id"]
        if pid not in assigned:
            def _allowed(a):
                if a not in restrict:
                    return True
                al = restrict[a]
                return pid in (al if isinstance(al, list) else [al])
            # a parcel left out of the comparison set (NO_OBSERVATION) has no
            # measurement at all; report 0.0 rather than inventing one
            best = max((iou_map.get((pid, a), 0.0) for a in a_geom if _allowed(a)),
                       default=0.0)
            assigned[pid] = {"field_polygon_ids": [], "match_type": "NO_MATCH",
                             "match_confidence": round(float(best), 3)}
        info = assigned[pid]
        rows.append({
            "id": f"MATCH-{pid}",
            "parcel_id": pid,
            "field_polygon_ids": info["field_polygon_ids"],
            "match_type": info["match_type"],
            "match_confidence": info["match_confidence"],
        })
    return rows
