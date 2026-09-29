---
tags: [file, runner, phase4]
---
# runner.py (Phase 4)
`backend/app/pipeline/runner.py`

## Overview
Pipeline execution controller for Phase 4 reconciliation. Manages evidence calculation loops, raster occlusion sampling, and candidate geometry preparation.

## Key Responsibilities in Phase 4
- **Reconciliation Loop Orchestration**:
  - Iterates through all parcels matched in Phase 3, loading their corresponding AI candidate polygons.
  - Passes stitched orthomosaic numpy array and affine transform to `measure_occlusion()` for physical vegetation and shadow quantification.
  - Invokes `compute_evidence()` for each parcel.
- **Batch Geometry Sanitization**:
  - Validates that reconciled candidate polygon boundaries satisfy simple polygon topology rules without self-intersections.
- **Downstream Hand-off**:
  - Prepares the complete evidence dataset required for the waterfall rule evaluation in Phase 5 Triage.
