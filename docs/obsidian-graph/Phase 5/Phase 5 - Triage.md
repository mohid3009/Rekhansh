---
tags: [phase]
phase: 5
---
# Phase 5 — Triage

## Purpose & Objective
Phase 5 implements the deterministic automated triage rule engine. Applying a strict waterfall decision matrix over Phase 4 mathematical evidence, it classifies each parcel into one of three administrative action states with explicit, legally justifiable reason codes.

## Data Flow & Architecture
- **Inputs**: Reconciled parcel records, match classifications, quantitative evidence metrics, and policy rules from `triage.yaml`.
- **Processing**:
  - **Waterfall Tier 1 (`INSUFFICIENT_EVIDENCE`)**: Evaluates missing matches, low AI confidence (<0.70), excessive canopy/shadow occlusion (>0.30), poor imagery, and degenerate ring geometries.
  - **Waterfall Tier 2 (`FLAGGED`)**: Evaluates area variance exceeding tolerance (>5%), ASBD boundary displacement (>2 m), low feature support (<60%), boundary overlap with neighbours, and split/merge scenarios.
  - **Waterfall Tier 3 (`CLEARED`)**: Default clearance when all evidence passes thresholds, ready for direct SRO sign-off.
- **Outputs**: Populated `triage_decisions` table recording parcel states, reason code lists, and timestamps.

## Phase Modules & Files
- [[P5-triage.py]]
- [[P5-triage.yaml]]
- [[P5-db.py]]
- [[P5-config.py]]
- [[P5-runner.py]]
