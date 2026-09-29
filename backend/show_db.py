"""One-off: show which DB file is live + village/meta/parcel counts."""
import sys

sys.path.insert(0, "backend")
from app import db  # noqa: E402

print("DB_PATH:", db.DB_PATH)
print("villages:", db.select("villages"))
print("meta:", db.select("village_meta"))
rows = db.select("parcels", order_by="id")
print("n parcels:", len(rows))
for r in rows[:35]:
    print(" ", r["id"], r["survey_number"], r["source"], r["recorded_area_ha"])
