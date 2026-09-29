---
tags: [file, frontend, screen, triage]
---
# EvidenceScreen.tsx
`frontend/src/screens/EvidenceScreen.tsx`

## Overview
Comprehensive diagnostic evidence dossier for an individual parcel, providing mathematical transparency and explainability behind automated triage classifications.

## Key Responsibilities
- **Quantitative Metric Cards**:
  - **Intersection over Union (IoU)**: Exact polygonal overlap metric against candidate AI polygons.
  - **Average Symmetric Boundary Distance (ASBD)**: Distance metric in meters quantifying edge deviation.
  - **Area Discrepancy %**: Percent delta between RoR legal documentation and satellite physical reality.
  - **Support Ratio**: Proportion of boundary perimeter supported by clear visible physical ground features (hedgerows, roads, canals).
- **Waterfall Rule Execution Trace**: Step-by-step breakdown of how `triage.yaml` rules were evaluated in sequence, showing which rule was triggered (e.g., `RULE_IOU_LOW`, `RULE_ASBD_EXCEEDED`, `RULE_AREA_MISMATCH`) and resulting in `CLEARED`, `FLAGGED`, or `INSUFFICIENT_EVIDENCE`.
- **Topological Adjacency Validation**: Verifies boundary sharing with neighbouring parcels, highlighting topological tears, overlaps, or boundary slivers.
- **Visual Evidence Overlays**: High-resolution zoom canvas showing the parcel boundary overlaid on both legacy scan and ESRI imagery with highlighted dispute zones.
