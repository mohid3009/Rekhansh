---
tags: [file, frontend, screen, verification]
---
# VerifyScreen.tsx
`frontend/src/screens/VerifyScreen.tsx`

## Overview
Human-in-the-loop decision console enabling field surveyors and Sub-Registrar Officers (SRO) to review AI recommendations, perform boundary adjustments, and execute binding sign-offs.

## Key Responsibilities
- **Interactive Boundary Editing**:
  - Drag-and-drop vertex manipulation on top of the MapLibre canvas for precision boundary correction.
  - Vertex snapping to adjacent parcel boundaries to preserve topological consistency and prevent gaps/overlaps.
  - Split and Merge tools for resolving parcel subdivision or land consolidation cases.
- **Decision Action Workflows**:
  - **Confirm**: Accept the AI-reconciled boundary as true and accurate without alterations.
  - **Correct**: Submit human-adjusted boundary coordinates with mandatory surveyor field justification notes.
  - **Escalate**: Flag the parcel for on-ground physical RTK-GNSS rover resurvey due to intractable boundary ambiguity or land disputes.
- **Backend Dispatch & Ledger Creation**: Dispatches verification payloads to `/api/parcels/:id/verify`. On success, writes a new version block to the immutable audit ledger.
