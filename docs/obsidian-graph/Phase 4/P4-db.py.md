---
tags: [file, shared, db, phase4]
---
# db.py (Phase 4)
`backend/app/db.py`

## Overview
Database persistence interface for storing candidate geometries and calculated reconciliation evidence in Phase 4.

## Key Responsibilities in Phase 4
- **Candidate Geometry Storage**:
  - Inserts reconciled boundary proposals into `candidate_geometries`, storing GeoJSON rings, source tier, and confidence metrics.
- **Evidence Metrics Recording**:
  - Updates `parcels` and intermediate tables with computed quantitative evidence: observed area, area variance %, ASBD distance, occlusion percentage, support ratio, and uncertainty score.
- **Atomic Transaction Scoping**:
  - Commits reconciliation evidence across all parcels atomically to maintain relational integrity before triage evaluation begins.
