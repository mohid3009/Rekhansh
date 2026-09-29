---
tags: [phase, segmentation]
phase: 1
---
# Phase 1 — Extract

## Purpose & Objective
Phase 1 orchestrates AI field-polygon extraction across agricultural landscapes. It bridges multiple segmentation tiers (classical computer vision, synthetic fallback, and external drone observations) to detect modern ground-truth agricultural field boundaries and physical landmarks.

## Data Flow & Architecture
- **Inputs**: Stitched high-resolution satellite orthomosaic PNG, world file affine parameters, and raw survey observations.
- **Processing**:
  - **Tier 2 (OpenCV)**: Grayscale conversion, Gaussian smoothing, Canny edge detection (40/120), contour extraction, and Ramer-Douglas-Peucker polygon approximation.
  - **Spectral Tagging**: Evaluates Excess Green Index ($ExG$) and brightness to classify detected features as `BUND`, `ROAD`, `IRRIGATION_CHANNEL`, or `BOUNDARY`.
  - **Tier 3 (Synthetic)**: Controlled topological perturbation (drift, split, merge, no-match, low-confidence) ensuring all triage branches are tested deterministically.
  - **Geometric Sanitization**: Reprojection to UTM CRS, resolving self-intersections, bow-ties, and enforcing correct ring orientations via Shapely.
- **Outputs**: Normalized `AIFieldPolygon` candidate records persisted into the `candidate_geometries` database table.

## Phase Modules & Files
- [[P1-extract.py]]
- [[P1-cvextract.py]]
- [[P1-realobs.py]]
- [[P1-geo.py]]
- [[P1-triage.yaml]]
- [[P1-runner.py]]
