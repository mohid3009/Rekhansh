---
tags: [file, config, phase7]
---
# config.py (Phase 7)
`backend/app/config.py`

## Overview
Configuration bindings supporting dynamic API configuration reading and YAML serialization in Phase 7.

## Key Responsibilities in Phase 7
- **Triage Configuration Serialization**:
  - Converts active `TriageConfig` objects into YAML format to serve `GET /api/config/triage`.
- **Dynamic Configuration Updates**:
  - Ingests updated YAML strings from `PUT /api/config/triage`, validates mathematical constraints, and safely writes changes to `backend/config/triage.yaml`.
- **Runtime Reload Notifications**:
  - Notifies pipeline runner instances that configuration values have changed so subsequent runs immediately reflect updated policy thresholds.
