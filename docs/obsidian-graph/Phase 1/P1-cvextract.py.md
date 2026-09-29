---
tags: [file, pipeline, opencv, vision]
---
# cvextract.py
`backend/app/cvextract.py`

## Overview
Tier 2 classical computer vision boundary extraction engine. Uses OpenCV algorithms directly on the stitched orthomosaic image to detect agricultural plot bunds, farm boundaries, and irrigation channels.

## Key Responsibilities
- **Image Preprocessing & Edge Detection**:
  - Converts RGB orthomosaic to grayscale and applies Gaussian smoothing to eliminate sensor grain.
  - Executes Canny edge detector with configurable hysteresis thresholds (low: 40, high: 120).
  - Performs morphological dilation and closing to bridge small gaps in field boundaries and hedgerows.
- **Contour Extraction & Polygonization**:
  - Runs `cv2.findContours` using `RETR_EXTERNAL` or `RETR_TREE` hierarchy.
  - Applies Ramer-Douglas-Peucker simplification via `cv2.approxPolyDP` (epsilon ~3.0 px) to convert pixel contours into clean vector polygons.
  - Filters out polygons smaller than `min_area_ha` or larger than `max_area_ha` to remove noise artifacts.
- **Spectral Feature Classification (`spectral_features`)**:
  - Samples pixel color statistics inside and along the contour boundary.
  - Evaluates Excess Green Index ($ExG = 2G - R - B$) and brightness thresholds to tag features as `BUND` (bare soil bunds between green crops), `IRRIGATION_CHANNEL` (dark, low-reflectance water bodies), `ROAD` (elongated corridors), or `BOUNDARY`.
- **Pixel-to-Geographic Projection**:
  - Maps image coordinates $(x, y)$ to real-world WGS84 coordinates using `WorldFileAffine` transformation parameters.
