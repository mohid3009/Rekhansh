---
tags: [phase]
phase: 7
---
# Phase 7 — API Layer

## Purpose & Objective
Phase 7 encapsulates backend business logic into a modern, production-ready REST API implemented with FastAPI. Adhering to the PRD Appendix A specification, it serves structured JSON data, spatial GeoJSON layers, and static orthomosaic raster tiles to the frontend client.

## Data Flow & Architecture
- **Inputs**: HTTP REST requests from frontend screens, incoming surveyor verification payloads, and pipeline execution triggers.
- **Processing**:
  - Application lifecycle management with automatic database bootstrap on first boot.
  - Endpoint routing across village summaries, tabular parcel inventories, detailed evidence dossiers, and cryptographic version histories.
  - Request payload validation and OpenAPI schema generation using Pydantic models.
  - Asynchronous pipeline run triggers (`POST /api/pipeline/run-full`) with execution timing and outcome metrics.
  - Static file hosting (`/static`) mounting local raster storage for seamless MapLibre tile consumption.
- **Outputs**: Strongly typed JSON REST responses, GeoJSON geographic exports, and OpenAPI Swagger documentation at `/docs`.

## Phase Modules & Files
- [[P7-main.py]]
- [[P7-routes.py]]
- [[P7-db.py]]
- [[P7-models.py]]
- [[P7-config.py]]
- [[P7-runner.py]]
