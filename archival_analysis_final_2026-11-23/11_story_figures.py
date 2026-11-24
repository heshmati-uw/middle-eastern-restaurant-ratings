"""Descriptive figures for the paper's motivation. Usage: python 11_story_figures.py

Figure 5. Which group moves, by county Trump share. Change in rating in the six weeks after the 2016 election and the travel ban
          (both events together), relative to American-first restaurants in the same county and period.
          Lines: linear fit (rating ~ restaurant FE + county-by-period FE + {ME, WPME} x After x {1, Trump share}).
          Points: the same model with Trump share in five bins instead of a line.
Figure 6. The WPME-minus-ME rating gap over time, April 2016 - July 2017, in consecutive periods of about six weeks
          (five before the election; after the election; between; after the travel ban; three later).
          Left: how much the gap rises per 10 points of county Trump share. Right: the gap in Trump-majority counties and in other counties.
          Each series is shown relative to its own average over the five pre-election periods.
          Model: rating ~ restaurant FE + county-by-period FE + WPME x period (+ WPME x period x Trump measure).
County-clustered 95% intervals throughout. WPME = Mediterranean-first with a baba mention; ME = all ME-first (national list).
"""
import glob
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from common import BUILT, FROZEN, OUT, Fit

INK, MUTED, GRID, SURF, BLUE, ORANGE, VIOLET, GREY = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb", "#2a78d6", "#eb6834", "#6250d6", "#8f8d86"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": GRID, "text.color": INK, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED})
s = pd.read_csv(FROZEN / "restaurants.csv", dtype={"county_fips": str}).dropna(subset=["trump_share"])


def clean(ax, grid="y"):
    ax.set_facecolor(SURF)
    ax.grid(axis=grid, color=GRID, lw=0.6)
    ax.tick_params(length=0)
    for sp in ["top", "right"]:
        ax.spines[sp].set_visible(False)


# =============== Figure 5: which group moves, by Trump share
tl = pd.read_csv(FROZEN / "timeline_cells.csv.gz").merge(s[s.wpme | s.me_national | s.american][["gmap_id", "county_fips", "trump_share", "wpme", "me_national"]], on="gmap_id")
tl["cb"] = tl.county_fips + "_" + tl.bin.astype(str)
tl["post"] = tl.bin.ge(100).astype(float)
tl["WP"], tl["ME"] = tl.wpme.astype(float), (tl.me_national & ~tl.wpme).astype(float)
tl["Z"] = (tl.trump_share - .4) / .1
for g in ["ME", "WP"]:
    tl[g + "p"], tl[g + "pZ"] = tl[g] * tl.post, tl[g] * tl.post * tl.Z
lin = Fit(tl, "mean", ["MEp", "MEpZ", "WPp", "WPpZ"], ["gmap_id", "cb"])
EDGES, MID = [0, .3, .4, .5, .6, 1.01], ["under 30%", "30-40%", "40-50%", "50-60%", "over 60%"]
tl["k"] = pd.cut(tl.trump_share, EDGES, labels=False, right=False)
bcols = []
for g in ["ME", "WP"]:
    for k in range(5):
        tl["%sb%d" % (g, k)] = tl[g] * tl.post * tl.k.eq(k)
        bcols.append("%sb%d" % (g, k))
binned = Fit(tl, "mean", bcols, ["gmap_id", "cb"])
xmid = tl[(tl.WP + tl.ME).gt(0)].drop_duplicates("gmap_id").groupby("k").trump_share.mean()
rows5 = []
fig, ax = plt.subplots(figsize=(8.8, 5.2), facecolor=SURF)
clean(ax)
ax.axhline(0, color=MUTED, lw=1)
xs = np.linspace(.15, .72, 60)
for g, colr, lab, off in [("ME", ORANGE, "Explicitly Middle Eastern (ME)", -0.004), ("WP", BLUE, "Broadly positioned (WPME)", +0.004)]:
    fit = [lin.lin(**{g + "p": 1, g + "pZ": (x - .4) / .1}) for x in xs]
    est, se = np.array([f["est"] for f in fit]), np.array([f["se"] for f in fit])
    ax.fill_between(100 * xs, est - 1.96 * se, est + 1.96 * se, color=colr, alpha=.14, lw=0)
    ax.plot(100 * xs, est, color=colr, lw=2.4, label=lab)
    for k in range(5):
        b = binned.lin(**{"%sb%d" % (g, k): 1})
        n = int(tl[tl[g].eq(1) & tl.k.eq(k)].gmap_id.nunique())
        xk = 100 * (xmid[k] + off)
        rows5.append(dict(group=lab, trump_share_bin=MID[k], mean_share=xmid[k], restaurants=n, **b))
    sl = lin.lin(**{g + "pZ": 1})
    rows5.append(dict(group=lab, trump_share_bin="slope per 10 pts (linear fit)", **sl))
    ax.text(71.5, est[-1] + (0.075 if g == "WP" else -0.085), "%+.3f stars per 10 points (p = %.2f)" % (sl["est"], sl["p"]), color=INK, fontsize=8.6, ha="right", va="center")
ax.text(15, 0.185, "Zero line = American-first restaurants in the same county", fontsize=8.2, color=MUTED, ha="left", va="top")
ax.set_xlim(14, 73)
ax.set_ylim(-0.3, 0.2)
ax.set_xlabel("County 2016 Trump vote share (%)")
ax.set_ylabel("Change in rating after the events,\nrelative to American-first restaurants (stars)")
ax.legend(frameon=False, fontsize=9, loc="lower left")
fig.suptitle("After the 2016 election and the travel ban, ratings of explicitly Middle Eastern restaurants\nfall as county Trump share rises",
             x=0.01, ha="left", fontsize=11.2, fontweight="bold", y=0.985)
fig.text(0.01, 0.012, "Six weeks after the 2016 election and the January 2017 travel ban versus the 210 days before the election. Lines: linear fit with 95% bands.\n"
         "Restaurant and county-by-period fixed effects; county-clustered intervals. Separate estimates for five Trump-share groups are uneven (see figure5_data.csv).\n"
         "The difference between the two lines is not robust to accounting for each reviewer's usual rating (desc_star_breakdown_leniency.csv).", fontsize=7.6, color=MUTED, va="bottom")
fig.tight_layout(rect=(0, 0.065, 1, 0.9))
fig.savefig(OUT / "figure5_which_group_moves_by_trump_share.png", dpi=150, facecolor=SURF)
plt.close(fig)
pd.DataFrame(rows5).to_csv(OUT / "figure5_data.csv", index=False)
print(pd.DataFrame(rows5)[["group", "trump_share_bin", "restaurants", "est", "se", "p"]].round(3).to_string(index=False))

# =============== Figure 6: the gap over time
STARTS = ["2016-04-12", "2016-05-24", "2016-07-05", "2016-08-16", "2016-09-27", "2016-11-08", "2016-12-20", "2017-01-27", "2017-03-10", "2017-04-21", "2017-06-02", "2017-07-14"]
edges = pd.to_datetime(STARTS)
path = FROZEN / "story_timeline_cells.csv.gz"
if not path.exists():
    ids = set(s[s.wpme | s.me_national | s.me_original].gmap_id)
    lo, hi = int(edges[0].value // 10**6), int(edges[-1].value // 10**6)
    parts = []
    for f in sorted(glob.glob(str(BUILT / "reviews_exact" / "*.csv.gz"))):
        x = pd.read_csv(f)
        parts.append(x[(x.time_ms >= lo) & (x.time_ms < hi) & x.gmap_id.isin(ids)])
    r = pd.concat(parts, ignore_index=True).drop_duplicates()
    r["period"] = np.searchsorted(edges.values, pd.to_datetime(r.time_ms, unit="ms").values, side="right") - 1
    r.groupby(["gmap_id", "period"]).rating.agg(["mean", "size"]).reset_index().rename(columns={"size": "n"}).to_csv(path, index=False)
c = pd.read_csv(path).merge(s[s.wpme | s.me_national][["gmap_id", "county_fips", "trump_share", "wpme"]], on="gmap_id")
c["W"] = c.wpme.astype(float)
c["cb"] = c.county_fips + "_" + c.period.astype(str)
P, PRE, REF = list(range(11)), [0, 1, 2, 3, 4], 4
mid = edges[:-1] + (edges[1:] - edges[:-1]) / 2


def profile(measure):
    d = c.copy()
    z = (d.trump_share - .4) / .1 if measure == "continuous" else (d.trump_share > .5).astype(float)
    cols = []
    for p in P:
        if p == REF:
            continue
        d["b%d" % p] = d.W * d.period.eq(p)
        d["d%d" % p] = d["b%d" % p] * z
        cols += ["b%d" % p, "d%d" % p]
    f = Fit(d, "mean", cols, ["gmap_id", "cb"])

    def series(parts):
        out = []
        for p in P:
            terms = {}
            for pre in PRE:
                for pref in parts:
                    if pre != REF:
                        terms[pref + str(pre)] = terms.get(pref + str(pre), 0) - 1 / len(PRE)
            if p != REF:
                for pref in parts:
                    terms[pref + str(p)] = terms.get(pref + str(p), 0) + 1
            out.append(f.lin(**terms))
        return pd.DataFrame(out).assign(period=P, mid=mid, start=edges[:-1])
    return f, series


f_c, ser_c = profile("continuous")
slope = ser_c(["d"])
f_m, ser_m = profile("majority")
other, major = ser_m(["b"]), ser_m(["b", "d"])
slope.assign(series="per 10 pts Trump share").to_csv(OUT / "figure6_data_slope.csv", index=False)
pd.concat([other.assign(series="Trump share 50% or less"), major.assign(series="Trump share above 50%")]).to_csv(OUT / "figure6_data_groups.csv", index=False)
per = c.drop_duplicates("gmap_id")
print("restaurants: %d WPME, %d ME; in Trump-majority counties: %d WPME, %d ME" % (per.W.sum(), (1 - per.W).sum(), (per.W * (per.trump_share > .5)).sum(), ((1 - per.W) * (per.trump_share > .5)).sum()))
print(slope[["start", "est", "se", "p"]].round(3).to_string(index=False))
print(major[["start", "est", "se", "p"]].round(3).to_string(index=False))

fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.9), facecolor=SURF)
for ax in axes:
    clean(ax)
    ax.axhline(0, color=MUTED, lw=1)
    for a, b_, lab in [(edges[5], edges[6], "after the\nelection"), (edges[7], edges[8], "after the\ntravel ban")]:
        ax.axvspan(a, b_, color="#f0efec", zorder=0)
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[5, 7, 9, 11, 1, 3]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
    ax.set_xlim(edges[0], edges[-1])
ax = axes[0]
ax.fill_between(slope.mid, slope.est - 1.96 * slope.se, slope.est + 1.96 * slope.se, color=BLUE, alpha=.13, lw=0)
ax.plot(slope.mid, slope.est, color=BLUE, lw=2.1, marker="o", ms=6, mec=SURF, mew=1.2)
ax.set_ylim(-0.11, 0.13)
for a, lab in [(edges[5], "after the\nelection"), (edges[7], "after the\ntravel ban")]:
    ax.text(a + pd.Timedelta(days=3), 0.127, lab, fontsize=7.8, color=MUTED, va="top")
ax.set_ylabel("WPME-minus-ME rating gap\nper 10 points of county Trump share (stars)")
ax.set_title("How much more the gap favors WPME as county Trump share rises", loc="left", fontsize=10, fontweight="bold", pad=8)
ax = axes[1]
ax.fill_between(major.mid, major.est - 1.96 * major.se, major.est + 1.96 * major.se, color=VIOLET, alpha=.12, lw=0)
ax.plot(other.mid, other.est, color=GREY, lw=1.8, marker="o", ms=4.5, mec=SURF, mew=1, label="Counties with Trump share 50% or less")
ax.plot(major.mid, major.est, color=VIOLET, lw=2.1, marker="o", ms=6, mec=SURF, mew=1.2, label="Trump-majority counties")
ax.set_ylim(-0.55, 0.65)
ax.set_ylabel("WPME-minus-ME rating gap (stars)")
ax.set_title("The gap in Trump-majority counties and elsewhere", loc="left", fontsize=10, fontweight="bold", pad=8)
ax.legend(frameon=False, fontsize=8.5, loc="lower left")
fig.suptitle("The rating gap rises after the election and again after the travel ban, and falls about as far in between",
             x=0.01, ha="left", fontsize=11.5, fontweight="bold", y=0.985)
fig.text(0.01, 0.012, "Periods of about six weeks, April 2016 to July 2017. Each series is relative to its own average over the five pre-election periods. Restaurant and county-by-period fixed effects;\n"
         "county-clustered 95%% bands. Trump-majority counties: %d WPME and %d ME restaurants." % ((per.W * (per.trump_share > .5)).sum(), ((1 - per.W) * (per.trump_share > .5)).sum()), fontsize=7.6, color=MUTED, va="bottom")
fig.tight_layout(rect=(0, 0.065, 1, 0.93), w_pad=2.5)
fig.savefig(OUT / "figure6_gap_over_time.png", dpi=150, facecolor=SURF)
print("figures saved")
