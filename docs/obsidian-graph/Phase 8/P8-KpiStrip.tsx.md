---
tags: [file, frontend, component, kpis]
---
# KpiStrip.tsx
`frontend/src/components/KpiStrip.tsx`

## Overview
High-visibility, top-level dashboard strip summarizing critical operational metrics and key performance indicators for the current resurvey session.

## Key Responsibilities
- **Triage Breakdown Metrics**:
  - **Cleared Ratio**: Percentage of parcels automatically cleared for direct SRO sign-off (Target: >60% operational efficiency).
  - **Flagged Ratio**: Percentage of parcels requiring desktop surveyor inspection and boundary verification.
  - **Insufficient Evidence Ratio**: Percentage requiring escalation to on-ground RTK field survey.
- **Pipeline Performance Metrics**:
  - Total end-to-end pipeline execution time in milliseconds.
  - Active segmentation tier indicator (Tier 1 High-Res AI / Tier 2 OpenCV Edge Contours / Tier 3 Perturbation Baseline).
  - Average IoU overlap score across the entire village dataset.
- **On-Ground Workload Reduction Metric**:
  - Computes and displays the net reduction in ground physical RTK-GNSS rover survey hours achieved through automated triage.
