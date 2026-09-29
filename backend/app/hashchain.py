"""Hash-chained parcel versions (PRD Module 09).

record_hash = SHA256(canonical_json({
    parcel_id, version_number, geometry, area_ha, verification_status,
    evidence_report_id, surveyor_action, timestamp, previous_version_hash }))
V1.previous_version_hash = null (genesis). Not a blockchain — a lightweight,
adequate-for-scope chained hash. Any edit to history breaks the chain visibly.
"""
from __future__ import annotations

import hashlib
import json
from typing import Optional


def _canonical(obj, depth: int = 0):
    """Deterministic canonicalisation: sorted keys, fixed separators, floats
    rounded to 9 decimals (~0.1 mm) so float text round-trips can't desync."""
    if depth > 12:
        raise ValueError("canonicalisation depth exceeded")
    if isinstance(obj, dict):
        return {k: _canonical(v, depth + 1) for k, v in sorted(obj.items())}
    if isinstance(obj, (list, tuple)):
        return [_canonical(v, depth + 1) for v in obj]
    if isinstance(obj, bool) or obj is None or isinstance(obj, (int, str)):
        return obj
    if isinstance(obj, float):
        return round(obj, 9)
    return str(obj)


def canonical_json(payload: dict) -> str:
    return json.dumps(_canonical(payload), sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False)


def compute_record_hash(
    parcel_id: str,
    version_number: int,
    geometry: dict,
    area_ha: float,
    verification_status: str,
    evidence_report_id: Optional[str],
    surveyor_action: Optional[str],
    timestamp: str,
    previous_version_hash: Optional[str],
) -> str:
    payload = {
        "parcel_id": parcel_id,
        "version_number": version_number,
        "geometry": geometry,
        "area_ha": area_ha,
        "verification_status": verification_status,
        "evidence_report_id": evidence_report_id,
        "surveyor_action": surveyor_action,
        "timestamp": timestamp,
        "previous_version_hash": previous_version_hash,
    }
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def verify_chain(versions: list[dict]) -> list[dict]:
    """Recompute every version's hash and chain linkage.

    `versions` must be ordered oldest -> newest with stored fields:
    parcel_id, version_number, geometry, area_ha, verification_status,
    evidence_report_id, surveyor_action, timestamp, previous_version_hash,
    record_hash.

    Returns per-version integrity entries. Once a break is found, every later
    version is flagged too (US-5.3), not just the one that changed.
    """
    broken_from: Optional[int] = None
    entries = []
    for i, v in enumerate(versions):
        recomputed = compute_record_hash(
            v["parcel_id"], v["version_number"], v["geometry"], v["area_ha"],
            v["verification_status"], v["evidence_report_id"], v["surveyor_action"],
            v["timestamp"], v["previous_version_hash"],
        )
        link_ok = True
        if i == 0:
            link_ok = v["previous_version_hash"] is None
        else:
            link_ok = v["previous_version_hash"] == versions[i - 1]["record_hash"]
        hash_ok = recomputed == v["record_hash"]
        if broken_from is None and not (hash_ok and link_ok):
            broken_from = i
        entries.append({
            "version_number": v["version_number"],
            "hash_ok": hash_ok and link_ok,
            "chain_verified": broken_from is None,
            "recomputed_hash": recomputed,
        })
    return entries
