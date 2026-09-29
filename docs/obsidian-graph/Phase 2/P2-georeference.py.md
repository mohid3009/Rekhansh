---
tags: [file, pipeline, georeference]
---
# georeference.py
`backend/app/pipeline/georeference.py`

## Overview
Module 02 — Legacy map georeferencing and spatial rectification engine. Solves a 6-parameter affine transformation matrix mapping historical scanned paper revenue maps to geographic coordinates using Ground Control Points (GCPs).

## Key Responsibilities
- **Least-Squares Affine Fit (`fit_affine`)**:
  - Sets up the linear system $M \cdot c = \mathbf{target}$ where $M = [x, y, 1]$ from pixel coordinates and targets are geographic $(\text{lon}, \text{lat})$.
  - Solves via `numpy.linalg.lstsq` to obtain 6 affine parameters: $A, B, C$ for longitude and $D, E, F$ for latitude:
    $$\text{lon} = A \cdot x + B \cdot y + C$$
    $$\text{lat} = D \cdot x + E \cdot y + F$$
- **Root Mean Square Error (RMSE) Computation**:
  - Calculates residual vectors for all control points in degrees, then projects residuals into local metric UTM coordinates to compute true physical $RMSE_m$ (Root Mean Square Error in meters).
  - Emits real $RMSE_m$ values directly into downstream uncertainty scoring (e.g. flagging parcels if georeferencing error exceeds tolerances).
- **Coordinate Space Projection (`pixel_to_lonlat`)**:
  - Projects scanned parcel boundary rings from image raster space into WGS84 GeoJSON polygons for overlay against modern imagery.
- **Distortion Provenance Logging**:
  - Records applied distortion metrics (rotation angle, scale factor drift, measurement noise) alongside recovered parameters for complete algorithmic auditability.
