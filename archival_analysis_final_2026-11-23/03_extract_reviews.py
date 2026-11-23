"""Step 3 (from raw). Every review of the sample restaurants, with its exact timestamp, from the raw state files.

Usage: python 03_extract_reviews.py <project root> [workers]
Reads:  analysis/2025-08-18-rohan/inputs/review-<State>.json.gz (one JSON review per line; 52 files)
Writes: built/reviews_exact/<State>.csv.gz  (gmap_id, time_ms, rating)
Ratings other than 1-5 are dropped. Exact duplicates (same restaurant, reviewer, timestamp, rating) are kept once.
No reviewer names, IDs or text are saved.
"""
import sys, gzip, json, csv, pathlib, time
from multiprocessing import Pool
from common import BUILT

ROOT = pathlib.Path(sys.argv[1])
WORKERS = int(sys.argv[2]) if len(sys.argv) > 2 else 16
SRC, DEST = ROOT / "analysis/2025-08-18-rohan/inputs", BUILT / "reviews_exact"
KEY = b'"gmap_id": "'


def scan(path):
    with open(BUILT / "sample_restaurants.csv", newline="", encoding="utf-8") as fh:
        ids = {row["gmap_id"].encode() for row in csv.DictReader(fh)}
    t0, seen, n, kept = time.time(), set(), 0, 0
    dest = DEST / (path.name.replace("review-", "").replace(".json.gz", "") + ".csv.gz")
    tmp = dest.with_suffix(".tmp")
    with gzip.open(path, "rb") as fh, gzip.open(tmp, "wt", newline="", encoding="utf-8") as out:
        w = csv.writer(out)
        w.writerow(["gmap_id", "time_ms", "rating"])
        for line in fh:
            n += 1
            i = line.rfind(KEY)
            if i < 0 or line[i + len(KEY):line.find(b'"', i + len(KEY))] not in ids:
                continue
            try:
                r = json.loads(line)
            except ValueError:
                continue
            t, stars = r.get("time"), r.get("rating")
            if not isinstance(t, (int, float)) or stars not in (1, 2, 3, 4, 5):
                continue
            k = (r["gmap_id"], r.get("user_id"), int(t), stars)
            if k in seen:
                continue
            seen.add(k)
            w.writerow([r["gmap_id"], int(t), stars])
            kept += 1
    tmp.replace(dest)
    return path.name, n, kept, time.time() - t0


if __name__ == "__main__":
    DEST.mkdir(parents=True, exist_ok=True)
    files = sorted(SRC.glob("review-*.json.gz"), key=lambda p: -p.stat().st_size)
    tot_n = tot_k = 0
    with Pool(WORKERS) as pool:
        for name, n, kept, secs in pool.imap_unordered(scan, files):
            tot_n += n
            tot_k += kept
    print("state files %d; reviews scanned %d; reviews kept %d" % (len(files), tot_n, tot_k), flush=True)
