"""One-off: inspect real_parcels bundle + raw pilot files in detail."""
import gzip
import json
from collections import Counter

d = json.load(open("backend/data/real_parcels.json"))
print("keys:", list(d.keys()))
print("n feats:", len(d["features"]))
c = Counter(f["properties"].get("geom_kind") for f in d["features"])
print("geom_kind:", dict(c))
c2 = Counter(f["properties"].get("survey_no") for f in d["features"])
print("survey_nos:", sorted(c2)[:20])
for f in d["features"][:3]:
    g = f["geometry"]
    print(" survey=", f["properties"]["survey_no"],
          "area_ha=", f["properties"]["area_hectares"],
          "geom=", g["type"], "nverts=", len(g["coordinates"][0]),
          "coords0=", [round(v, 6) for v in g["coordinates"][0][0]])
print("meta:", {k: v for k, v in d.items() if k != "features"})

for name in ("backend/data/pilot_village_raw.json", "backend/data/pilot_village_real.geojson"):
    try:
        dd = json.load(open(name))
        print("---", name, "keys:", list(dd.keys()) if isinstance(dd, dict) else type(dd))
        if isinstance(dd, dict):
            for k, v in dd.items():
                if k == "features":
                    print("  n feats:", len(v))
                elif isinstance(v, (str, int, float)):
                    print(f"  {k}: {v}")
                else:
                    print(f"  {k}: {str(v)[:200]}")
    except Exception as e:
        print("---", name, "ERR", e)
