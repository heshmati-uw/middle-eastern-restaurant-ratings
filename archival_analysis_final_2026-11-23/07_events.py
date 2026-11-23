"""Exhibit 3. Stigma events: does the WPME-minus-ME rating gap shift in more Trump-leaning counties after the 2016 election and the travel ban?

Usage: python 07_events.py
Unit: restaurant x 42-day period. Outcome: mean rating of the restaurant's reviews dated in the period (exact timestamps, UTC).
Model for one event:  rating = restaurant FE + county-by-period FE + beta WPME x After + delta WPME x After x Trump measure.
After = the 42 days starting on the event date; before = the 210 days preceding it (five periods). County-clustered SEs. delta is reported.
Parts:
  A  each of six events, first 6 weeks and weeks 7-18, with a pre-period test
  B  pooled: the two focus events stacked, with event-specific fixed effects (also all six, for the appendix)
  C  shared baseline: one timeline; before = 210 days before the election; separate deltas after the election and after the ban, and their average
  D  which group moves: American-first restaurants in the same county and period as the reference group
  E  gap levels in each window (restaurant mean rating in the window; county FE)
  F  ordinary dates: the same model on dates with no event
"""
import numpy as np, pandas as pd
from common import FROZEN, OUT, ME_LISTS, FOCUS, OTHER, EVENTS, BIN_DAYS, Fit, zscore

s = pd.read_csv(FROZEN / "restaurants.csv", dtype={"county_fips": str, "state_fips": str}).dropna(subset=["trump_share"])
ev = pd.read_csv(FROZEN / "event_cells.csv.gz")
tl = pd.read_csv(FROZEN / "timeline_cells.csv.gz")
MEASURES = ["continuous", "majority"]


def did(c, post_bins, measure, fe=("gmap_id", "cb")):
    d = c[c.bin.lt(0) | c.bin.isin(post_bins)].copy()
    d["WP"] = d.W * d.bin.ge(0)
    d["WPZ"] = d.WP * zscore(d.trump_share, measure)
    f = Fit(d, "mean", ["WP", "WPZ"], list(fe))
    return dict(**f.lin(WPZ=1), restaurants=d.gmap_id.nunique(), counties=f.G, reviews_after=int(d[d.bin.ge(0)].n.sum()))


def pretest(c, measure):
    d = c[c.bin.lt(0)].copy()
    z = zscore(d.trump_share, measure)
    cols = []
    for bn in [-5, -4, -2, -1]:
        d["g%d" % bn] = d.W * d.bin.eq(bn)
        d["z%d" % bn] = d["g%d" % bn] * z
        cols += ["g%d" % bn, "z%d" % bn]
    return Fit(d, "mean", cols, ["gmap_id", "cb"]).joint([k for k in cols if k.startswith("z")])


A, C, Dc, E, F_ = [], [], [], [], []
for lname, col in ME_LISTS.items():
    g = s[s.wpme | s[col]][["gmap_id", "county_fips", "trump_share"]].assign(W=s[s.wpme | s[col]].wpme.astype(float).to_numpy())
    cells = ev.merge(g, on="gmap_id", how="inner")
    cells["cb"] = cells.county_fips + "_" + cells.bin.astype(str)
    stack = {}
    # ---- A: each event
    for name, date in EVENTS:
        c = cells[cells.kind.eq("event") & cells.event.eq(name)]
        stack[name] = c
        for m in MEASURES:
            pt = pretest(c, m)
            for wl, pb in [("first 6 weeks", [0]), ("weeks 7-18", [1, 2])]:
                A.append(dict(me_list=lname, event=name, date=date, trump_measure=m, window=wl, pretrend_p=pt, **did(c, pb, m)))
    # ---- B: pooled
    for lab, names in [("POOLED: election and travel ban", [n for n, _ in FOCUS]), ("POOLED: all six events", [n for n, _ in EVENTS])]:
        st = pd.concat([stack[n] for n in names], ignore_index=True)
        st["rid"] = st.gmap_id + "|" + st.event
        st["cbe"] = st.cb + "|" + st.event
        for m in MEASURES:
            for wl, pb in [("first 6 weeks", [0]), ("weeks 7-18", [1, 2])]:
                A.append(dict(me_list=lname, event=lab, date="", trump_measure=m, window=wl, pretrend_p=np.nan, **did(st, pb, m, fe=("rid", "cbe"))))
    # ---- C: shared baseline
    t2 = tl.merge(g, on="gmap_id", how="inner")
    t2["cb"] = t2.county_fips + "_" + t2.bin.astype(str)
    for m in MEASURES:
        z = zscore(t2.trump_share, m)
        t2["E"], t2["B"] = t2.W * t2.bin.eq(100), t2.W * t2.bin.eq(200)
        t2["EZ"], t2["BZ"] = t2.E * z, t2.B * z
        f = Fit(t2, "mean", ["E", "B", "EZ", "BZ"], ["gmap_id", "cb"])
        for nm, terms in [("after election", dict(EZ=1)), ("after travel ban", dict(BZ=1)), ("average of the two", dict(EZ=.5, BZ=.5))]:
            C.append(dict(me_list=lname, trump_measure=m, quantity="delta: " + nm, restaurants=t2.gmap_id.nunique(), counties=f.G, **f.lin(**terms)))
        if m == "continuous":
            for sh in [.2, .3, .4, .5, .6, .7]:
                zz = (sh - .4) / .1
                C.append(dict(me_list=lname, trump_measure=m, quantity="implied change in gap at %d%% Trump share (average of the two)" % round(100 * sh),
                              restaurants=t2.gmap_id.nunique(), counties=f.G, **f.lin(E=.5, B=.5, EZ=zz / 2, BZ=zz / 2)))
    # ---- D: which group moves (American-first reference)
    g3 = s[s.wpme | s[col] | s.american][["gmap_id", "county_fips", "trump_share", "wpme", col]]
    t3 = tl.merge(g3, on="gmap_id", how="inner")
    t3["cb"] = t3.county_fips + "_" + t3.bin.astype(str)
    t3["WPg"], t3["MEg"] = t3.wpme.astype(float), (t3[col] & ~t3.wpme).astype(float)
    z = zscore(t3.trump_share, "continuous")
    cols = []
    for gname in ["MEg", "WPg"]:
        for k, bn in [("E", 100), ("B", 200)]:
            t3[gname + k] = t3[gname] * t3.bin.eq(bn)
            t3[gname + k + "Z"] = t3[gname + k] * z
            cols += [gname + k, gname + k + "Z"]
    f = Fit(t3, "mean", cols, ["gmap_id", "cb"])
    n3 = dict(n_wpme=int(t3[t3.WPg.eq(1)].gmap_id.nunique()), n_me=int(t3[t3.MEg.eq(1)].gmap_id.nunique()), n_american=int(t3[(t3.WPg + t3.MEg).eq(0)].gmap_id.nunique()))
    for nm, terms in [("ME vs American: after election, per 10 pts", dict(MEgEZ=1)), ("ME vs American: after travel ban, per 10 pts", dict(MEgBZ=1)),
                      ("ME vs American: average, per 10 pts", dict(MEgEZ=.5, MEgBZ=.5)),
                      ("WPME vs American: after election, per 10 pts", dict(WPgEZ=1)), ("WPME vs American: after travel ban, per 10 pts", dict(WPgBZ=1)),
                      ("WPME vs American: average, per 10 pts", dict(WPgEZ=.5, WPgBZ=.5)),
                      ("WPME minus ME: average, per 10 pts", dict(WPgEZ=.5, WPgBZ=.5, MEgEZ=-.5, MEgBZ=-.5)),
                      ("ME vs American: average change at 40% Trump share", dict(MEgE=.5, MEgB=.5)), ("WPME vs American: average change at 40% Trump share", dict(WPgE=.5, WPgB=.5)),
                      ("ME vs American: average change at 60% Trump share", dict(MEgE=.5, MEgB=.5, MEgEZ=1, MEgBZ=1)),
                      ("WPME vs American: average change at 60% Trump share", dict(WPgE=.5, WPgB=.5, WPgEZ=1, WPgBZ=1))]:
        Dc.append(dict(me_list=lname, quantity=nm, **n3, **f.lin(**terms)))
    # ---- E: gap levels by window
    t2["win"] = np.where(t2.bin.lt(0), "210 days before the election", np.where(t2.bin.eq(100), "6 weeks after the election", "6 weeks after the travel ban"))
    t2["rs"] = t2["mean"] * t2.n
    for win, dd in t2.groupby("win"):
        d = dd.groupby("gmap_id").agg(rs=("rs", "sum"), n=("n", "sum"), county_fips=("county_fips", "first"), trump_share=("trump_share", "first"), W=("W", "first")).reset_index()
        d["rating"] = d.rs / d.n
        d["WZ"] = d.W * zscore(d.trump_share, "continuous")
        f = Fit(d, "rating", ["W", "WZ"], ["county_fips"])
        E.append(dict(me_list=lname, window=win, quantity="slope per 10 pts", restaurants=len(d), **f.lin(WZ=1)))
        for sh in [.3, .4, .5, .6]:
            E.append(dict(me_list=lname, window=win, quantity="fitted gap at %d%% Trump share" % round(100 * sh), restaurants=len(d), **f.lin(W=1, WZ=(sh - .4) / .1)))
        for gl, mask in [("gap where Trump share is 50% or less", d.trump_share <= .5), ("gap where Trump share is above 50%", d.trump_share > .5)]:
            E.append(dict(me_list=lname, window=win, quantity=gl, restaurants=int(mask.sum()), **Fit(d[mask], "rating", ["W"], ["county_fips"]).lin(W=1)))
    # ---- F: ordinary dates
    if lname == "national":
        real = [pd.Timestamp(d) for _, d in EVENTS]
        span = pd.Timedelta(days=BIN_DAYS)
        for date, c in cells[cells.kind.eq("ordinary")].groupby("date"):
            dt = pd.Timestamp(date)
            overlap = any((dt + span > rr) and (dt < rr + span) for rr in real)
            for m in MEASURES:
                F_.append(dict(date=date, trump_measure=m, overlaps_event=overlap, **did(c, [0], m)))
out = {"exhibit3_events": A, "exhibit3_shared_baseline": C, "exhibit3_which_group_moves": Dc, "exhibit3_gap_levels": E, "exhibit3_ordinary_dates": F_}
for k, v in out.items():
    pd.DataFrame(v).to_csv(OUT / (k + ".csv"), index=False)
pd.set_option("display.width", 230)
pd.set_option("display.max_colwidth", 70)
a = pd.DataFrame(A)
print(a[a.me_list.eq("national") & a.trump_measure.eq("continuous")][["event", "window", "est", "se", "p", "pretrend_p", "restaurants", "reviews_after"]].round(4).to_string(index=False))
print(pd.DataFrame(C)[lambda x: x.me_list.eq("national")][["trump_measure", "quantity", "est", "se", "p"]].round(4).to_string(index=False))
print(pd.DataFrame(Dc)[lambda x: x.me_list.eq("national")][["quantity", "est", "se", "p"]].round(4).to_string(index=False))
q = pd.DataFrame(F_)
q = q[q.trump_measure.eq("continuous") & ~q.overlaps_event]
print("ordinary dates: %d; mean %.4f, SD %.4f, min %.4f, max %.4f, share p<.05 %.2f" % (len(q), q.est.mean(), q.est.std(), q.est.min(), q.est.max(), q.p.lt(.05).mean()))
