---
tags: [file, frontend, screen]
---
# ParcelsScreen.tsx
`frontend/src/screens/ParcelsScreen.tsx`

## Overview
Primary tabular inventory dashboard providing surveyors and revenue officials with a complete overview of all land parcels within the surveyed village.

## Key Responsibilities
- **Multi-Facet Filtering**: Allows real-time filtering by Triage Status (All, Cleared, Flagged, Insufficient Evidence), Match Type (1-to-1, Split, Merge, No Match), and Verification Status (Unverified, Confirmed, Corrected, Escalated).
- **Search Capabilities**: Client-side full-text search across Survey Numbers and RoR (Record of Rights) owner names.
- **Metric Comparison Columns**:
  - Legacy RoR recorded area vs. current AI-extracted area.
  - Calculated area variance percentage (color-coded red/amber/green).
  - Match confidence score (IoU %) and boundary deviation flags.
  - Primary reason codes explaining automatic triage classification.
- **Workflow Action Shortcuts**:
  - Direct deep-links to `EvidenceScreen` (`/evidence/:id`) for inspection of failure modes.
  - Direct link to `VerifyScreen` (`/verify/:id`) for active manual review and sign-off.
  - Quick access to `HistoryScreen` (`/history/:id`) to inspect audit version chains.
