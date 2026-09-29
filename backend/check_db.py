"""One-off: inspect current DB state."""
import sqlite3

c = sqlite3.connect("backend/data/app.db")
print("tables:", [r[0] for r in c.execute("select name from sqlite_master where type='table'")])
print("parcels:", c.execute("select count(*) from parcels").fetchone())
for r in c.execute("select id, survey_number, recorded_area_ha, source from parcels limit 5"):
    print("  parcel:", r)
print("triage:", c.execute("select state, count(*) from triage_decisions group by state").fetchall())
print("ai:", c.execute("select source, count(*) from ai_field_polygons group by source").fetchall())
print("runs:", c.execute("select id, tier, ok from pipeline_runs").fetchall())
