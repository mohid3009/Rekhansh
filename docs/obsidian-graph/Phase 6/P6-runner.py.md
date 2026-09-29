---
tags: [file, runner, phase6]
---
# runner.py (Phase 6)
`backend/app/pipeline/runner.py`

## Overview
Pipeline execution controller for Phase 6 KPIs and version initialization. Manages post-triage version creation and metric calculations.

## Key Responsibilities in Phase 6
- **AI Version Append**:
  - Automatically appends a Version 1 record (`action = AI_RECONCILE`) for every parcel, capturing the reconciled geometry, triage state, and computed SHA-256 hash anchored to the genesis hash.
- **KPI Generation**:
  - Triggers `compute_kpis()` following pipeline completion to calculate operational metrics.
- **Pipeline Run Record Completion**:
  - Finalizes the pipeline run execution log with overall runtime, total parcels processed, triage outcome breakdown, and current KPI snapshot.
