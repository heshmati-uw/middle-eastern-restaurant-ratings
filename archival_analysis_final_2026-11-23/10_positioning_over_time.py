"""Exhibit 4. Positioning over time: are restaurants that appear after the 2016 election more often positioned as WPME?

Usage: python 10_positioning_over_time.py

What can and cannot be seen. Google categories are a 2021 snapshot, so a restaurant changing its label is not observable.
What is observable is each restaurant's FIRST review date, used here as a proxy for when it opened. The question becomes:
among restaurants that are WPME or ME, is the WPME share higher for those first reviewed after the election than before,
and more so in Trump-leaning counties?
Two cautions built into the output:
  - Google reviews were sparse before 2016, so many restaurants "first reviewed" in 2016-17 are older.
  - WPME requires a baba ghanoush mention in some review, and newer restaurants have fewer reviews, which pushes the WPME share
    of recent cohorts down mechanically. Two checks: controlling for log review count, and requiring a baba mention on both sides.
Models: linear probability, outcome 1 if WPME. After = first review on or after 2016-11-08.
  overall    After, county fixed effects, within a window of first-review dates around the election
  by Trump   After x Trump measure, county fixed effects and first-review-year fixed effects
County-clustered SEs.
"""
import glob
import numpy as np, pandas as pd
from common import BUILT, FROZEN, OUT, ME_LISTS, Fit, zscore

fr_path = FROZEN / "first_review.csv"
if not fr_path.exists():
    parts = [pd.read_csv(f).groupby("gmap_id").time_ms.min() for f in sorted(glob.glob(str(BUILT / "reviews_exact" / "*.csv.gz")))]
    fr = pd.concat(parts).groupby(level=0).min()
    pd.DataFrame({"gmap_id": fr.index, "first_review_date": pd.to_datetime(fr.values, unit="ms").strftime("%Y-%m-%d")}).to_csv(fr_path, index=False)
s = pd.read_csv(FROZEN / "restaurants.csv", dtype={"county_fips": str, "state_fips": str}).merge(pd.read_csv(fr_path), on="gmap_id", how="inner")
s = s.dropna(subset=["trump_share"]).copy()
s["first"] = pd.to_datetime(s.first_review_date)
s["year"] = s["first"].dt.year
s["logrev"] = np.log(s.n_reviews)
E = pd.Timestamp("2016-11-08")
s["After"] = (s["first"] >= E).astype(float)
rows, cohorts = [], []
for lname, col in ME_LISTS.items():
    for comp, d0 in [("WPME vs all ME", s[s.wpme | s[col]]), ("both with a baba mention", s[s.wpme | (s[col] & s.baba)])]:
        d0 = d0.copy()
        d0["y"] = d0.wpme.astype(float)
        for (yr, tm), dd in d0.assign(tm=np.where(d0.trump_share > .5, "Trump share above 50%", "Trump share 50% or less")).groupby(["year", "tm"]):
            if 2010 <= yr <= 2021:
                p = dd.y.mean()
                cohorts.append(dict(me_list=lname, comparison=comp, first_review_year=yr, county_type=tm, restaurants=len(dd), share_wpme=p,
                                    se=np.sqrt(p * (1 - p) / len(dd)), median_reviews=dd.n_reviews.median()))
        for yr, dd in d0.groupby("year"):
            if 2010 <= yr <= 2021:
                p = dd.y.mean()
                cohorts.append(dict(me_list=lname, comparison=comp, first_review_year=yr, county_type="all counties", restaurants=len(dd), share_wpme=p,
                                    se=np.sqrt(p * (1 - p) / len(dd)), median_reviews=dd.n_reviews.median()))
        for wl, yrs in [("first reviewed within 2 years of the election", 2), ("within 1 year", 1)]:
            d = d0[(d0["first"] >= E - pd.DateOffset(years=yrs)) & (d0["first"] < E + pd.DateOffset(years=yrs))].copy()
            base = dict(me_list=lname, comparison=comp, window=wl, restaurants=len(d), n_before=int((1 - d.After).sum()), n_after=int(d.After.sum()),
                        share_before=d[d.After.eq(0)].y.mean(), share_after=d[d.After.eq(1)].y.mean())
            for cl, ctr in [("no review-count control", []), ("controlling log review count", ["logrev"])]:
                rows.append(dict(**base, model="overall: After", control=cl, **Fit(d, "y", ["After"] + ctr, ["county_fips"], dof_adjust=True).lin(After=1)))
                for m in ["continuous", "majority"]:
                    d["AT"] = d.After * zscore(d.trump_share, m)
                    rows.append(dict(**base, model="by Trump: After x " + m, control=cl, **Fit(d, "y", ["AT"] + ctr, ["county_fips", "year"], dof_adjust=True).lin(AT=1)))
res, coh = pd.DataFrame(rows), pd.DataFrame(cohorts)
res.to_csv(OUT / "exhibit4_positioning_over_time.csv", index=False)
coh.to_csv(OUT / "exhibit4_cohorts.csv", index=False)
pd.set_option("display.width", 240)
pd.set_option("display.max_rows", 200)
c = coh[coh.me_list.eq("national") & coh.comparison.eq("WPME vs all ME")]
print("Share WPME among restaurants first reviewed in each year (national list, WPME vs all ME)")
t = c.pivot(index="first_review_year", columns="county_type", values="share_wpme").round(3)
n = c.pivot(index="first_review_year", columns="county_type", values="restaurants")
t["n all"], t["n >50%"], t["median reviews"] = n["all counties"], n["Trump share above 50%"], c[c.county_type.eq("all counties")].set_index("first_review_year").median_reviews
print(t.to_string())
print("\nSame, both sides with a baba mention")
c2 = coh[coh.me_list.eq("national") & coh.comparison.eq("both with a baba mention")]
print(c2.pivot(index="first_review_year", columns="county_type", values="share_wpme").round(3).to_string())
print("\nModels (national list)")
print(res[res.me_list.eq("national")][["comparison", "window", "model", "control", "n_before", "n_after", "share_before", "share_after", "est", "se", "p"]].round(4).to_string(index=False))

# ---------------- figure
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
INK, MUTED, GRID, SURF, BLUE, ORANGE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb", "#2a78d6", "#eb6834"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": GRID, "text.color": INK, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED})
fig, ax = plt.subplots(figsize=(8.6, 4.8), facecolor=SURF)
ax.set_facecolor(SURF)
cc = c[c.first_review_year.between(2012, 2020)]
for ct, colr, lab in [("Trump share 50% or less", BLUE, "Trump share 50% or less"), ("Trump share above 50%", ORANGE, "Trump share above 50%")]:
    d = cc[cc.county_type.eq(ct)].sort_values("first_review_year")
    ax.fill_between(d.first_review_year, 100 * (d.share_wpme - 1.96 * d.se), 100 * (d.share_wpme + 1.96 * d.se), color=colr, alpha=.13, lw=0)
    ax.plot(d.first_review_year, 100 * d.share_wpme, color=colr, lw=2, marker="o", ms=5.5, mec=SURF, mew=1.2, label=lab)
ax.axvline(2016.85, color=MUTED, lw=0.8, ls=(0, (3, 3)))
ax.text(2016.9, 97, "2016 election", fontsize=8, color=MUTED, va="top")
ax.set_xlim(2011.7, 2020.4)
ax.set_ylim(0, 100)
ax.set_yticks([0, 25, 50, 75, 100])
ax.set_xticks(range(2012, 2021))
ax.set_xlabel("Year of the restaurant's first Google review")
ax.set_ylabel("% positioned as WPME")
ax.grid(axis="y", color=GRID, lw=0.6)
ax.tick_params(length=0)
ax.legend(frameon=False, fontsize=8.5, loc="lower left", title="County", title_fontsize=8.5)
for sp in ["top", "right"]:
    ax.spines[sp].set_visible(False)
fig.suptitle("Restaurants first reviewed after the 2016 election are not more often positioned as WPME", x=0.01, ha="left", fontsize=11, fontweight="bold", y=0.975)
fig.text(0.01, 0.012, "WPME or ME restaurants (national list), by year of first review. Bands are 95% intervals. Categories are a 2021 snapshot, so relabeling by existing\n"
         "restaurants is not observable. Trump-majority counties have 37-62 new restaurants a year.", fontsize=7.6, color=MUTED, va="bottom")
fig.tight_layout(rect=(0, 0.065, 1, 0.94))
fig.savefig(OUT / "figure4_positioning_over_time.png", dpi=150, facecolor=SURF)
print("figure saved")
