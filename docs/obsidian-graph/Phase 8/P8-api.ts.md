---
tags: [file, frontend, network]
---
# api.ts
`frontend/src/api.ts`

## Overview
Centralized, strongly typed HTTP client and TypeScript domain definitions bridging the frontend UI with the FastAPI backend REST endpoints.

## Key Responsibilities
- **HTTP Client Wrapper**: Implements typed wrapper functions `api.get<T>()` and `api.post<T>()` over the browser `fetch` API. Automatically serializes JSON payloads, unpacks backend error envelopes (`detail` fields), and configures base URLs across local Vite proxies and deployed environments.
- **Asset URL Resolution**: Exports `api.staticUrl(rel)` to resolve paths for backend raster artifacts including stitched orthomosaics, georeferenced cadastral scans, and digital surface models.
- **Type Definitions & Schemas**:
  - `TriageState`: Tri-state enum (`CLEARED`, `FLAGGED`, `INSUFFICIENT_EVIDENCE`) paired with UI color tokens and badge styling.
  - `Role`: Authorization roles (`VIEWER`, `SURVEYOR`, `ADMIN` / `SRO`).
  - `ParcelRow`: Tabular row schema including survey number, recorded area (ha), current AI area (ha), triage state, reason codes, match type, and verification status.
  - `Summary`: Aggregate village statistics, survey sensor provenance, and triage breakdown counts.
  - `EvidenceData`: Metric payloads comprising IoU overlap, ASBD boundary deviation, area delta %, support ratio, and step-by-step waterfall rule evaluations.
  - `ParcelVersion`: Immutable ledger entry schema with SHA-256 hash chains, author metadata, timestamp, and geometric differences.
