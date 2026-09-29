# Rural Land Resurvey Triage (Prototype)

A full-stack prototype for triaging rural land resurvey cases: an offline-first
FastAPI + SQLite + Shapely backend that runs a complete
extract → georeference → match → reconcile → triage pipeline over real ESRI
imagery, and a React/Vite + MapLibre frontend with five screens for reviewing
proposed boundaries before an SRO signs off. Built to `PRD.md` and
`USERSTORIES.md`.

> **Prototype data note** — parcels are **real** Bhu-Naksha cadastral polygons
> (Bond Gavhan, Mahur taluka, Nanded — 30 parcels, survey nos 1-30), imagery is
> **real** ESRI World Imagery (z18, ~0.56 m/px), elevation is the real Copernicus
> GLO-30 DEM, and AI field polygons are real observations snapped to imagery edges
> + classical CV. Owner names, the legacy scan render and the RTK traces are
> simulated. Nothing here is a legal record.

## Quick start

Backend (Python 3.10+, deps in `requirements.txt`):

```bash
pip install -r requirements.txt
python -m uvicorn app.main:app --app-dir backend --port 8000
# → seeds Bond Gavhan (30 real parcels), runs the full pipeline once, serves :8000
```

Frontend (Node 18+):

```bash
cd frontend
npm install
npm run dev        # http://127.0.0.1:5173 — proxies /api, /static, /health
```

Tests:

```bash
python -m pytest backend/tests -q     # 39 tests: formulas, triage, hash chain, pipeline
cd frontend && npx tsc --noEmit && npm run build
```

Open http://127.0.0.1:5173 — the KPI strip and prototype banner load on boot.
Use **Run full pipeline** in the header to reset/re-run the demo (US-6.1).

## How it works

| Stage | Module | What happens |
|---|---|---|
| Seed | `backend/app/seed/` | Real Bhu-Naksha cadastral import (30 parcels, survey nos 1-30), ESRI orthomosaic stitched from real z18 tiles + world file, legacy cadastral scan render, OSM linear features |
| Extract | `pipeline/extract.py` | Tier 1 vendored delineated fields (FTW India-10K / OSM) → Tier 2a parcel-guided snap of every recorded ring onto real imagery edges → Tier 2b classical CV context; the designed SPLIT / MERGE / NO_OBSERVATION cases ride on the scenario plan (PRD Module 04) |
| Georeference | `pipeline/georeference.py` | Affine fit from control points (`[px, py, lon, lat]`), RMSE in metres |
| Match | `pipeline/matching.py` | IoU + boundary distance matching, ASBD via projected side vertices |
| Reconcile | `pipeline/reconcile.py` | Per-parcel `MatchResult` + candidate geometry, sanitised rings |
| Triage | `pipeline/triage.py` | Rule table (config `triage.yaml`): CLEARED / FLAGGED / INSUFFICIENT_EVIDENCE with reason codes |
| KPIs | `pipeline/kpis.py` | boundary_rmse_m, ms/parcel, false-clear/false-flag rates, `sample_sizes` |
| Versions | `pipeline/versions.py` | Hash-chained evidence versions; tamper-evident (US-5.3) |
| RTK | `pipeline/rtk.py` | ACCEPT / CORRECT / REJECT decisions from checkpoints |

Runtime never needs the network: imagery, OSM context and the legacy scan are
vendored under `backend/data/` (see `.gitignore` — only `*.db*` is excluded).

## Screens → user stories

1. **Parcels** (US-1.x) — KPI strip, status/panchayat/area/fuzzy filters, triage table.
2. **Map compare** (US-2.x) — cadastral vs AI overlay on ESRI imagery, match inspector.
3. **Evidence** (US-3.x) — metric gauges vs thresholds, plain-language reasons, per-stage evidence.
4. **Verify** (US-4.x) — RTK checkpoints, decision panel, submit with scope note.
5. **History** (US-5.x) — hash-chained version timeline + integrity check + JSON export.

Role switcher (Field Helper / Surveyor / SRO) drives the visibility rules in
US-4.4 (the all-caps warning above **Submit decision**).

## API

Every PRD Appendix A route is implemented and smoke-tested — see
`PRD.md §Appendix A`. Base URL `/api`; static imagery at `/static/...`;
`GET /health` for liveness. Errors: 404 unknown parcel/village, 422 bad body,
503 pipeline not yet run.

## Configuration

| Where | Key | Purpose |
|---|---|---|
| `backend/config/site.yaml` | `seed`, site lat/lon, imagery zoom | Deterministic village + fetch window |
| `backend/config/triage.yaml` | thresholds, reason codes, copy | Triage rule table (hot-editable) |
| `backend/config/triage.yaml` | `extraction.guided.SNAP_RADIUS_M` | Real-boundary search radius (4 m; calibration measured in the file) |
| env `CORS_ORIGINS` | comma-separated origins, default `*` | Backend CORS |
| env `VITE_API_BASE_URL` | deployed backend URL | Production client base path |
| `frontend/vite.config.ts` | `server.proxy` | Dev proxy for `/api`, `/static`, `/health` (pinned to `127.0.0.1:8000`) |

## Deployment

**Backend → Render** (`render.yaml` is included): create a Web Service from this
repo; build `pip install -r requirements.txt`, start
`python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port $PORT`.
Set `CORS_ORIGINS` to your frontend domain. First boot seeds + runs the
pipeline from the committed imagery (~seconds, no network needed).

**Frontend → Vercel** (`vercel.json` is included): import the repo, it builds
`frontend/` with Vite (`npm --prefix frontend run build` → `frontend/dist`).
Either:

1. Replace `YOUR-BACKEND.onrender.com` in `vercel.json` rewrites so `/api`,
   `/static`, `/health` are same-origin proxied (client needs no env), **or**
2. Delete those three rewrites and set project env `VITE_API_BASE_URL=https://<backend>`
   — the client calls the backend cross-origin (CORS already handles it).

The catch-all rewrite serves the SPA (`index.html` fallback).

## Repository layout

```
backend/
  app/
    api/routes.py        # PRD Appendix A endpoints
    pipeline/            # extract → georeference → match → reconcile → triage → kpis → versions → rtk
    seed/                # real cadastral import, ESRI tile fetch, legacy scan, OSM context
    config/              # site.yaml + triage.yaml
  data/                  # committed: cadastre, imagery/, legacy/, context/ | runtime: app.db*
  reseed_run.py          # wipe + reseed + full run (demo reset)
  check_db.py            # read-only database smoke check
  check_api.py           # read-only API smoke check (polygon provenance + metrics)
  tests/                 # 39 pytest tests
frontend/
  src/
    App.tsx              # shell: role switcher, KPI strip, banner, routing
    api.ts               # typed client (VITE_API_BASE_URL aware)
    screens/             # Parcels, MapCompare, Evidence, Verify, History
    components/          # ui.tsx primitives, KpiStrip
  vite.config.ts         # dev proxy
PRD.md  USERSTORIES.md   # requirements
requirements.txt  render.yaml  vercel.json
```

## Verification status

- `python -m pytest backend/tests -q` — **39 passed** (formulas vs hand
  calculations, units/projection regressions, triage precedence, hash-chain
  tamper detection, offline end-to-end pipeline, determinism).
- API smoke of every documented route incl. 404/422/503 behaviour.
- `npx tsc --noEmit` clean; `npm run build` succeeds.
- Fresh boot reproduces (`python backend/reseed_run.py`): 30 real parcels →
  4 CLEARED / 25 FLAGGED / 1 INSUFFICIENT_EVIDENCE; match types
  ONE_TO_ONE 25 / SPLIT 2 / MERGE 2 / NO_MATCH 1.
- `python backend/check_api.py` prints the summary plus the guided polygons and
  `evidence_note` provenance behind each designed case.

## Assumptions & limitations (US-0.x)

- Cadastre is real (Bhu-Naksha Tier A, ODbL-1.0) and imagery is real ESRI
  World Imagery, but tiles are for demonstration only (respect ESRI/OSM
  attribution + terms). Owner names, the legacy scan and the RTK traces are
  simulated; AI polygons come from imagery, never from the cadastre.
- Single village (`VIL-PILOT`, Bond Gavhan) — site config can point elsewhere.
- Vite dev server pins host `127.0.0.1` (IPv4) so the proxy and browser agree.
- SQLite file DB (`backend/data/app.db`), deleted/rebuilt on first boot.
- No auth: roles are client-side for demo visibility rules only.
