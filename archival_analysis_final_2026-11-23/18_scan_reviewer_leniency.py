"""Raw pass for the reviewer-leniency control.

Usage: python 18_scan_reviewer_leniency.py <project root> [workers]
Pass 1: reviews of WPME, ME (national) and American-first restaurants dated 2016-04-12 to 2017-03-09 (the shared election + travel-ban
        timeline), with reviewer ID -> built/timeline_reviews_users/<State>.csv.gz
Pass 2: for every reviewer seen in pass 1, how many 1-, 2-, 3-, 4- and 5-star reviews they wrote anywhere in the data, any year
        -> built/reviewer_star_counts.csv
Output stays in built/ (it contains reviewer IDs).
"""
import sys, gzip, json, csv, pathlib, glob
from multiprocessing import Pool
import pandas as pd
from common import BUILT, FROZEN

ROOT = pathlib.Path(sys.argv[1])
WORKERS = int(sys.argv[2]) if len(sys.argv) > 2 else 16
SRC, DEST = ROOT / "analysis/2025-08-18-rohan/inputs", BUILT / "timeline_reviews_users"
KEY, UKEY, RKEY = b'"gmap_id": "', b'{"user_id": "', b'"rating": '
LO, HI = int(pd.Timestamp("2016-04-12").value // 10**6), int(pd.Timestamp("2017-03-10").value // 10**6)


def pass1(path):
    s = pd.read_csv(FROZEN / "restaurants.csv")
    ids = {x.encode() for x in s[(s.wpme | s.me_national | s.american) & s.trump_share.notna()].gmap_id}
    dest = DEST / (path.name.replace("review-", "").replace(".json.gz", "") + ".csv.gz")
    seen, kept = set(), 0
    with gzip.open(path, "rb") as fh, gzip.open(dest, "wt", newline="", encoding="utf-8") as out:
        w = csv.writer(out)
        w.writerow(["gmap_id", "time_ms", "rating", "user_id"])
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
            w.writerow([r["gmap_id"], int(t), stars, r.get("user_id") or ""])
            kept += 1
    return kept


def init(users):
    global USERS
    USERS = users


def pass2(path):
    users, out, n = USERS, {}, len(UKEY)
    with gzip.open(path, "rb") as fh:
        for line in fh:
            if not line.startswith(UKEY):
                continue
            u = line[n:line.find(b'"', n)]
            if u not in users:
                continue
            j = line.find(RKEY)
            c = line[j + len(RKEY):j + len(RKEY) + 1] if j > 0 else b""
            if c in (b"1", b"2", b"3", b"4", b"5"):
                a = out.get(u)
                if a is None:
                    a = out[u] = [0, 0, 0, 0, 0]
                a[int(c) - 1] += 1
    return out


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
    total = {}
    with Pool(WORKERS, initializer=init, initargs=(users,)) as pool:
        for part in pool.imap_unordered(pass2, files):
            for u, a in part.items():
                b = total.get(u)
                if b is None:
                    total[u] = a
                else:
                    for k in range(5):
                        b[k] += a[k]
    d = pd.DataFrame.from_dict({k.decode(): v for k, v in total.items()}, orient="index", columns=["u1", "u2", "u3", "u4", "u5"])
    d.index.name = "user_id"
    d.to_csv(BUILT / "reviewer_star_counts.csv")
    print("pass 2: reviewers counted %d" % len(d), flush=True)
