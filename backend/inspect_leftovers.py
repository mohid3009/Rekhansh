"""One-off: inspect leftover helper scripts + geojson + nanded fetch state."""
import gzip
import json
from collections import Counter

for name in ("backend/data/pilot_village_raw.json",):
    try:
        with open(name, "rb") as fh:
            raw = fh.read(400)
        print(name, "first bytes:", raw[:60])
        d = json.loads(raw.decode("utf-8", "replace") if False else open(name, encoding="utf-8", errors="replace").read()[:10])
        print("  parsed head ok")
    except Exception as e:
        print(name, "ERR", type(e).__name__, e)

d = json.load(open("backend/data/pilot_village_real.geojson"))
print("geojson n:", len(d["features"]))
c = Counter()
for f in d["features"][:25]:
    p = f["properties"]
    print("  survey=", p.get("survey_no"), "area=", p.get("area_hectares"),
          "geom=", f["geometry"]["type"], "keys=", sorted(p.keys()))
