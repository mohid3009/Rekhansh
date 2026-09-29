---
tags: [file, shared, geo, phase2]
---
# geo.py (Phase 2)
`backend/app/geo.py`

## Overview
Geometric and coordinate projection operations specialized for Phase 2 georeferencing and residual error analysis.

## Key Responsibilities in Phase 2
- **Projection Transforms for Error Metrics**:
  - Instantiates pyproj `Transformer` instances from WGS84 (EPSG:4326) to appropriate UTM zones (e.g. EPSG:32643).
  - Converts angular affine residual vectors $(\Delta \text{lon}, \Delta \text{lat})$ into metric displacement vectors $(\Delta x, \Delta y)$ in meters to calculate genuine ground distance residuals.
- **Centroid and Bounding Box Operations**:
  - Computes spatial centroids of GCP clusters and parcel polygons to verify distribution across the map sheet.
  - Determines spatial extents ensuring affine transformation matrices are evaluated within valid mathematical domains without singularity errors.
