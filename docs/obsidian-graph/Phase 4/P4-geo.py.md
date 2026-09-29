---
tags: [file, shared, geo, phase4]
---
# geo.py (Phase 4)
`backend/app/geo.py`

## Overview
High-precision metric geometric algorithms powering Phase 4 reconciliation calculations.

## Key Responsibilities in Phase 4
- **ASBD Metric Evaluation (`asbd_projected`)**:
  - Samples points along the boundary perimeter of polygon A and evaluates minimum Euclidean distance to polygon B's boundary in projected meters.
  - Symmetrically computes distance from B to A and averages the two integrals to produce true Average Symmetric Boundary Distance in meters.
- **Physical Support Ratio Calculation (`support_ratio_pct`)**:
  - Buffers linear detected ground features (bunds, roads) by configured tolerance distance `SUPPORT_BUFFER_M`.
  - Calculates line-string intersection length with parcel boundary perimeter, computing percentage of boundary verified by ground truth features.
- **Neighbor Overlap Percentage (`neighbor_overlap_pct`)**:
  - Intersects parcel candidate geometry against all immediate neighbours in the adjacency graph, detecting boundary disputes and encroachment slivers.
