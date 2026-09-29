---
tags: [file, shared, db, phase7]
---
# db.py (Phase 7)
`backend/app/db.py`

## Overview
Database persistence module serving read and write queries executed by API route handlers in Phase 7.

## Key Responsibilities in Phase 7
- **High-Throughput Read Queries**:
  - Serves fast indexed queries for village summaries, parcel listings, evidence dossiers, and version histories across SQLite tables.
- **Relational Joining & Filtering**:
  - Executes parameterized SQL operations joining `parcels`, `triage_decisions`, and `match_results` to produce unified API response payloads.
- **Verification Mutation Persistence**:
  - Executes atomic write transactions when surveyors submit boundary verifications or corrections via `/api/parcels/{pid}/verify`.
