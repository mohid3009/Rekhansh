---
tags: [file, pipeline, segmentation]
---
# extract.py
`backend/app/pipeline/extract.py`

## Overview
Module 04 — AI field polygon extraction orchestrator. Bridges multi-tier boundary detection pipelines (OpenCV computer vision, synthetic scenario generators, and external real observation GeoJSONs) into a unified polygon output schema for downstream matching.

## Key Responsibilities
- **Multi-Tier Execution Selection**:
  - **Tier 2 (Computer Vision)**: Invokes `cvextract.py` to run edge detection and contour extraction on the stitched orthomosaic.
  - **Tier 3 (Synthetic Scenario Fallback)**: Generates controlled boundary perturbations (drift, split, merge, no-match, low-confidence) for reproducible testing of all triage rules.
  - **Real Observations**: Loads vetted ground-truth GeoJSON polygons from pilot datasets.
- **Scenario Allocation Engine (`assign_scenarios`)**:
  - Deterministically distributes test scenarios across village parcels using adjacency graphs.
  - Evaluates topological adjacency so merged parcels share legitimate physical boundaries rather than arbitrary geometries.
- **Geometric Perturbation & Sanitization**:
  - Transforms geometries into metric UTM CRS before applying shifts, rotations, and polygon splitting cuts.
  - Applies `sanitize_poly` to fix self-intersections, bow-ties, duplicate vertices, and winding orders via `shapely.validation`.
- **Output Schema Standardization**:
  - Emits normalized `AIFieldPolygon` structures containing GeoJSON polygons in WGS84, confidence scores (0.0 to 1.0), and detected feature tags (`BOUNDARY`, `BUND`, `ROAD`, `IRRIGATION_CHANNEL`).
