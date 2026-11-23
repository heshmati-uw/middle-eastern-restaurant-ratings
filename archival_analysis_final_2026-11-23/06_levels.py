"""Exhibit 2. Ordinary-times performance: WPME versus ME in the same county, all years.

Usage: python 06_levels.py
Unit: restaurant with 10+ reviews. Outcomes: mean rating over all reviews; log number of reviews (with first-review-year fixed effects).
County fixed effects; county-clustered SEs. Reported: the overall gap, the gap within Trump-share groups, and the interaction with each Trump measure.
Robustness row: the same comparison against ME restaurants that also have a baba ghanoush mention (same review evidence on both sides).
"""
import numpy as np, pandas as pd
from common import FROZEN, OUT, ME_LISTS, MIN_REVIEWS_LEVEL, Fit, zscore

s = pd.read_csv(FROZEN / "restaurants.csv", dtype={"county_fips": str, "state_fips": str})
s = s.dropna(subset=["trump_share", "n_reviews"])
s = s[s.n_reviews.ge(MIN_REVIEWS_LEVEL)].copy()
s["logrev"] = np.log(s.n_reviews)
rows = []
for lname, col in ME_LISTS.items():
    for comp, d in [("WPME vs all ME", s[s.wpme | s[col]]), ("WPME vs ME with a baba mention", s[s.wpme | (s[col] & s.baba)])]:
        d = d.copy()
        d["W"] = d.wpme.astype(float)
        for y, fes in [("mean_rating", ["county_fips"]), ("logrev", ["county_fips", "first_year"])]:
            base = dict(me_list=lname, comparison=comp, outcome=y, n_wpme=int(d.W.sum()), n_me=int((1 - d.W).sum()))
            rows.append(dict(**base, quantity="gap, all counties", **Fit(d, y, ["W"], fes, dof_adjust=True).lin(W=1)))
            for gl, mask in [("gap, Trump share 50% or less", d.trump_share <= .5), ("gap, Trump share above 50%", d.trump_share > .5)]:
                rows.append(dict(**base, quantity=gl, **Fit(d[mask], y, ["W"], fes, dof_adjust=True).lin(W=1)))
            for measure in ["continuous", "majority"]:
                d["WT"] = d.W * zscore(d.trump_share, measure)
                rows.append(dict(**base, quantity="interaction with Trump measure: " + measure, **Fit(d, y, ["W", "WT"], fes, dof_adjust=True).lin(WT=1)))
res = pd.DataFrame(rows)
res.to_csv(OUT / "exhibit2_levels.csv", index=False)
pd.set_option("display.width", 220)
print(res[res.me_list.eq("national")].drop(columns="me_list").round(4).to_string(index=False))
