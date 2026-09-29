---
tags: [file, frontend, screen, audit]
---
# HistoryScreen.tsx
`frontend/src/screens/HistoryScreen.tsx`

## Overview
Tamper-evident audit ledger visualization displaying the complete lifecycle, provenance, and mutation history of an individual parcel boundary.

## Key Responsibilities
- **Cryptographic Hash Chain Timeline**:
  - Displays each version entry in chronological sequence from Genesis (Phase 0 seed) to AI Reconciliation (Phase 4) and Surveyor/SRO Verification (Phase 8).
  - Displays `parent_hash` and `current_hash` (SHA-256) calculated over payload attributes (geometry, area, surveyor notes, timestamp).
  - Visual indicator certifying that the hash chain is unbroken and valid (no database tampering).
- **Geometric Delta Inspection**:
  - Visual comparison between version N and version N-1 showing modified vertices and boundary shifts.
  - Quantitative diff of recorded area, perimeter, and shape compactness.
- **Actor & Authorization Attribution**:
  - Clear attribution of modifications to specific actors (`SYSTEM_PIPELINE`, `SURVEYOR_<ID>`, `SRO_<ID>`).
  - Recorded rationale, timestamp, and linked physical RTK measurement certificates if applicable.
