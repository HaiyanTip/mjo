#!/usr/bin/env python3
"""Fetch the BoM RMM index and write mjo.json for the MJO monitor."""
import json, urllib.request

URLS = [
    "https://www.bom.gov.au/clim_data/IDCKGEM000/rmm.74toRealtime.txt",
    "http://www.bom.gov.au/climate/mjo/graphics/rmm.74toRealtime.txt",
]
raw = None
for url in URLS:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (mjo-monitor)"})
        raw = urllib.request.urlopen(req, timeout=60).read().decode("latin-1")
        print("fetched", url)
        break
    except Exception as e:
        print("failed", url, e)
if raw is None:
    raise SystemExit("All BoM URLs failed")

rows = []
for ln in raw.splitlines():
    p = ln.split()
    if len(p) < 5:
        continue
    try:
        y, m, d = int(p[0]), int(p[1]), int(p[2])
        r1, r2 = float(p[3]), float(p[4])
    except ValueError:
        continue  # header lines
    if abs(r1) >= 1e30 or abs(r2) >= 1e30:
        continue  # missing value (1.E36)
    rows.append([f"{y:04d}-{m:02d}-{d:02d}", round(r1, 3), round(r2, 3)])

if len(rows) < 10000:
    raise SystemExit(f"Only {len(rows)} rows parsed, aborting")
with open("mjo.json", "w") as f:
    json.dump({"updated": rows[-1][0], "source": "BoM RMM", "data": rows}, f, separators=(",", ":"))
print(len(rows), "rows, last", rows[-1])
