---
tags: [file, shared, geo, phase3]
---
# geo.py (Phase 3)
`backend/app/geo.py`

## Overview
Spatial intersection and geometric overlap calculations powering Phase 3 polygon matching.

## Key Responsibilities in Phase 3
- **Polygonal Overlap Metrics (`iou`, `overlap_fraction`)**:
  - `iou(poly1, poly2)`: Calculates exact Jaccard index / Intersection-over-Union over valid planar Shapely polygons in metric projection.
  - `overlap_fraction(p_sub, p_base)`: Computes the proportion of base geometry $p_{base}$ encompassed within candidate $p_{sub}$.
- **Unary Union & Multipolygon Decomposition**:
  - Employs `shapely.ops.unary_union` to aggregate multiple overlapping candidate polygons during SPLIT evaluation, calculating collective area coverage.
- **Topological Validity Enforcement**:
  - Ensures intersection and union operations handle complex ring topologies without generating collapsed line segments or topological geometry collection exceptions.
