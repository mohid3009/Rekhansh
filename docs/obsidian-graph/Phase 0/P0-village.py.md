---
tags: [file, seed]
---
# village.py
`backend/app/seed/village.py`

## Overview
Module 01 — Pilot data ingestion and synthetic village generation. Establishes the foundational cadastral baseline by importing real Bhu-Naksha survey data or generating a geometrically sound procedural village for testing and simulation.

## Key Responsibilities
- **Real Cadastral Ingestion**:
  - Loads real Mahabhunakasha parcel geometry for Bond Gavhan village (`pilot_village_real.geojson` / `real_parcels.json`, Tier A ODbL-1.0).
  - Preserves authentic survey numbers, administrative hierarchies (State: Maharashtra, District: Akola, Taluka: Murtijapur), and officially declared areas.
- **Procedural Village Fallback**:
  - If external datasets are absent, generates an 18-parcel synthetic layout with realistic agricultural field boundaries and shared internal borders.
  - Generates realistic mock RoR (Record of Rights) owner names and declared areas.
- **Topological & Spatial Graph Processing**:
  - Projects coordinates to appropriate local UTM CRS (Universal Transverse Mercator) to ensure metric accuracy.
  - Builds an adjacency graph identifying all neighbouring parcels sharing boundary segments.
- **Database Seeding**:
  - Populates the `villages` table with centroid, bounding box, and provenance metadata.
  - Populates the `parcels` table with initial recorded areas, geometries, and topological adjacency lists.
