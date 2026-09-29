"""FastAPI entrypoint — serves the JSON API and the static imagery/scan files.

On boot: initialise the DB, seed the pilot village if empty (uses vendored
imagery; network only needed on a true first boot), and run the pipeline once
if no triage state exists, so a fresh clone works with zero extra setup (US-9.2).
"""
from __future__ import annotations

import os
import threading

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .api.routes import router
from .config import DATA_DIR
from . import db

app = FastAPI(
    title="Rural Land Resurvey Triage API",
    version="0.1.0",
    description="Prototype triage API (PRD-assigned backend: FastAPI + SQLite).",
)

origins = os.environ.get("CORS_ORIGINS", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in origins.split(",")] if origins != "*" else ["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")
DATA_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(DATA_DIR)), name="static")


def _bootstrap() -> None:
    from .pipeline.runner import ensure_seeded, run_full
    db.init_db()
    ensure_seeded()
    if not db.select("triage_decisions"):
        run_full()


@app.on_event("startup")
def startup() -> None:
    # background so the API answers /api/meta immediately on slow first boot
    threading.Thread(target=_bootstrap, daemon=True).start()


@app.get("/health")
def health():
    return {"ok": True, "data_dir": str(DATA_DIR)}
