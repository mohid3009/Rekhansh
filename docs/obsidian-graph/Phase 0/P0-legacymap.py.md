---
tags: [file, seed, legacy]
---
# legacymap.py
`backend/app/seed/legacymap.py`

## Overview
Module 02 — Legacy cadastral scan rendering and artificial degradation generator. Simulates decades-old physical paper revenue maps, complete with cartographic distortions, scale inaccuracies, and scanner artefacts.

## Key Responsibilities
- **Cadastral Vector Rendering**:
  - Draws legacy parcel boundary lines, survey parcel numbers, and survey station marks onto a high-resolution raster canvas.
- **Physical Artefact Simulation**:
  - Applies non-linear affine warps, rotation skews, and slight scale expansions/contractions simulating paper shrinkage and moisture distortion.
  - Adds scanner noise, paper texture tinting, folds, and coffee/dust stains to replicate historical archival conditions.
- **Ground Control Point (GCP) Placement**:
  - Imprints identifiable cartographic tick marks and tri-junction boundary stones (GCPs) with known ground coordinates.
  - Generates synthetic `.pgw` / GCP coordinate tables used as input for Phase 2 Georeferencing evaluation.
