---
tags: [file, api, routes]
---
# routes.py
`backend/app/api/routes.py`

## Overview
REST API implementation adhering to PRD Appendix A specification. Exposes all administrative, spatial, diagnostic, and verification endpoints consumed by the frontend.

## Key Responsibilities
- **Village & Inventory Endpoints**:
  - `GET /api/meta`: Returns system operational status, active village ID, and whether triage state exists.
  - `GET /api/villages`: Lists all registered revenue villages.
  - `GET /api/villages/{vid}/summary`: Returns parcel counts, triage outcome distributions (Cleared, Flagged, Insufficient), and exemplar parcel IDs.
  - `GET /api/villages/{vid}/parcels`: Returns full tabular parcel dataset with recorded and AI areas, triage status, and reason codes.
- **Evidence & Diagnostic Endpoints**:
  - `GET /api/parcels/{pid}/evidence`: Serves the complete evidence dossier for a parcel: IoU score, ASBD meters, area delta %, support ratio %, occlusion %, and step-by-step waterfall evaluation traces.
- **Verification & Audit Endpoints**:
  - `POST /api/parcels/{pid}/verify`: Ingests surveyor decisions (`ACCEPT`, `CORRECT`, `ESCALATE`), attaches field notes/corrected coordinates, and records an immutable block in the version ledger.
  - `GET /api/parcels/{pid}/history`: Returns the chronological version history and validates the cryptographic SHA-256 hash chain.
  - `GET /api/parcels/{pid}/export/geojson`: Exports official survey GeoJSON package for GIS interoperability.
- **Operational & Config Endpoints**:
  - `GET /api/kpis`: Returns real-time metrics including false-clear rate, RTK reduction %, and boundary RMSE.
  - `POST /api/pipeline/run-full`: Triggers end-to-end pipeline execution across phases 1–6.
  - `GET /api/config/triage` & `PUT /api/config/triage`: Dynamic reading and updating of triage rule thresholds.
