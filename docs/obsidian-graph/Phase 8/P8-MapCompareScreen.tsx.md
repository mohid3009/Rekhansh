---
tags: [file, frontend, screen, gis]
---
# MapCompareScreen.tsx
`frontend/src/screens/MapCompareScreen.tsx`

## Overview
Interactive GIS mapping interface built on MapLibre GL, providing side-by-side or layered spatial visual analysis between historical records and modern high-resolution satellite/drone imagery.

## Key Responsibilities
- **MapLibre GL Map Canvas**: Renders real-world geographic coordinates with pan, zoom, pitch, and rotation capabilities centered on the village bounding box.
- **Multi-Layer Stacking & Transparency**:
  - Base ESRI high-resolution satellite orthomosaic tile layer.
  - Georeferenced legacy cadastral revenue map scan overlay with real-time opacity slider control.
  - Raw AI extracted candidate polygon layer (Tier 2 OpenCV contours / Tier 3 predictions).
  - Official cadastral parcel vector boundaries colored dynamically by triage outcome.
- **Interactive Inspection**:
  - Hover highlights and click-to-inspect popups showing parcel ID, survey number, RoR owner name, and calculated area.
  - Boundary comparison tool visually rendering discrepancy areas between legacy paper maps and ground-truth satellite boundaries.
