"""Fetch real field boundaries (Fields of the World Global, CC-BY-4.0) and pick
a compact 10-30 field cluster for the pilot village."""
import numpy as np
import pyarrow.parquet as pq
import requests
import shapely

URL = ("https://data.source.coop/ftw/global-data/predictions/vectors/alpha/"
       "results-by-admin-conf/admin:country_code=IN/IN_GA.parquet")
r = requests.get(URL, timeout=180)
print("download:", r.status_code, len(r.content), "bytes")
open("backend/data/IN_GA.parquet", "wb").write(r.content)

t = pq.read_table("backend/data/IN_GA.parquet")
print("fields:", t.num_rows, "columns:", t.schema.names)

conf = t["confidence"].to_pylist()
areas = t["metrics:area"].to_pylist()
geoms = [shapely.from_wkb(w) for w in t["geometry"].to_pylist()]
keep = [i for i, g in enumerate(geoms)
        if g is not None and g.geom_type == "Polygon" and g.is_valid]
geoms = [geoms[i] for i in keep]
areas = [areas[i] for i in keep]
conf = [conf[i] for i in keep]
cents = np.array([(g.centroid.x, g.centroid.y) for g in geoms], dtype=float)
cent_lon, cent_lat = cents[:, 0], cents[:, 1]
cs = [c for c in conf if c is not None]
print("valid polygons:", len(geoms), "conf:", min(cs), "-", max(cs))

# full pairwise cluster scan (Goa partition is small enough)
dy = cent_lat[:, None] - cent_lat[None, :]
dxm = (cent_lon[:, None] - cent_lon[None, :]) * 111_320.0 * np.cos(
    np.radians(cent_lat[:, None]))
dist2 = dxm * dxm + dy * dy

R = 400.0
counts = (dist2 <= R ** 2).sum(axis=1)
printed = 0
for j in np.argsort(-counts):
    n = int(counts[j])
    if n < 10 or n > 30:
        continue
    nb = np.where(dist2[j] <= R ** 2)[0]
    bs = [geoms[k].bounds for k in nb]
    span = max((max(b[3] for b in bs) - min(b[1] for b in bs)) * 110_540.0,
               (max(b[2] for b in bs) - min(b[0] for b in bs)) * 111_320.0
               * np.cos(np.radians(cent_lat[j])))
    sizes = [(areas[k] or 0) / 10_000.0 for k in nb]
    print(f"candidate ({cent_lat[j]:.5f},{cent_lon[j]:.5f}) n={n} span={int(span)}m "
          f"areas_ha={sorted(round(a, 3) for a in sizes)}")
    printed += 1
    if printed >= 15:
        break
