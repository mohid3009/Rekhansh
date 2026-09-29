---
tags: [file, runner, phase7]
---
# runner.py (Phase 7)
`backend/app/pipeline/runner.py`

## Overview
Pipeline integration module connecting HTTP API triggers directly to core pipeline execution in Phase 7.

## Key Responsibilities in Phase 7
- **Full Pipeline Invocation (`run_full`)**:
  - Handles POST requests sent to `/api/pipeline/run-full`.
  - Executes phases 1 through 6 sequentially with high-resolution performance timers.
  - Returns structured `RunResult` containing execution run ID, total execution duration in milliseconds, tier used, and triage outcome counts.
- **Seeding Verification (`ensure_seeded`)**:
  - Checks if the village database is populated; if empty, automatically performs first-boot initialization.
- **Concurrency & Lock Management**:
  - Employs thread locking to prevent concurrent pipeline runs from colliding or corrupting the SQLite database during long-running tasks.
