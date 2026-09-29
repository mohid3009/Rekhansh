---
tags: [file, frontend, app]
---
# App.tsx
`frontend/src/App.tsx`

## Overview
Root React application component managing global state, role-based navigation, metadata synchronization, and client-side routing across all five primary resurvey workflows.

## Key Responsibilities
- **Role Switcher & Context**: Manages active user role (`FIELD_HELPER`, `SURVEYOR`, `SRO`) persisted to `localStorage`. Enforces role-based permissions (e.g., only SROs can execute formal sign-offs, Surveyors perform boundary verification).
- **Metadata & State Sync**: Automatically polls and refreshes village summary statistics, triage breakdowns (CLEARED, FLAGGED, INSUFFICIENT_EVIDENCE), and parcel collections on initial load and following pipeline execution.
- **Pipeline Execution Orchestrator**: Houses the one-click `Run Full Pipeline` trigger that dispatches an asynchronous call to `/api/pipeline/run-full` and displays execution duration, tier selection, and triage outcome counts.
- **Client-Side Routing**: Configures React Router routes for:
  - `/` — Inventory of all parcels (`ParcelsScreen`)
  - `/map` — Interactive dual-view spatial comparison (`MapCompareScreen`)
  - `/evidence/:id` — Diagnostic metric breakdown and waterfall reasoning (`EvidenceScreen`)
  - `/verify/:id` — Boundary editing, vertex snapping, and sign-off (`VerifyScreen`)
  - `/history/:id` — Immutable cryptographic hash-chain audit ledger (`HistoryScreen`)
- **Quick Example Jumpers**: Provides instant navigation shortcuts to exemplar parcels representing each triage outcome state.
