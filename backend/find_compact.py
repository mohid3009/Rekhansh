"""One-off: find the most compact connected cluster of 10-30 parcels in
Bond Gavhan (real polygons), so the pilot fits a high-res Esri mosaic."""
import json
import math

from shapely.geometry import shape

d = json.load(open("backend/data/pilot_village_real.geojson"))
feats = d["features"]
geoms = [shape(f["geometry"]) for f in feats]
n = len(feats)
cx = [g.centroid.x for g in geoms]
cy = [g.centroid.y for g in geoms]
LAT0 = sum(cy) / n


def mdist(i, j):
    return math.hypot((cx[i] - cx[j]) * 111320.0 * math.cos(math.radians(LAT0)),
                      (cy[i] - cy[j]) * 110540.0)


def span_of(idxs):
    xs = [cx[i] for i in idxs]
    ys = [cy[i] for i in idxs]
    return max((max(xs) - min(xs)) * 111320.0 * math.cos(math.radians(LAT0)),
               (max(ys) - min(ys)) * 110540.0)


def touches(i, j):
    return geoms[i].touches(geoms[j]) or geoms[i].overlaps(geoms[j])


# greedy growth from every seed, keep connected, target sizes
results = []
for target in (18, 20, 22, 24):
    for s in range(n):
        chosen = [s]
        rest = set(range(n)) - {s}
        while len(chosen) < target and rest:
            # nearest parcel (to cluster) that touches the cluster if possible
            touching = [i for i in rest
                        if any(touches(i, c) for c in chosen)]
            pool = touching or list(rest)
            nxt = min(pool, key=lambda i: min(mdist(i, c) for c in chosen))
            chosen.append(nxt)
            rest.remove(nxt)
        sp = span_of(chosen)
        n_touching_links = sum(1 for a in range(len(chosen))
                               for b in range(a + 1, len(chosen))
                               if touches(chosen[a], chosen[b]))
        results.append((sp, target, s, sorted(chosen), n_touching_links))

results.sort()
print("best 12 (span_m, target, seed, n_links):")
for sp, target, s, chosen, links in results[:12]:
    surveys = sorted(feats[i]["properties"]["survey_no"] for i in chosen)
    areas = [float(feats[i]["properties"]["area_hectares"] or 0)
             for i in chosen]
    lon = sum(cx[i] for i in chosen) / len(chosen)
    lat = sum(cy[i] for i in chosen) / len(chosen)
    print(f"  span={sp:.0f}m target={target} seedparcel={s} links={links} "
          f"@{lat:.5f},{lon:.5f}")
    print(f"    surveys={surveys}")
    print(f"    areas: min={min(areas):.2f} max={max(areas):.2f}")
