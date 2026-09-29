---
tags: [phase]
phase: 3
---
# Phase 3 — Match

## Purpose & Objective
Phase 3 performs topological polygon matching between historical cadastral parcels and newly extracted modern AI field boundaries. It evaluates spatial overlap and assigns correspondences to identify boundary consistency, property subdivisions, and land consolidations.

## Data Flow & Architecture
- **Inputs**: Rectified cadastral parcel geometries from `parcels` and AI candidate polygons from `candidate_geometries`.
- **Processing**:
  - Metric UTM projection of all candidate and cadastral shapes.
  - Pairwise Intersection-over-Union (IoU) matrix and directional overlap fraction computations.
  - Classification into 4 topological states:
    - **`NO_MATCH`**: Maximum IoU falls below `MIN_IOU_FLOOR` (<0.20).
    - **`MERGE`**: Single AI polygon encompasses $\ge 2$ cadastral plots ($\ge 40\%$ overlap each).
    - **`SPLIT`**: Single cadastral plot partitioned across $\ge 2$ AI polygons (combined IoU $\ge 0.55$).
    - **`ONE_TO_ONE`**: Direct singular correspondence meeting `MIN_IOU_ONE_TO_ONE`.
- **Outputs**: Populated `match_results` table containing matched candidate references, match types, and confidence scores.

## Phase Modules & Files
- [[P3-matching.py]]
- [[P3-geo.py]]
- [[P3-runner.py]]
