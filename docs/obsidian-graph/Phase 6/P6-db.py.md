---
tags: [file, shared, db, phase6]
---
# db.py (Phase 6)
`backend/app/db.py`

## Overview
Database persistence module managing version records, hash chains, and RTK survey verifications in Phase 6.

## Key Responsibilities in Phase 6
- **Version Ledger Persistence**:
  - Inserts sequential version blocks into `parcel_versions` table: `parcel_id`, `version_number`, `parent_hash`, `current_hash`, `author`, `action`, `geometry`, and `timestamp`.
- **RTK Decision Storage**:
  - Stores field survey measurements and surveyor judgments in `rtk_verifications` table.
- **Relational Integrity Guarantees**:
  - Enforces unique constraints on `(parcel_id, version_number)` to prevent version collisions.
