"""SQLite store — single file, geometries as GeoJSON text parsed on read (PRD)."""
from __future__ import annotations

import json
import os
import sqlite3
import threading
from pathlib import Path
from typing import Any, Iterable

from .config import DATA_DIR

DB_PATH = Path(os.environ.get("APP_DB_PATH") or (Path(__file__).resolve().parents[1] / "data" / "app.db"))

_local = threading.local()

SCHEMA = """
CREATE TABLE IF NOT EXISTS villages (
    id TEXT PRIMARY KEY, name TEXT NOT NULL, district TEXT, state TEXT,
    lat REAL, lon REAL, source TEXT, notes TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS parcels (
    id TEXT PRIMARY KEY,
    village_id TEXT NOT NULL,
    survey_number TEXT NOT NULL,
    recorded_area_ha REAL NOT NULL,
    recorded_geometry TEXT NOT NULL,
    ror_owner_name TEXT NOT NULL,
    source TEXT NOT NULL,
    created_at TEXT NOT NULL,
    seed_role TEXT,
    UNIQUE (village_id, survey_number)
);
CREATE TABLE IF NOT EXISTS legacy_maps (
    id TEXT PRIMARY KEY, village_id TEXT NOT NULL, raster_path TEXT NOT NULL,
    georeferenced_path TEXT, control_points TEXT NOT NULL,
    affine_transform TEXT NOT NULL, rmse_m REAL NOT NULL,
    applied_distortion TEXT, created_at TEXT
);
CREATE TABLE IF NOT EXISTS aerial_surveys (
    id TEXT PRIMARY KEY, village_id TEXT NOT NULL, orthomosaic_path TEXT NOT NULL,
    dsm_path TEXT, resolution_cm_per_px REAL NOT NULL, capture_date TEXT NOT NULL,
    checkpoints TEXT NOT NULL, provenance TEXT, bounds TEXT, created_at TEXT
);
CREATE TABLE IF NOT EXISTS ai_field_polygons (
    id TEXT PRIMARY KEY, survey_id TEXT NOT NULL, geometry TEXT NOT NULL,
    confidence REAL NOT NULL, detected_features TEXT NOT NULL, source TEXT NOT NULL,
    evidence_note TEXT,
    created_at TEXT
);
CREATE TABLE IF NOT EXISTS match_results (
    id TEXT PRIMARY KEY, parcel_id TEXT NOT NULL UNIQUE,
    field_polygon_ids TEXT NOT NULL, match_type TEXT NOT NULL,
    match_confidence REAL NOT NULL, created_at TEXT
);
CREATE TABLE IF NOT EXISTS evidence_reports (
    id TEXT PRIMARY KEY, parcel_id TEXT NOT NULL, area_diff_ha REAL NOT NULL,
    area_diff_pct REAL NOT NULL, boundary_displacement_m REAL NOT NULL,
    iou REAL NOT NULL, support_ratio_pct REAL NOT NULL, occlusion_fraction REAL NOT NULL,
    topology_status TEXT NOT NULL, topology_issues TEXT NOT NULL,
    uncertainty_score REAL NOT NULL, evidence_quality TEXT NOT NULL,
    ai_confidence REAL NOT NULL DEFAULT 0,
    computed_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS triage_decisions (
    id TEXT PRIMARY KEY, parcel_id TEXT NOT NULL, state TEXT NOT NULL,
    reason_codes TEXT NOT NULL, evidence_report_id TEXT NOT NULL,
    computed_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS rtk_verifications (
    id TEXT PRIMARY KEY, parcel_id TEXT NOT NULL, checkpoints TEXT NOT NULL,
    observed_error_m REAL NOT NULL, corrected_geometry TEXT,
    surveyor_decision TEXT NOT NULL, surveyor_notes TEXT NOT NULL,
    verified_by TEXT NOT NULL, verified_at TEXT NOT NULL,
    triage_state_at_audit TEXT
);
CREATE TABLE IF NOT EXISTS parcel_versions (
    id TEXT PRIMARY KEY, parcel_id TEXT NOT NULL, version_number INTEGER NOT NULL,
    geometry TEXT NOT NULL, area_ha REAL NOT NULL, verification_status TEXT NOT NULL,
    evidence_report_id TEXT, surveyor_action TEXT, timestamp TEXT NOT NULL,
    previous_version_id TEXT, previous_version_hash TEXT, record_hash TEXT NOT NULL,
    UNIQUE (parcel_id, version_number)
);
CREATE TABLE IF NOT EXISTS pipeline_runs (
    id TEXT PRIMARY KEY, started_at TEXT NOT NULL, finished_at TEXT,
    seed INTEGER, tier TEXT, steps TEXT, notes TEXT DEFAULT '',
    ok INTEGER DEFAULT 1, parcel_count INTEGER
);
CREATE TABLE IF NOT EXISTS village_meta (
    village_id TEXT PRIMARY KEY, seed_examples TEXT, updated_at TEXT,
    seed INTEGER, code_version TEXT, created_at TEXT
);
"""
JSON_COLUMNS: dict[str, set[str]] = {
    "villages": set(),
    "parcels": {"recorded_geometry"},
    "legacy_maps": {"control_points", "affine_transform", "applied_distortion"},
    "aerial_surveys": {"checkpoints", "provenance", "bounds"},
    "ai_field_polygons": {"geometry", "detected_features", "evidence_note"},
    "match_results": {"field_polygon_ids"},
    "evidence_reports": {"topology_issues"},
    "triage_decisions": {"reason_codes"},
    "rtk_verifications": {"checkpoints", "corrected_geometry"},
    "parcel_versions": {"geometry"},
    "pipeline_runs": {"steps"},
    "village_meta": {"seed_examples"},
}



def get_conn() -> sqlite3.Connection:
    conn = getattr(_local, "conn", None)
    if conn is None or getattr(_local, "path", None) != str(DB_PATH):
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(DB_PATH), timeout=30)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        _local.conn = conn
        _local.path = str(DB_PATH)
    return conn


def init_db() -> None:
    conn = get_conn()
    conn.executescript(SCHEMA)
    # Lightweight migration for DBs created before evidence_note existed.
    cols = [r[1] for r in conn.execute("PRAGMA table_info(ai_field_polygons)")]
    if "evidence_note" not in cols:
        conn.execute("ALTER TABLE ai_field_polygons ADD COLUMN evidence_note TEXT")
    conn.commit()
    # forward migrations for databases created by earlier dev builds
    cols = {r["name"] for r in conn.execute("PRAGMA table_info(evidence_reports)")}
    if "ai_confidence" not in cols:
        conn.execute("ALTER TABLE evidence_reports ADD COLUMN ai_confidence "
                     "REAL NOT NULL DEFAULT 0")
    rtk_cols = {r["name"] for r in conn.execute("PRAGMA table_info(rtk_verifications)")}
    if "triage_state_at_audit" not in rtk_cols:
        conn.execute("ALTER TABLE rtk_verifications ADD COLUMN "
                     "triage_state_at_audit TEXT")
    conn.commit()


def _encode(table: str, row: dict[str, Any]) -> dict[str, Any]:
    out = {}
    for k, v in row.items():
        if k in JSON_COLUMNS.get(table, set()) and v is not None and not isinstance(v, str):
            out[k] = json.dumps(v)
        else:
            out[k] = v
    return out


def _decode(table: str, row: sqlite3.Row) -> dict[str, Any]:
    d = dict(row)
    for k in JSON_COLUMNS.get(table, set()):
        if isinstance(d.get(k), str) and d[k]:
            try:
                d[k] = json.loads(d[k])
            except (json.JSONDecodeError, TypeError):
                pass
    return d


def insert(table: str, row: dict[str, Any]) -> None:
    row = _encode(table, row)
    cols = ", ".join(row)
    ph = ", ".join("?" for _ in row)
    conn = get_conn()
    conn.execute(f"INSERT OR REPLACE INTO {table} ({cols}) VALUES ({ph})", tuple(row.values()))
    conn.commit()


def insert_many(table: str, rows: Iterable[dict[str, Any]]) -> None:
    rows = list(rows)
    if not rows:
        return
    # Rows may carry extra keys (e.g. evidence_note on older code paths);
    # restrict to real table columns so mixed-shape batches insert cleanly.
    cols_info = query(f"PRAGMA table_info({table})")
    cols = [r["name"] for r in cols_info] if cols_info else list(rows[0].keys())
    enc = [_encode(table, {k: r.get(k) for k in cols}) for r in rows]
    ph = ", ".join("?" for _ in cols)
    conn = get_conn()
    conn.executemany(f"INSERT OR REPLACE INTO {table} ({', '.join(cols)}) VALUES ({ph})",
                     [tuple(r[k] for k in cols) for r in enc])
    conn.commit()


def select(table: str, order_by: str | None = None, **where: Any) -> list[dict[str, Any]]:
    sql = f"SELECT * FROM {table}"
    args: list[Any] = []
    if where:
        clauses = []
        for k, v in where.items():
            if v is None:
                clauses.append(f"{k} IS NULL")
            elif isinstance(v, (list, tuple, set)):
                clauses.append(f"{k} IN ({', '.join('?' for _ in v)})")
                args.extend(v)
            else:
                clauses.append(f"{k} = ?")
                args.append(v)
        sql += " WHERE " + " AND ".join(clauses)
    if order_by:
        sql += f" ORDER BY {order_by}"
    conn = get_conn()
    return [_decode(table, r) for r in conn.execute(sql, tuple(args)).fetchall()]


def select_one(table: str, **where: Any) -> dict[str, Any] | None:
    rows = select(table, **where)
    return rows[0] if rows else None


def update(table: str, key_col: str, key: Any, values: dict[str, Any]) -> None:
    values = _encode(table, values)
    sets = ", ".join(f"{k} = ?" for k in values)
    conn = get_conn()
    conn.execute(f"UPDATE {table} SET {sets} WHERE {key_col} = ?",
                 tuple(values.values()) + (key,))
    conn.commit()


def execute(sql: str, params: tuple = ()) -> None:
    conn = get_conn()
    conn.execute(sql, params)
    conn.commit()


def query(sql: str, params: tuple = ()) -> list[dict[str, Any]]:
    conn = get_conn()
    return [dict(r) for r in conn.execute(sql, params).fetchall()]


def reset_triage_state() -> None:
    """Clear *current* pipeline state for a re-run (US-6.1).

    Keeps parcels, legacy map, survey, **all** ParcelVersion history, all
    RTKVerification rows and all EvidenceReports (versions link to them by id),
    so a reset never erases prior verifications.
    """
    conn = get_conn()
    for t in ("triage_decisions", "match_results", "ai_field_polygons"):
        conn.execute(f"DELETE FROM {t}")
    conn.commit()


def reset_all() -> None:
    conn = get_conn()
    for t in ("parcel_versions", "rtk_verifications", "triage_decisions", "evidence_reports",
              "match_results", "ai_field_polygons", "aerial_surveys", "legacy_maps",
              "parcels", "village_meta", "villages"):
        conn.execute(f"DELETE FROM {t}")
    conn.commit()
