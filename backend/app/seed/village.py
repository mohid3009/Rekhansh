"""Module 01 — Pilot data ingestion.

Primary path: REAL Bhu-Naksha cadastral parcels for Bond Gavhan village
(`backend/data/pilot_village_real.geojson` — all 30 village parcels, true
survey polygons + survey numbers + declared areas as recorded by the
Maharashtra Department of Land Records; see site.yaml for provenance).
Falls back to the legacy single-file bundle (`real_parcels.json`), then to
the procedural mock generator only if neither vendored file exists.

RoR owner names are MOCK placeholders (Tier A excludes owner data) and the
`source` flag distinguishes IMPORTED (real) from MOCK rows.
"""
from __future__ import annotations

import json
import math
import os

import numpy as np
from shapely.geometry import Polygon, mapping, shape

from ..config import DATA_DIR
from ..geo import make_transformer, make_inverse, polygon_area_ha

_REAL_CACHE: dict | None = None

# Vendored real-parcel files, preferred first.
_REAL_FILES = ("pilot_village_real.geojson", "real_parcels.json")


def real_parcel_bundle() -> dict | None:
    """Load the real-parcel bundle, or None if none was ever fetched."""
    global _REAL_CACHE
    if _REAL_CACHE is not None:
        return _REAL_CACHE
    for name in _REAL_FILES:
        path = DATA_DIR / name
        if not path.exists():
            continue
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, dict) and "features" in data:
            bundle = {"features": data["features"]}
            for k in ("district", "taluka", "village", "village_giscode",
                      "source", "licence", "lon", "lat"):
                if k in data:
                    bundle[k] = data[k]
            feats = bundle["features"]
            if feats:
                p0 = feats[0].get("properties", {})
                bundle.setdefault("district", p0.get("district"))
                bundle.setdefault("taluka", p0.get("taluka"))
                bundle.setdefault("village", p0.get("village"))
                bundle.setdefault(
                    "source",
                    "https://mahabhunakasha.mahabhumi.gov.in/ via "
                    "huggingface.co/datasets/Ashutosh99/"
                    "maharashtra-cadastral-tier-a (Tier A, ODbL-1.0)")
                bundle.setdefault("licence", "ODbL-1.0")
            _REAL_CACHE = bundle
            return _REAL_CACHE
    return None


# MOCK only — clearly labelled as generated, never presented as real RoR data.
_MOCK_GIVEN = ["Ramesh", "Sunita", "Anil", "Vaishali", "Ganesh", "Shalini", "Prakash",
               "Meera", "Dattatray", "Savita", "Iqbal", "Rehana", "Suresh", "Kavita",
               "Balasaheb", "Jyoti", "Vikram", "Pooja", "Nitin", "Anjali"]
_MOCK_FAMILY = ["Jadhav", "Pawar", "Shinde", "Deshmukh", "Kulkarni", "Patil", "More",
                "Bhosale", "Gaikwad", "Chavan", "Joshi", "Shinde", "Sawant", "Rane"]


def _survey_numbers(n: int, rng: np.random.Generator) -> list[str]:
    """Distinct survey numbers in NNN/N convention (no duplicates, US-0.1)."""
    bases = rng.permutation(np.arange(12, 990))[:n]
    subs = rng.integers(1, 9, size=n)
    return [f"{int(b)}/{int(s)}" for b, s in zip(bases, subs)]


def _mock_owner(rng: np.random.Generator) -> str:
    return (f"{_MOCK_GIVEN[int(rng.integers(0, len(_MOCK_GIVEN)))]} "
            f"{_MOCK_FAMILY[int(rng.integers(0, len(_MOCK_FAMILY)))]}")


def real_design(village_id: str) -> tuple[list[dict], list[dict], list[dict]] | None:
    """Return (design_geoms, layout_meta, parcel_meta) from REAL parcels.

    parcel_meta carries survey_number / recorded_area / source per parcel so
    `parcel_rows` uses the real record values instead of inventing them.
    """
    bundle = real_parcel_bundle()
    if not bundle:
        return None
    feats = bundle["features"]
    geoms, meta, pmeta = [], [], []
    for i, f in enumerate(feats):
        g = f["geometry"]
        poly = shape(g)
        if poly.geom_type == "MultiPolygon":
            poly = max(poly.geoms, key=lambda p: p.area)
        if not poly.is_valid:
            poly = poly.buffer(0)
        props = f["properties"]
        try:
            area_ha = float(props.get("area_hectares") or 0) or None
        except (TypeError, ValueError):
            area_ha = None
        geoms.append(mapping(poly))
        meta.append({"row": 0, "col": i, "index": i,
                     "plotid": props.get("plotid"),
                     "village_giscode": props.get("village_giscode")})
        pmeta.append({
            "survey_number": str(props.get("survey_no") or f"REAL/{i + 1}"),
            "recorded_area_ha": (round(area_ha, 4) if area_ha
                                 # declared area absent/zero (e.g. survey 24): fall back
                                 # to the geometry's own projected area so the
                                 # record stays usable
                                 else round(polygon_area_ha(mapping(poly)), 4)),
            "source": "IMPORTED",
        })
    return geoms, meta, pmeta


def generate_design(
    lat: float,
    lon: float,
    parcel_count: int,
    seed: int,
    target_area_ha: float = 0.62,
) -> tuple[list[dict], list[dict]]:
    """Return (design_geoms WGS84, layout_meta) for `parcel_count` parcels.

    A jittered lattice keeps neighbouring cells contiguous (no accidental
    overlaps/gaps) while producing organic, non-rectangular polygons.
    """
    rng = np.random.default_rng(seed)
    cols = max(3, int(round(math.sqrt(parcel_count * 1.15))))
    rows = int(math.ceil(parcel_count / cols))

    fwd = make_transformer(lon, lat)
    inv = make_inverse(lon, lat)

    cell = math.sqrt(parcel_count * target_area_ha * 10_000.0) / math.sqrt(cols * rows)
    # lattice in local metres centred on the site
    lat_span_m = rows * cell * 1.18
    lon_span_m = cols * cell * 1.18
    xs = np.linspace(-lon_span_m / 2, lon_span_m / 2, cols + 1)
    ys = np.linspace(-lat_span_m / 2, lat_span_m / 2, rows + 1)
    X, Y = np.meshgrid(xs, ys)
    jitter_sd = cell * 0.16
    Xj = X + rng.normal(0, jitter_sd, X.shape) * 0.9
    Yj = Y + rng.normal(0, jitter_sd, Y.shape) * 0.9
    # keep the outer boundary convex-ish so the block stays coherent
    Xj[0, :], Xj[-1, :] = X[0, :], X[-1, :]
    Xj[:, 0], Xj[:, -1] = X[:, 0], X[:, -1]
    Yj[0, :], Yj[-1, :] = Y[0, :], Y[-1, :]
    Yj[:, 0], Yj[:, -1] = Y[:, 0], Y[:, -1]

    # midpoint jitter is shared per lattice *edge*, so neighbouring cells keep
    # exactly matching boundaries (no accidental sliver overlaps; the only
    # overlap in the dataset is the deliberate topology-demo one)
    mid_cache: dict[tuple, tuple] = {}

    def edge_mid(p1, p2):
        key = tuple(sorted((tuple(np.round(p1, 6)), tuple(np.round(p2, 6)))))
        if key not in mid_cache:
            mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
            mid_cache[key] = (float(mx + rng.normal(0, cell * 0.05)),
                              float(my + rng.normal(0, cell * 0.05)))
        return mid_cache[key]

    site_x, site_y = fwd.transform(lon, lat)
    geoms: list[dict] = []
    meta: list[dict] = []
    idx = 0
    for r in range(rows):
        for c in range(cols):
            if idx >= parcel_count:
                break
            corners = [(Xj[r, c], Yj[r, c]), (Xj[r, c + 1], Yj[r, c + 1]),
                       (Xj[r + 1, c + 1], Yj[r + 1, c + 1]), (Xj[r + 1, c], Yj[r + 1, c])]
            ring = []
            for i in range(4):
                p1, p2 = corners[i], corners[(i + 1) % 4]
                ring.append((float(p1[0]), float(p1[1])))
                ring.append(edge_mid(p1, p2))
            ring_m = np.array(ring)
            lonlons, lats = inv.transform(site_x + ring_m[:, 0], site_y + ring_m[:, 1])
            poly = Polygon(np.column_stack([lonlons, lats]))
            if not poly.is_valid:
                poly = poly.buffer(0)
            geoms.append(mapping(poly))
            meta.append({"row": r, "col": c, "index": idx})
            idx += 1
        if idx >= parcel_count:
            break

    return geoms, meta


def parcel_rows(
    geoms: list[dict],
    village_id: str,
    seed: int,
    created_at: str,
    parcel_meta: list[dict] | None = None,
) -> list[dict]:
    """Turn georeferenced geometries into Parcel rows.

    With real parcels, survey numbers / recorded areas / source come from the
    Bhu-Naksha record (parcel_meta); otherwise they are generated as mock
    data. Owner names are always MOCK placeholders in this prototype.
    """
    rng = np.random.default_rng(seed + 7)
    numbers = _survey_numbers(len(geoms), rng)
    rows = []
    for i, g in enumerate(geoms):
        meta = parcel_meta[i] if parcel_meta and i < len(parcel_meta) else {}
        area = meta.get("recorded_area_ha") or round(polygon_area_ha(g), 4)
        rows.append({
            "id": f"PAR-{village_id}-{i + 1:03d}",
            "village_id": village_id,
            "survey_number": meta.get("survey_number") or numbers[i],
            "recorded_area_ha": area,
            "recorded_geometry": g,
            "ror_owner_name": _mock_owner(rng),
            "source": meta.get("source") or "MOCK",
            "created_at": created_at,
        })
    return rows


def adjacency(geoms: list[dict], tol_m: float = 6.0) -> list[list[int]]:
    """Indices of parcels touching each parcel (by shared boundary proximity)."""
    fwd = None
    from shapely.ops import transform as sh_transform
    from ..geo import make_transformer
    from shapely.geometry import shape as sh_shape
    c = sh_shape(geoms[0]).centroid
    fwd = make_transformer(c.x, c.y)
    proj = [sh_transform(lambda x, y, z=None: fwd.transform(x, y), sh_shape(g)) for g in geoms]
    out = []
    for i, gi in enumerate(proj):
        nb = []
        for j, gj in enumerate(proj):
            if i == j:
                continue
            if gi.buffer(tol_m).intersects(gj):
                nb.append(j)
        out.append(nb)
    return out
