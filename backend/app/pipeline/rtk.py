"""Module 08 — manual RTK verification (primary decision path).

Submitting a verification appends an RTKVerification row AND a new immutable
ParcelVersion (CONFIRMED / CORRECTED / ESCALATED per US-4.3). `observed_error_m`
is the ASBD between the pre-verification record and the corrected geometry; it
is 0 when the surveyor accepts without correction (US-4.1: computed once a
corrected geometry exists).
"""
from __future__ import annotations

from datetime import datetime, timezone

import numpy as np

from .. import db
from ..config import load_triage_config
from ..geo import boundary_displacement_m, geom_of, make_transformer, polygon_area_ha
from .versions import append_version, latest_version


def submit_verification(
    parcel_id: str,
    decision: str,
    notes: str,
    verified_by: str,
    corrected_geometry: dict | None = None,
    checkpoints: list[dict] | None = None,
) -> dict:
    if decision not in ("ACCEPT", "CORRECT", "REJECT"):
        raise ValueError("decision must be ACCEPT, CORRECT or REJECT")
    if decision == "CORRECT" and not corrected_geometry:
        raise ValueError("CORRECT requires a corrected geometry")
    if corrected_geometry is not None and not geom_of(corrected_geometry).is_valid:
        raise ValueError("corrected geometry must be a valid polygon")

    prev = latest_version(parcel_id)
    prev_geom = prev["geometry"]

    observed_error_m = 0.0
    new_geom = prev_geom
    status = {"ACCEPT": "CONFIRMED", "CORRECT": "CORRECTED", "REJECT": "ESCALATED"}[decision]
    if corrected_geometry is not None:
        fwd = make_transformer(geom_of(prev_geom).centroid.x, geom_of(prev_geom).centroid.y)
        observed_error_m = round(boundary_displacement_m(
            prev_geom, corrected_geometry, fwd,
            load_triage_config().boundary.SAMPLE_INTERVAL_M), 3)
        new_geom = corrected_geometry

    evidence = db.select_one("triage_decisions", parcel_id=parcel_id)
    triage_at_audit = evidence["state"] if evidence else None
    evidence_report_id = evidence["evidence_report_id"] if evidence else None

    new_area = round(polygon_area_ha(new_geom), 4)
    ts = datetime.now(timezone.utc).isoformat(timespec="microseconds")
    row = {
        "id": f"RTK-{parcel_id}-{ts.replace(':', '').replace('-', '').replace('+0000', 'Z')}"
              f"-{decision}",
        "parcel_id": parcel_id,
        "checkpoints": checkpoints or [],
        "observed_error_m": observed_error_m,
        "corrected_geometry": corrected_geometry,
        "surveyor_decision": decision,
        "surveyor_notes": notes,
        "verified_by": verified_by,
        "verified_at": ts,
        "triage_state_at_audit": triage_at_audit,
    }
    db.insert("rtk_verifications", row)
    v = append_version(parcel_id, new_geom, new_area, status,
                       evidence_report_id, decision)
    row["version_id"] = v["id"]
    return row


def verifications_for(parcel_id: str) -> list[dict]:
    return db.select("rtk_verifications", order_by="verified_at", parcel_id=parcel_id)
