---
tags: [file, pipeline, versions, audit]
---
# versions.py
`backend/app/pipeline/versions.py`

## Overview
Parcel boundary lifecycle and version progression manager. Maintains append-only historical records for every boundary mutation from initial seed to final SRO approval.

## Key Responsibilities
- **Append-Only History Model**:
  - Ensures boundary edits are never written in-place over past records; every modification creates a sequential version block ($v_0, v_1, v_2, \dots$).
- **Version Query Interface (`versions_for(parcel_id)`)**:
  - Retrieves the complete chronological lifecycle for any parcel, including timestamps, operating surveyor, action type (`GENESIS`, `AI_RECONCILE`, `CORRECT`, `CONFIRM`), geometry, and recorded notes.
- **Delta Analysis**:
  - Calculates area deltas and boundary vertex displacements between consecutive versions for surveyor review and legal audit.
