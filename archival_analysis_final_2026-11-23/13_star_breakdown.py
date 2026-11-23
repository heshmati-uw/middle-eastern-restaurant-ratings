"""Descriptive: star breakdown. Is the post-event fall in ME ratings a rise in one-star reviews or a general slide?

Usage: python 13_star_breakdown.py
Timeline shared by both events: before = 210 days before 2016-11-08 (five 42-day periods); after = 2016-11-08 to 2016-12-19 and 2017-01-27 to 2017-03-09.
Unit: restaurant x period. Outcomes: the share of the restaurant's reviews in the period with each star rating (1 to 5), and the mean rating.
Model, one per outcome: outcome ~ restaurant FE + county-by-period FE + {ME, WPME} x After x {1, Trump share per 10 pts}.
Reference group: American-first restaurants in the same county and period. County-clustered SEs.
The five star-share coefficients for a group add up to zero.
Also: raw star distributions before and after, by group and county type.
"""
import glob
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from common import BUILT, FROZEN, OUT, BIN_DAYS, Fit

s = pd.read_csv(FROZEN / "restaurants.csv", dtype={"county_fips": str}).dropna(subset=["trump_share"])
s = s[s.wpme | s.me_national | s.american]
path = FROZEN / "star_cells.csv.gz"
e1, e2, span = pd.Timestamp("2016-11-08"), pd.Timestamp("2017-01-27"), pd.Timedelta(days=BIN_DAYS)
if not path.exists():
    ids = set(s.gmap_id)
    lo, hi = int((e1 - 5 * span).value // 10**6), int((e2 + span).value // 10**6)
    parts = []
    for f in sorted(glob.glob(str(BUILT / "reviews_exact" / "*.csv.gz"))):
        x = pd.read_csv(f)
        parts.append(x[(x.time_ms >= lo) & (x.time_ms < hi) & x.gmap_id.isin(ids)])
    r = pd.concat(parts, ignore_index=True).drop_duplicates()
    dt = pd.to_datetime(r.time_ms, unit="ms")
    r["bin"] = np.where(dt < e1, np.floor((dt - e1).dt.total_seconds() / (BIN_DAYS * 86400)).astype(int), np.where(dt < e1 + span, 100, np.where(dt >= e2, 200, -999)))
    r = r[r.bin.ne(-999)]
    c = r.groupby(["gmap_id", "bin", "rating"]).size().unstack("rating", fill_value=0).reindex(columns=[1, 2, 3, 4, 5], fill_value=0)
    c.columns = ["n%d" % k for k in c.columns]
    c.reset_index().to_csv(path, index=False)
c = pd.read_csv(path).merge(s[["gmap_id", "county_fips", "trump_share", "wpme", "me_national"]], on="gmap_id")
c["n"] = c[["n1", "n2", "n3", "n4", "n5"]].sum(axis=1)
for k in range(1, 6):
    c["s%d" % k] = c["n%d" % k] / c.n
c["mean"] = sum(k * c["n%d" % k] for k in range(1, 6)) / c.n
c["cb"] = c.county_fips + "_" + c.bin.astype(str)
c["post"] = c.bin.ge(100).astype(float)
c["WP"], c["ME"] = c.wpme.astype(float), (c.me_national & ~c.wpme).astype(float)
c["Z"] = (c.trump_share - .4) / .1
for g in ["ME", "WP"]:
    c[g + "p"], c[g + "pZ"] = c[g] * c.post, c[g] * c.post * c.Z
rows = []
for y, lab in [("mean", "mean rating")] + [("s%d" % k, "share %d-star" % k) for k in range(1, 6)]:
    f = Fit(c, y, ["MEp", "MEpZ", "WPp", "WPpZ"], ["gmap_id", "cb"])
    for g, gl in [("ME", "ME"), ("WP", "WPME")]:
        rows.append(dict(outcome=lab, group=gl, quantity="per 10 pts Trump share", **f.lin(**{g + "pZ": 1})))
        rows.append(dict(outcome=lab, group=gl, quantity="change at 60% Trump share", **f.lin(**{g + "p": 1, g + "pZ": 2})))
    rows.append(dict(outcome=lab, group="WPME minus ME", quantity="per 10 pts Trump share", **f.lin(WPpZ=1, MEpZ=-1)))
res = pd.DataFrame(rows)
res.to_csv(OUT / "desc_star_breakdown.csv", index=False)
c["group"] = np.where(c.WP.eq(1), "WPME", np.where(c.ME.eq(1), "ME", "American"))
c["county"] = np.where(c.trump_share > .5, "Trump share above 50%", "Trump share 50% or less")
c["window"] = np.where(c.post.eq(1), "after", "before")
raw = c.groupby(["county", "group", "window"])[["n1", "n2", "n3", "n4", "n5"]].sum()
raw["reviews"] = raw.sum(axis=1)
for k in range(1, 6):
    raw["%d-star %%" % k] = 100 * raw["n%d" % k] / raw.reviews
raw = raw[["reviews"] + ["%d-star %%" % k for k in range(1, 6)]].reset_index()
raw.to_csv(OUT / "desc_star_distribution_raw.csv", index=False)
pd.set_option("display.width", 220)
print(res[res.quantity.eq("per 10 pts Trump share")].pivot(index="outcome", columns="group", values="est").round(4).to_string())
print("p-values")
print(res[res.quantity.eq("per 10 pts Trump share")].pivot(index="outcome", columns="group", values="p").round(3).to_string())
print(res[res.quantity.eq("change at 60% Trump share")].pivot(index="outcome", columns="group", values="est").round(4).to_string())
print(raw.round(1).to_string(index=False))

# ---------------- figure
INK, MUTED, GRID, SURF, BLUE, ORANGE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb", "#2a78d6", "#eb6834"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": GRID, "text.color": INK, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED})
fig, ax = plt.subplots(figsize=(8.6, 4.8), facecolor=SURF)
ax.set_facecolor(SURF)
ax.axhline(0, color=MUTED, lw=1)
d = res[res.quantity.eq("per 10 pts Trump share") & res.outcome.str.startswith("share")]
x = np.arange(5)
for g, colr, off, lab in [("ME", ORANGE, -0.17, "Explicitly Middle Eastern (ME)"), ("WPME", BLUE, 0.17, "Broadly positioned (WPME)")]:
    dd = d[d.group.eq(g)].reset_index(drop=True)
    ax.bar(x + off, 100 * dd.est, width=0.3, color=colr, label=lab, zorder=2)
    ax.errorbar(x + off, 100 * dd.est, yerr=100 * 1.96 * dd.se, fmt="none", ecolor=INK, elinewidth=1, capsize=3, zorder=3)
ax.set_xticks(x)
ax.set_xticklabels(["1 star", "2 stars", "3 stars", "4 stars", "5 stars"])
ax.set_ylabel("Change in the share of reviews with each rating,\nper 10 points of county Trump share (percentage points)")
ax.grid(axis="y", color=GRID, lw=0.6)
ax.tick_params(length=0)
ax.legend(frameon=False, fontsize=9, loc="upper center", ncol=2)
for sp in ["top", "right"]:
    ax.spines[sp].set_visible(False)
fig.suptitle("Which star ratings move after the election and the travel ban", x=0.01, ha="left", fontsize=11.5, fontweight="bold", y=0.975)
fig.text(0.01, 0.012, "Six weeks after each event versus the 210 days before the election, relative to American-first restaurants in the same county and period.\n"
         "Restaurant and county-by-period fixed effects; county-clustered 95% intervals.", fontsize=7.6, color=MUTED, va="bottom")
fig.tight_layout(rect=(0, 0.065, 1, 0.94))
fig.savefig(OUT / "desc_star_breakdown.png", dpi=150, facecolor=SURF)
print("figure saved")
