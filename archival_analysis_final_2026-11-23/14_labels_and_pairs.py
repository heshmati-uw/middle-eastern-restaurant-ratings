"""Descriptives: (a) how restaurants that serve Middle Eastern food label themselves; (b) example pairs for anecdotes.

Usage: python 14_labels_and_pairs.py <project root>
(a) Among businesses with a baba ghanoush mention in any review (master frame), the first Google category: counts and shares.
(b) Pairs in the same county: one WPME and one ME (national list), both with a baba mention and 50+ reviews,
    review counts within a factor of 3, ranked by distance. Business names come from the master frame; they are public listings.
"""
import sys, pathlib
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from common import FROZEN, OUT, BUILT

ROOT = pathlib.Path(sys.argv[1])
m = pd.read_csv(ROOT / "analysis/2025-08-18-rohan/categorized output/all-states.csv", low_memory=False)
# ---- (a) labels
b = m[m.review_baba.eq(1)].copy()
b["first"] = b.category.fillna("(none)").str.strip()
t = b["first"].value_counts().rename_axis("first_category").reset_index(name="restaurants")
t["share_pct"] = 100 * t.restaurants / len(b)
t.to_csv(OUT / "desc_first_categories_baba.csv", index=False)
print("businesses with a baba ghanoush mention: %d" % len(b))
print(t.head(16).round(1).to_string(index=False))
INK, MUTED, GRID, SURF, BLUE, ORANGE, GREY = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb", "#2a78d6", "#eb6834", "#a8a69f"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": GRID, "text.color": INK, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED})
top = t.head(12).iloc[::-1]
me_words = ["middle eastern", "lebanese", "persian", "turkish", "syrian", "egyptian", "moroccan", "afghan", "armenian", "iraqi", "yemen", "halal", "shawarma", "kebab", "falafel"]
col = [BLUE if "mediterranean" in c.lower() else (ORANGE if any(w in c.lower() for w in me_words) else GREY) for c in top.first_category]
fig, ax = plt.subplots(figsize=(8.4, 4.8), facecolor=SURF)
ax.set_facecolor(SURF)
ax.barh(top.first_category, top.share_pct, color=col, height=0.62)
for y, (v, n) in enumerate(zip(top.share_pct, top.restaurants)):
    ax.text(v + 0.4, y, "%.0f%%  (%d)" % (v, n), va="center", fontsize=8.4, color=MUTED)
ax.set_xlim(0, top.share_pct.max() * 1.22)
ax.set_xlabel("Share of businesses whose reviews mention baba ghanoush (%)")
ax.grid(axis="x", color=GRID, lw=0.6)
ax.tick_params(length=0)
for sp in ["top", "right", "left"]:
    ax.spines[sp].set_visible(False)
ax.tick_params(axis="y", labelsize=9, labelcolor=INK)
fig.suptitle("What restaurants serving baba ghanoush call themselves on Google", x=0.01, ha="left", fontsize=11.5, fontweight="bold", y=0.975)
fig.text(0.01, 0.012, "First Google category, 2021. Blue: Mediterranean. Orange: explicitly Middle Eastern or a related label. Grey: other. Top 12 of %d categories; n = %d." % (len(t), len(b)),
         fontsize=7.6, color=MUTED, va="bottom")
fig.tight_layout(rect=(0, 0.04, 1, 0.94))
fig.savefig(OUT / "desc_first_categories.png", dpi=150, facecolor=SURF)

# ---- (b) example pairs
s = pd.read_csv(FROZEN / "restaurants.csv", dtype={"county_fips": str}).dropna(subset=["trump_share"])
loc = pd.read_csv(BUILT / "sample_restaurants.csv", usecols=["gmap_id", "latitude", "longitude"])
s = s.merge(loc, on="gmap_id").merge(m[["gmap_id", "business_name", "address"]], on="gmap_id", how="left")
s = s[s.baba & s.n_reviews.ge(50)]
W, M = s[s.wpme], s[s.me_national]
p = W.merge(M, on="county_fips", suffixes=("_wpme", "_me"))
p["km"] = 6371 * 2 * np.arcsin(np.sqrt(np.sin(np.radians(p.latitude_me - p.latitude_wpme) / 2) ** 2 + np.cos(np.radians(p.latitude_wpme)) * np.cos(np.radians(p.latitude_me)) * np.sin(np.radians(p.longitude_me - p.longitude_wpme) / 2) ** 2))
p["ratio"] = np.maximum(p.n_reviews_wpme, p.n_reviews_me) / np.minimum(p.n_reviews_wpme, p.n_reviews_me)
p = p[(p.ratio <= 3) & (p.km <= 10)].sort_values("km")
p = p.drop_duplicates("gmap_id_wpme").drop_duplicates("gmap_id_me")
cols = ["county_fips", "trump_share_wpme", "mena_wpme", "business_name_wpme", "first_category_wpme", "mean_rating_wpme", "n_reviews_wpme",
        "business_name_me", "first_category_me", "mean_rating_me", "n_reviews_me", "km", "address_wpme", "address_me"]
p = p[cols].rename(columns={"trump_share_wpme": "trump_share", "mena_wpme": "mena_share"})
p.to_csv(OUT / "desc_example_pairs.csv", index=False)
pd.set_option("display.width", 250)
pd.set_option("display.max_colwidth", 34)
print("\ncandidate pairs within 10 km: %d; in Trump-majority counties: %d" % (len(p), (p.trump_share > .5).sum()))
print(p[p.trump_share > .5].sort_values("km").head(12).drop(columns=["address_wpme", "address_me", "mena_share"]).round(2).to_string(index=False))
