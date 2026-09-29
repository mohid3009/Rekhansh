---
tags: [file, runner, phase3]
---
# runner.py (Phase 3)
`backend/app/pipeline/runner.py`

## Overview
Pipeline execution controller for Phase 3 matching. Orchestrates spatial comparisons across all village parcels and candidate extractions.

## Key Responsibilities in Phase 3
- **Batch Matching Coordination**:
  - Pulls recorded parcel geometries from `parcels` and newly extracted candidates from `candidate_geometries`.
  - Dispatches `match_parcels()` with loaded `TriageConfig` thresholds.
- **Match Results Persistence**:
  - Writes comprehensive `match_results` rows: `parcel_id`, `candidate_id`, `match_type` (`ONE_TO_ONE`, `SPLIT`, `MERGE`, `NO_MATCH`), and `match_confidence`.
- **Telemetry & Step Reporting**:
  - Logs match type breakdown counts (e.g. 12 One-to-One, 2 Split, 2 Merge, 2 No Match) and execution latency in milliseconds.
