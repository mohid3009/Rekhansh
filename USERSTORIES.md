# User Stories — Rural Land Resurvey Triage

Companion to `rural-land-resurvey-prd.md`. Same actors, same module and screen
numbering, same config defaults — read the PRD for architecture and formulas;
this is what to build against, story by story.

**Handoff target:** GLM 5.3
**Format:** *As a [role], I want [goal], so that [benefit]* — with acceptance
criteria a build can be checked against directly, not just read.

## Actors

| Actor | Who they are here |
|---|---|
| Developer | Builds the prototype (this is GLM, functionally) |
| Surveyor | Reviews flagged / insufficient-evidence parcels, submits verification |
| Reviewing official | Watches the dashboard, reads evidence, exports records |
| Judge | Walks the five-screen demo end to end, evaluates the pitch |

## Priority

- **P0** — required for the demo script (PRD, *Demo Script*) to run start to finish
- **P1** — meaningfully improves the demo, not launch-blocking
- **P2** — stretch, cut first under time pressure

---

## Epic 0 — Environment & Seed Data

### US-0.1 — Mock village generator
*As a developer, I want a mock data generator that creates one village with
10–30 procedurally generated parcels, so the whole pipeline can be exercised
without real government data access.*

- Output is a GeoJSON `FeatureCollection` matching the `Parcel` schema.
- Parcel count and random seed are both configurable; the same seed reproduces
  identical output.
- Survey numbers follow the `NNN/N` convention; no two parcels in a village
  share one. — **P0**

### US-0.2 — Externalized triage config
*As a developer, I want the triage thresholds in one config file rather than
hardcoded, so calibration values can be tuned without touching pipeline code.*

- Every value in the PRD's Reference Config table (`CLEAR_MAX_AREA_DIFF_PCT`,
  `CLEAR_MIN_SUPPORT_RATIO_PCT`, etc.) lives in one config file.
- Changing a threshold and re-running the pipeline changes triage outcomes
  accordingly, with no code change. — **P0**

---

## Epic 1 — Village Overview (Screen 1)

### US-1.1 — See every parcel's triage status at a glance
*As a reviewing official, I want all parcels in the pilot village on a map
colored by triage state, so I can immediately gauge how many need attention.*

- Every parcel renders with a fill/border color matching its current
  `TriageDecision.state` (🟢 cleared / 🟠 flagged / 🔴 insufficient evidence).
- A summary row shows counts per state (e.g. "18 cleared · 8 flagged · 4
  insufficient").
- A "PROTOTYPE DATA — NOT AN OFFICIAL RECORD" label is visible on screen. — **P0**

### US-1.2 — Filter and search the parcel list
*As a reviewing official, I want to filter by triage state or search by survey
number, so I can jump straight to the parcels I need to review.*

- Multi-select filter for `CLEARED` / `FLAGGED` / `INSUFFICIENT_EVIDENCE`.
- Search matches on `survey_number`.
- Map and list stay in sync with the active filter. — **P1**

### US-1.3 — Drill into a parcel
*As a reviewing official, I want clicking a parcel to take me straight to its
comparison view, so I don't have to look up its ID separately.*

- Clicking a parcel on the map or list opens Screen 2 for that `parcel_id`.
- Navigating back returns to the same filter and scroll position. — **P0**

---

## Epic 2 — Parcel Comparison (Screen 2)

### US-2.1 — Compare recorded vs observed boundary
*As a reviewing official, I want the cadastral polygon and the AI-observed
field polygon overlaid on the aerial image, so I can judge how well they line
up before reading the numbers.*

- Cadastral polygon renders as a solid line, AI polygon(s) as dashed, both
  over the orthomosaic.
- Both `recorded_area_ha` and the observed area are labeled on screen.
- The `match_type` badge (`ONE_TO_ONE` / `SPLIT` / `MERGE` / `NO_MATCH`) is
  visible.
- A layer toggle shows or hides each polygon independently.
- If `match_type == NO_MATCH`, the AI layer is empty and a message says no
  matching field was detected — not a blank map with no explanation. — **P0**

---

## Epic 3 — Evidence Panel (Screen 3)

### US-3.1 — See why a parcel was triaged the way it was
*As a reviewing official, I want the exact metrics behind a parcel's triage
decision, so I understand the reasoning, not just the color.*

- Displays `area_diff_pct`, `area_diff_ha`, `boundary_displacement_m`, `iou`,
  `support_ratio_pct`, `occlusion_fraction`, `topology_status` (+
  `topology_issues` if `FAIL`), `uncertainty_score`, `evidence_quality`.
- Displays `reason_codes` in plain language (e.g. "Boundary shift 0.42 m —
  within tolerance"), not just the raw code strings.
- Numbers shown match the `EvidenceReport` linked by the decision's
  `evidence_report_id` — never a stale or recomputed-on-the-fly value that
  could disagree with what's on Screen 1. — **P0**

### US-3.2 — Send a parcel forward for verification
*As a surveyor, I want one clear action to send a parcel to field
verification, so the workflow moves forward without me touching the API.*

- Button reads "Send to random audit" for `CLEARED` parcels, "Send to field
  verification" for `FLAGGED` / `INSUFFICIENT_EVIDENCE`.
- Clicking it opens Screen 4 pre-loaded with this parcel. — **P0**

---

## Epic 4 — Field Verification (Screen 4)

### US-4.1 — Correct a boundary without RTK hardware
*As a surveyor, I want to redraw a parcel's boundary directly on the map, so I
can verify it even though no RTK/GNSS hardware is available for this build.*

- A polygon editor over the map lets me redraw the boundary; this is the
  primary path and must work with no CSV import.
- A CSV import control for checkpoints (`point_id, lat, lon, elevation_m,
  horizontal_accuracy_m, vertical_accuracy_m, captured_at`) is present for a
  future real-hardware deployment, but nothing on this screen depends on it.
- `observed_error_m` is computed and shown once a corrected geometry exists. — **P0**

### US-4.2 — Record accept / correct / reject
*As a surveyor, I want to record my decision with notes, so my judgment is
captured alongside the system's evidence, not silently overwritten by it.*

- `ACCEPT` / `CORRECT` / `REJECT` are mutually exclusive.
- `CORRECT` can't be submitted without a corrected geometry present.
- `REJECT` requires a note; `ACCEPT`/`CORRECT` notes are optional.
- Submitting creates one `RTKVerification` and one new `ParcelVersion`, then
  returns to Screen 3 or 5 showing the updated state. — **P0**

### US-4.3 — Rejections stay visible, not silently dropped
*As a reviewing official, I want a rejected verification to show as
"escalated" rather than disappear, so I know it still needs attention.*

- After a `REJECT`, the parcel's latest `ParcelVersion.verification_status`
  is `ESCALATED`.
- Screens 1 and 5 visually distinguish `ESCALATED` from `CONFIRMED` /
  `CORRECTED`.
- No geometry change is applied to the record on `REJECT`. — **P1**

---

## Epic 5 — Versioned Record (Screen 5)

### US-5.1 — See the full version history
*As a reviewing official, I want a parcel's complete version history, so I can
trace exactly what changed, when, and why.*

- Timeline shows every `ParcelVersion` in order with timestamp,
  `verification_status`, `surveyor_action`, and a short hash (first 8 hex
  chars of `record_hash`).
- Each version links to its `evidence_report_id` where one exists.
- Clicking a version shows its full geometry/area snapshot at that point. — **P0**

### US-5.2 — Export a record
*As a reviewing official, I want to export a parcel's final record as JSON, so
I can share it outside the demo.*

- Export downloads the current `ParcelVersion` plus its linked
  `EvidenceReport` and `RTKVerification` (if any).
- The export includes `record_hash` and `previous_version_hash`. — **P1**

### US-5.3 — Detect a broken hash chain
*As a reviewing official, I want the UI to flag it if a version's hash no
longer matches its recomputed value, so I can trust the integrity of the
record trail rather than assume it.*

- Recomputing `record_hash` for each stored version and comparing against the
  stored value is exposed as an integrity check.
- A break at any version visibly flags every version after it as
  unverified-chain, not just the one that changed. — **P2**

---

## Epic 6 — Pipeline Execution

### US-6.1 — Reset the demo to a known state
*As a developer, I want one action that re-runs the full pipeline for the
village, so the demo can be reset between run-throughs.*

- `POST /api/pipeline/run-full` regenerates AI polygons (Tier 3 synthetic
  fallback for the current build) and recomputes `MatchResult`,
  `EvidenceReport`, and `TriageDecision` for every parcel.
- Existing `ParcelVersion` history is untouched by a reset — it only affects
  current/unverified triage state, never erases prior verifications.
- Given a fixed seed, running it twice on unmodified input produces the same
  triage states each time. — **P0**

---

## Epic 7 — KPI Reporting

### US-7.1 — See the core KPIs on every screen
*As a reviewing official or judge, I want a persistent KPI strip showing
false-clear rate, % cleared without RTK, boundary RMSE, area error,
false-flag rate, and processing time per parcel, so the prototype's core
claim is visible at a glance.*

- `GET /api/kpis` returns all six metrics per the PRD's definitions.
- Metrics recompute automatically whenever a new `RTKVerification` is
  submitted.
- A metric with no data yet (e.g. zero audits run) shows as "—", never `0%`
  or `NaN`, so it isn't misread as a real result. — **P0**

---

## Epic 8 — Prototype Trust

### US-8.1 — Never mistake mock data for a real record
*As a judge, I want every screen showing generated data to say so clearly, so
I don't mistake it for a real government record.*

- A visible "PROTOTYPE DATA — NOT AN OFFICIAL RECORD" banner appears on
  Screens 1, 2, and 5 wherever parcel or RoR data is shown — not buried in
  fine print. — **P1**

---

## Epic 9 — Demo Access

### US-9.1 — One link, no setup
*As a judge, I want to open a single link and see the whole demo working, so
I don't need any local setup to evaluate it.*

- Frontend is reachable at one Vercel URL.
- All API calls resolve to the separately hosted backend with no CORS errors
  and no hardcoded `localhost` URLs.
- A loading state covers the backend's cold-start latency on first load
  rather than showing a broken or empty screen. — **P0**

### US-9.2 — Walk the demo script without a dead end
*As a judge, I want to complete the full demo script — overview, comparison,
evidence, the three seeded verifications, final record, KPI strip — in one
sitting with nothing breaking.*

- The three seeded example parcels (one cleared → audit, one flagged → RTK,
  one insufficient → field verification) exist in seed data and are reachable
  from Screen 1 with no extra setup.
- Completing the script updates the KPI strip to non-placeholder values.
- No step requires a backend restart or manual data reset mid-walkthrough. — **P0**
