---
tags: [file, pipeline, triage]
---
# triage.py
`backend/app/pipeline/triage.py`

## Overview
Module 07 — Deterministic triage rule engine. Applies a hierarchical waterfall decision table over Phase 4 mathematical evidence to assign each land parcel into one of three regulatory states with explicit, auditable reason codes.

## Key Responsibilities
- **Strict Waterfall Rule Evaluation**:
  - **Tier 1: `INSUFFICIENT_EVIDENCE` (Evaluated First)**:
    - `NO_MATCHING_FIELD`: If match type is `NO_MATCH`.
    - `LOW_AI_CONFIDENCE`: If candidate AI confidence score $< \text{MIN\_AI\_CONFIDENCE}$ (e.g. <0.70).
    - `OCCLUSION_EXCEEDS_LIMIT`: If tree canopy or shadow occlusion $> \text{MAX\_OCCLUSION\_FRAC}$ (e.g. >0.30).
    - `IMAGERY_QUALITY_POOR`: If sensor resolution or cloud cover compromises evidence fidelity.
    - `GEOMETRY_INVALID`: If candidate polygon exhibits non-planar, unclosed, or self-intersecting rings.
  - **Tier 2: `FLAGGED` (Evaluated Second if not Insufficient)**:
    - `AREA_DIFF_EXCEEDS_TOLERANCE`: If area delta % exceeds `MAX_AREA_DIFF_PCT` (e.g. >5.0%).
    - `BOUNDARY_DISPLACEMENT_EXCEEDS_TOLERANCE`: If ASBD boundary distance exceeds `MAX_BOUNDARY_DISPLACEMENT_M` (e.g. >2.0 m).
    - `LOW_SUPPORT_RATIO`: If physical ground feature support falls below `MIN_SUPPORT_RATIO_PCT` (e.g. <60.0%).
    - `NEIGHBOR_OVERLAP_EXCEEDS_TOLERANCE`: If parcel boundary illegally encroaches upon an adjacent parcel.
    - `SPLIT_DETECTED`: If cadastral unit has been partitioned into multiple operational holdings.
    - `MERGE_DETECTED`: If multiple cadastral units have been physically unified.
  - **Tier 3: `CLEARED` (Default when no failures trigger)**:
    - Assigned `CLEAR_BOUNDARY`. Ready for automated or fast-track SRO sign-off without field visits.
- **Triage Decision Persistence**:
  - Emits records for the `triage_decisions` table with parcel ID, assigned state, array of triggered reason codes, and timestamp.
