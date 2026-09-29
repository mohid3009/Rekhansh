---
tags: [file, shared, models, phase7]
---
# models.py (Phase 7)
`backend/app/models.py`

## Overview
Pydantic data models defining the serialization schemas, request bodies, and response envelopes for the REST API in Phase 7.

## Key Responsibilities in Phase 7
- **API Request Validation**:
  - Validates client payloads for boundary verification requests: checks survey decision enums (`ACCEPT`, `CORRECT`, `ESCALATE`), surveyor ID formats, and GeoJSON coordinate integrity.
- **API Response Schemas**:
  - Formulates standardized JSON responses: `VillageSummaryResponse`, `ParcelListResponse`, `EvidenceResponse`, `KpiResponse`, and `RunPipelineResult`.
- **Automatic OpenAPI / Swagger Documentation**:
  - Generates comprehensive interactive API documentation at `/docs` and `/redoc` with type annotations, field descriptions, and example JSON payloads.
