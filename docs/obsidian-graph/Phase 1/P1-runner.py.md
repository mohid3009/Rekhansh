---
tags: [file, runner, phase1]
---
# runner.py (Phase 1)
`backend/app/pipeline/runner.py`

## Overview
Pipeline execution coordinator for Phase 1. Manages execution timeouts, tier fallbacks, and candidate geometry persistence during extraction.

## Key Responsibilities in Phase 1
- **Tier Dispatch & Fallback Management**:
  - Checks configuration and environmental flags to determine whether to execute Tier 2 (OpenCV CV on orthomosaic) or fallback to Tier 3 (controlled synthetic perturbation).
  - Handles runtime exceptions in OpenCV image processing gracefully by falling back to synthetic observations with full diagnostic logging.
- **Candidate Geometry Persistence**:
  - Persists extracted AI field polygons into the `candidate_geometries` database table.
  - Associates each candidate geometry with run ID, extraction tier, confidence rating, and spatial bounding boxes.
- **Phase Timing & Diagnostics**:
  - Tracks extraction phase duration (in milliseconds) and logs polygon counts and scenario distributions for downstream matching stages.
