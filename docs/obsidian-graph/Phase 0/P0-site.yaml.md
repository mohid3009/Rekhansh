---
tags: [file, config, seed]
---
# site.yaml
`backend/config/site.yaml`

## Overview
Primary declarative configuration file defining geographic boundaries, pilot site coordinates, imagery resolution parameters, and procedural seeding switches.

## Key Responsibilities
- **Site Metadata**:
  - Sets village identity, district, state, and central geographic latitude/longitude anchor coordinates.
- **Imagery Extraction Parameters**:
  - Specifies ESRI imagery tile zoom level (typically 18 for sub-meter resolution).
  - Configures bounding box padding margins around parcel polygons.
- **Cadastral & Procedural Seed Knobs**:
  - Defines pseudorandom generator seed integer ensuring deterministic, reproducible village generation across test runs.
  - Specifies target parcel count (e.g. 18 parcels) and artificial perturbation variance settings.
- **Hot-Reloadable Design**:
  - Structured for zero-restart reloading by backend services during development and field deployment.
