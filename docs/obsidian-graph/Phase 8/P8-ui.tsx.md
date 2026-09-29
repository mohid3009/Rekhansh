---
tags: [file, frontend, component, design-system]
---
# ui.tsx
`frontend/src/components/ui.tsx`

## Overview
Reusable UI component toolkit providing standardized, accessible, and theme-consistent micro-components across all frontend views.

## Key Responsibilities
- **Status Badges (`Badge`)**:
  - Dynamically renders semantic badge styling for triage classifications (`CLEARED` = Forest Green, `FLAGGED` = Amber, `INSUFFICIENT_EVIDENCE` = Crimson).
  - Renders match classification badges (`ONE_TO_ONE`, `SPLIT`, `MERGE`, `NO_MATCH`) with high-contrast text and border styling.
- **Feedback & Notification Banners (`Banner`, `AlertBanner`)**:
  - Displays dismissible alerts, pipeline execution success summaries, and error toast messages.
- **Loading Primitives (`Spinner`, `Skeleton`)**:
  - Animated SVG spinners and skeleton placeholders for smooth asynchronous loading states during pipeline execution or data refreshes.
- **Interactive Modals & Cards (`Modal`, `Card`, `StatBox`)**:
  - Clean container abstractions for metric cards, confirmation dialogues, and interactive popup sheets.
