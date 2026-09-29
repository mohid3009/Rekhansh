---
tags: [phase]
phase: 8
---
# Phase 8 — Frontend

## Purpose & Objective
Phase 8 delivers an intuitive, role-aware web client built with React, Vite, TailwindCSS, and MapLibre GL. Designed for field surveyors, GIS operators, and Sub-Registrar Officers (SRO), it provides spatial boundary inspection, diagnostic evidence transparency, interactive vertex manipulation, and formal legal sign-off.

## Data Flow & Architecture
- **Inputs**: REST API endpoints from `/api/*`, static orthomosaic raster tiles, and user role selection (`FIELD_HELPER`, `SURVEYOR`, `SRO`).
- **Processing**:
  - **Inventory Dashboard (`ParcelsScreen`)**: Full-text search and multi-criteria filtering across 18 parcels with area comparison tables and triage badges.
  - **Interactive GIS Map (`MapCompareScreen`)**: Dual-view and opacity-slider overlay of satellite orthomosaic, legacy cadastral scan, and modern AI boundaries.
  - **Diagnostic Evidence (`EvidenceScreen`)**: Detailed quantitative metric cards (IoU, ASBD, Area %, Support Ratio) and waterfall rule evaluation traces.
  - **Boundary Verification (`VerifyScreen`)**: Interactive vertex snapping, polygon adjustment, and decision actions (`Confirm`, `Correct`, `Escalate`).
  - **Audit Ledger (`HistoryScreen`)**: Visual cryptographic SHA-256 hash-chain timeline verifying immutable version lineages.
  - **Operational KPIs (`KpiStrip`)**: High-visibility metric strip displaying real-time clearance rates, processing latency, and field survey reduction ratios.
- **Outputs**: Verified parcel boundaries, surveyor audit justifications, and formal legal sign-off records dispatched to the backend.

## Phase Modules & Files
- [[P8-App.tsx]]
- [[P8-api.ts]]
- [[P8-ParcelsScreen.tsx]]
- [[P8-MapCompareScreen.tsx]]
- [[P8-EvidenceScreen.tsx]]
- [[P8-VerifyScreen.tsx]]
- [[P8-HistoryScreen.tsx]]
- [[P8-KpiStrip.tsx]]
- [[P8-ui.tsx]]
