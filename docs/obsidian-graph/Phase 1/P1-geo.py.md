---
tags: [file, shared, geo, phase1]
---
# geo.py (Phase 1)
`backend/app/geo.py`

## Overview
Geometric utilities and spatial transformations powering Phase 1 field extraction. Provides rigorous metric coordinate projections and polygon validation routines using Shapely and pyproj.

## Key Responsibilities in Phase 1
- **Metric Projections (`make_transformer`, `make_inverse`)**:
  - Builds high-precision pyproj transformers between geographic coordinates (WGS84 EPSG:4326) and local metric projections (UTM EPSG:32643).
  - Enables accurate distance, buffer, and perturbation operations in physical SI units (meters) rather than distorted angular degrees.
- **Polygon Sanitization (`sanitize_poly`)**:
  - Repairs malformed contours generated during computer vision vectorization or polygon cutting.
  - Resolves self-intersecting loops and duplicate vertices using `shapely.validation.make_valid`, buffering zero distances (`poly.buffer(0)`), and enforcing clockwise exterior / counter-clockwise interior ring conventions.
- **Area Calculation (`polygon_area_ha`)**:
  - Computes exact surface area in hectares ($10,000 \text{ m}^2$) over UTM-projected coordinates.
