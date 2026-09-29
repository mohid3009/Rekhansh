---
tags: [phase]
phase: 4
---
# Phase 4 — Reconcile

## Purpose & Objective
Phase 4 acts as the mathematical evidence compilation and spatial reconciliation engine. It synthesizes match correspondences into unified boundary proposals and calculates rigorous quantitative metrics across physical area, boundary deviation, physical ground support, and aerial occlusion.

## Data Flow & Architecture
- **Inputs**: Matched parcel pairs, candidate geometries, orthomosaic raster pixels, affine world parameters, and `triage.yaml` threshold rules.
- **Processing**:
  - Reconciled candidate geometry creation via union of matched AI polygons.
  - Observed area computation in metric hectares.
  - Calculation of Area Variance Percentage ($\Delta_{\text{area}}\%$).
  - Average Symmetric Boundary Distance (ASBD) measurement in projected meters.
  - Pixel-level sampling of orthomosaic for shadow and dense tree canopy occlusion.
  - Verification of physical feature support ratio along parcel perimeter within tolerance buffer.
  - Composite uncertainty score calculation incorporating georeference RMSE, occlusion, and boundary complexity.
- **Outputs**: Reconciled boundary geometries, quantitative evidence records, and topological adjacency metrics.

## Phase Modules & Files
- [[P4-reconcile.py]]
- [[P4-geo.py]]
- [[P4-db.py]]
- [[P4-models.py]]
- [[P4-runner.py]]
