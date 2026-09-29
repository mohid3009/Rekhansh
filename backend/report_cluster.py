"""One-off: area/validity/contiguity report for the Bond Gavhan 25-parcel cluster."""
import json

from shapely.geometry import shape

d = json.load(open("backend/data/pilot_village_real.geojson"))
feats = d["features"]
print("n:", len(feats))
geoms = [shape(f["geometry"]) for f in feats]
print("all valid:", all(g.is_valid for g in geoms))
print("types:", sorted(set(g.geom_type for g in geoms)))
xs = [c[0] for g in geoms for c in g.exterior.coords]
ys = [c[1] for g in geoms for c in g.exterior.coords]
print("bbox lon [%.5f, %.5f] lat [%.5f, %.5f]" % (min(xs), max(xs), min(ys), max(ys)))
print("span: %.0fm x %.0fm" % ((max(xs) - min(xs)) * 105000, (max(ys) - min(ys)) * 110600))
print("centroid: %.5f, %.5f" % (sum(ys) / len(ys), sum(xs) / len(xs)))
n_touch = sum(1 for i in range(len(geoms)) for j in range(i + 1, len(geoms))
              if geoms[i].touches(geoms[j]))
n_over = sum(1 for i in range(len(geoms)) for j in range(i + 1, len(geoms))
             if geoms[i].overlaps(geoms[j]))
print("touching pairs: %d  overlapping pairs: %d" % (n_touch, n_over))
areas = sorted(f["properties"]["area_hectares"] for f in feats)
print("recorded area_ha min/med/max: %.2f / %.2f / %.2f" % (areas[0], areas[len(areas) // 2], areas[-1]))
print("survey_nos:", sorted(f["properties"]["survey_no"] for f in feats)[:30])
