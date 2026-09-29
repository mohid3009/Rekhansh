"""Module 09 — append-only, hash-chained parcel versions (US-6.1, US-5.3)."""
from __future__ import annotations

from datetime import datetime, timezone

from .. import db
from ..hashchain import compute_record_hash, verify_chain


def versions_for(parcel_id: str) -> list[dict]:
    return db.select("parcel_versions", order_by="version_number",
                     parcel_id=parcel_id)


def latest_version(parcel_id: str) -> dict:
    vs = versions_for(parcel_id)
    if not vs:
        raise LookupError(f"no versions for {parcel_id}")
    return vs[-1]


def current_geometry(parcel_id: str) -> dict:
    return latest_version(parcel_id)["geometry"]


def append_version(parcel_id: str, geometry: dict, area_ha: float,
                   verification_status: str, evidence_report_id: str | None,
                   surveyor_action: str | None) -> dict:
    """Append the next immutable version; hash links it to its predecessor."""
    vs = versions_for(parcel_id)
    prev = vs[-1] if vs else None
    ts = datetime.now(timezone.utc).isoformat(timespec="microseconds")
    rec = compute_record_hash(
        parcel_id, len(vs) + 1, geometry, area_ha, verification_status,
        evidence_report_id, surveyor_action, ts,
        prev["record_hash"] if prev else None,
    )
    row = {
        "id": f"VER-{parcel_id}-{len(vs) + 1:04d}",
        "parcel_id": parcel_id,
        "version_number": len(vs) + 1,
        "geometry": geometry,
        "area_ha": area_ha,
        "verification_status": verification_status,
        "evidence_report_id": evidence_report_id,
        "surveyor_action": surveyor_action,
        "timestamp": ts,
        "previous_version_id": prev["id"] if prev else None,
        "previous_version_hash": prev["record_hash"] if prev else None,
        "record_hash": rec,
    }
    db.insert("parcel_versions", row)
    return row


def create_genesis(parcels: list[dict]) -> None:
    """V1 for every parcel at seed time (UNVERIFIED, geometry = recorded)."""
    for p in parcels:
        append_version(p["id"], p["recorded_geometry"], p["recorded_area_ha"],
                       "UNVERIFIED", None, None)


def chain_integrity(parcel_id: str) -> list[dict]:
    return verify_chain(versions_for(parcel_id))
