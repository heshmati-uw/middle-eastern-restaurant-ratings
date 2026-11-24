"""Publication figures (vector PDF and 600 dpi PNG) in outputs/publication/. No titles inside the figures; captions are in FIGURE_CAPTIONS.md.

Usage: python 30_publication_figures.py          (Figure 2, the map, is drawn by 31_publication_map.R)
Figure 1  Positioning: first Google category of businesses with a baba ghanoush mention; share WPME by county Middle Eastern ancestry.
Figure 3  Change in rating after each event by county Trump share, ME and WPME relative to American-first restaurants (lead result).
Figure 4  Each group's Trump-share gradient over time, April 2016 - July 2017.
Figure 5  Change in the share of reviews at each star level, by event.
Figure A1 The lead estimate under alternative specifications (from 25_verify_with_fixest.R and 19_star_breakdown_leniency.py).
All models: restaurant and county-by-period fixed effects, county-clustered 95% intervals, restaurant-period cells weighted equally.
Style: Arial 8 pt, 6.5 in wide, color plus line style/marker so the groups are distinguishable in grayscale.
"""
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from common import FROZEN, OUT, Fit

PUB = OUT / "publication"
PUB.mkdir(exist_ok=True)
INK, GREY, LIGHT, ME_C, WP_C = "#000000", "#6b6b6b", "#d9d9d9", "#c8501e", "#1f5fae"
plt.rcParams.update({"font.family": "Arial", "font.size": 8, "axes.linewidth": 0.6, "axes.edgecolor": INK, "text.color": INK, "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
                     "xtick.major.width": 0.6, "ytick.major.width": 0.6, "xtick.major.size": 3, "ytick.major.size": 3, "pdf.fonttype": 42, "ps.fonttype": 42, "savefig.facecolor": "white",
                     "figure.facecolor": "white", "axes.facecolor": "white", "legend.frameon": False, "legend.fontsize": 8, "hatch.linewidth": 0.5})
ME_L, WP_L = "Explicitly Middle Eastern", "Broadly positioned (Mediterranean)"
STY = {"ME": dict(color=ME_C, ls="-", marker="o"), "WP": dict(color=WP_C, ls=(0, (5, 2)), marker="s")}
R = lambda n: pd.read_csv(OUT / n)
fp = lambda v: "p < .01" if v < .01 else "p = %.2f" % v
fe = lambda v: ("%+.3f" % v).replace("-", "−")


def tidy(ax):
    for sp in ["top", "right"]:
        ax.spines[sp].set_visible(False)


def panel(ax, letter, text):
    ax.set_title("%s  %s" % (letter, text), loc="left", fontsize=8.5, fontweight="bold", pad=6)


def save(fig, name):
    fig.savefig(PUB / (name + ".pdf"))
    fig.savefig(PUB / (name + ".png"), dpi=600)
    plt.close(fig)
    print("saved", name)


# ================= Figure 1
cats = R("desc_first_categories_baba.csv").head(8).iloc[::-1]
bins = R("exhibit1_label_choice_bins.csv").query("me_list == 'national' and by == 'mena'")
fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.5, 2.7), gridspec_kw={"width_ratios": [1.15, 1]})
is_med, is_me = cats.first_category.str.contains("Mediterranean"), cats.first_category.str.contains("Middle Eastern|Lebanese|Turkish|Persian")
cols = np.where(is_med, WP_C, np.where(is_me, ME_C, LIGHT))
bars = a1.barh(cats.first_category.str.replace(" restaurant", "", regex=False).str.replace("^Restaurant$", "Restaurant (no cuisine)", regex=True), cats.share_pct, color=cols, edgecolor=INK, lw=0.4, height=0.68)
for b_, m_ in zip(bars, is_med):
    if m_:
        b_.set_hatch("///")
for v, y in zip(cats.share_pct, range(len(cats))):
    a1.text(v + 0.8, y, "%.0f%%" % v, va="center", fontsize=7.5)
a1.set_xlim(0, 47); a1.set_xlabel("Share of businesses (%)"); tidy(a1); a1.tick_params(axis="y", length=0)
panel(a1, "A", "First Google category")
x = np.arange(len(bins))
a2.errorbar(x, 100 * bins.share_wpme, yerr=100 * 1.96 * bins.se, fmt="o", color=INK, ms=4.5, lw=0.9, capsize=2.5, mfc=WP_C, mec=INK, mew=0.5)
a2.plot(x, 100 * bins.share_wpme, color=INK, lw=0.7, zorder=1)
a2.set_xticks(x); a2.set_xticklabels([b.replace("under ", "<").replace("over ", ">").replace("%", "") for b in bins.bin])
a2.set_xlabel("County residents of Middle Eastern ancestry (%)"); a2.set_ylabel("Positioned as Mediterranean (%)"); a2.set_ylim(20, 80); tidy(a2)
panel(a2, "B", "Positioning by local community")
fig.tight_layout(w_pad=2.2)
save(fig, "figure1_positioning")
n_baba = int(R("desc_first_categories_baba.csv").restaurants.sum())

# ================= Figure 3: change in rating after each event by Trump share
s = pd.read_csv(FROZEN / "restaurants.csv", dtype={"county_fips": str}).dropna(subset=["trump_share"])
g3 = s[s.wpme | s.me_national | s.american][["gmap_id", "county_fips", "trump_share", "wpme", "me_national"]]
tl = pd.read_csv(FROZEN / "timeline_cells.csv.gz").merge(g3, on="gmap_id")
tl["cb"] = tl.county_fips + "_" + tl.bin.astype(str)
tl["WP"], tl["ME"] = tl.wpme.astype(float), (tl.me_national & ~tl.wpme).astype(float)
z = (tl.trump_share - .4) / .1
EV = [("b", 200, "After the travel ban (January 27, 2017)"), ("e", 100, "After the election (November 8, 2016)")]
cols3 = []
for g in ["ME", "WP"]:
    for k, bn, _ in EV:
        tl[g + k], tl[g + k + "Z"] = tl[g] * tl.bin.eq(bn), tl[g] * tl.bin.eq(bn) * z
        cols3 += [g + k, g + k + "Z"]
f3 = Fit(tl, "mean", cols3, ["gmap_id", "cb"])
n3 = dict(obs=f3.n, counties=f3.G, me=int(tl[tl.ME.eq(1)].gmap_id.nunique()), wp=int(tl[tl.WP.eq(1)].gmap_id.nunique()), am=int(tl[(tl.ME + tl.WP).eq(0)].gmap_id.nunique()))
xs = np.linspace(.15, .70, 56)
fig, axes = plt.subplots(1, 2, figsize=(6.5, 2.9), sharey=True)
slopes = {}
for ax, (k, bn, ttl), letter in zip(axes, EV, "AB"):
    ax.axhline(0, color=INK, lw=0.6)
    for g, lab in [("ME", ME_L), ("WP", WP_L)]:
        fit = [f3.lin(**{g + k: 1, g + k + "Z": (x_ - .4) / .1}) for x_ in xs]
        est, se = np.array([q["est"] for q in fit]), np.array([q["se"] for q in fit])
        ax.fill_between(100 * xs, est - 1.96 * se, est + 1.96 * se, color=STY[g]["color"], alpha=.16, lw=0)
        ax.plot(100 * xs, est, color=STY[g]["color"], ls=STY[g]["ls"], lw=1.6, label=lab)
        slopes[(g, k)] = f3.lin(**{g + k + "Z": 1})
    ax.set_xlim(15, 70); ax.set_ylim(-0.32, 0.22); ax.set_xlabel("County 2016 Trump vote share (%)"); tidy(ax)
    panel(ax, letter, ttl)
    ax.text(0.03, 0.05, "Slope per 10 points\n%s: %s (%s)\n%s: %s (%s)" % ("Explicit", fe(slopes[("ME", k)]["est"]), fp(slopes[("ME", k)]["p"]), "Broad", fe(slopes[("WP", k)]["est"]), fp(slopes[("WP", k)]["p"])),
            transform=ax.transAxes, fontsize=7.2, va="bottom", ha="left")
axes[0].set_ylabel("Change in mean rating relative to\nAmerican restaurants (stars)")
axes[1].legend(loc="upper right", handlelength=2.6)
fig.tight_layout(w_pad=1.5)
save(fig, "figure3_rating_change_by_trump_share")

# ================= Figure 4: each group over time
f7 = R("figure7_data.csv")
ser = f7[f7.period.astype(str).str.fullmatch(r"\d+")].copy()
ser["mid"], ser["start"] = pd.to_datetime(ser["mid"]), pd.to_datetime(ser["start"])
E1, E2, SPAN = pd.Timestamp("2016-11-08"), pd.Timestamp("2017-01-27"), pd.Timedelta(days=42)
fig, axes = plt.subplots(2, 1, figsize=(6.5, 4.3), sharex=True, sharey=True)
for ax, (key, g, lab), letter in zip(axes, [("ME vs American", "ME", ME_L), ("WPME vs American", "WP", WP_L)], "AB"):
    d = ser[ser.series.eq(key)]
    for a_ in [E1, E2]:
        ax.axvspan(a_, a_ + SPAN, color="#ececec", zorder=0, lw=0)
    ax.axhline(0, color=INK, lw=0.6)
    ax.fill_between(d.mid, d.est - 1.96 * d.se, d.est + 1.96 * d.se, color=STY[g]["color"], alpha=.16, lw=0)
    ax.plot(d.mid, d.est, color=STY[g]["color"], ls=STY[g]["ls"], lw=1.5, marker=STY[g]["marker"], ms=4, mfc="white", mew=1)
    ax.set_ylim(-0.085, 0.085); tidy(ax); panel(ax, letter, lab)
    ax.set_ylabel("Rating gradient per 10 points\nof Trump share (stars)")
axes[0].text(E1 + pd.Timedelta(days=2), 0.081, "Election", fontsize=7.2, va="top"); axes[0].text(E2 + pd.Timedelta(days=2), 0.081, "Travel ban", fontsize=7.2, va="top")
axes[1].xaxis.set_major_locator(mdates.MonthLocator(bymonth=[5, 7, 9, 11, 1, 3])); axes[1].xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
axes[1].set_xlim(pd.Timestamp("2016-04-12"), pd.Timestamp("2017-07-14"))
fig.tight_layout(h_pad=1.2)
save(fig, "figure4_each_group_over_time")

# ================= Figure 5: star shares by event
sc = pd.read_csv(FROZEN / "star_cells.csv.gz").merge(g3, on="gmap_id")
sc["n"] = sc[["n1", "n2", "n3", "n4", "n5"]].sum(axis=1)
sc["cb"] = sc.county_fips + "_" + sc.bin.astype(str)
sc["WP"], sc["ME"] = sc.wpme.astype(float), (sc.me_national & ~sc.wpme).astype(float)
zs = (sc.trump_share - .4) / .1
for g in ["ME", "WP"]:
    for k, bn, _ in EV:
        sc[g + k], sc[g + k + "Z"] = sc[g] * sc.bin.eq(bn), sc[g] * sc.bin.eq(bn) * zs
rows5 = []
for st in range(1, 6):
    sc["y"] = sc["n%d" % st] / sc.n
    f = Fit(sc, "y", cols3, ["gmap_id", "cb"])
    for g in ["ME", "WP"]:
        for k, _, ttl in EV:
            rows5.append(dict(stars=st, group=g, event=k, **f.lin(**{g + k + "Z": 1})))
r5 = pd.DataFrame(rows5)
r5.to_csv(PUB / "figure5_data.csv", index=False)
fig, axes = plt.subplots(1, 2, figsize=(6.5, 2.8), sharey=True)
xx = np.arange(5)
for ax, (k, bn, ttl), letter in zip(axes, EV, "AB"):
    ax.axhline(0, color=INK, lw=0.6)
    for g, lab, off, hatch in [("ME", ME_L, -0.19, None), ("WP", WP_L, 0.19, "///")]:
        d = r5[(r5.group == g) & (r5.event == k)].sort_values("stars")
        ax.bar(xx + off, 100 * d.est, width=0.34, color=STY[g]["color"], edgecolor=INK, lw=0.4, hatch=hatch, label=lab, alpha=0.9)
        ax.errorbar(xx + off, 100 * d.est, yerr=100 * 1.96 * d.se, fmt="none", ecolor=INK, elinewidth=0.8, capsize=2)
    ax.set_xticks(xx); ax.set_xticklabels(["1 star", "2 stars", "3 stars", "4 stars", "5 stars"]); tidy(ax); ax.tick_params(axis="x", length=0)
    panel(ax, letter, ttl)
axes[0].set_ylabel("Change in share of reviews per 10 points\nof Trump share (percentage points)")
axes[1].legend(loc="lower left", handlelength=1.6)
fig.tight_layout(w_pad=1.5)
save(fig, "figure5_star_shares")

# ================= Figure A1: the lead estimate under alternative specifications
rb = R("verification_robustness.csv")
ln = R("desc_star_breakdown_leniency.csv")
lrow = ln[(ln.spec == "relative to the reviewer's usual | travel ban") & (ln.outcome == "mean rating") & (ln.group == "ME")].iloc[0]
order = [("as reported (each restaurant-period equal weight; county clusters)", "As reported"), ("original 20-category ME list", "Original 20-category list of explicit labels"),
         ("clustered by state", "Standard errors clustered by state"), ("state-by-period FE instead of county-by-period", "State-by-period fixed effects"),
         ("restaurant and period FE only (no county-by-period FE)", "Restaurant and period fixed effects only"), ("LEN", "Rating relative to each reviewer's usual"),
         ("cells with 3 or more reviews", "Restaurant-periods with 3 or more reviews"), ("weighted by number of reviews in the cell", "Weighted by number of reviews")]
pts = []
for key, lab in order:
    x_ = lrow if key == "LEN" else rb[(rb.variant == key) & (rb.term == "MEgBZ")].iloc[0]
    pts.append((lab, x_.est, x_.se, x_.p))
fig, ax = plt.subplots(figsize=(6.5, 2.9))
yy = np.arange(len(pts))[::-1]
ax.axvline(0, color=INK, lw=0.6)
ax.errorbar([p_[1] for p_ in pts], yy, xerr=[1.96 * p_[2] for p_ in pts], fmt="o", color=INK, ms=4.5, mfc=ME_C, mec=INK, mew=0.5, lw=0.9, capsize=2.5)
for y_, p_ in zip(yy, pts):
    ax.text(0.047, y_, "%s (%s)" % (fe(p_[1]), fp(p_[3])), va="center", fontsize=7.3)
ax.set_yticks(yy); ax.set_yticklabels([p_[0] for p_ in pts]); ax.tick_params(axis="y", length=0)
ax.set_xlim(-0.075, 0.085); ax.set_xticks([-0.06, -0.04, -0.02, 0, 0.02, 0.04])
ax.set_xlabel("Change in mean rating of explicitly Middle Eastern restaurants after the travel ban,\nper 10 points of county Trump share (stars)"); tidy(ax)
fig.tight_layout()
save(fig, "figureA1_specifications")

# ================= captions
cap = """# Figure captions

**Figure 1. How restaurants serving Middle Eastern food position themselves.** (A) First Google category of the %s businesses whose reviews mention baba ghanoush; the eight most common categories are shown. Hatched bar: Mediterranean. (B) Share of restaurants positioned as Mediterranean rather than under an explicit Middle Eastern label, by the percentage of county residents reporting Middle Eastern ancestry (American Community Survey, 2017-2021). Bars are 95%% confidence intervals from county-clustered standard errors.

**Figure 2. Geography of broad positioning.** Each circle is a county with five or more restaurants in the sample; area is proportional to the number of restaurants, and shading shows the share positioned as Mediterranean. Drawn by `31_publication_map.R`.

**Figure 3. Rating changes after the travel ban and the 2016 election, by county Trump vote share.** Lines show the estimated change in mean rating in the six weeks after each event, relative to the 210 days before the election and to American restaurants in the same county and period, as a linear function of the county's 2016 Trump vote share. Shaded areas are 95%% confidence intervals. Restaurant and county-by-period fixed effects; standard errors clustered by county. %s restaurant-period observations; %s explicitly Middle Eastern, %s broadly positioned and %s American restaurants in %s counties.

**Figure 4. Rating gradient in county Trump vote share over time.** Each point is the estimated difference in mean rating per 10 percentage points of county Trump vote share, relative to American restaurants in the same county and period, in consecutive periods of about six weeks from April 2016 to July 2017. Estimates are relative to the group's average over the five pre-election periods. Grey bands mark the six weeks after the election and after the travel ban. Shaded areas are 95%% confidence intervals; standard errors clustered by county.

**Figure 5. Which star ratings change.** Change in the share of a restaurant's reviews at each star level per 10 percentage points of county Trump vote share, in the six weeks after each event, relative to American restaurants in the same county and period. Bars are 95%% confidence intervals; standard errors clustered by county. Within a group and event the five estimates sum to zero.

**Figure A1. The travel-ban estimate under alternative specifications.** Each row re-estimates the coefficient on explicitly Middle Eastern x after the travel ban x county Trump vote share (per 10 points) from the model in Figure 3. Bars are 95%% confidence intervals. The estimate is stable across fixed-effect structures, clustering, the definition of explicit labels and an adjustment for each reviewer's usual rating; it is about one third as large and not statistically significant when restaurant-periods are weighted by their number of reviews or restricted to those with three or more reviews.
""" % (format(n_baba, ","), format(n3["obs"], ","), format(n3["me"], ","), format(n3["wp"], ","), format(n3["am"], ","), format(n3["counties"], ","))
(PUB / "FIGURE_CAPTIONS.md").write_text(cap, encoding="utf-8")
print(n3, {k: (round(v["est"], 4), round(v["p"], 3)) for k, v in slopes.items()})
print(r5[r5.stars.eq(1)].round(4).to_string(index=False))
