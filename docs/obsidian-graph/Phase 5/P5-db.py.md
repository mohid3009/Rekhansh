---
tags: [file, shared, db, phase5]
---
# db.py (Phase 5)
`backend/app/db.py`

## Overview
Database persistence module managing triage state updates and decision storage across SQLite tables in Phase 5.

## Key Responsibilities in Phase 5
- **Triage Decisions Storage**:
  - Inserts complete evaluation records into `triage_decisions`: `parcel_id`, `triage_state` (`CLEARED`, `FLAGGED`, `INSUFFICIENT_EVIDENCE`), `reason_codes` (JSON array), and evaluation timestamp.
- **Parcel Record Synchronization**:
  - Updates the active status on the primary `parcels` table with current triage state and primary reason code, enabling fast indexing and queries.
- **Relational Integrity Guarantees**:
  - Ensures triage decisions are tightly bound to existing `match_results` and `candidate_geometries` entries.
