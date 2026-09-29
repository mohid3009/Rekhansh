---
tags: [file, db, seed]
---
# db.py
`backend/app/db.py`

## Overview
Thin, transactional SQLite database abstraction layer and schema manager managing persistence across `backend/data/app.db`.

## Key Responsibilities
- **Schema Management & Migrations**:
  - Automatically initializes and verifies table schemas: `villages`, `parcels`, `match_results`, `candidate_geometries`, `triage_decisions`, `parcel_versions`, and `rtk_decisions`.
  - Configures WAL (Write-Ahead Logging) mode and foreign key constraints for concurrent read/write stability.
- **Generic CRUD Operations**:
  - `select(table, **where)`: Executes parameterized SQL queries with dictionary-based filtering.
  - `select_one(table, **where)`: Fetches a single record or returns `None`.
  - `upsert(table, row, conflict_keys)`: Atomic INSERT OR REPLACE / ON CONFLICT UPDATE semantics.
  - `delete(table, **where)`: Clean deletion of records.
- **Connection Context Manager**:
  - Provides thread-safe transaction scoping with automatic commit on success and rollback on exceptions.
