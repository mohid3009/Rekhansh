"""Hash-chained versions (PRD Module 09): genesis, linkage, tamper detection."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import db
from app.hashchain import canonical_json, compute_record_hash, verify_chain
from app.pipeline.versions import append_version, chain_integrity, versions_for
from shapely.geometry import Polygon, mapping


def sq(off=0.0):
    return mapping(Polygon([(73.9 + off, 19.91), (73.901 + off, 19.91),
                            (73.901 + off, 19.911), (73.9 + off, 19.911)]))


def test_canonical_json_is_key_order_independent():
    assert canonical_json({"b": 1, "a": 2}) == canonical_json({"a": 2, "b": 1})


def test_canonical_json_rounds_floats():
    assert canonical_json({"x": 0.1234567894}) == canonical_json({"x": 0.1234567890})


def test_hash_changes_when_geometry_changes():
    h1 = compute_record_hash("P", 1, sq(), 1.0, "UNVERIFIED", None, None,
                             "t", None)
    h2 = compute_record_hash("P", 1, sq(0.0001), 1.0, "UNVERIFIED", None, None,
                             "t", None)
    assert h1 != h2


def test_chain_append_and_verify():
    db.init_db()
    pid = "TEST-PARCEL-1"
    db.execute("DELETE FROM parcel_versions WHERE parcel_id = ?", (pid,))
    geom = sq()
    append_version(pid, geom, 1.0, "UNVERIFIED", None, None)
    append_version(pid, geom, 1.0, "CONFIRMED", "E1", "ACCEPT")
    append_version(pid, sq(0.0001), 1.01, "CORRECTED", "E1", "CORRECT")
    entries = chain_integrity(pid)
    assert len(entries) == 3
    assert all(e["hash_ok"] and e["chain_verified"] for e in entries)


def test_tampering_breaks_chain_from_that_version_onward():
    db.init_db()
    pid = "TEST-PARCEL-2"
    db.execute("DELETE FROM parcel_versions WHERE parcel_id = ?", (pid,))
    append_version(pid, sq(), 1.0, "UNVERIFIED", None, None)
    append_version(pid, sq(), 1.0, "CONFIRMED", None, "ACCEPT")
    append_version(pid, sq(), 1.0, "CONFIRMED", None, "ACCEPT")
    # tamper with version 2's stored hash (simulates edited history)
    vs = versions_for(pid)
    db.execute("UPDATE parcel_versions SET record_hash = ? WHERE id = ?",
               ("deadbeef", vs[1]["id"]))
    entries = chain_integrity(pid)
    assert entries[0]["hash_ok"] and entries[0]["chain_verified"]
    assert not entries[1]["chain_verified"]     # break detected here...
    assert not entries[2]["chain_verified"]     # ...and propagated forward


def test_previous_hash_links_versions():
    db.init_db()
    pid = "TEST-PARCEL-3"
    db.execute("DELETE FROM parcel_versions WHERE parcel_id = ?", (pid,))
    v1 = append_version(pid, sq(), 1.0, "UNVERIFIED", None, None)
    v2 = append_version(pid, sq(), 1.0, "CONFIRMED", None, "ACCEPT")
    assert v1["previous_version_hash"] is None
    assert v2["previous_version_hash"] == v1["record_hash"]
    assert v2["previous_version_id"] == v1["id"]
