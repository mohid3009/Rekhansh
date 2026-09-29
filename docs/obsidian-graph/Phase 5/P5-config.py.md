---
tags: [file, config, phase5]
---
# config.py (Phase 5)
`backend/app/config.py`

## Overview
Configuration bindings and Pydantic validation structures providing typed access to triage rules in Phase 5.

## Key Responsibilities in Phase 5
- **`TriageConfig` Model Loading**:
  - Ingests `triage.yaml` and parses nested subsections: `insufficient`, `clear`, `extraction`, and `match`.
  - Enforces logical validation rules (e.g. ensuring `MIN_IOU_FLOOR` < `MIN_IOU_ONE_TO_ONE`, and threshold values fall within reasonable bounds).
- **In-Memory Rule Caching**:
  - Caches parsed configuration models in memory to enable sub-millisecond evaluation across large village datasets containing hundreds of parcels.
