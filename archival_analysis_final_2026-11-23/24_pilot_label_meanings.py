"""Pilot survey (Prolific, November 2026; run by Susie Choe): what the labels "Middle Eastern" and "Mediterranean" mean to people.

Usage: python 24_pilot_label_meanings.py [path to the Qualtrics export]
Default export path: built/pilot_export.csv (local only: it holds Prolific IDs and IP addresses).
101 completed responses. Each respondent rated both restaurant categories on three owner associations (1 "Not at all" to 7 "Very strongly"),
sorted 12 national cuisines into Middle Eastern / Mediterranean / Both / Neither / Not sure, rated overall culinary overlap (1-7),
and reported how often they eat each kind of food.
Writes aggregates only: outputs/pilot_associations.csv, pilot_cuisine_sort.csv, pilot_frequency.csv, pilot_by_party.csv, figure0_pilot.png.
"""
import sys
import numpy as np, pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from common import BUILT, OUT

path = sys.argv[1] if len(sys.argv) > 1 else BUILT / "pilot_export.csv"
d = pd.read_csv(path, skiprows=[1, 2])
num = lambda s: pd.to_numeric(s.replace({"Not at all": 1, "Very strongly": 7}), errors="coerce")
ASSOC = [("WHITE", "Owners perceived as racially White", 1), ("MENA", "Owners of Middle Eastern ancestry", -1), ("EUROPE", "Owners of European ancestry", 1)]
rows, gaps = [], {}
for k, lab, sign in ASSOC:
    me, med = num(d[k + "_1"]), num(d[k + "_2"])
    g = (med - me).dropna()
    t = stats.ttest_1samp(g, 0)
    h = stats.t.ppf(.975, len(g) - 1) * g.std(ddof=1) / np.sqrt(len(g))
    gaps[k] = med - me
    rows.append(dict(association=lab, mean_middle_eastern=me.mean(), mean_mediterranean=med.mean(), se_middle_eastern=me.sem(), se_mediterranean=med.sem(),
                     gap_med_minus_me=g.mean(), ci_low=g.mean() - h, ci_high=g.mean() + h, t=t.statistic, p=t.pvalue, dz=g.mean() / g.std(ddof=1), n=len(g)))
A = pd.DataFrame(rows)
A.to_csv(OUT / "pilot_associations.csv", index=False)

GROUPS = ["Middle Eastern", "Mediterranean", "Both", "Neither", "Not sure"]
cnt = {}
for i, gname in enumerate(GROUPS):
    for cell in d["CUISINE_SORT_%d_GROUP" % i].dropna():
        for c in cell.split(","):
            cnt[(c.strip(), gname)] = cnt.get((c.strip(), gname), 0) + 1
S = pd.Series(cnt).unstack(fill_value=0)[GROUPS]
S = (100 * S.div(S.sum(axis=1), axis=0)).sort_values("Middle Eastern", ascending=False)
S.index.name = "cuisine"
S.to_csv(OUT / "pilot_cuisine_sort.csv")

FREQ = ["Never", "Less than once a year", "A few times a year", "About once a month", "About once a week", "Several times a week"]
F = pd.DataFrame({"Middle Eastern food": d.Q23_1.value_counts(normalize=True), "Mediterranean food": d.Q23_2.value_counts(normalize=True)}).reindex(FREQ).fillna(0) * 100
F.index.name = "how_often"
F.to_csv(OUT / "pilot_frequency.csv")

P = pd.DataFrame({k: gaps[k] for k, _, _ in ASSOC}).assign(party=d.Q5)
P = P[P.party.isin(["Democrat", "Republican", "Independent"])]
pr = P.groupby("party").agg(n=("WHITE", "size"), white_gap=("WHITE", "mean"), me_ancestry_gap=("MENA", lambda x: -x.mean()), european_gap=("EUROPE", "mean"))
for col, k in [("white_gap", "WHITE"), ("me_ancestry_gap", "MENA"), ("european_gap", "EUROPE")]:
    pr.loc["ANOVA p", col] = stats.f_oneway(*[x[k].dropna() for _, x in P.groupby("party")]).pvalue
pr.to_csv(OUT / "pilot_by_party.csv")
ov = pd.to_numeric(d.OVERLAP_1, errors="coerce").dropna()
pd.set_option("display.width", 200)
print("completed responses: %d" % len(d))
print(A.round(3).to_string(index=False)); print(S.round(1).to_string()); print(F.round(1).to_string()); print(pr.round(3).to_string())
print("overlap rating: n %d, mean %.2f, SD %.2f; share 1-3 %.0f%%, 5-7 %.0f%%" % (len(ov), ov.mean(), ov.std(), 100 * (ov <= 3).mean(), 100 * (ov >= 5).mean()))
print("eat less than once a year or never: ME %.0f%%, MED %.0f%%" % (F.iloc[:2, 0].sum(), F.iloc[:2, 1].sum()))

# ---------------- figure
INK, MUTED, GRID, SURF, BLUE, ORANGE, VIOLET = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb", "#2a78d6", "#eb6834", "#6250d6"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": GRID, "text.color": INK, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED})
fig, (a1, a2) = plt.subplots(1, 2, figsize=(12.6, 5.0), facecolor=SURF, gridspec_kw={"width_ratios": [1, 1.25]})
for ax in (a1, a2):
    ax.set_facecolor(SURF); ax.tick_params(length=0)
    for sp in ["top", "right"]:
        ax.spines[sp].set_visible(False)
y = np.arange(len(A))[::-1]
a1.grid(axis="x", color=GRID, lw=0.6)
for col, se, colr, lab, off in [("mean_middle_eastern", "se_middle_eastern", ORANGE, "\"Middle Eastern restaurants\"", 0.17), ("mean_mediterranean", "se_mediterranean", BLUE, "\"Mediterranean restaurants\"", -0.17)]:
    a1.barh(y + off, A[col], height=0.3, color=colr, label=lab, edgecolor=SURF, lw=1.5)
    a1.errorbar(A[col], y + off, xerr=1.96 * A[se], fmt="none", ecolor=INK, elinewidth=1, capsize=2.5)
    for yy, v, s_ in zip(y + off, A[col], A[se]):
        a1.text(v + 1.96 * s_ + 0.1, yy, "%.1f" % v, va="center", fontsize=8.6)
a1.set_yticks(y); a1.set_yticklabels([s.replace("Owners ", "Owners\n") for s in A.association], color=INK)
a1.set_xlim(1, 7); a1.set_xlabel("How strongly the category is associated with... (1 = not at all, 7 = very strongly)")
a1.legend(frameon=False, fontsize=8.4, ncol=2, loc="upper center", bbox_to_anchor=(0.5, -0.13), handlelength=1.2)
a1.set_title("The two labels signal different owners", loc="left", fontsize=10.2, fontweight="bold", pad=8)
order = S.index[::-1]
left = np.zeros(len(order))
for gname, colr in [("Middle Eastern", ORANGE), ("Both", VIOLET), ("Mediterranean", BLUE), ("Neither", "#c9c7c0"), ("Not sure", "#e6e4de")]:
    v = S.loc[order, gname].to_numpy()
    a2.barh(np.arange(len(order)), v, left=left, color=colr, label=gname, edgecolor=SURF, lw=1.5, height=0.72)
    left += v
a2.set_yticks(np.arange(len(order))); a2.set_yticklabels(order, color=INK)
a2.set_xlim(0, 100); a2.set_xlabel("Share of respondents placing the cuisine in each group (%)")
a2.legend(frameon=False, fontsize=8.4, ncol=5, loc="upper center", bbox_to_anchor=(0.5, -0.13), handlelength=1.2, columnspacing=1.2)
a2.set_title("Which national cuisines count as Middle Eastern", loc="left", fontsize=10.2, fontweight="bold", pad=8)
fig.suptitle("Pilot survey: the \"Mediterranean\" label signals far less Middle Eastern ownership",
             x=0.01, ha="left", fontsize=11, fontweight="bold", y=0.985)
fig.text(0.01, 0.01, "Prolific pilot, November 2026, %d respondents. Left: means with 95%% intervals; each respondent rated both categories. Right: each respondent sorted 12 national cuisines." % len(d), fontsize=7.6, color=MUTED, va="bottom")
fig.tight_layout(rect=(0, 0.05, 1, 0.94), w_pad=2.5)
fig.savefig(OUT / "figure0_pilot.png", dpi=150, facecolor=SURF)
print("figure saved")
