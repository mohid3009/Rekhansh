---
tags: [file, seed, raster]
---
# fetch_imagery.py
`backend/app/seed/fetch_imagery.py`

## Overview
Module 03 — Pre-existing spatial data acquisition and tile caching. Downloads authentic high-resolution satellite imagery from ESRI World Imagery and contextual OpenStreetMap layers to serve as modern ground truth.

## Key Responsibilities
- **ESRI Tile Fetching & Stitching**:
  - Calculates XYZ tile coordinates covering the target village bounding box at zoom level 18 (~0.6 m/pixel ground resolution).
  - Fetches raster image tiles over HTTP with exponential retry and local file caching.
  - Stitches individual 256x256 tiles into a continuous georeferenced orthomosaic PNG.
- **Georeference World File Generation**:
  - Generates companion ESRI `.pgw` world file establishing affine mapping (pixel dimensions, rotation, upper-left origin coordinates).
- **OSM Vector Integration**:
  - Queries OpenStreetMap Overpass API for contextual linear vector infrastructure (major/minor roads, waterways, drainage canals).
  - Venders fallback static vector layers if network queries fail, maintaining fully offline capability.
- **Sensor Provenance Tracking**:
  - Emits `provenance.json` detailing imagery provider, acquisition epoch, spatial resolution, and licence attribution for compliance audit.
