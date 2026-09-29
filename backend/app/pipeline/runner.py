"""Pipeline orchestrator (PRD suggested build sequence).

bootstrap: village design -> georeference -> legacy scan render -> real imagery
fetch (cached; synthetic fallback only if offline) -> parcels + genesis versions.
run-full: georeference replay -> extraction -> matching -> reconciliation ->
triage, timed; ParcelVersion history is never rewritten (US-6.1).
"""
from __future__ import annotations

import json
import time
from datetime import datetime, timezone

import numpy as np
from shapely import affinity
from shapely.geometry import shape
from shapely.ops import transform as sh_transform

from .. import db
from ..config import DATA_DIR, load_site_config, load_triage_config
from ..geo import make_transformer, polygon_area_ha
from ..pipeline import matching, reconcile, triage as triage_mod
from ..pipeline.extract import extract_synthetic, extract_tier2
from ..pipeline.georeference import fit_affine, run_georeferencing
from ..pipeline.versions import create_genesis, current_geometry, versions_for
from ..seed import village as village_mod
from ..seed.fetch_imagery import fetch_osm_context, fetch_orthomosaic, load_cached
from ..seed.legacymap import render_scan


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _apply_topology_demo(geoms: list[dict], adj: list[list[int]],
                         seed: int) -> tuple[list[dict], dict | None]:
    """Deliberately overlap one adjacent recorded pair by 2.5-5% of its own
    area (a plausible legacy digitising error) so the topology rule of the
    triage engine is reachable. Uses the pair with the *longest shared edge*
    so the move cannot collide with any other parcel. Deterministic."""
    from shapely.geometry import Polygon as SPoly

    shapes = [shape(g) for g in geoms]
    candidates = []
    for i in range(len(geoms)):
        for j in adj[i]:
            if i >= j:
                continue
            shared = float(shapes[i].boundary.intersection(shapes[j].boundary).length)
            if shared > 0:
                candidates.append((-shared, i, j))       # longest edge first
    if not candidates:
        # fallback: nearest centroid pair
        for i in range(len(geoms)):
            for j in adj[i]:
                if i < j:
                    d = shapes[i].centroid.distance(shapes[j].centroid)
                    candidates.append((d, i, j))
    if not candidates:
        return geoms, None
    candidates.sort()
    _, i, j = candidates[0]
    gi, gj0 = shapes[i], shapes[j]
    ci, cj = gi.centroid, gj0.centroid
    vx, vy = ci.x - cj.x, ci.y - cj.y
    for f in np.linspace(0.004, 0.25, 70):
        gj = affinity.translate(gj0, xoff=vx * f, yoff=vy * f)
        pct = 100.0 * gj.intersection(gi).area / gj.area if gj.area else 0.0
        if 2.5 <= pct <= 5.0:
            out = list(geoms)
            out[j] = gj.__geo_interface__
            return out, {"moved_index": j, "into_index": i,
                         "shift_fraction": round(float(f), 4),
                         "overlap_pct": round(pct, 2),
                         "note": "deliberate legacy digitising overlap (demo topology FAIL)"}
    return geoms, None


def _synthetic_orthomosaic(site, village_id: str) -> dict:
    """OFFLINE FALLBACK ONLY: a clearly-labelled SYNTHETIC orthomosaic."""
    from PIL import Image, ImageDraw
    from ..raster import WorldFileAffine, save_png

    n_px = 1024
    span_m = 420.0
    rng = np.random.default_rng(site.seed + 3)
    base = (np.ones((n_px, n_px, 3)) * np.array([168, 158, 120])) + rng.normal(0, 14, (n_px, n_px, 3))
    im = Image.fromarray(np.clip(base, 0, 255).astype("uint8"))
    d = ImageDraw.Draw(im, "RGBA")
    for _ in range(90):
        x0, y0 = int(rng.integers(0, n_px)), int(rng.integers(0, n_px))
        w, h = int(rng.integers(60, 240)), int(rng.integers(60, 240))
        col = (int(rng.integers(70, 130)), int(rng.integers(120, 190)),
               int(rng.integers(50, 90)), 210)
        d.rectangle([x0, y0, min(n_px - 1, x0 + w), min(n_px - 1, y0 + h)],
                    fill=col, outline=(190, 180, 140))
    arr = np.asarray(im)

    span_lon = span_m / (111_320.0 * np.cos(np.radians(site.lat)))
    span_lat = span_m / 110_540.0
    dpp_lon, dpp_lat = span_lon / n_px, span_lat / n_px
    aff = WorldFileAffine(A=dpp_lon, B=0.0, C=site.lon - span_lon / 2,
                          D=0.0, E=-dpp_lat, F=site.lat + span_lat / 2)
    out = DATA_DIR / "imagery"
    out.mkdir(parents=True, exist_ok=True)
    save_png(arr, out / f"{village_id}_ortho.png")
    aff.write_world_file(out / f"{village_id}_ortho.pgw")
    prov = {"provider": "SYNTHETIC_FALLBACK (network unavailable at first boot)",
            "generated_by_this_project": True, "attribution": "n/a",
            "resolution_cm_per_px": round(aff.resolution_m_per_px(site.lat) * 100, 3),
            "bounds_wgs84": aff.bounds_wgs84(n_px, n_px), "fetched_at": _now()}
    (out / f"{village_id}_ortho.json").write_text(json.dumps(prov, indent=2))
    return {"path": f"imagery/{village_id}_ortho.png", "affine": aff, "image": arr,
            "resolution_cm_per_px": prov["resolution_cm_per_px"], "provenance": prov,
            "capture_date": _now()[:10], "bounds": prov["bounds_wgs84"]}



VILLAGE_ID = "VIL-PILOT"


def ensure_seeded(force: bool = False) -> dict:
    """First boot: design -> georeference -> scan render -> imagery -> parcels.
    Deterministic: same config seed -> identical village (US-0.1)."""
    db.init_db()
    if force:
        db.reset_all()
    v = db.select_one("villages", id=VILLAGE_ID)
    if v:
        # Site/config switch (e.g. mock Nashik -> real Nanded parcels) must
        # take effect instead of serving stale seeded rows: compare a content
        # signature of the seeding inputs against the stored one.
        import hashlib

        try:
            _site_now = load_site_config()
            _bundle_now = village_mod.real_parcel_bundle()
            _feats = (_bundle_now or {}).get("features", [])
            _sig_src = "|".join([
                str(_site_now.lat), str(_site_now.lon), str(_site_now.zoom),
                str(_site_now.tiles), str(_site_now.parcel_count),
                str(_site_now.seed), str(CODE_VERSION),
                ",".join(str((f.get("properties", {}) or {}).get("plotid")
                             or (f.get("properties", {}) or {}).get("survey_no"))
                         for f in _feats),
            ])
            _sig_now = hashlib.sha1(_sig_src.encode("utf-8")).hexdigest()[:12]
            _meta_now = db.select_one("village_meta", village_id=VILLAGE_ID)
            if not _meta_now or _meta_now.get("code_version") != _sig_now:
                db.reset_all()
            else:
                return v
        except Exception:
            return v

    site = load_site_config()
    cfg = load_triage_config()
    seed, now = site.seed, _now()
    gcfg = cfg.georeferencing
    rng = np.random.default_rng(seed + 1)

    real = village_mod.real_design(VILLAGE_ID)
    if real is not None:
        design, _layout_meta, parcel_meta = real
        design_source = "IMPORTED"
    else:
        design, _layout_meta = village_mod.generate_design(
            site.lat, site.lon, site.parcel_count, seed)
        parcel_meta = None
        design_source = "MOCK"
    gr = run_georeferencing(design, site.lat, site.lon,
                            gcfg.SCAN_ROTATION_DEG, gcfg.SCAN_SCALE_PCT,
                            gcfg.SCAN_NOISE_M, gcfg.CONTROL_POINT_GRID, rng)
    recorded, topo = _apply_topology_demo(gr.recorded,
                                          village_mod.adjacency(gr.recorded), seed)
    parcels = village_mod.parcel_rows(recorded, VILLAGE_ID, seed, now, parcel_meta)
    scan_rel = render_scan(gr, [p["survey_number"] for p in parcels],
                           site.name, VILLAGE_ID)
    db.insert("legacy_maps", {
        "id": f"LEG-{VILLAGE_ID}", "village_id": VILLAGE_ID, "raster_path": scan_rel,
        "georeferenced_path": None, "control_points": gr.control_points,
        "affine_transform": gr.affine, "rmse_m": round(gr.rmse_m, 3),
        "applied_distortion": {"distortion": gr.distortion, "topology_demo": topo},
        "created_at": now,
    })

    pack = load_cached(VILLAGE_ID)
    if pack is None:
        try:
            pack = fetch_orthomosaic(site, VILLAGE_ID)
        except Exception:
            pack = _synthetic_orthomosaic(site, VILLAGE_ID)
    try:
        osm = fetch_osm_context(site.lat, site.lon)
    except Exception:
        osm = None

    r2 = np.random.default_rng(seed + 9)
    m_per_deg_lat, m_per_deg_lon = 110_540.0, 111_320.0 * np.cos(np.radians(site.lat))
    checkpoints = []
    for k in range(10):
        p = parcels[int(r2.integers(0, len(parcels)))]
        ring = p["recorded_geometry"]["coordinates"][0]
        lon, lat = ring[int(r2.integers(0, len(ring)))]
        checkpoints.append({
            "point_id": f"GCP-{k + 1:02d}",
            "lat": float(lat + r2.normal(0, 0.04) / m_per_deg_lat),
            "lon": float(lon + r2.normal(0, 0.04) / m_per_deg_lon),
            "elevation_m": float(site.elevation_m + 1.0
                               + (lat - site.lat) * 110_540.0 * 0.004
                               - (lon - site.lon) * m_per_deg_lon * 0.002
                               + r2.normal(0, 0.4)),
            "horizontal_accuracy_m": float(r2.uniform(0.02, 0.05)),
            "vertical_accuracy_m": float(r2.uniform(0.05, 0.12)),
            "captured_at": now,
        })
    db.insert("aerial_surveys", {
        "id": f"SUR-{seed}", "village_id": VILLAGE_ID,
        "orthomosaic_path": pack["path"], "dsm_path": None,
        "resolution_cm_per_px": pack["resolution_cm_per_px"],
        "capture_date": pack["capture_date"], "checkpoints": checkpoints,
        "provenance": {**pack["provenance"],
                       "checkpoints_source": "SIMULATED_XY_OVER_REAL_DEM "
                                               "(Copernicus GLO-30 via open-meteo; "
                                               "SW 262 m / centre 259 m / NE 254 m)",
                       "approx_elevation_m": site.elevation_m,
                       "osm_linear_context": bool(osm)},
        "bounds": pack["bounds"], "created_at": now,
    })
    for p in parcels:
        db.insert("parcels", p)
    create_genesis(parcels)
    import hashlib as _hashlib

    _bundle_now = village_mod.real_parcel_bundle() or {}
    _feats_seeded = _bundle_now.get("features", [])
    _sig_src2 = "|".join([
        str(site.lat), str(site.lon), str(site.zoom), str(site.tiles),
        str(site.parcel_count), str(seed),
        ",".join(str((f.get("properties", {}) or {}).get("plotid")
                     or (f.get("properties", {}) or {}).get("survey_no"))
                 for f in _feats_seeded),
    ])
    _sig2 = _hashlib.sha1(_sig_src2.encode("utf-8")).hexdigest()[:12]
    db.insert("village_meta", {"village_id": VILLAGE_ID, "seed_examples": {},
                               "code_version": _sig2, "updated_at": now})
    village = {"id": VILLAGE_ID, "name": site.name, "district": site.district,
               "state": site.state, "lat": site.lat, "lon": site.lon,
               "source": design_source,
               "notes": ("real Bhu-Naksha cadastral parcels (IMPORTED); "
                         "imagery from Esri World Imagery (see provenance)")
                        if design_source == "IMPORTED" else
                        "pilot site seeded; imagery from Esri World Imagery (see provenance)"}
    db.insert("villages", village)
    return village


def run_full() -> dict:
    """PRD: Re-run georeference -> extraction -> matching -> reconciliation ->
    triage. Version history and prior EvidenceReports are never rewritten."""
    site = load_site_config()
    cfg = load_triage_config()
    seed = site.seed
    village = ensure_seeded()
    vid = village["id"]
    started = _now()
    run_id = f"RUN-{started.replace(':', '').replace('-', '').replace('+0000', 'Z')}"

    parcels = db.select("parcels", village_id=vid, order_by="survey_number")
    for p in parcels:
        p["current_geometry"] = current_geometry(p["id"])
    db.insert("pipeline_runs", {"id": run_id, "started_at": started,
                                "finished_at": None, "seed": seed, "tier": "",
                                "steps": [], "notes": "", "ok": 1,
                                "parcel_count": len(parcels)})
    steps: list[dict] = []
    db.reset_triage_state()
    try:
        # ---- 1. georeference replay (re-fit stored control points) -------- #
        t = time.perf_counter()
        legacy = db.select_one("legacy_maps", village_id=vid)
        cps = np.array([[c["pixel_x"], c["pixel_y"], c["lon"], c["lat"]]
                        for c in legacy["control_points"]])
        params, resid = fit_affine(cps)
        m_lon = 111_320.0 * np.cos(np.radians(site.lat))
        res_m = np.column_stack([resid[:, 0] * m_lon, resid[:, 1] * 110_540.0])
        rmse = float(np.sqrt((res_m ** 2).sum(axis=1).mean()))
        steps.append({"name": "georeference", "ms": round((time.perf_counter() - t) * 1000, 1),
                      "rmse_m": round(rmse, 3),
                      "replay_drift_m": round(abs(rmse - legacy["rmse_m"]), 6)})

        # ---- 2. extraction (Tier 2 CV on real imagery, Tier 3 fallback) --- #
        t = time.perf_counter()
        img_pack = load_cached(vid)
        tier_wanted = cfg.extraction.synthetic.DEFAULT_TIER
        polys: list[dict] = []
        tier_used = tier_wanted
        if tier_wanted == "CV_MODEL" and img_pack:
            polys, extract_report = extract_tier2(
                img_pack["image"], img_pack["affine"], cfg,
                img_pack["affine"].resolution_m_per_px(site.lat),
                survey_id=f"SUR-{seed}", site=site, parcels=parcels,
                seed=seed)
            tier_used = "CV_MODEL"
        scenarios = None
        extract_report = extract_report if tier_wanted == "CV_MODEL" and img_pack else {}
        if not polys:
            if tier_wanted == "CV_MODEL":
                tier_used = "SYNTHETIC_FALLBACK (cv_empty)"
            adj = village_mod.adjacency([p["recorded_geometry"] for p in parcels])
            polys, scenarios = extract_synthetic(parcels, adj, cfg, seed)
            if tier_wanted != "CV_MODEL":
                tier_used = "SYNTHETIC_FALLBACK"
        now = _now()
        for row in polys:
            row["created_at"] = now
        db.insert_many("ai_field_polygons", polys)
        steps.append({"name": "extraction", "ms": round((time.perf_counter() - t) * 1000, 1),
                      "polygons": len(polys),
                      **({"tier1_polygons": extract_report.get("tier1_polygons", 0),
                          "tier2_polygons": extract_report.get("tier2_polygons", 0),
                          "guided_polygons": extract_report.get("guided_polygons", 0),
                          "cv_polygons": extract_report.get("cv_polygons", 0),
                          "ftw_note": extract_report.get("ftw_note", ""),
                          "osm_note": extract_report.get("osm_note", "")}
                         if extract_report else {})})

        # ---- 3. matching ---------------------------------------------------- #
        # Guided polygons are restricted to the parcel(s) they were
        # derived from (merge-emitter polygons cover their pair), so
        # whole-image CV context can never hijack a parcel's match.
        # Co-located Tier-1 / classical CV polygons match freely by true
        # location. Variant scenarios ride on the extraction report.
        t = time.perf_counter()
        scenarios = extract_report.get("guided_scenarios", {}) or {}
        emitter_of: dict[str, str] = {}
        for a in polys:
            if a["id"].startswith("AIFP-GD-"):
                # id = AIFP-GD-{seed}-{parcel_index} (a split's second half
                # carries a trailing -B), so the id names its owning parcel
                # and ownership survives NO_OBSERVATION / MERGE / SPLIT.
                try:
                    emitter_of[a["id"]] = parcels[int(a["id"].split("-")[3]) - 1]["id"]
                except (ValueError, IndexError):
                    pass
        guided_owner: dict[str, list[str]] = {}
        for aid, emitter in emitter_of.items():
            scen = scenarios.get(emitter, "GUIDED")
            if scen == "GUIDED_MERGE":
                guided_owner[aid] = [emitter] + [
                    pid for pid, s in scenarios.items()
                    if s == "GUIDED_MERGE" and pid != emitter]
            else:
                guided_owner[aid] = [emitter]
        no_obs = {pid for pid, s in scenarios.items() if s == "NO_OBSERVATION"}
        matches = matching.match_parcels(parcels, polys, cfg,
                                         restrict=guided_owner or None,
                                         no_observation=no_obs or None)
        for m in matches:
            m["created_at"] = now
        db.insert_many("match_results", matches)
        steps.append({"name": "matching", "ms": round((time.perf_counter() - t) * 1000, 1),
                      "types": {k: sum(1 for m in matches if m["match_type"] == k)
                                for k in ("ONE_TO_ONE", "SPLIT", "MERGE", "NO_MATCH")}})

        # ---- 4. reconciliation ---------------------------------------------- #
        t = time.perf_counter()
        ai_by_id = {a["id"]: a for a in polys}
        match_by = {m["parcel_id"]: m for m in matches}
        img = img_pack["image"] if img_pack else None
        aff = img_pack["affine"] if img_pack else None
        orng = np.random.default_rng(seed + 77)
        evidence_rows, ev_by = [], {}
        for p in parcels:
            ev = reconcile.compute_evidence(p, match_by[p["id"]], ai_by_id, parcels,
                                            cfg, legacy["rmse_m"], img, aff, orng)
            n = len(db.select("evidence_reports", parcel_id=p["id"])) + 1
            ev["id"] = f"EVD-{p['id']}-{n:03d}"
            ev_by[p["id"]] = ev
            evidence_rows.append(ev)
        db.insert_many("evidence_reports", evidence_rows)
        steps.append({"name": "reconciliation", "ms": round((time.perf_counter() - t) * 1000, 1)})

        # ---- 5. triage -------------------------------------------------------- #
        t = time.perf_counter()
        decisions = [triage_mod.triage_parcel(p, match_by[p["id"]], ev_by[p["id"]], cfg)
                     for p in parcels]
        db.insert_many("triage_decisions", decisions)
        steps.append({"name": "triage", "ms": round((time.perf_counter() - t) * 1000, 1),
                      "states": {s: sum(1 for d in decisions if d["state"] == s)
                                 for s in ("CLEARED", "FLAGGED", "INSUFFICIENT_EVIDENCE")}})

        # one seeded example per triage class (US-9.1)
        examples = {s: next((d["parcel_id"] for d in decisions if d["state"] == s), None)
                    for s in ("CLEARED", "FLAGGED", "INSUFFICIENT_EVIDENCE")}
        db.update("village_meta", "village_id", vid,
                  {"seed_examples": examples, "updated_at": _now()})

        total_ms = round(sum(s["ms"] for s in steps), 1)
        db.update("pipeline_runs", "id", run_id,
                  {"finished_at": _now(), "steps": steps, "tier": tier_used,
                   "notes": json.dumps({"scenarios": scenarios or {}}), "ok": 1})
        return {"run_id": run_id, "tier": tier_used, "steps": steps,
                "parcel_count": len(parcels), "total_ms": total_ms,
                "outcomes": {s: sum(1 for d in decisions if d["state"] == s)
                             for s in ("CLEARED", "FLAGGED", "INSUFFICIENT_EVIDENCE")},
                "seed_examples": examples}
    except Exception as exc:                                     # pragma: no cover
        db.update("pipeline_runs", "id", run_id,
                  {"finished_at": _now(), "steps": steps, "ok": 0,
                   "notes": f"{type(exc).__name__}: {exc}"})
        raise
