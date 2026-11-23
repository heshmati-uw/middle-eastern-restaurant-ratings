"""Descriptives, raw pass. Review text and reviewer activity for WPME and ME restaurants around the 2016 election and the travel ban.

Usage: python 12_scan_text_and_reviewers.py <project root> [workers]
Pass 1: reviews of WPME / ME restaurants dated 2016-04-12 to 2017-07-13 (UTC), with text and reviewer ID -> built/text_reviews/<State>.csv.gz
Pass 2: for every reviewer seen in pass 1, the number of reviews they wrote anywhere in the data, any year -> built/reviewer_counts.csv
These files stay in built/ (not in the repository): they contain review text and reviewer IDs.
"""
import sys, gzip, json, csv, pathlib, glob
from collections import Counter
from multiprocessing import Pool
import pandas as pd
from common import BUILT, FROZEN

ROOT = pathlib.Path(sys.argv[1])
WORKERS = int(sys.argv[2]) if len(sys.argv) > 2 else 16
SRC, DEST = ROOT / "analysis/2025-08-18-rohan/inputs", BUILT / "text_reviews"
KEY, UKEY = b'"gmap_id": "', b'{"user_id": "'
LO, HI = int(pd.Timestamp("2016-04-12").value // 10**6), int(pd.Timestamp("2017-07-14").value // 10**6)


def target_ids():
    s = pd.read_csv(FROZEN / "restaurants.csv")
    s = s[(s.wpme | s.me_national | s.me_original) & s.trump_share.notna()]
    return {x.encode() for x in s.gmap_id}


def pass1(path):
    ids = target_ids()
    dest = DEST / (path.name.replace("review-", "").replace(".json.gz", "") + ".csv.gz")
    seen, kept = set(), 0
    with gzip.open(path, "rb") as fh, gzip.open(dest, "wt", newline="", encoding="utf-8") as out:
        w = csv.writer(out)
        w.writerow(["gmap_id", "time_ms", "rating", "user_id", "text"])
        for line in fh:
            i = line.rfind(KEY)
            if i < 0 or line[i + len(KEY):line.find(b'"', i + len(KEY))] not in ids:
                continue
            try:
                r = json.loads(line)
            except ValueError:
                continue
            t, stars = r.get("time"), r.get("rating")
            if not isinstance(t, (int, float)) or stars not in (1, 2, 3, 4, 5) or not (LO <= t < HI):
                continue
            k = (r["gmap_id"], r.get("user_id"), int(t), stars)
            if k in seen:
                continue
            seen.add(k)
            w.writerow([r["gmap_id"], int(t), stars, r.get("user_id") or "", (r.get("text") or "").replace("\r", " ").replace("\n", " ")])
            kept += 1
    return kept


def pass2(path):
    users = USERS
    c = Counter()
    n = len(UKEY)
    with gzip.open(path, "rb") as fh:
        for line in fh:
            if line.startswith(UKEY):
                u = line[n:line.find(b'"', n)]
                if u in users:
                    c[u] += 1
    return c


def init(users):
    global USERS
    USERS = users


if __name__ == "__main__":
    DEST.mkdir(parents=True, exist_ok=True)
    files = sorted(SRC.glob("review-*.json.gz"), key=lambda p: -p.stat().st_size)
    with Pool(WORKERS) as pool:
        kept = sum(pool.imap_unordered(pass1, files))
    print("pass 1: reviews kept %d" % kept, flush=True)
    users = set()
    for f in glob.glob(str(DEST / "*.csv.gz")):
        users |= {u.encode() for u in pd.read_csv(f, usecols=["user_id"], dtype=str).user_id.dropna()}
    print("pass 1: distinct reviewers %d" % len(users), flush=True)
    total = Counter()
    with Pool(WORKERS, initializer=init, initargs=(users,)) as pool:
        for c in pool.imap_unordered(pass2, files):
            total.update(c)
    pd.DataFrame({"user_id": [k.decode() for k in total], "reviews_total": list(total.values())}).to_csv(BUILT / "reviewer_counts.csv", index=False)
    print("pass 2: reviewers counted %d" % len(total), flush=True)
