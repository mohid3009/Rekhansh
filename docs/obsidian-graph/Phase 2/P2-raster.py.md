---
tags: [file, raster, georeference]
---
# raster.py
`backend/app/raster.py`

## Overview
Raster processing and GIS spatial reference utility library. Manages ESRI world files, affine transformations, PNG compression, and sensor metadata.

## Key Responsibilities
- **World File Affine Mathematics (`WorldFileAffine`)**:
  - Encapsulates 6 standard ESRI world file parameters ($A, D, B, E, C, F$): pixel size $X$, rotational skew $Y$, rotational skew $X$, pixel size $Y$ (negative), upper-left $X$, upper-left $Y$.
  - Provides forward `pixel_to_geo(px, py)` and inverse `geo_to_pixel(x, y)` coordinate mapping functions.
- **World File I/O (`save_png`, `write_world_file`)**:
  - Writes companion `.pgw` and `.wld` files adhering to open GIS standards, allowing raster scans and orthomosaics to be loaded directly into QGIS, ArcGIS, or MapLibre.
- **Tile Matrix Calculations (`tile_affine`)**:
  - Derives exact bounding boxes and pixel dimensions for web Mercator XYZ tile grids across arbitrary zoom levels.
- **Sensor Provenance Archiving (`write_provenance`)**:
  - Writes structured `provenance.json` records capturing image timestamps, resolution centimeters per pixel, and spatial bounds.
