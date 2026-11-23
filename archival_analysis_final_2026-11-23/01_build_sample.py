"""Step 1 (from raw). Restaurant sample: Mediterranean-first and ME-first restaurants from the master frame, plus American-first benchmarks.

Usage: python 01_build_sample.py <project root>
Reads:  analysis/2025-08-18-rohan/categorized output/all-states.csv   (businesses with a hummus or baba mention in any review)
        data/Google Reviews/Meta_data_combined.csv                    (all businesses; first category "American restaurant")
Writes: built/sample_restaurants.csv
"""
import sys, re, csv, ast, pathlib
import pandas as pd
from common import BUILT, ME_NATIONAL, ME_ORIGINAL

ROOT = pathlib.Path(sys.argv[1])
BUILT.mkdir(exist_ok=True)
m = pd.read_csv(ROOT / "analysis/2025-08-18-rohan/categorized output/all-states.csv", low_memory=False)
assert m.gmap_id.is_unique
first = m.category.fillna("").str.strip().str.lower()
m["med_first"] = first.str.contains("mediterranean")
m["me_national"] = first.str.contains(ME_NATIONAL) & ~m.med_first
m["me_original"] = first.isin(ME_ORIGINAL)
m["baba"] = m.review_baba.eq(1)
m["wpme"] = m.med_first & m.baba
m["american"] = False
cols = ["gmap_id", "latitude", "longitude", "first_category", "med_first", "baba", "wpme", "me_national", "me_original", "american"]
keep = m[m.med_first | m.me_national | m.me_original].rename(columns={"category": "first_category"})[cols]

csv.field_size_limit(2**31 - 1)
seen, rows = set(keep.gmap_id), []
with open(ROOT / "data/Google Reviews/Meta_data_combined.csv", newline="", encoding="utf-8", errors="replace") as fh:
    rd = csv.reader(fh)
    head = next(rd)
    ix = {k: head.index(k) for k in ["gmap_id", "latitude", "longitude", "category"]}
    for row in rd:
        if len(row) <= ix["category"] or "merican" not in row[ix["category"]]:
            continue
        try:
            lst = ast.literal_eval(row[ix["category"]])
        except Exception:
            continue
        if lst and str(lst[0]).strip().lower() == "american restaurant" and row[ix["gmap_id"]] not in seen:
            seen.add(row[ix["gmap_id"]])
            rows.append(dict(gmap_id=row[ix["gmap_id"]], latitude=row[ix["latitude"]], longitude=row[ix["longitude"]], first_category="American restaurant",
                             med_first=False, baba=False, wpme=False, me_national=False, me_original=False, american=True))
out = pd.concat([keep, pd.DataFrame(rows)[cols]], ignore_index=True)
out.to_csv(BUILT / "sample_restaurants.csv", index=False)
print(out[["med_first", "wpme", "me_national", "me_original", "american"]].sum().to_string())
print("sample restaurants:", len(out))
