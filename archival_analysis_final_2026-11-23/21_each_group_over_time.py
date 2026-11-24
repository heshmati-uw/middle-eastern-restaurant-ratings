"""Figure 7. Each group's rating over time, relative to American-first restaurants: how long does the ME decline last?

Usage: python 21_each_group_over_time.py
Same eleven periods of about six weeks as figure 6 (April 2016 - July 2017), but with American-first restaurants in the same county
and period as the reference group, so ME and WPME are each shown on their own instead of as a gap.
Model: rating ~ restaurant FE + county-by-period FE + {ME, WPME} x period x {1, Trump share per 10 points}.
Plotted: for each group, the Trump-share slope in each period, relative to its own average over the five pre-election periods.
Reads frozen/story_timeline_cells_3group.csv.gz; builds it from built/reviews_exact/ if it is missing.
"""
import glob
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from common import BUILT, FROZEN, OUT, Fit

INK, MUTED, GRID, SURF, BLUE, ORANGE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb", "#2a78d6", "#eb6834"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": GRID, "text.color": INK, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED})
s = pd.read_csv(FROZEN / "restaurants.csv", dtype={"county_fips": str}).dropna(subset=["trump_share"])
STARTS = ["2016-04-12", "2016-05-24", "2016-07-05", "2016-08-16", "2016-09-27", "2016-11-08", "2016-12-20", "2017-01-27", "2017-03-10", "2017-04-21", "2017-06-02", "2017-07-14"]
edges = pd.to_datetime(STARTS)
path = FROZEN / "story_timeline_cells_3group.csv.gz"
if not path.exists():
    ids = set(s[s.wpme | s.me_national | s.me_original | s.american].gmap_id)
    lo, hi = int(edges[0].value // 10**6), int(edges[-1].value // 10**6)
    parts = []
    for f in sorted(glob.glob(str(BUILT / "reviews_exact" / "*.csv.gz"))):
        x = pd.read_csv(f)
        parts.append(x[(x.time_ms >= lo) & (x.time_ms < hi) & x.gmap_id.isin(ids)])
    r = pd.concat(parts, ignore_index=True).drop_duplicates()
    r["period"] = np.searchsorted(edges.values, pd.to_datetime(r.time_ms, unit="ms").values, side="right") - 1
    r.groupby(["gmap_id", "period"]).rating.agg(["mean", "size"]).reset_index().rename(columns={"size": "n"}).to_csv(path, index=False)
c = pd.read_csv(path).merge(s[s.wpme | s.me_national | s.american][["gmap_id", "county_fips", "trump_share", "wpme", "me_national"]], on="gmap_id")
c["cb"] = c.county_fips + "_" + c.period.astype(str)
c["WP"], c["ME"] = c.wpme.astype(float), (c.me_national & ~c.wpme).astype(float)
z = (c.trump_share - .4) / .1
P, PRE, REF = list(range(11)), [0, 1, 2, 3, 4], 4
mid = edges[:-1] + (edges[1:] - edges[:-1]) / 2
cols = []
for g in ["ME", "WP"]:
    for p in P:
        if p == REF:
            continue
        c["%sb%d" % (g, p)] = c[g] * c.period.eq(p)
        c["%sd%d" % (g, p)] = c["%sb%d" % (g, p)] * z
        cols += ["%sb%d" % (g, p), "%sd%d" % (g, p)]
f = Fit(c, "mean", cols, ["gmap_id", "cb"])


def terms(g, p, sign=1.0, t=None):
    """Slope of group g in period p minus its pre-election average."""
    t = {} if t is None else t
    for pre in PRE:
        if pre != REF:
            k = "%sd%d" % (g, pre)
            t[k] = t.get(k, 0) - sign / len(PRE)
    if p != REF:
        k = "%sd%d" % (g, p)
        t[k] = t.get(k, 0) + sign
    return t


rows = []
for g, lab in [("ME", "ME vs American"), ("WP", "WPME vs American")]:
    for p in P:
        rows.append(dict(series=lab, period=p, start=edges[p], mid=mid[p], **f.lin(**terms(g, p))))
for p in P:
    rows.append(dict(series="WPME minus ME", period=p, start=edges[p], mid=mid[p], **f.lin(**terms("ME", p, -1.0, terms("WP", p)))))
# summaries: the two event windows together; the period between; the three later periods together
for g, lab in [("ME", "ME vs American"), ("WP", "WPME vs American")]:
    for nm, ps in [("average of the two event windows", [5, 7]), ("between the events", [6]), ("average of the three later periods", [8, 9, 10])]:
        t = {}
        for p in ps:
            t = terms(g, p, 1.0 / len(ps), t)
        rows.append(dict(series=lab, period=nm, **f.lin(**t)))
for g, lab in [("ME", "ME vs American"), ("WP", "WPME vs American")]:
    # joint test that the four pre-election slopes equal the reference period's (no pre-period movement)
    rows.append(dict(series=lab, period="pre-period joint test (p only)", p=f.joint(["%sd%d" % (g, p) for p in PRE if p != REF])))
res = pd.DataFrame(rows)
res.to_csv(OUT / "figure7_data.csv", index=False)
per = c.drop_duplicates("gmap_id")
print("restaurants: %d ME, %d WPME, %d American; cells %d" % (per.ME.sum(), per.WP.sum(), len(per) - per.ME.sum() - per.WP.sum(), len(c)))
pd.set_option("display.width", 200)
print(res[["series", "period", "est", "se", "p"]].round(3).to_string(index=False))

ser = res[res.period.apply(lambda v: isinstance(v, (int, np.integer)))].copy()
ser["mid"] = pd.to_datetime(ser["mid"])
fig, ax = plt.subplots(figsize=(9.2, 5.0), facecolor=SURF)
ax.set_facecolor(SURF)
ax.grid(axis="y", color=GRID, lw=0.6)
ax.tick_params(length=0)
for sp in ["top", "right"]:
    ax.spines[sp].set_visible(False)
ax.axhline(0, color=MUTED, lw=1)
for a, b_, lab in [(edges[5], edges[6], "after the\nelection"), (edges[7], edges[8], "after the\ntravel ban")]:
    ax.axvspan(a, b_, color="#f0efec", zorder=0)
    ax.text(a + pd.Timedelta(days=3), 0.118, lab, fontsize=7.8, color=MUTED, va="top")
for lab, colr, name in [("ME vs American", ORANGE, "Explicitly Middle Eastern (ME)"), ("WPME vs American", BLUE, "Broadly positioned (WPME)")]:
    d = ser[ser.series.eq(lab)]
    ax.fill_between(d.mid, d.est - 1.96 * d.se, d.est + 1.96 * d.se, color=colr, alpha=.13, lw=0)
    ax.plot(d.mid, d.est, color=colr, lw=2.2, marker="o", ms=5.5, mec=SURF, mew=1.2, label=name)
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[5, 7, 9, 11, 1, 3]))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
ax.set_xlim(edges[0], edges[-1])
ax.set_ylim(-0.12, 0.12)
ax.set_ylabel("Rating relative to American-first restaurants,\nper 10 points of county Trump share (stars)")
ax.legend(frameon=False, fontsize=9, loc="lower left")
fig.suptitle("Each group's rating over time as county Trump share rises, relative to American-first restaurants",
             x=0.01, ha="left", fontsize=11.2, fontweight="bold", y=0.985)
fig.text(0.01, 0.012, "Periods of about six weeks, April 2016 to July 2017. Each line is relative to its own average over the five pre-election periods.\n"
         "Zero line = American-first restaurants in the same county and period. Restaurant and county-by-period fixed effects; county-clustered 95% bands.", fontsize=7.6, color=MUTED, va="bottom")
fig.tight_layout(rect=(0, 0.065, 1, 0.93))
fig.savefig(OUT / "figure7_each_group_over_time.png", dpi=150, facecolor=SURF)
print("figure saved")
