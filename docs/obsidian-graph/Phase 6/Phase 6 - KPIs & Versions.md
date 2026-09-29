---
tags: [phase]
phase: 6
---
# Phase 6 — KPIs & Versions

## Purpose & Objective
Phase 6 delivers operational analytics and cryptographic auditability. It computes real-time system performance KPIs and manages an immutable, append-only SHA-256 hash-chained version ledger tracking all parcel boundary mutations and surveyor decisions (US-5.3).

## Data Flow & Architecture
- **Inputs**: Triage decisions, ground-truth RTK rover verifications, and historical version records.
- **Processing**:
  - **KPI Computations**:
    - **False-Clear Rate**: Proportion of automatically cleared parcels where ground audit detected unacceptable error.
    - **Cleared Without RTK**: Percentage of total village land cleared without expensive physical fieldwork.
    - **Boundary RMSE**: True physical displacement between AI boundary proposals and millimeter-accurate RTK coordinates.
    - **False-Flag Rate**: Surveyor efficiency metric tracking unnecessary field investigations.
  - **Tamper-Evident Version Ledger**:
    - Appends sequential version blocks ($v_0, v_1, \dots$).
    - Computes cryptographic SHA-256 digests over canonical JSON payloads chained to previous block hashes.
    - Verifies hash chain continuity to detect database tampering.
- **Outputs**: Comprehensive KPI reports and updated immutable audit ledger in `parcel_versions`.

## Phase Modules & Files
- [[P6-kpis.py]]
- [[P6-versions.py]]
- [[P6-hashchain.py]]
- [[P6-rtk.py]]
- [[P6-db.py]]
- [[P6-models.py]]
- [[P6-runner.py]]
