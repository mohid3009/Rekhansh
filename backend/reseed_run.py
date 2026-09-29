"""One-off: reseed + run pipeline, print village/parcel/meta summary."""
import sys

sys.path.insert(0, "backend")
from app import db  # noqa: E402
from app.pipeline.runner import ensure_seeded, run_full  # noqa: E402

db.init_db()
v = ensure_seeded()
print("village", v["name"], v["lat"], v["lon"], v["source"])
print("n parcels", len(db.select("parcels")))
print("meta", db.select_one("village_meta", village_id="VIL-PILOT"))
import json  # noqa: E402

print(json.load(open("backend/data/imagery/VIL-PILOT_ortho.json")))
r = run_full()
print("tier", r["tier"], "outcomes", r["outcomes"])
for s in r["steps"]:
    print(" ", {k: val for k, val in s.items()})
