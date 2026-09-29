---
tags: [file, runner, phase5]
---
# runner.py (Phase 5)
`backend/app/pipeline/runner.py`

## Overview
Pipeline execution controller for Phase 5 triage. Coordinates parcel evaluation batches, logs state distributions, and reports triage summaries.

## Key Responsibilities in Phase 5
- **Triage Evaluation Loop**:
  - Iterates through all parcels in the village dataset, loading associated matches and reconciliation evidence.
  - Passes records to `triage_parcel()` with loaded `TriageConfig` rules.
- **Batch State Aggregation**:
  - Tallying summary statistics: total Cleared parcels, Flagged parcels, and Insufficient Evidence parcels.
  - Identifies seed examples for each outcome category to provide frontend shortcut navigation.
- **Pipeline Progression Gate**:
  - Validates that every parcel has received exactly one deterministic triage state before progressing to Phase 6 KPIs and versioning.
