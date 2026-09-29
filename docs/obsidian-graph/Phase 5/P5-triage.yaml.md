---
tags: [file, config, rules, phase5]
---
# triage.yaml (Phase 5)
`backend/config/triage.yaml`

## Overview
Declarative threshold table and policy rulebook driving the Phase 5 triage engine. Decouples administrative legal tolerances from executable application code.

## Key Responsibilities in Phase 5
- **Triage Threshold Sections**:
  - `insufficient`:
    - `MIN_AI_CONFIDENCE`: Threshold below which AI polygon predictions are considered unreliable (default 0.70).
    - `MAX_OCCLUSION_FRAC`: Maximum allowable tree canopy and shadow occlusion before triggering ground survey (default 0.30).
  - `clear`:
    - `MAX_AREA_DIFF_PCT`: Maximum permissible percentage deviation between recorded RoR and observed boundary (default 5.0%).
    - `MAX_BOUNDARY_DISPLACEMENT_M`: Permissible ASBD boundary displacement limit in meters (default 2.0 m).
    - `MIN_SUPPORT_RATIO_PCT`: Minimum percentage of boundary verified by visible ground features (default 60.0%).
    - `MAX_NEIGHBOR_OVERLAP_PCT`: Maximum tolerated boundary encroachment into adjacent plots (default 1.0%).
- **Policy Hot-Reloading**:
  - Allows state revenue commissioners to adjust survey clearance tolerances (e.g. relaxing area tolerance for hilly terrain) without code recompilation or backend restart.
