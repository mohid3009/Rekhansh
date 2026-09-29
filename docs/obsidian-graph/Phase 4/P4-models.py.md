---
tags: [file, shared, models, phase4]
---
# models.py (Phase 4)
`backend/app/models.py`

## Overview
Pydantic data models defining the mathematical evidence and candidate geometry contracts in Phase 4.

## Key Responsibilities in Phase 4
- **Candidate Geometry Schema (`CandidateGeometry`)**:
  - Validates polygon coordinates, coordinate reference systems, generation timestamps, and tier provenance.
- **Evidence Contract Schema (`ParcelEvidence`)**:
  - Enforces strict floating-point bounds on mathematical metrics: IoU ($0.0 \le \text{IoU} \le 1.0$), ASBD ($\ge 0.0$ meters), area delta percentage, support ratio ($0.0 \le \text{ratio} \le 100.0\%$), and uncertainty score ($0.0 \le \text{score} \le 1.0$).
- **JSON Serialization & Validation**:
  - Provides standardized serializers converting Shapely geometries to valid GeoJSON coordinate arrays for database storage and API responses.
