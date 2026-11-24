"""Verification report: compares the Python estimates with the independent fixest (R) re-estimates, and checks the data behind them.

Usage: python 26_verification_report.py     (run 25_verify_with_fixest.R first)
Writes outputs/verification_report.csv (one row per coefficient: Python, fixest, differences) and prints the data checks.
"""
import glob
import numpy as np, pandas as pd
from common import BUILT, FROZEN, OUT, BIN_DAYS

R = lambda n: pd.read_csv(OUT / n)
fx = R("verification_fixest.csv")
lab = R("exhibit1_label_choice.csv").query("me_list == 'national' and trump_measure == 'continuous'").set_index("controls")
ev = R("exhibit3_events.csv").query("me_list == 'national' and trump_measure == 'continuous' and window == 'first 6 weeks'").set_index("event")
wg = R("exhibit3_which_group_moves.csv").query("me_list == 'national'").set_index("quantity")
f7 = R("figure7_data.csv"); f7["period"] = f7.period.astype(str)
g7 = lambda s_, p_: f7[(f7.series == s_) & (f7.period == str(p_))].iloc[0]
st = R("desc_star_breakdown.csv").query("quantity == 'per 10 pts Trump share' and outcome == 'share 1-star'").set_index("group")
ln = R("desc_star_breakdown_leniency.csv").query("outcome == 'mean rating'").set_index(["spec", "group"])
U = "relative to the reviewer's usual | "
PY = {("label choice: state FE only", "Trump share per 10 pts"): (lab.loc["state FE only", "trump_est"], lab.loc["state FE only", "trump_se"]),
      ("label choice: + population, density", "Trump share per 10 pts"): (lab.loc["+ population, density", "trump_est"], lab.loc["+ population, density", "trump_se"]),
      ("label choice: + college, foreign-born", "Trump share per 10 pts"): (lab.loc["+ college, foreign-born", "trump_est"], lab.loc["+ college, foreign-born", "trump_se"]),
      ("label choice: + college, foreign-born", "Middle Eastern ancestry per 1 pt"): (lab.loc["+ college, foreign-born", "mena_est"], lab.loc["+ college, foreign-born", "mena_se"]),
      ("event gap: 2016 election", "WPME x After x Trump share"): (ev.loc["2016 election", "est"], ev.loc["2016 election", "se"]),
      ("event gap: Travel ban", "WPME x After x Trump share"): (ev.loc["Travel ban", "est"], ev.loc["Travel ban", "se"]),
      ("event gap: pooled election and travel ban", "WPME x After x Trump share"): (ev.loc["POOLED: election and travel ban", "est"], ev.loc["POOLED: election and travel ban", "se"]),
      ("which group moves", "ME x after election x Trump share"): tuple(wg.loc["ME vs American: after election, per 10 pts", ["est", "se"]]),
      ("which group moves", "ME x after travel ban x Trump share"): tuple(wg.loc["ME vs American: after travel ban, per 10 pts", ["est", "se"]]),
      ("which group moves", "WPME x after election x Trump share"): tuple(wg.loc["WPME vs American: after election, per 10 pts", ["est", "se"]]),
      ("which group moves", "WPME x after travel ban x Trump share"): tuple(wg.loc["WPME vs American: after travel ban, per 10 pts", ["est", "se"]]),
      ("which group moves", "ME: average of the two events"): tuple(wg.loc["ME vs American: average, per 10 pts", ["est", "se"]]),
      ("which group moves", "WPME: average of the two events"): tuple(wg.loc["WPME vs American: average, per 10 pts", ["est", "se"]]),
      ("each group over time", "ME: period after election vs pre-election average"): tuple(g7("ME vs American", 5)[["est", "se"]]),
      ("each group over time", "ME: period after travel ban vs pre-election average"): tuple(g7("ME vs American", 7)[["est", "se"]]),
      ("each group over time", "WPME: period after election vs pre-election average"): tuple(g7("WPME vs American", 5)[["est", "se"]]),
      ("each group over time", "WPME: period after travel ban vs pre-election average"): tuple(g7("WPME vs American", 7)[["est", "se"]]),
      ("star breakdown: share 1-star", "ME x After x Trump share"): tuple(st.loc["ME", ["est", "se"]]),
      ("star breakdown: share 1-star", "WPME x After x Trump share"): tuple(st.loc["WPME", ["est", "se"]]),
      ("leniency: rating relative to reviewer's usual", "ME x after travel ban x Trump share"): tuple(ln.loc[(U + "travel ban", "ME"), ["est", "se"]]),
      ("leniency: rating relative to reviewer's usual", "ME x after election x Trump share"): tuple(ln.loc[(U + "election", "ME"), ["est", "se"]]),
      ("leniency: rating relative to reviewer's usual", "WPME x after travel ban x Trump share"): tuple(ln.loc[(U + "travel ban", "WPME"), ["est", "se"]])}
rows = []
for _, x in fx.iterrows():
    k = (x.model, x.term)
    if k in PY:
        e, s_ = PY[k]
        rows.append(dict(model=x.model, term=x.term, python_est=e, fixest_est=x.est, python_se=s_, fixest_se=x.se, est_diff=abs(e - x.est), se_ratio=s_ / x.se, n_obs=x.n))
rep = pd.DataFrame(rows)
rep.to_csv(OUT / "verification_report.csv", index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 60)
print(rep.round(5).to_string(index=False))
print("\ncoefficients compared: %d; largest estimate difference: %.2e; standard-error ratio range: %.4f to %.4f" % (len(rep), rep.est_diff.max(), rep.se_ratio.min(), rep.se_ratio.max()))

# ---------------- data checks
s = pd.read_csv(FROZEN / "restaurants.csv", dtype={"county_fips": str})
print("\nDATA CHECKS")
print("restaurants %d; duplicate ids %d" % (len(s), s.gmap_id.duplicated().sum()))
print("WPME and ME-first at once: %d; WPME without Mediterranean-first or baba: %d; ME (national) that are Mediterranean-first: %d" % (
    (s.wpme & s.me_national).sum(), (s.wpme & ~(s.med_first & s.baba)).sum(), (s.me_national & s.med_first).sum()))
print("American-first overlapping WPME or ME: %d" % (s.american & (s.wpme | s.me_national)).sum())
print("Trump share range %.3f to %.3f; missing for %d of %d WPME/ME" % (s.trump_share.min(), s.trump_share.max(), s[s.wpme | s.me_national].trump_share.isna().sum(), (s.wpme | s.me_national).sum()))
for f, keys in [("timeline_cells", ["gmap_id", "bin"]), ("event_cells", ["gmap_id", "bin", "event", "date"]), ("star_cells", ["gmap_id", "bin"]), ("story_timeline_cells_3group", ["gmap_id", "period"])]:
    d = pd.read_csv(FROZEN / (f + ".csv.gz"))
    m = d["mean"] if "mean" in d else None
    print("%s: %d rows; duplicate keys %d%s" % (f, len(d), d.duplicated(keys).sum(), "" if m is None else "; mean rating within 1-5: %s; min n %d" % (bool(m.between(1, 5).all()), d.n.min())))
tl, sc = pd.read_csv(FROZEN / "timeline_cells.csv.gz"), pd.read_csv(FROZEN / "star_cells.csv.gz")
sc["n"] = sc[["n1", "n2", "n3", "n4", "n5"]].sum(axis=1)
sc["mean"] = sum(k * sc["n%d" % k] for k in range(1, 6)) / sc.n
m = tl.merge(sc, on=["gmap_id", "bin"], suffixes=("", "_star"))
print("timeline cells vs star cells (built separately): %d matched cells; max difference in mean rating %.2e; review counts equal: %s" % (len(m), (m["mean"] - m.mean_star).abs().max(), bool((m.n == m.n_star).all())))
# recompute the after-travel-ban cells straight from the review extract with separate code
files = sorted(glob.glob(str(BUILT / "reviews_exact" / "*.csv.gz")))
if files:
    lo, hi = pd.Timestamp("2017-01-27").value // 10**6, pd.Timestamp("2017-03-10").value // 10**6
    ids = set(tl.gmap_id)
    parts = []
    for f in files:
        x = pd.read_csv(f)
        parts.append(x[(x.time_ms >= lo) & (x.time_ms < hi) & x.gmap_id.isin(ids)])
    r = pd.concat(parts).drop_duplicates()
    chk = r.groupby("gmap_id").rating.agg(["mean", "size"]).reset_index().merge(tl[tl.bin == 200], on="gmap_id", how="outer", suffixes=("_new", ""))
    print("after-travel-ban cells recomputed from the review extract (2017-01-27 to 2017-03-09 UTC): %d cells; unmatched %d; max difference in mean %.2e; counts equal: %s; reviews %d" % (
        len(chk), chk[["mean_new", "mean"]].isna().any(axis=1).sum(), (chk.mean_new - chk["mean"]).abs().max(), bool((chk["size"] == chk.n).all()), int(chk.n.sum())))
