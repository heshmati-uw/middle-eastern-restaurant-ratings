"""Descriptive: identity as the lens for a bad experience.
Do negative reviews reference identity more than positive ones, and more at ME restaurants than at WPME restaurants?

Usage: python 17_identity_lens.py
Reads built/text_reviews/*.csv.gz (from 12_scan_text_and_reviewers.py): all reviews with text, 2016-04-12 to 2017-07-13, WPME and ME (national list).
Identity words (strict): muslim*, islam*, racis*, bigot*, foreigner*, immigra*, refugee*, terror*.
Broad list adds: arab*, ethnic*, "these people", "those people", "their own people/kind".
"""
import glob, re
import numpy as np, pandas as pd
from scipy import stats
from common import BUILT, FROZEN, OUT

s = pd.read_csv(FROZEN / "restaurants.csv").dropna(subset=["trump_share"])
s = s[s.wpme | s.me_national][["gmap_id", "trump_share", "wpme"]]
r = pd.concat([pd.read_csv(f, dtype={"user_id": str}) for f in sorted(glob.glob(str(BUILT / "text_reviews" / "*.csv.gz")))], ignore_index=True).merge(s, on="gmap_id")
r["text"] = r.text.fillna("")
r = r[r.text.str.strip().ne("")].copy()
STRICT = re.compile(r"\b(?:muslim\w*|islam\w*|racis\w*|bigot\w*|foreigner\w*|immigra\w*|refugee\w*|terror\w*)\b", re.I)
BROAD = re.compile(r"\b(?:muslim\w*|islam\w*|arab\w*|racis\w*|bigot\w*|foreigner\w*|immigra\w*|refugee\w*|terror\w*|ethnic\w*|their (?:own )?(?:people|kind)|these people|those people)\b", re.I)
r["strict"], r["broad"] = r.text.str.contains(STRICT), r.text.str.contains(BROAD)
r["group"] = np.where(r.wpme, "WPME", "ME")
r["stars"] = np.where(r.rating <= 2, "1-2 stars", np.where(r.rating == 3, "3 stars", "4-5 stars"))
t = r.groupby(["stars", "group"]).agg(text_reviews=("strict", "size"), strict=("strict", "sum"), broad=("broad", "sum")).reset_index()
t["strict_per_1000"], t["broad_per_1000"] = 1000 * t.strict / t.text_reviews, 1000 * t.broad / t.text_reviews
low = r[r.rating <= 2]
tests = []
for col in ["strict", "broad"]:
    a, b = low[low.group == "ME"][col], low[low.group == "WPME"][col]
    tests.append(dict(word_list=col, me_per_1000=1000 * a.mean(), wpme_per_1000=1000 * b.mean(),
                      fisher_p=stats.fisher_exact([[a.sum(), len(a) - a.sum()], [b.sum(), len(b) - b.sum()]])[1]))
t.to_csv(OUT / "desc_identity_mentions_by_stars.csv", index=False)
pd.DataFrame(tests).to_csv(OUT / "desc_identity_mentions_me_vs_wpme.csv", index=False)
print(t.round(1).to_string(index=False))
print(pd.DataFrame(tests).round(3).to_string(index=False))
