"""Descriptives: what reviewers wrote and who they are, around the 2016 election and the travel ban.

Usage: python 16_text_and_reviewers.py
Reads built/text_reviews/*.csv.gz and built/reviewer_counts.csv (from 12_scan_text_and_reviewers.py). WPME and ME (national list) only.
Windows: before = 2016-04-12 to 2016-11-07; after = 2016-11-08 to 2016-12-19 and 2017-01-27 to 2017-03-09.
(a) Political mentions: share of reviews whose text mentions politics or identity
    (trump, election, politic*, travel/muslim ban, muslim*, islam*, immigra*, refugee*, terror*, racis*, bigot*, xenophob*, boycott*, deport*, foreigner*).
(b) Reviewer activity: each reviewer's total number of reviews anywhere in the data (any year). One-time = 1; light = 2-9; frequent = 10+.
    The event model (rating ~ restaurant FE + county-by-period FE + WPME x After + WPME x After x Trump share per 10 pts) is run
    separately on reviews from each reviewer type, and on the share of a restaurant's reviews that come from one-time reviewers.
(c) Reading file (local only, contains review text): built/desc_review_quotes.csv
"""
import glob, re
import numpy as np, pandas as pd
from common import BUILT, FROZEN, OUT, Fit

s = pd.read_csv(FROZEN / "restaurants.csv", dtype={"county_fips": str}).dropna(subset=["trump_share"])
s = s[s.wpme | s.me_national][["gmap_id", "county_fips", "trump_share", "wpme"]]
r = pd.concat([pd.read_csv(f, dtype={"user_id": str}) for f in sorted(glob.glob(str(BUILT / "text_reviews" / "*.csv.gz")))], ignore_index=True)
r = r.merge(s, on="gmap_id", how="inner").merge(pd.read_csv(BUILT / "reviewer_counts.csv", dtype={"user_id": str}), on="user_id", how="left")
r["dt"] = pd.to_datetime(r.time_ms, unit="ms")
e1, e2, span = pd.Timestamp("2016-11-08"), pd.Timestamp("2017-01-27"), pd.Timedelta(days=42)
r["bin"] = np.where(r.dt < e1, np.floor((r.dt - e1).dt.total_seconds() / (42 * 86400)).astype(int), np.where(r.dt < e1 + span, 100, np.where((r.dt >= e2) & (r.dt < e2 + span), 200, -999)))
r = r[r.bin.ne(-999)].copy()
r["window"] = np.where(r.bin.lt(0), "before", np.where(r.bin.eq(100), "after election", "after travel ban"))
r["after"] = r.bin.ge(100)
r["group"] = np.where(r.wpme, "WPME", "ME")
r["county"] = np.where(r.trump_share > .5, "Trump share above 50%", "Trump share 50% or less")
r["text"] = r.text.fillna("")
r["has_text"] = r.text.str.strip().ne("")
# "go back to" was in a first version and was dropped: 48 of its matches were customers saying they would return.
POL = re.compile(r"\b(?:trump|election|politic\w*|travel ban|muslim ban|muslim\w*|islam\w*|immigra\w*|refugee\w*|terror\w*|racis\w*|bigot\w*|xenophob\w*|boycott\w*|deport\w*|foreigner\w*)\b", re.I)
r["political"] = r.text.str.contains(POL)
print("reviews in the windows: %d (with text: %d); reviewers: %d" % (len(r), r.has_text.sum(), r.user_id.nunique()))

# ---- (a) political mentions
a = r[r.has_text].groupby(["county", "group", "window"]).agg(reviews_with_text=("political", "size"), political=("political", "sum")).reset_index()
a["per_1000"] = 1000 * a.political / a.reviews_with_text
a.to_csv(OUT / "desc_political_mentions.csv", index=False)
pd.set_option("display.width", 230)
print(a.pivot(index=["county", "group"], columns="window", values="per_1000")[["before", "after election", "after travel ban"]].round(1).to_string())
print(a.pivot(index=["county", "group"], columns="window", values="political")[["before", "after election", "after travel ban"]].to_string())
terms = r[r.political].text.str.findall(POL).explode().str.lower().str.replace(r"(s|ed|ing|al|ally|ion|ism|ist|nts?)$", "", regex=True)
print("most common matched words:", terms.value_counts().head(12).to_dict())
pol = r[r.political]
print("political-mention reviews by rating, ME vs WPME, after windows:")
print(pol[pol.after].groupby(["group", "rating"]).size().unstack(fill_value=0).to_string())

# ---- (b) reviewer activity
r["rtype"] = np.where(r.reviews_total.fillna(1) <= 1, "one-time (1 review ever)", np.where(r.reviews_total < 10, "light (2-9)", "frequent (10+)"))
print("\nreviewer types (share of reviews):", r.rtype.value_counts(normalize=True).round(3).to_dict())
d1 = r.groupby(["county", "group", "window", "rtype"]).rating.agg(["mean", "size"]).reset_index()
d1.to_csv(OUT / "desc_reviewer_types_raw.csv", index=False)
rows = []


def did(sub, label, y="mean"):
    c = sub.groupby(["gmap_id", "bin"]).agg(mean=("rating", "mean"), n=("rating", "size"), one=("one", "mean")).reset_index().merge(s, on="gmap_id")
    c["cb"] = c.county_fips + "_" + c.bin.astype(str)
    c["W"] = c.wpme.astype(float)
    c["WP"] = c.W * c.bin.ge(100)
    c["WPZ"] = c.WP * (c.trump_share - .4) / .1
    f = Fit(c, y, ["WP", "WPZ"], ["gmap_id", "cb"])
    rows.append(dict(sample=label, outcome="rating" if y == "mean" else "share of reviews from one-time reviewers", restaurants=c.gmap_id.nunique(),
                     reviews_after=int(c[c.bin.ge(100)].n.sum()), **f.lin(WPZ=1)))


r["one"] = (r.rtype == "one-time (1 review ever)").astype(float)
did(r, "all reviewers")
for t in ["one-time (1 review ever)", "light (2-9)", "frequent (10+)"]:
    did(r[r.rtype.eq(t)], t)
did(r, "all reviewers", y="one")
res = pd.DataFrame(rows)
res.to_csv(OUT / "desc_reviewer_types.csv", index=False)
print(res.round(4).to_string(index=False))
print("\nmean rating by reviewer type, ME restaurants, Trump share above 50%:")
print(d1[(d1.group == "ME") & (d1.county == "Trump share above 50%")].pivot(index="rtype", columns="window", values="mean")[["before", "after election", "after travel ban"]].round(2).to_string())
print(d1[(d1.group == "ME") & (d1.county == "Trump share above 50%")].pivot(index="rtype", columns="window", values="size")[["before", "after election", "after travel ban"]].to_string())

# ---- (c) reading file, local only
q = r[r.after & r.has_text & (r.political | ((r.rating <= 2) & (r.trump_share > .45)))].copy()
q["chars"] = q.text.str.len()
q = q.sort_values(["political", "trump_share"], ascending=[False, False])
q[["group", "window", "county_fips", "trump_share", "rating", "political", "reviews_total", "dt", "gmap_id", "text"]].to_csv(BUILT / "desc_review_quotes.csv", index=False)
print("\nreading file: %d reviews (%d with political mentions) -> built/desc_review_quotes.csv" % (len(q), q.political.sum()))
short = pol[pol.after & pol.text.str.len().lt(220)].sort_values("trump_share", ascending=False)
for _, x in short.head(14).iterrows():
    print("  [%s, %s, %d stars, Trump %.0f%%] %s" % (x.group, x.window, x.rating, 100 * x.trump_share, x.text[:210]))
