---
tags: [file, runner, phase2]
---
# runner.py (Phase 2)
`backend/app/pipeline/runner.py`

## Overview
Pipeline execution controller for Phase 2 georeferencing. Integrates ground control point collection with transformation fitting and updates database records with georeferenced boundaries.

## Key Responsibilities in Phase 2
- **Georeference Execution Scoping**:
  - Fetches GCP coordinate pairs from the database or survey parameters.
  - Invokes `run_georeferencing()` with error catching and performance timers.
- **Cadastral Boundary Update**:
  - Updates the `parcels` table with newly rectified geographic boundary geometries.
  - Attaches calculated $RMSE_m$ values to village survey metadata.
- **Quality Gate Verification**:
  - Checks if georeferencing RMSE exceeds maximum acceptable tolerances (e.g. >2.5 m). If exceeded, flags the survey run and alerts downstream triage stages to wider uncertainty bounds.
