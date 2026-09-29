---
tags: [phase]
phase: 0
---
# Phase 0 — Seed & Setup

## Purpose & Objective
Phase 0 handles the one-time data ingestion, external asset acquisition, and environment bootstrapping. It establishes the baseline records for the pilot village by importing authenticated cadastral boundaries, downloading high-resolution satellite imagery tiles, rendering synthetic legacy paper cadastral maps, and creating the SQLite database schema with Genesis audit versioning.

## Data Flow & Architecture
- **Inputs**: Geographic center coordinates, village metadata from `site.yaml`, Mahabhunakasha Tier A real cadastral GeoJSON.
- **Processing**:
  - Ingestion of real cadastral parcels or procedural 18-parcel synthetic layout with realistic agricultural field boundaries and shared internal borders.
  - Projection to metric UTM CRS and construction of parcel adjacency graph.
  - Downloading and stitching ESRI World Imagery XYZ tiles at zoom level 18 into an orthomosaic PNG with accompanying `.pgw` world file.
  - Rendering legacy revenue cadastral paper scan with realistic aging, folds, scanner noise, and Ground Control Points (GCPs).
- **Outputs**: Populated `villages` and `parcels` database tables, local tile caches, Genesis Version 0 ledger blocks.

## Phase Modules & Files
- [[P0-village.py]]
- [[P0-fetch_imagery.py]]
- [[P0-legacymap.py]]
- [[P0-site.yaml]]
- [[P0-runner.py]]
- [[P0-config.py]]
- [[P0-db.py]]
