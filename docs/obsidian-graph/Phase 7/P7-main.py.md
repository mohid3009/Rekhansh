---
tags: [file, api, fastapi]
---
# main.py
`backend/app/main.py`

## Overview
FastAPI application entrypoint and server lifecycle manager. Bootstraps the application, mounts API routers, serves static spatial assets, and configures cross-origin security.

## Key Responsibilities
- **Application Startup & Auto-Bootstrap**:
  - Automatically initializes SQLite database schema on startup via `@app.on_event("startup")`.
  - Spawns background worker thread to ensure village seeding and execute an initial pipeline run if triage state is absent, enabling zero-configuration first boot (US-9.2).
- **Router & Static Mounts**:
  - Mounts API router under `/api` prefix.
  - Mounts `DATA_DIR` under `/static` via `StaticFiles`, serving orthomosaic PNGs, legacy map scans, and world files directly to the frontend MapLibre canvas.
- **CORS Configuration**:
  - Integrates `CORSMiddleware` supporting configurable domain origins or wildcards for local Vite dev servers and remote web deployments.
- **Health Check Endpoint (`/health`)**:
  - Provides system diagnostic endpoint reporting server status, process uptime, and data directory accessibility.
