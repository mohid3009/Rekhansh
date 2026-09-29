---
tags: [file, pipeline, rtk, verification]
---
# rtk.py
`backend/app/pipeline/rtk.py`

## Overview
RTK-GNSS rover field verification handler. Ingests high-precision centimeter-level ground rover survey measurements and records human surveyor verification decisions.

## Key Responsibilities
- **Surveyor Verification Ingestion (`record_verification`)**:
  - Ingests surveyor actions: `ACCEPT` (boundary confirmed as-is), `CORRECT` (boundary adjusted with field measurements), or `ESCALATE` (dispute referred for formal administrative inquiry).
  - Validates observed error metrics in meters comparing AI boundary with physical RTK rover coordinates.
- **Ledger Mutation Trigger**:
  - When a surveyor submits a corrected boundary, triggers `versions.py` and `hashchain.py` to append a new immutable version block to the audit ledger.
- **KPI Ground Truth Feed**:
  - Populates the `rtk_verifications` table which provides the empirical ground-truth baseline used by `kpis.py` to calculate false-clear rates and boundary RMSE.
