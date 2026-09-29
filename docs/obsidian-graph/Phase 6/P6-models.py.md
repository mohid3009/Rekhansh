---
tags: [file, shared, models, phase6]
---
# models.py (Phase 6)
`backend/app/models.py`

## Overview
Pydantic data models defining the schemas for KPIs, RTK verifications, and version ledger records in Phase 6.

## Key Responsibilities in Phase 6
- **KPI Response Schema (`KpiReport`)**:
  - Validates dashboard KPI fields: `false_clear_rate`, `cleared_without_rtk`, `boundary_rmse_m`, `area_error_pct`, and `false_flag_rate`.
- **RTK Verification Schema (`RtkVerificationPayload`)**:
  - Validates surveyor input payloads: `surveyor_id`, `decision` (`ACCEPT`, `CORRECT`, `ESCALATE`), `observed_error_m`, `notes`, and optional corrected GeoJSON geometry.
- **Version Ledger Schema (`ParcelVersionRecord`)**:
  - Validates cryptographic hash structures: enforces 64-character hexadecimal SHA-256 strings for `parent_hash` and `current_hash`.
