---
tags: [file, pipeline, kpis]
---
# kpis.py
`backend/app/pipeline/kpis.py`

## Overview
Module 08 / US-7.x — Operational KPI dashboard calculations and statistical performance evaluator. Quantifies algorithmic accuracy, regulatory safety, and field survey efficiency.

## Key Responsibilities
- **False-Clear Rate Calculation (`false_clear_rate`)**:
  - Measures regulatory failure: proportion of parcels automatically designated `CLEARED` where subsequent ground RTK audit revealed boundary displacement $> \text{FALSE\_CLEAR\_ERROR\_M}$ (e.g. >0.5 m) or surveyor rejection.
  - Critical safety metric guaranteeing bad boundaries are not silently approved.
- **On-Ground Fieldwork Reduction (`cleared_without_rtk`)**:
  - Calculates the percentage of total village parcels cleared without requiring physical rover fieldwork, representing direct economic and labor savings for the survey department.
- **Empirical Accuracy Metrics**:
  - `boundary_rmse_m`: True physical boundary Root Mean Square Error (in meters) comparing reconciled boundaries directly against RTK ground-truth coordinates.
  - `area_error_pct`: Mean absolute percentage error between legally declared area and high-precision RTK ground truth.
- **False-Flag Rate (`false_flag_rate`)**:
  - Computes the proportion of parcels flagged for review that surveyors found were actually accurate, quantifying surveyor fatigue and review efficiency.
