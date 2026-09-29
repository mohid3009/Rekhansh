---
tags: [file, config, rules, phase1]
---
# triage.yaml (Phase 1)
`backend/config/triage.yaml`

## Overview
Declarative configuration defining thresholds and parameter matrices governing field polygon extraction and scenario generation in Phase 1.

## Key Responsibilities in Phase 1
- **Extraction Thresholds (`extraction`)**:
  - `min_area_ha`: Minimum parcel size filter (e.g. 0.05 ha) to discard tiny visual contour artifacts.
  - `max_area_ha`: Maximum parcel size filter (e.g. 20.0 ha) to eliminate full-image boundary errors.
  - `canny_low` & `canny_high`: Edge detector sensitivity parameters tuned for satellite orthomosaic contrasts.
- **Synthetic Scenario Controls (`extraction.synthetic`)**:
  - Sets exact counts and ratios for generated test scenarios: `NO_MATCH_COUNT`, `SPLIT_COUNT`, `MERGE_COUNT`, `DRIFT_COUNT`, `LOW_CONF_COUNT`.
  - Defines spatial variance boundaries (drift distances in meters, angle rotations in degrees) used when perturbing cadastral bounds.
