"""Exhibit 1. Label choice: which restaurants serving Middle Eastern food lead with "Mediterranean" (WPME) rather than an explicit ME label?

Usage: python 05_label_choice.py
Unit: restaurant with at least one review, a county and a Trump share. Outcome: 1 if WPME, 0 if ME.
Linear probability model with state fixed effects; county-clustered SEs.
Regressors: county Trump measure, then county controls added in steps (population and density; Middle Eastern ancestry share; college and foreign-born shares).
"""
import numpy as np, pandas as pd
from common import FROZEN, OUT, ME_LISTS, CONTROLS, Fit, zscore

OUT.mkdir(exist_ok=True)
s = pd.read_csv(FROZEN / "restaurants.csv", dtype={"county_fips": str, "state_fips": str})
s = s.dropna(subset=["trump_share", "n_reviews"] + CONTROLS)
SETS = [("state FE only", []), ("+ population, density", ["log_pop", "log_density"]), ("+ Middle Eastern ancestry", ["log_pop", "log_density", "mena"]),
        ("+ college, foreign-born", CONTROLS)]
rows, bins = [], []
for lname, col in ME_LISTS.items():
    d = s[s.wpme | s[col]].copy()
    d["y"] = d.wpme.astype(float)
    for measure in ["continuous", "majority"]:
        d["T"] = zscore(d.trump_share, measure)
        for sl, ctr in SETS:
            f = Fit(d, "y", ["T"] + ctr, ["state_fips"], dof_adjust=True)
            row = dict(me_list=lname, trump_measure=measure, controls=sl, n=len(d), counties=f.G, share_wpme=d.y.mean(), **{"trump_" + k: v for k, v in f.lin(T=1).items()})
            if "mena" in ctr:
                row.update({"mena_" + k: v for k, v in f.lin(mena=1).items()})
            rows.append(row)
    for var, edges, labs in [("trump_share", [0, .3, .4, .5, .6, 1.01], ["under 30%", "30-40%", "40-50%", "50-60%", "over 60%"]),
                             ("mena", [0, .25, .5, 1, 2, 100], ["under 0.25%", "0.25-0.5%", "0.5-1%", "1-2%", "over 2%"])]:
        d["bin"] = pd.cut(d[var], edges, labels=labs, right=False)
        for bn, dd in d.groupby("bin", observed=True):
            g = dd.groupby("county_fips").y.agg(["sum", "size"])
            pbar = dd.y.mean()
            se = np.sqrt(((g["sum"] - pbar * g["size"]) ** 2).sum()) / len(dd) * np.sqrt(len(g) / max(len(g) - 1, 1))
            bins.append(dict(me_list=lname, by=var, bin=bn, n=len(dd), counties=len(g), share_wpme=pbar, se=se))
pd.DataFrame(rows).to_csv(OUT / "exhibit1_label_choice.csv", index=False)
pd.DataFrame(bins).to_csv(OUT / "exhibit1_label_choice_bins.csv", index=False)
pd.set_option("display.width", 220)
print(pd.DataFrame(rows)[["me_list", "trump_measure", "controls", "n", "trump_est", "trump_p", "mena_est", "mena_p"]].round(4).to_string(index=False))
