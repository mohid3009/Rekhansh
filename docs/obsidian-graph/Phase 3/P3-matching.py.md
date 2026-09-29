---
tags: [file, pipeline, matching]
---
# matching.py
`backend/app/pipeline/matching.py`

## Overview
Module 05 — Polygon matching and topological correspondence engine. Evaluates spatial overlap (IoU) and boundary intersections between historical cadastral parcels and modern AI-extracted polygons, categorizing relationships into four canonical states.

## Key Responsibilities
- **IoU & Overlap Fraction Computation**:
  - Projects all geometries to local metric UTM coordinates to avoid spherical distortion.
  - Computes pairwise Intersection-over-Union ($\text{IoU} = \frac{\text{Area}(A \cap B)}{\text{Area}(A \cup B)}$) and directional overlap fractions ($\frac{\text{Area}(A \cap B)}{\text{Area}(A)}$).
- **Four-Way Topological Classification**:
  - **`NO_MATCH`**: Evaluated first. Triggered when the maximum IoU against all candidate polygons falls below `MIN_IOU_FLOOR` (e.g. <0.20), indicating no physical boundary correlation on the ground.
  - **`MERGE`**: Triggered when a single AI-extracted polygon simultaneously covers two or more adjoining cadastral parcels, each exceeding `MERGE_MIN_OVERLAP_FRAC` (e.g. $\ge 0.40$), indicating physical plot consolidation or joint farming.
  - **`SPLIT`**: Triggered when two or more distinct AI polygons partition an individual cadastral parcel, reaching `SPLIT_COMBINED_IOU` ($\ge 0.55$) without a single polygon explaining the whole parcel. Identifies legal inheritance subdivision or land fragmentation.
  - **`ONE_TO_ONE`**: Direct match where a single AI polygon corresponds cleanly to a cadastral parcel.
- **Match Confidence Assignment**:
  - Assigns calibrated `match_confidence` ratings carrying IoU scores and overlap ratios into the `match_results` schema.
