---
tags: [file, pipeline, data]
---
# realobs.py
`backend/app/pipeline/realobs.py`

## Overview
Ground observation loader for real-world drone surveys and external field polygon datasets. Ingests authenticated boundary observation files as direct inputs to the pipeline.

## Key Responsibilities
- **GeoJSON Parsing & Extraction**:
  - `load_real_observations(data_dir)`: Scans `backend/data/` for `pilot_village_real.geojson` or pre-processed drone vector outputs.
  - Normalizes external coordinate systems to standard WGS84 GeoJSON geometry format.
- **Confidence Attribution**:
  - Assigns sensor confidence scores based on GPS metadata, survey date, and boundary quality attributes present in external files.
- **Contract Compatibility**:
  - Wraps ingested features into the standard `AIFieldPolygon` schema so downstream georeferencing and matching engines treat real observations identically to CV or synthetic tiers.
