# Rural Land Resurvey Triage System — Technical Reference (v2)
**PS 26010 — Survey/Resurvey of Rural Agricultural Land in India (DoLR, Hardware category)**
Status as of: September 27, 2026 · Updated for PPT/idea-submission phase · Nothing below is built or measured yet unless explicitly marked otherwise.

**Changes since v1:** CORS access status resolved (was "unverified"); added pitch-ready USP, simplified workflow, and a labeled impact estimate; build order timeboxed. All other open items remain genuinely open — nothing else has been verified since v1, and nothing is claimed as resolved unless a source is given below.

---

## 1. One-line summary

A triage system for rural land resurvey. Drone imagery, a legacy-map comparison, and a measured error budget decide which parcels already agree with the existing records. RTK surveyors go only where the evidence says they must. The system does not decide legal boundaries and does not replace Bhunaksha or existing state resurvey programs — it sits in front of them.

**USP, one line:** *We don't resurvey every parcel — we tell you which ones actually need it, with a measured error bound on that decision.*

---

## 2. Pitch-ready essentials

Use this section for slides and the 3-minute pitch. Section 4 has the full technical version (σ_total, overlap graph, tiering logic) — keep that for Q&A and the appendix, not the main deck.

**Simplified workflow (slide version):**
```
   Drone imagery + legacy cadastral map
                 │
                 ▼
          AI Triage Engine
                 │
      ┌──────────┼───────────┐
      ▼          ▼           ▼
  CLEARED     FLAGGED    INSUFFICIENT
 (audit only) (verify)    (verify)
                 │
                 ▼
     Surveyor: accept / correct / reject
```

**Impact estimate (label this as an estimate on any slide — not a measured result):**
If the triage engine clears an estimated 60–70% of parcels without a field visit (audited by random RTK sample rather than skipped outright), a 30-parcel village survey could drop from roughly 30 surveyor visits to roughly 9–12. This is a projection to be replaced with the prototype's actual measured false-clear rate — do not present it as a finding. Useful context, not a funding claim: DILRMP 3.0 operates at ₹565.5 crore, 2026–31, national scale (confirmed via PIB, see §8).

---

## 3. Problem and positioning

- Village cadastral maps are commonly at 1:4000 scale; subdivisions recorded in the Field Measurement Book (FMB) often aren't reflected in the map.
- Survey number and landholding don't line up cleanly — an Andhra Pradesh pilot village showed mismatched counts between the two.
- Existing programs (Andhra's drone/CORS/GNSS resurvey, Bhunaksha's legacy-map georeferencing) measure or digitize parcels directly.
- **Your role:** decide which parcels genuinely need that expensive treatment and which don't — with evidence, not assumption.

---

## 4. Full technical workflow (appendix / Q&A reference)

```
Legacy map + RoR + FMB
        │
        ▼
  Georeference to RTK control points  →  σ_cadastral
        │
        ▼
  Drone capture (RTK/PPK + GCPs + checkpoints)
        │
        ▼
  Photogrammetry → orthomosaic + DSM   →  σ_ortho
        │
        ▼
  AI extraction of field boundaries    →  σ_extract (conformal band)
        │
        ▼
  Match extracted fields ↔ cadastral parcels (overlap graph)
        │
        ▼
  Decision engine: CLEARED / FLAGGED / INSUFFICIENT EVIDENCE
        │
        ├─ CLEARED ──────────────► random audit sample (RTK)
        ├─ FLAGGED ──────────────► tiered field verification
        └─ INSUFFICIENT EVIDENCE ─► tiered field verification
                        │
                        ▼
              Surveyor accept / correct / reject
                        │
                        ▼
        Versioned record + evidence + hash chain
                        │
                        ▼
              Evidence/version API (external consumers)
```

---

## 5. Decision engine (the core differentiator)

```
σ_total = sqrt(σ_rtk² + σ_ortho² + σ_cadastral² + σ_extract²)

support_ratio = share of the recorded boundary's length
                with a visible matching feature within tolerance

match = overlap_graph(extracted_fields, cadastral_parcel)   # 1:1 | split | merge | none

if match ≠ 1:1 OR support_ratio < s_min OR evidence quality poor:
    → INSUFFICIENT EVIDENCE
elif boundary_shift ≤ k · σ_total AND area matches RoR:
    → CLEARED  (goes into random audit pool)
else:
    → FLAGGED  (tiered field verification)
```

- `k` and `s_min` must be calibrated against RTK-surveyed truth, not chosen by hand.
- A parcel is cleared only on **positive evidence** (high support ratio), never because the model simply found nothing wrong — low model recall on faint boundaries makes "no discrepancy detected" unreliable on its own.
- The **cleared pool is audited**: a random RTK-checked sample gives a false-clear rate with a confidence interval — this is the single most convincing number to show a judge.
- Field verification runs in **three tiers**: cleared (no visit, audit only), small/ambiguous shifts (phone evidence + neighbour confirmation), large/contested/insufficient (RTK surveyor, accept/correct/reject).

---

## 6. Tech stack — fit review and improvements

| Layer | Chosen tech | Why it fits | What to improve / watch |
|---|---|---|---|
| **Photogrammetry** | OpenDroneMap / WebODM | Free, open-source, self-calibrates camera parameters during bundle adjustment, produces orthomosaic + DSM, documented RAM/image sizing (~4 GB for ≤100–200 images, ~16 GB for 250, ~32 GB for 500) | Run a fast/low-resolution preview pass in the field to catch bad coverage before packing up (verify ODM exposes a quick-preview mode); defer full-resolution processing to the edge node so field time isn't wasted waiting |
| **Ground control / ground truth** | RTK/PPK drone + GNSS rover (survey-grade or benchmarked DIY) | Matches the accuracy tier you need to claim; PPK fallback covers weak-connectivity fields | Never use a DIY rover as ground truth until it's benchmarked against a survey-grade one on the same points; log raw RINEX for PPK whenever NTRIP drops |
| **Corrections network** | Survey of India CORS via NTRIP | Removes the need to run your own base station | **Resolved:** public self-registration process confirmed — register at `cors.surveyofindia.gov.in` (TPP Web) with personal/organization details and a security code; account is admin-approved by email before RINEX data access opens. A college workshop (Loreto College, Kolkata) has walked students through this exact registration. **Still open:** you have not registered your own team account yet — do this before pitching, and note approval turnaround time is unknown |
| **Geospatial processing** | PostGIS, GeoPandas, Shapely, GDAL, QGIS | Standard, well-supported, handles area, IoU, topology and vector operations natively | Use PostGIS's topology extension for automated gap/overlap detection instead of hand-rolled checks; use a graph library (e.g. `networkx`) for the field-to-parcel overlap graph rather than custom logic |
| **AI / extraction** | PyTorch, YOLO11-based fine-tune (Delineate Anything lineage), OpenCV | Purpose-built for field boundaries (not generic building segmentation), small model variants are edge-viable | **Real risk to flag:** most off-the-shelf conformal prediction libraries (e.g. MAPIE) target classification/regression, not segmentation masks — you will likely need to implement the mask-to-band calibration yourself; budget time for this |
| **Backend / API** | FastAPI, PostgreSQL/PostGIS, job queue | Lightweight, async-capable, strong geospatial extension support | Use a simple queue (RQ/Dramatiq) for long photogrammetry jobs rather than building your own; keep the edge-node SQLite/SpatiaLite schema identical to the central Postgres schema to simplify sync logic |
| **API contract** | OGC API – Features, GeoJSON, OpenAPI | Standards-based; lets QGIS and other GIS tools connect without custom clients; matches DILRMP 3.0's own stated push for API-based integration | Implement only the conformance classes you actually need, not the full OGC spec, to control scope; keep restricted (ownership) data on a clearly separate auth boundary from public geometry/status endpoints |
| **Field app** | Offline-first native or Flutter, SQLite/SpatiaLite, event-sourced sync | Cross-platform, supports Bluetooth pairing with a GNSS rover | Verify Web Bluetooth support before considering a PWA route — native/Flutter is the safer default for rover pairing; check your rover's SDK compatibility with your chosen framework before committing |
| **Sync protocol** | Signed events with base-version checks; conflicts routed to a human | Avoids silent, incorrect auto-merges of legal geometry | Never use CRDT-style auto-merge for geometry; assign each parcel to one surveyor at a time (soft check-out) to reduce conflict volume |
| **Dashboard** | React + MapLibre | No license cost (unlike Mapbox GL), good vector tile support | Keep it minimal for the hackathon timeline — a simple table-plus-map view proves the workflow; skip a full design system |
| **Records & audit** | Append-only versioned table, SHA-256 hash chaining, surveyor signatures | Cheap, defensible, matches the "tamper-evident" claim without overreach | This is explicitly **not** a blockchain — say so directly in the pitch to preempt the obvious skeptical question; a signed append-only log is the honest description |
| **Security** | RBAC, encrypted-at-rest storage, restricted vs public data classes | Matches the "AI proposes, human approves" model | Use a maintained auth library (FastAPI's OAuth2/JWT tooling, or Keycloak) rather than rolling your own session/token logic |

---

## 7. Data sources — full inventory

| Source | Type | Status / access | Use in project | Caveat |
|---|---|---|---|---|
| **Your own drone imagery + RTK checkpoints** (prototype site) | Primary, self-collected | Not yet collected — top priority | Ground truth for `σ_rtk`, `σ_ortho`; core evaluation dataset | Nothing else in this table substitutes for this |
| **Digitized village cadastral map, RoR, FMB** | Government record | Real access unverified; mock data likely necessary | Georeferencing baseline, area/topology comparison | State clearly in the pitch if using mock data |
| **Fields of The World (FTW)**, incl. an India-labeled subset (~10,000 fields from a smallholder-focused study) | Public research dataset | Open, verify license | Fine-tuning the field-boundary extraction model on India-like conditions | Best available direct fit for this problem — prioritize this over generic sets |
| **FBIS-22M** | Public research dataset | Open (Hugging Face), verify license | Large-scale pretraining base for the Delineate Anything-style model | 22.9M instances — plan for subsampling given compute budget |
| **Delineate Anything model weights** | Public pretrained checkpoint | Open, verify commercial/hackathon-use terms | Starting point for fine-tuning rather than training from scratch | Authors' reported accuracy numbers are unverified on your own imagery until tested |
| **AI4Boundaries** | Public EU dataset | Open | Optional cross-domain pretraining only | European domain shift risk — do not present as India-representative |
| **Survey of India CORS network** | Government service, not a dataset | **Resolved:** public self-registration confirmed at `cors.surveyofindia.gov.in`, admin-approved via email | RTK correction source for both rover and drone ground truth | Registration is open to the public; complete it and confirm approval before pitching — turnaround time for a student team is not yet known |
| **Bhunaksha** | Government system | Public web viewer exists; bulk data/API access unclear | Reference for legacy-map georeferencing conventions; eventual export target | Verify actual import/export formats before designing your export module |
| **ULPIN / Bhu-Aadhaar spec** | DoLR concept paper | Publicly described at a high level | Parcel identifier key throughout the system | Verify the exact ID structure/checksum rules before implementing generation logic |
| **SVAMITVA drone imagery** | Government program | No confirmed public bulk download found | Would strengthen realism if accessible | Treat as aspirational; don't assume access |
| **DILRMP 3.0 operational guidelines (full document)** | Government policy document | Only press/PIB coverage confirmed so far; full document not yet fetched | Policy alignment and positioning | Do not quote parcel counts or digitization percentages from secondary sites as government-stated fact until the primary document is checked |
| ~~WHU, SpaceNet, AIRS, Google Open Buildings~~ | Public building-focused datasets | Open | **Not used** in this agricultural version | Kept here only as a note — these were relevant to an earlier vertical/urban building-mapping iteration of the idea, not to field-boundary extraction; do not include them in this pitch |

---

## 8. India-specific innovation layer

- **Presumptive vs conclusive titling** is a long-documented, distinct fact independent of any single scheme: Indian land records are presumptive (rebuttable in court), and government policy since 2008 has aimed at conclusive titling (state-guaranteed, per Torrens-style mirror/curtain/insurance principles).
- **NITI Aayog's 2020 Model Bill on Conclusive Land Titling** proposes the actual mechanism: a Title Registration Officer publishes a **draft title list from existing records** (legal notice) → claimants file **objections within a set period** → TRO verifies → unresolved disputes go to a **Land Dispute Resolution Officer**. Adoption has stalled since 2020 — verify current state-by-state status before citing it as active law anywhere.
- **Map the system onto this pipeline directly:**
  - Your reconciled parcel package = the **draft title candidate**.
  - Add a **notice/objection module** (not yet designed) logging claimant objections as a case type distinct from your own AI/surveyor flags.
  - Your version history + evidence bundle = what an **LDRO case file** would need.
- **DILRMP 3.0** — confirmed via PIB (September 9–10, 2026): ₹565.5 crore, 2026–31, Central Sector Scheme, builds a GIS-enabled "Land Stack" as Digital Public Infrastructure, Universal ULPIN, Registration Seva Kendras, RCCMS, NAKSHA pilot completion, and **explicit API-based integration** to reduce citizen office visits — this directly validates the API-layer design above.
  - **Not confirmed from the primary PIB release**, only from secondary sites: the 40.58 crore parcel figure, 97%/99.90% digitization percentages, the term "Bharat Land Stack," and any explicit conclusive-titling language inside DILRMP 3.0 itself. Do not present these as government-stated facts without checking the actual operational guidelines document.

---

## 9. Brief comparison with other countries

- **Rwanda:** fast, cheap demarcation relied on no legacy cadastre and general/visible boundaries by community consensus. India's problem is the opposite — decades of legacy records plus unrecorded partition inside joint holdings.
- **Tanzania (MAST) and the EU's satellite monitoring:** both validate tiering effort by risk/confidence rather than treating every parcel identically — the basis for this project's decision engine.
- **Brazil (SIGEF):** shows the cost of self-declared boundaries without objective cross-checking — the area-vs-RoR and topology checks here address the same failure mode proactively.

---

## 10. Evaluation plan and prototype scope

- **Scope:** one real site, 10–30 parcels, real drone flight, real RTK checkpoints.
- Since real discrepancies won't naturally occur, **plant known synthetic shifts** (e.g. 0.5 m, 1 m, 2 m) in a copy of the records and label these tests as synthetic.
- **Report:** checkpoint RMSE (horizontal/vertical) with N; conformal band coverage vs RTK truth; false-clear rate with confidence interval; false-flag rate; share of parcels per tier; time/clicks per parcel vs manual delineation.
- **Baseline comparison:** the uncertainty-and-support-ratio rule vs a naive fixed-threshold rule, plus an ablation with/without the support ratio. Report honestly even if the rule doesn't clearly beat the baseline.
- **Offline test:** run the full loop in airplane mode, sync afterward with zero lost events, and force one conflict to show it routes to a human.

---

## 11. What this does not claim

- Legal determination of boundaries — a surveyor, and ultimately the legal titling process, decides that.
- Replacement of Bhunaksha, NAKSHA, or existing state resurvey programs.
- Cost savings or national-scale impact, until measured.
- That DILRMP 3.0 itself states a conclusive-titling objective (unconfirmed from the primary source).

---

## 12. Build order — timeboxed

Adjust the week numbers to your actual submission/prototype window — this assumes a roughly 6-week runway from PPT submission to a working demo.

1. **Weeks 1–2:** Village dataset + georeferencing + decision engine, tested on planted synthetic shifts, with a baseline comparison.
2. **Weeks 3–4:** Real extraction + support ratio, with a calibrated conformal band.
3. **Week 5:** Offline field app with sync, tested under a forced conflict and airplane mode.
4. **Week 6:** Officer dashboard.
5. **Stretch:** API with a second independent client.
6. **Stretch:** DIY rover, benchmarked against a survey-grade one.

---

## 13. To verify before pitching

- ~~CORS access process for students~~ — **resolved**, registration process identified (§6, §7); remaining action: actually complete registration and confirm account approval.
- DPDP obligations for any real personal data used in the prototype.
- Licenses for the field-delineation model and any Indian label datasets (FTW-India, FBIS-22M, Delineate Anything weights).
- Current state-by-state adoption of the Model Bill on Conclusive Land Titling.
- The actual DILRMP 3.0 operational guidelines document (only press coverage checked so far).
- Bhunaksha's real import/export formats.
- Legal acceptance (or lack of it) of phone-based/general-boundary field evidence in Indian resurvey practice.
