---
tags: [phase]
phase: 2
---
# Phase 2 — Georeference

## Purpose & Objective
Phase 2 performs spatial rectification of legacy paper revenue map scans. It estimates a 6-parameter affine transformation mapping image pixel coordinates into true geographic WGS84 coordinates, providing real-world Root Mean Square Error (RMSE) quantification.

## Data Flow & Architecture
- **Inputs**: Scanned cadastral raster image, Ground Control Point (GCP) coordinate correspondences (pixel $x, y \to \text{lon, lat}$).
- **Processing**:
  - Least-squares 6-parameter affine fitting ($A, B, C, D, E, F$) using `numpy.linalg.lstsq`.
  - Computing residuals in degrees, projecting residual vectors into metric UTM coordinates, and deriving true ground $RMSE_m$ in meters.
  - Forward-projecting scanned parcel boundary coordinates into geographic space.
  - Generating standard ESRI world files (`.pgw`) for GIS raster alignment.
- **Outputs**: Georeferenced cadastral parcel vectors, spatial raster world files, and calibrated georeference uncertainty metrics ($RMSE_m$).

## Phase Modules & Files
- [[P2-georeference.py]]
- [[P2-raster.py]]
- [[P2-geo.py]]
- [[P2-runner.py]]
