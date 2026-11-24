"""Descriptive: the star breakdown, accounting for who is reviewing.

Usage: python 19_star_breakdown_leniency.py
Reads built/timeline_reviews_users/*.csv.gz and built/reviewer_star_counts.csv (from 18_scan_reviewer_leniency.py).
Reviewer leniency = the reviewer's rating history on every OTHER review they wrote in the data (any business, any year):
their average rating, and the share of their reviews at each star level.
Same model and timeline as 13_star_breakdown.py (restaurant FE, county-by-period FE, American-first reference, per 10 points of Trump share), three ways:
  baseline            as before
  + leniency control  adds the average leniency of the restaurant's reviewers in the period (and the share of reviewers with no other reviews)
  relative to usual   each review is expressed relative to that reviewer's own history (rating minus their usual average; a 1-star indicator
                      minus their usual 1-star share, and so on); reviews by people with no other reviews are left out
Also: whether the reviewers themselves change (average leniency of a restaurant's reviewers as the outcome).
"""
import glob
import numpy as np, pandas as pd
from common import BUILT, FROZEN, OUT, BIN_DAYS, Fit

s = pd.read_csv(FROZEN / "restaurants.csv", dtype={"county_fips": str}).dropna(subset=["trump_share"])
s = s[s.wpme | s.me_national | s.american][["gmap_id", "county_fips", "trump_share", "wpme", "me_national"]]
r = pd.concat([pd.read_csv(f, dtype={"user_id": str}) for f in sorted(glob.glob(str(BUILT / "timeline_reviews_users" / "*.csv.gz")))], ignore_index=True).drop_duplicates()
u = pd.read_csv(BUILT / "reviewer_star_counts.csv", dtype={"user_id": str})
r = r.merge(u, on="user_id", how="left").merge(s, on="gmap_id", how="inner")
dt = pd.to_datetime(r.time_ms, unit="ms")
e1, e2, span = pd.Timestamp("2016-11-08"), pd.Timestamp("2017-01-27"), pd.Timedelta(days=BIN_DAYS)
r["bin"] = np.where(dt < e1, np.floor((dt - e1).dt.total_seconds() / (BIN_DAYS * 86400)).astype(int), np.where(dt < e1 + span, 100, np.where(dt >= e2, 200, -999)))
r = r[r.bin.ne(-999)].copy()
tot = r[["u1", "u2", "u3", "u4", "u5"]].sum(axis=1)
other = tot - 1
r["has_hist"] = other.ge(1) & tot.notna()
ssum = sum(k * r["u%d" % k] for k in range(1, 6))
r["len_mean"] = np.where(r.has_hist, (ssum - r.rating) / other.where(other > 0), np.nan)
for k in range(1, 6):
    r["i%d" % k] = (r.rating == k).astype(float)
    r["len%d" % k] = np.where(r.has_hist, (r["u%d" % k] - r["i%d" % k]) / other.where(other > 0), np.nan)
    r["rel%d" % k] = r["i%d" % k] - r["len%d" % k]
r["rel_mean"] = r.rating - r.len_mean
print("reviews on the timeline: %d; reviewers: %d; reviews whose reviewer has other reviews: %.1f%%" % (len(r), r.user_id.nunique(), 100 * r.has_hist.mean()))
print("reviewer leniency (their usual average rating): mean %.2f, SD %.2f" % (r.len_mean.mean(), r.len_mean.std()))


def cells(d, cols):
    c = d.groupby(["gmap_id", "bin"])[cols].mean()
    c["n"] = d.groupby(["gmap_id", "bin"]).size()
    c = c.reset_index().merge(s, on="gmap_id")
    c["cb"] = c.county_fips + "_" + c.bin.astype(str)
    c["post"] = c.bin.ge(100).astype(float)
    c["WP"], c["ME"] = c.wpme.astype(float), (c.me_national & ~c.wpme).astype(float)
    z = (c.trump_share - .4) / .1
    for g in ["ME", "WP"]:
        c[g + "p"], c[g + "pZ"] = c[g] * c.post, c[g] * c.post * z
        for k, bn in [("e", 100), ("b", 200)]:  # each event on its own
            c[g + k] = c[g] * c.bin.eq(bn)
            c[g + k + "Z"] = c[g + k] * z
    return c


rows = []
base_cols = ["rating"] + ["i%d" % k for k in range(1, 6)]
c_all = cells(r.assign(nohist=(~r.has_hist).astype(float), lenfill=r.len_mean.fillna(r.len_mean.mean())), base_cols + ["nohist", "lenfill"])
c_rel = cells(r[r.has_hist], ["rel_mean"] + ["rel%d" % k for k in range(1, 6)] + ["len_mean"])
# restaurant-by-period cells relative to each reviewer's usual (no reviewer IDs), so the model can be re-estimated from frozen/
c_rel[["gmap_id", "bin", "rel_mean", "rel1", "len_mean", "n"]].to_csv(FROZEN / "leniency_cells.csv.gz", index=False)
c_all[["gmap_id", "bin", "rating", "i1", "lenfill", "nohist", "n"]].to_csv(FROZEN / "leniency_cells_all.csv.gz", index=False)
X = ["MEp", "MEpZ", "WPp", "WPpZ"]
LAB = {"rating": "mean rating", **{"i%d" % k: "share %d-star" % k for k in range(1, 6)}}
for y, lab in LAB.items():
    for spec, cols in [("baseline", X), ("+ leniency control", X + ["lenfill", "nohist"])]:
        f = Fit(c_all, y, cols, ["gmap_id", "cb"])
        for g, gl in [("ME", "ME"), ("WP", "WPME")]:
            rows.append(dict(spec=spec, outcome=lab, group=gl, **f.lin(**{g + "pZ": 1})))
        rows.append(dict(spec=spec, outcome=lab, group="WPME minus ME", **f.lin(WPpZ=1, MEpZ=-1)))
    yr = "rel_mean" if y == "rating" else "rel" + y[1]
    f = Fit(c_rel, yr, X, ["gmap_id", "cb"])
    for g, gl in [("ME", "ME"), ("WP", "WPME")]:
        rows.append(dict(spec="relative to the reviewer's usual", outcome=lab, group=gl, **f.lin(**{g + "pZ": 1})))
    rows.append(dict(spec="relative to the reviewer's usual", outcome=lab, group="WPME minus ME", **f.lin(WPpZ=1, MEpZ=-1)))
f = Fit(c_rel, "len_mean", X, ["gmap_id", "cb"])
for g, gl in [("ME", "ME"), ("WP", "WPME")]:
    rows.append(dict(spec="reviewer mix", outcome="average leniency of the restaurant's reviewers", group=gl, **f.lin(**{g + "pZ": 1})))
# each event on its own (spec is suffixed with the event)
XE = [g + k + sfx for g in ["ME", "WP"] for k in ["e", "b"] for sfx in ["", "Z"]]
for y, lab in [("rating", "mean rating"), ("i1", "share 1-star")]:
    for spec, data, yy in [("baseline", c_all, y), ("relative to the reviewer's usual", c_rel, "rel_mean" if y == "rating" else "rel1")]:
        f = Fit(data, yy, XE, ["gmap_id", "cb"])
        for k, kl in [("e", "election"), ("b", "travel ban")]:
            rows.append(dict(spec=spec + " | " + kl, outcome=lab, group="ME", **f.lin(**{"ME" + k + "Z": 1})))
            rows.append(dict(spec=spec + " | " + kl, outcome=lab, group="WPME", **f.lin(**{"WP" + k + "Z": 1})))
            rows.append(dict(spec=spec + " | " + kl, outcome=lab, group="WPME minus ME", **f.lin(**{"WP" + k + "Z": 1, "ME" + k + "Z": -1})))
res = pd.DataFrame(rows)
res.to_csv(OUT / "desc_star_breakdown_leniency.csv", index=False)
print(res[res.spec.str.contains("|", regex=False)][["spec", "outcome", "group", "est", "se", "p"]].round(4).to_string(index=False))
pd.set_option("display.width", 220)
for g in ["ME", "WPME", "WPME minus ME"]:
    print("\n%s: change per 10 points of Trump share" % g)
    t = res[res.group.eq(g) & res.spec.ne("reviewer mix")]
    print(t.pivot(index="outcome", columns="spec", values="est")[["baseline", "+ leniency control", "relative to the reviewer's usual"]].round(4).to_string())
    print(t.pivot(index="outcome", columns="spec", values="p")[["baseline", "+ leniency control", "relative to the reviewer's usual"]].round(3).to_string())
print(res[res.spec.eq("reviewer mix")][["group", "est", "se", "p"]].round(4).to_string(index=False))
