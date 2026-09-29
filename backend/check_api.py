"""Smoke-check the API payloads the UI reads (no server needed).

`python backend/check_api.py` prints the village summary, then — for the
designed edge-case parcels (SPLIT / MERGE / NO_MATCH) plus one CLEARED and one
FLAGGED parcel — the guided polygons with their `evidence_note` provenance and
the reconciliation metrics the Evidence screen shows, so the exact JSON the
frontend fetches can be eyeballed right after a reseed.
"""
import json
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")           # httpx/starlette deprecation notice

sys.path.insert(0, str(Path(__file__).resolve().parent))

from fastapi.testclient import TestClient   # noqa: E402

from app.main import app                    # noqa: E402

METRICS = ("area_diff_pct", "boundary_displacement_m", "support_ratio_pct",
           "ai_confidence", "occlusion_fraction", "uncertainty_score",
           "evidence_quality", "iou")


def show(c, row: dict, label: str) -> None:
    pid = row["id"]
    comp = c.get(f"/api/parcels/{pid}/comparison").json()
    ev = c.get(f"/api/parcels/{pid}/evidence").json()
    match = comp.get("match") or {}
    print(f"\n=== {pid} [{label}] survey={row.get('survey_number')} "
          f"triage={row.get('triage_state')}")
    print(f"  match={match.get('match_type') or row.get('match_type')} "
          f"conf={match.get('match_confidence', row.get('match_confidence'))}")
    for a in comp.get("ai_polygons", []):
        print(f"  poly {a['id']} src={a.get('source')} conf={a.get('confidence')}")
        if a.get("evidence_note"):
            print(f"    note: {a['evidence_note']}")
    print("  metrics: " + json.dumps({k: ev.get("evidence", {}).get(k) for k in METRICS
                                      if k in ev.get("evidence", {})}, default=str))
    print("  reasons: " + json.dumps(ev.get("reasons"), default=str))


c = TestClient(app)
vids = c.get("/api/villages").json()
vid = vids[0]["id"] if isinstance(vids, list) else vids["villages"][0]["id"]
summary = c.get(f"/api/villages/{vid}/summary").json()
print(f"village: {vid}  parcels: {summary['parcel_count']}")
print(f"  counts: {summary['counts']}")

parcels = c.get(f"/api/villages/{vid}/parcels").json()
if isinstance(parcels, dict):
    parcels = parcels.get("parcels", [])
print(f"  {len(parcels)} parcels, keys: {sorted(parcels[0]) if parcels else '-'}")

for p in parcels:
    if p.get("match_type") not in (None, "ONE_TO_ONE"):
        show(c, p, p["match_type"])
for state in ("CLEARED", "FLAGGED"):
    hit = next((p for p in parcels if p.get("triage_state") == state), None)
    if hit:
        show(c, hit, state)

