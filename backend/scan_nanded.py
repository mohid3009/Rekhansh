"""Scan Nanded cadastral file progressively: village list WITHOUT loading
geometry into memory. Reads the gz file as raw text in chunks and extracts
only property fields (streaming regex over village/taluka/survey_no/geom_kind)
so RAM stays flat. Prints per-(taluka, village) parcel counts + geometry kinds,
then the best 10-30 parcel polygon villages for the pilot."""
import gzip
import json
import re
import sys
from collections import defaultdict

PATH = "backend/data/nanded.geojson.gz"

# Each feature: "properties": {...}, "geometry": {...}. We only need props.
# Stream the decompressed text in chunks, splitting on '"properties"' tokens
# is overkill; instead match per-feature property dicts with a regex over a
# rolling buffer.
PROP_RE = re.compile(
    r'"taluka"\s*:\s*"([^"]*)".*?"village"\s*:\s*"([^"]*)"'
    r'.*?"village_giscode"\s*:\s*"([^"]*)".*?"survey_no"\s*:\s*"([^"]*)"'
    r'.*?"geom_kind"\s*:\s*"([^"]*)"'
)

counts = defaultdict(int)
polys = defaultdict(int)
examples = {}
features = 0
buf = ""
CH = 8 * 1024 * 1024
with gzip.open(PATH, "rt", encoding="utf-8") as fh:
    while True:
        chunk = fh.read(CH)
        if not chunk:
            break
        buf += chunk
        # process all complete matches, keep tail (a feature may straddle)
        matches = list(PROP_RE.finditer(buf))
        if matches:
            last_end = 0
            for m in matches:
                # avoid partial match at very end of buffer when more data coming
                last_end = m.end()
                taluka, village, gis, survey, kind = m.groups()
                key = (taluka, village, gis)
                counts[key] += 1
                if kind == "polygon":
                    polys[key] += 1
                if key not in examples:
                    examples[key] = survey
                features += 1
            buf = buf[last_end:]
        else:
            buf = buf[-2000:]  # keep overlap
        print(f"  ... {features} features scanned", end="\r")
# final pass on remainder
for m in PROP_RE.finditer(buf):
    taluka, village, gis, survey, kind = m.groups()
    key = (taluka, village, gis)
    counts[key] += 1
    if kind == "polygon":
        polys[key] += 1
    if key not in examples:
        examples[key] = survey
    features += 1

print(f"\nfeatures scanned: {features}, villages: {len(counts)}")
# candidate villages: 10..40 parcels (allow trimming to 10-30 later)
cands = [(k, counts[k], polys[k]) for k in counts
         if 10 <= counts[k] <= 40 and polys[k] >= 8]
cands.sort(key=lambda t: (-t[2], t[1]))
print(f"candidate villages (10-40 parcels, >=8 polygons): {len(cands)}")
for (tal, vil, gis), n, p in cands[:25]:
    print(f"  {tal} / {vil} (gis={gis}): parcels={n} polygons={p} "
          f"ex_survey={examples[(tal, vil, gis)]}")
# also: polygon coverage overall + taluka totals
tot_poly = sum(polys.values())
print(f"total polygon-geom parcels: {tot_poly} / {features}")
tal_tot = defaultdict(lambda: [0, 0])
for (tal, vil, gis), n in counts.items():
    tal_tot[tal][0] += n
    tal_tot[tal][1] += polys[(tal, vil, gis)]
for tal in sorted(tal_tot):
    print(f"  taluka {tal}: parcels={tal_tot[tal][0]} polygons={tal_tot[tal][1]}")
