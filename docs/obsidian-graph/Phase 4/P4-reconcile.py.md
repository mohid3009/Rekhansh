---
tags: [file, pipeline, reconcile]
---
# reconcile.py
`backend/app/pipeline/reconcile.py`

## Overview
Module 06 — Spatial reconciliation and mathematical evidence compilation engine. Combines match correspondences with geographic vector geometry to produce candidate boundary proposals and compute quantitative triage metrics.

## Key Responsibilities
- **Quantitative Metric Computation (`compute_evidence`)**:
  - **Observed Area (ha)**: Exact surface area of the union of matched AI polygons calculated in projected metric CRS.
  - **Area Delta %**: Percent difference between legally recorded RoR area and observed satellite area:
    $$\Delta_{\text{area}}\% = \frac{|\text{Area}_{\text{observed}} - \text{Area}_{\text{recorded}}|}{\text{Area}_{\text{recorded}}} \times 100$$
  - **ASBD (Average Symmetric Boundary Distance)**: Symmetrical Hausdorff-like boundary metric in meters measuring average deviation between recorded and AI boundaries.
  - **Support Ratio %**: Percentage of recorded parcel perimeter falling within a spatial buffer (e.g. 1.5 m) of confirmed physical ground features (hedgerows, bunds, fences).
- **Pixel-Level Orthomosaic Occlusion Analysis (`measure_occlusion`)**:
  - Samples real orthomosaic pixels inside parcel polygon.
  - Quantifies tree canopy foliage (via Excess Green Index $ExG > \text{DENSE\_EXG\_MIN}$) and deep cast shadows (brightness $< \text{SHADOW\_V\_MAX}$) that obscure true boundary lines from aerial view.
- **Composite Uncertainty Scoring**:
  - Computes weighted uncertainty incorporating normalized georeference RMSE, inverse match confidence, measured occlusion ratio, and shape compactness.
- **Topological Adjacency & Overlap Check**:
  - Evaluates overlap with adjacent parcels to detect slivers, gaps, and border infringements.
