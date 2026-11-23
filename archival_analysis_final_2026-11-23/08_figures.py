"""Figures for the three exhibits. Usage: python 08_figures.py"""
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from common import OUT

INK, MUTED, GRID, SURF, BLUE, ORANGE, GREY = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb", "#2a78d6", "#eb6834", "#a8a69f"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": GRID, "text.color": INK,
                     "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED})
fp = lambda v: "p < .01" if v < .01 else "p = %.2f" % v


def clean(ax, grid="y"):
    ax.set_facecolor(SURF)
    ax.grid(axis=grid, color=GRID, lw=0.6)
    ax.tick_params(length=0)
    for sp in ["top", "right"]:
        ax.spines[sp].set_visible(False)


# ---------------- Figure 1: label choice
b = pd.read_csv(OUT / "exhibit1_label_choice_bins.csv")
b = b[b.me_list.eq("national")]
m = pd.read_csv(OUT / "exhibit1_label_choice.csv")
m = m[m.me_list.eq("national") & m.trump_measure.eq("continuous")].set_index("controls")
fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), sharey=True, facecolor=SURF)
notes = {"mena": "Per 1 pt of Middle Eastern ancestry, with Trump share\nand county controls held fixed: %+.1f pts (%s)" % (100 * m.loc["+ college, foreign-born", "mena_est"], fp(m.loc["+ college, foreign-born", "mena_p"])),
         "trump_share": "Per 10 pts of Trump share:\n  within state  %+.1f pts (%s)\n  with county controls  %+.1f pts (%s)" % (
             100 * m.loc["state FE only", "trump_est"], fp(m.loc["state FE only", "trump_p"]), 100 * m.loc["+ college, foreign-born", "trump_est"], fp(m.loc["+ college, foreign-born", "trump_p"]))}
for ax, (var, xl) in zip(axes, [("mena", "County residents with Middle Eastern ancestry"), ("trump_share", "County 2016 Trump vote share")]):
    clean(ax)
    d = b[b.by.eq(var)].reset_index(drop=True)
    x = np.arange(len(d))
    ax.fill_between(x, 100 * (d.share_wpme - 1.96 * d.se), 100 * (d.share_wpme + 1.96 * d.se), color=BLUE, alpha=.13, lw=0)
    ax.plot(x, 100 * d.share_wpme, color=BLUE, lw=2, marker="o", ms=6, mec=SURF, mew=1.2)
    for xi, (v, n) in enumerate(zip(d.share_wpme, d.n)):
        ax.text(xi, 100 * v + 6, "%.0f%%" % (100 * v), ha="center", fontsize=8.6, color=INK)
        ax.text(xi, 4, "n=%d" % n, ha="center", fontsize=7.5, color=MUTED)
    ax.text(0.03, 0.97, notes[var], transform=ax.transAxes, va="top", ha="left", fontsize=7.9, color=MUTED, linespacing=1.4)
    ax.set_xticks(x)
    ax.set_xticklabels(d.bin, fontsize=8.3)
    ax.set_ylim(0, 112)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_xlabel(xl)
axes[0].set_ylabel('% positioned as "Mediterranean" (WPME)')
fig.suptitle("Broad positioning tracks the local Middle Eastern community, not Trump support", x=0.01, ha="left", fontsize=11.5, fontweight="bold", y=0.985)
fig.text(0.01, 0.012, "Restaurants that are WPME (Mediterranean-first with a baba ghanoush mention) or ME (explicit ME first label, national list). Bands are county-clustered 95% intervals.",
         fontsize=7.6, color=MUTED, va="bottom")
fig.tight_layout(rect=(0, 0.04, 1, 0.94), w_pad=2)
fig.savefig(OUT / "figure1_label_choice.png", dpi=150, facecolor=SURF)
plt.close(fig)

# ---------------- Figure 2: events
r = pd.read_csv(OUT / "exhibit3_events.csv")
r = r[r.me_list.eq("national") & r.trump_measure.eq("continuous") & r.window.eq("first 6 weeks")].set_index("event")
sb = pd.read_csv(OUT / "exhibit3_shared_baseline.csv")
sb = sb[sb.me_list.eq("national") & sb.trump_measure.eq("continuous")].set_index("quantity")
p = pd.read_csv(OUT / "exhibit3_ordinary_dates.csv")
p = p[p.trump_measure.eq("continuous") & ~p.overlaps_event]
ROWS = [("2016 election  (Nov 8, 2016)", r.loc["2016 election"]), ("Travel ban  (Jan 27, 2017)", r.loc["Travel ban"]), None,
        ("Both events pooled", r.loc["POOLED: election and travel ban"]), ("Both events, shared pre-election baseline", sb.loc["delta: average of the two"])]
fig, ax = plt.subplots(figsize=(9.5, 5.2), facecolor=SURF)
clean(ax, "x")
ax.spines["left"].set_visible(False)
lo, hi = p.est.min(), p.est.max()
ax.axvspan(lo, hi, color="#f0efec", zorder=0)
ax.axvline(0, color=MUTED, lw=0.8, zorder=1)
y, ticks, labs = len(ROWS), [], []
for item in ROWS:
    y -= 1
    if item is None:
        ax.axhline(y, color=GRID, lw=0.8)
        continue
    lab, row = item
    pooled = lab.startswith("Both")
    ax.plot([row.est - 1.96 * row.se, row.est + 1.96 * row.se], [y, y], color=BLUE, lw=2.2, alpha=.55, solid_capstyle="round", zorder=2)
    ax.scatter([row.est], [y], s=70 if pooled else 48, marker="D" if pooled else "o", color=BLUE, edgecolor=SURF, linewidth=1.2, zorder=3)
    ax.text(0.112, y, "%+.3f   %s" % (row.est, fp(row.p)), va="center", fontsize=8.6, color=MUTED)
    ticks.append(y)
    labs.append(lab)
ax.scatter(p.est, np.full(len(p), -1.1), s=22, color=GREY, edgecolor=SURF, linewidth=0.8, zorder=3)
ticks.append(-1.1)
labs.append("%d ordinary dates (no event)" % len(p))
ax.text((lo + hi) / 2, len(ROWS) - 0.35, "range of ordinary dates", ha="center", fontsize=7.8, color=MUTED)
ax.set_yticks(ticks)
ax.set_yticklabels(labs, fontsize=9, color=INK)
ax.set_ylim(-1.7, len(ROWS) - 0.1)
ax.set_xlim(-0.06, 0.16)
ax.set_xticks([-0.05, 0, 0.05, 0.10])
ax.set_xlabel("Change in the WPME-minus-ME rating gap per 10 points of county Trump share,\nfirst 6 weeks after the event (stars, 95% interval)")
o = r
fig.suptitle("After the 2016 election and the travel ban, the rating gap shifts toward WPME\nin Trump-leaning counties for about six weeks", x=0.01, ha="left", fontsize=11.5, fontweight="bold", y=0.985)
fig.text(0.01, 0.012, "Exact review dates. Restaurant and county-by-period fixed effects; county-clustered intervals. Before = 210 days preceding each date.\n"
         "Four later events were also tested and are not shown: travel ban 2.0 (%+.3f), travel ban 3.0 (%+.3f), Supreme Court ruling (%+.3f),\n"
         "Soleimani strike (%+.3f); all six pooled: %+.3f." % (o.loc["Travel ban 2.0", "est"], o.loc["Travel ban 3.0", "est"], o.loc["Supreme Court ruling", "est"],
                                                              o.loc["Soleimani strike", "est"], o.loc["POOLED: all six events", "est"]), fontsize=7.6, color=MUTED, va="bottom")
fig.tight_layout(rect=(0, 0.085, 1, 0.9))
fig.savefig(OUT / "figure2_events.png", dpi=150, facecolor=SURF)
plt.close(fig)

# ---------------- Figure 3: which group moves
w = pd.read_csv(OUT / "exhibit3_which_group_moves.csv")
w = w[w.me_list.eq("national")].set_index("quantity")
fig, ax = plt.subplots(figsize=(8.2, 3.6), facecolor=SURF)
clean(ax, "x")
ax.spines["left"].set_visible(False)
ax.axvline(0, color=MUTED, lw=0.8)
items = [("Explicitly Middle Eastern (ME)", "ME vs American: average, per 10 pts", ORANGE), ("Broadly positioned (WPME)", "WPME vs American: average, per 10 pts", BLUE)]
for i, (lab, key, colr) in enumerate(items):
    row, yy = w.loc[key], 1 - i
    ax.plot([row.est - 1.96 * row.se, row.est + 1.96 * row.se], [yy, yy], color=colr, lw=2.4, alpha=.55, solid_capstyle="round")
    ax.scatter([row.est], [yy], s=60, color=colr, edgecolor=SURF, linewidth=1.2, zorder=3)
    ax.text(0.047, yy, "%+.3f   %s" % (row.est, fp(row.p)), va="center", fontsize=8.8, color=MUTED)
ax.set_yticks([1, 0])
ax.set_yticklabels([i[0] for i in items], fontsize=9.2, color=INK)
ax.set_ylim(-0.6, 1.6)
ax.set_xlim(-0.07, 0.075)
ax.set_xlabel("Change in rating relative to American-first restaurants in the same county,\nper 10 points of Trump share, six weeks after the election and the travel ban (stars, 95% interval)")
fig.suptitle("The shift comes from ratings of explicitly Middle Eastern restaurants falling", x=0.01, ha="left", fontsize=11.5, fontweight="bold", y=0.97)
fig.tight_layout(rect=(0, 0, 1, 0.92))
fig.savefig(OUT / "figure3_which_group_moves.png", dpi=150, facecolor=SURF)
print("figures saved")
