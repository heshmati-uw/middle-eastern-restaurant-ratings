"""Raw pass: every review (all years) of a WPME or ME restaurant whose text contains "authentic".

Usage: python 22_scan_authentic_reviews.py <project root> [workers]
Writes built/authentic_reviews/<State>.csv.gz (gmap_id, time_ms, rating, user_id, text) and built/authentic_review_totals.csv
(per restaurant: number of reviews and number of reviews with text, all years). Output stays in built/ (review text and reviewer IDs).
"""
import sys, gzip, json, csv, pathlib
from collections import Counter
from multiprocessing import Pool
import pandas as pd
from common import BUILT, FROZEN

ROOT = pathlib.Path(sys.argv[1])
WORKERS = int(sys.argv[2]) if len(sys.argv) > 2 else 16
SRC, DEST = ROOT / "analysis/2025-08-18-rohan/inputs", BUILT / "authentic_reviews"
KEY = b'"gmap_id": "'


def scan(path):
    s = pd.read_csv(FROZEN / "restaurants.csv")
    ids = {x.encode() for x in s[s.wpme | s.me_national | s.me_original].gmap_id}
    dest = DEST / (path.name.replace("review-", "").replace(".json.gz", "") + ".csv.gz")
    seen, n_all, n_text = set(), Counter(), Counter()
    with gzip.open(path, "rb") as fh, gzip.open(dest, "wt", newline="", encoding="utf-8") as out:
        w = csv.writer(out)
        w.writerow(["gmap_id", "time_ms", "rating", "user_id", "text"])
        for line in fh:
            i = line.rfind(KEY)
            if i < 0:
                continue
            g = line[i + len(KEY):line.find(b'"', i + len(KEY))]
            if g not in ids:
                continue
            try:
                r = json.loads(line)
            except ValueError:
                continue
            t, stars, text = r.get("time"), r.get("rating"), r.get("text") or ""
            if not isinstance(t, (int, float)) or stars not in (1, 2, 3, 4, 5):
                continue
            k = (r["gmap_id"], r.get("user_id"), int(t), stars)
            if k in seen:
                continue
            seen.add(k)
            n_all[r["gmap_id"]] += 1
            if text.strip():
                n_text[r["gmap_id"]] += 1
                if "authentic" in text.lower():
                    w.writerow([r["gmap_id"], int(t), stars, r.get("user_id") or "", text.replace("\r", " ").replace("\n", " ")])
    return n_all, n_text


if __name__ == "__main__":
    DEST.mkdir(parents=True, exist_ok=True)
    files = sorted(SRC.glob("review-*.json.gz"), key=lambda p: -p.stat().st_size)
    A, T = Counter(), Counter()
    with Pool(WORKERS) as pool:
        for a, t in pool.imap_unordered(scan, files):
            A.update(a)
            T.update(t)
    pd.DataFrame({"gmap_id": list(A), "reviews": [A[k] for k in A], "text_reviews": [T[k] for k in A]}).to_csv(BUILT / "authentic_review_totals.csv", index=False)
    print("restaurants %d; reviews %d; with text %d" % (len(A), sum(A.values()), sum(T.values())))
