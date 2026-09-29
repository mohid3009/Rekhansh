"""One-off scan: find compact 10-30 field clusters in each real dataset."""
import math
import random

import numpy as np
import pyarrow.parquet as pq
import shapely

random.seed(0)

SPECS = [
    ("backend/data/india_fields_2016.parquet", ["area", "geometry"]),
    ("backend/data/IN_GA.parquet", ["metrics:area", "bbox", "geometry"]),
]

for name, cols in SPECS:
    print("====", name)
    t = pq.read_table(name, columns=cols)
    n = t.num_rows
    idx = random.sample(range(n), min(n, 6000))
    if "bbox" in cols:
        bl = t.column("bbox").to_pylist()
        cx = np.array([(bl[i]["xmin"] + bl[i]["xmax"]) / 2 for i in idx])
        cy = np.array([(bl[i]["ymin"] + bl[i]["ymax"]) / 2 for i in idx])
        ar = np.array(t.column("metrics:area").to_pylist(), dtype=float)[idx]
    else:
        wl = t.column("geometry").to_pylist()
        gl = [shapely.from_wkb(wl[i]) for i in idx]
        cx = np.array([g.centroid.x for g in gl])
        cy = np.array([g.centroid.y for g in gl])
        ar = np.array(t.column("area").to_pylist(), dtype=float)[idx]
    print("lon range", round(cx.min(), 3), round(cx.max(), 3),
          "lat range", round(cy.min(), 3), round(cy.max(), 3))
    print("area m2 median/p90", round(float(np.median(ar)), 0),
          round(float(np.percentile(ar, 90)), 0))
    pts = list(zip(cx.tolist(), cy.tolist()))
    best = []
    for k in random.sample(range(len(pts)), min(len(pts), 400)):
        lon0, lat0 = pts[k]
        dx = (cx - lon0) * 111320.0 * math.cos(math.radians(lat0))
        dy = (cy - lat0) * 110540.0
        nb = np.where(dx * dx + dy * dy <= 260.0 ** 2)[0]
        if 10 <= len(nb) <= 30:
            span = max((cy[nb].max() - cy[nb].min()) * 110540.0,
                       (cx[nb].max() - cx[nb].min()) * 111320.0
                       * math.cos(math.radians(lat0)))
            best.append((len(nb), round(float(np.median(ar[nb])), 0),
                         int(span), round(lon0, 5), round(lat0, 5)))
    best.sort(reverse=True)
    print("clusters10-30 found:", len(best))
    for b in best[:12]:
        print("  n=%d medArea=%dm2 span=%dm @ %.5f,%.5f" % b)
