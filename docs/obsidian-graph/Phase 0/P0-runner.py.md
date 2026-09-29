---
tags: [file, runner, seed]
---
# runner.py
`backend/app/pipeline/runner.py`

## Overview
Pipeline orchestrator and lifecycle engine. In Phase 0, executes the initial database bootstrap and raw asset acquisition prior to pipeline execution.

## Key Responsibilities
- **Bootstrap Execution (`bootstrap(cfg)`)**:
  - Initializes SQLite database schema, ensuring all tables, indexes, and foreign keys exist.
  - Triggers `village.py` to ingest real or procedural cadastral parcels and writes initial records into `villages` and `parcels`.
  - Dispatches `fetch_imagery.py` to download ESRI satellite tiles and stitch the base orthomosaic.
  - Calls `legacymap.py` to generate the georeferenced legacy cadastral raster scan.
- **Genesis Versioning**:
  - Seeds Genesis Version (Version 0) blocks into `parcel_versions` with initial SHA-256 hashes establishing immutable provenance before any processing runs.
- **Pipeline Pre-Flight Verification**:
  - Validates that database connections, raster files, and coordinate reference transformers are healthy before downstream phases execute.
