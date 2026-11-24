"""Build RESULTS_SUMMARY.html: every result with its figure, how solid it is, and a recommendation on whether to include it.
Usage: python 20_results_summary_html.py
Numbers are read from the tables in outputs/. Three short review excerpts are read from built/ (local data); if built/ is absent they are skipped.
"""
import base64, html
import numpy as np, pandas as pd
from common import HERE, OUT, BUILT, FROZEN, INPUTS

R = lambda name: pd.read_csv(OUT / name)
fp = lambda v: "p &lt; .001" if v < .001 else ("p &lt; .01" if v < .01 else ("p = %.2f" % v).replace("0.", "."))
fe = lambda v, d=3: (("%+." + str(d) + "f") % v).replace("-", "−")
pct = lambda v: "%.0f%%" % (100 * v)


def img(name, alt):
    b = base64.b64encode((OUT / name).read_bytes()).decode()
    return '<figure><img alt="%s" src="data:image/png;base64,%s"><figcaption>%s</figcaption></figure>' % (html.escape(alt), b, html.escape(name))


def table(head, rows):
    h = "".join("<th>%s</th>" % c for c in head)
    b = "".join("<tr>" + "".join("<td>%s</td>" % c for c in r) + "</tr>" for r in rows)
    return '<div class="tw"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (h, b)


def sec(num, title, rec, body):
    cls = {"Main text": "main", "Appendix": "app", "Leave out": "out", "One sentence": "app"}[rec]
    return '<section id="r%d"><h2><span class="n">%d</span> %s <span class="tag %s">%s</span></h2>%s</section>' % (num, num, title, cls, rec, body)


# ---------------- data
lab = R("exhibit1_label_choice.csv").query("me_list == 'national'")
lc = lambda ctl, m="continuous": lab[(lab.controls == ctl) & (lab.trump_measure == m)].iloc[0]
bins = R("exhibit1_label_choice_bins.csv").query("me_list == 'national' and by == 'mena'")
ev = R("exhibit3_events.csv").query("me_list == 'national'")
E = lambda name, m="continuous", w="first 6 weeks": ev[(ev.event == name) & (ev.trump_measure == m) & (ev.window == w)].iloc[0]
sb = R("exhibit3_shared_baseline.csv").query("me_list == 'national'")
S = lambda q, m="continuous": sb[(sb.quantity == q) & (sb.trump_measure == m)].iloc[0]
wg = R("exhibit3_which_group_moves.csv").query("me_list == 'national'").set_index("quantity")
od = R("exhibit3_ordinary_dates.csv").query("trump_measure == 'continuous' and not overlaps_event")
f6 = R("figure6_data_slope.csv")
f5 = R("figure5_data.csv")
f7 = R("figure7_data.csv")
G7 = lambda series, period: f7[(f7.series == series) & (f7.period.astype(str) == str(period))].iloc[0]
st = R("desc_star_breakdown.csv")
sl = R("desc_star_breakdown_leniency.csv")
L = lambda spec, out, g: sl[(sl.spec == spec) & (sl.outcome == out) & (sl.group == g)].iloc[0]
x4 = R("exhibit4_positioning_over_time.csv").query("me_list == 'national' and comparison == 'WPME vs all ME' and control == 'no review-count control' and window.str.contains('2 years')", engine="python")
cats = R("desc_first_categories_baba.csv")
mp = R("desc_map_county_data.csv")
mp5 = mp[mp.n >= 5]
pairs = R("desc_example_pairs.csv")
pm = R("desc_political_mentions.csv")
idm = R("desc_identity_mentions_by_stars.csv")
idt = R("desc_identity_mentions_me_vs_wpme.csv").set_index("word_list")
rt = R("desc_reviewer_types.csv")
rest = pd.read_csv(FROZEN / "restaurants.csv", dtype={"county_fips": str})
n_wp, n_me = int((rest.wpme & rest.trump_share.notna()).sum()), int((rest.me_national & rest.trump_share.notna()).sum())

parts = []
# ---------------- overview
overview = [
    ("1", "How these restaurants label themselves", "Main text", "Opens the paper: most do not call themselves Middle Eastern"),
    ("2", "Where broad positioning is common (map)", "Main text", "Shows the geography at a glance"),
    ("3", "Label choice tracks the local community", "Main text", "Step 1. Strong and stable"),
    ("4", "Matched pairs in the same county", "Main text", "One pair as the opening anecdote"),
    ("5", "The rating gap shifts after the election and the travel ban", "Main text", "The comparison with WPME. Significant, short-lived, weaker once reviewer leniency is accounted for"),
    ("6", "Each group and the gap over time", "Main text", "Shows the travel-ban dip in ME ratings and how brief it is"),
    ("7", "Which group moves", "Main text", "Step 2, the lead estimate: ME ratings fall, most clearly after the travel ban"),
    ("8", "Star breakdown and reviewer leniency", "Main text", "The ME fall is one-star reviews and survives the leniency control"),
    ("9", "Other events examined", "Appendix", "For completeness"),
    ("10", "Positioning over time", "Appendix", "No shift after the election"),
    ("11", "What reviewers write: identity as the lens", "Main text", "Motivates the experiment; three excerpts"),
    ("12", "Who the reviewers are", "One sentence", "No sign of drive-by reviewing"),
]
cls = {"Main text": "main", "Appendix": "app", "Leave out": "out", "One sentence": "app"}
parts.append("<h2 class='plain'>At a glance</h2>" + table(["#", "Result", "Recommendation", "Why"],
             [[n, '<a href="#r%s">%s</a>' % (n, t), '<span class="tag %s">%s</span>' % (cls[r], r), w] for n, t, r, w in overview]))
_me = lambda q: wg.loc["ME vs American: " + q]
_wp = lambda q: wg.loc["WPME vs American: " + q]
_ban, _elec = "relative to the reviewer's usual | travel ban", "relative to the reviewer's usual | election"
parts.append("<h2 class='plain'>The Step 2 claim</h2>"
    "<p class='rec'>After the January 2017 travel ban, ratings of explicitly Middle Eastern restaurants fell in more Trump-leaning counties, relative to other restaurants in the same county, for about six weeks. "
    "The 2016 election shows a smaller dip in the same direction. Broadly positioned restaurants show no such pattern across counties, though we cannot say they were spared.</p>"
    "<ul><li><b>The travel ban.</b> ME against American-first restaurants in the same county: %s stars per 10 points of Trump share (%s). "
    "It is just as large when each review is measured against that reviewer's usual rating (%s, %s), and one-star reviews rise by %s points (%s).</li>"
    "<li><b>The election.</b> Same direction, smaller: %s (%s). One-star reviews of ME restaurants rise here too (%s points, %s). The two events together: %s (%s).</li>"
    "<li><b>Brief.</b> ME ratings are back to baseline in the months that follow (%s, %s).</li>"
    "<li><b>Broadly positioned restaurants.</b> WPME shows no gradient with Trump share (%s, %s). The WPME-minus-ME difference is not significant once each reviewer's usual rating is accounted for (%s, %s), "
    "and at 40%% Trump share both groups sit below American-first restaurants after the events (WPME %s, %s; ME %s, %s). What sets ME apart is that its decline deepens as Trump share rises.</li>"
    "<li><b>What it means for the paper.</b> The archival study shows a penalty for the explicit label around a stigma event. Whether broad positioning protects against it is what the experiment tests directly.</li></ul>" % (
        fe(_me("after travel ban, per 10 pts").est), fp(_me("after travel ban, per 10 pts").p),
        fe(L(_ban, "mean rating", "ME").est), fp(L(_ban, "mean rating", "ME").p), fe(100 * L(_ban, "share 1-star", "ME").est, 2), fp(L(_ban, "share 1-star", "ME").p),
        fe(_me("after election, per 10 pts").est), fp(_me("after election, per 10 pts").p), fe(100 * L(_elec, "share 1-star", "ME").est, 2), fp(L(_elec, "share 1-star", "ME").p),
        fe(_me("average, per 10 pts").est), fp(_me("average, per 10 pts").p),
        fe(G7("ME vs American", "average of the three later periods").est), fp(G7("ME vs American", "average of the three later periods").p),
        fe(_wp("average, per 10 pts").est), fp(_wp("average, per 10 pts").p),
        fe(L("relative to the reviewer's usual", "mean rating", "WPME minus ME").est), fp(L("relative to the reviewer's usual", "mean rating", "WPME minus ME").p),
        fe(_wp("average change at 40% Trump share").est), fp(_wp("average change at 40% Trump share").p), fe(_me("average change at 40% Trump share").est), fp(_me("average change at 40% Trump share").p)))
parts.append("""<h2 class='plain'>How to read this</h2>
<ul>
<li><b>WPME</b> (broadly positioned): first Google category contains "Mediterranean" and at least one review mentions baba ghanoush. %d restaurants.</li>
<li><b>ME</b> (explicitly positioned): first Google category is Middle Eastern or a national label such as Lebanese, Persian or Turkish. %d restaurants.</li>
<li><b>Trump share</b>: 2016 Trump votes divided by all presidential votes in the restaurant's county. Main measure is per 10 percentage points; the secondary measure is share above 50%%.</li>
<li><b>Event model</b>: each restaurant's mean rating in the 42 days starting on the event date, compared with the 210 days before, with restaurant and county-by-period fixed effects. Exact review dates.</li>
<li>Everything is exploratory; many specifications were examined.</li>
</ul>""" % (n_wp, n_me))

# ---------------- 1
top = cats.head(6)
parts.append(sec(1, "How these restaurants label themselves", "Main text",
    "<p><b>What we did.</b> Took every business whose Google reviews mention baba ghanoush (%d) and tabulated its first Google category.</p>" % cats.restaurants.sum()
    + "<p><b>Result.</b> %s lead with \"Mediterranean restaurant\". Only %s lead with \"Middle Eastern restaurant\" and %s with \"Lebanese restaurant\"; %s use plain \"Restaurant\".</p>" % (
        pct(top.share_pct.iloc[0] / 100), pct(cats[cats.first_category == "Middle Eastern restaurant"].share_pct.iloc[0] / 100),
        pct(cats[cats.first_category == "Lebanese restaurant"].share_pct.iloc[0] / 100), pct(cats[cats.first_category == "Restaurant"].share_pct.iloc[0] / 100))
    + img("desc_first_categories.png", "First Google category of businesses whose reviews mention baba ghanoush")
    + "<p><b>How solid.</b> A simple count. The category is Google's 2021 snapshot and a baba mention is a rough marker of the food served.</p>"
    + "<p class='rec'><b>Recommendation: main text.</b> It establishes the phenomenon in one figure.</p>"))
# ---------------- 2
parts.append(sec(2, "Where broad positioning is common", "Main text",
    "<p><b>What we did.</b> For each county with five or more WPME or ME restaurants (%d counties, %d restaurants), computed the share that are WPME.</p>" % (len(mp5), mp5.n.sum())
    + "<p><b>Result.</b> Explicit labels cluster around Detroit, the Northeast corridor and the Washington area; broad labels dominate the South and Southwest. "
      "Across these counties the WPME share correlates %s with the Middle Eastern ancestry share and %s with Trump share.</p>" % (fe(np.corrcoef(mp5.share, mp5.mena)[0, 1], 2), fe(np.corrcoef(mp5.share, mp5.trump_share)[0, 1], 2))
    + img("desc_map_wpme_share.png", "County map of the WPME share")
    + "<p><b>How solid.</b> Descriptive only; it previews result 3.</p><p class='rec'><b>Recommendation: main text</b>, or the appendix if space is short.</p>"))
# ---------------- 3
a, b_, c_ = lc("state FE only"), lc("+ population, density"), lc("+ college, foreign-born")
parts.append(sec(3, "Label choice tracks the local Middle Eastern community", "Main text",
    "<p><b>What we did.</b> Among WPME and ME restaurants (%d in %d counties), modeled the chance of being WPME on county Trump share and county characteristics, with state fixed effects. "
    "Middle Eastern ancestry is the percent of county residents reporting Arab, Iranian, Turkish, Afghan, Armenian or Assyrian ancestry.</p>" % (a.n, a.counties)
    + table(["Controls", "Per 10 pts of Trump share", "Per 1 pt of Middle Eastern ancestry"],
            [["State only", "%s pts (%s)" % (fe(100 * a.trump_est, 1), fp(a.trump_p)), ""],
             ["+ county population and density", "%s pts (%s)" % (fe(100 * b_.trump_est, 1), fp(b_.trump_p)), ""],
             ["+ ancestry, education, foreign-born", "%s pts (%s)" % (fe(100 * c_.trump_est, 1), fp(c_.trump_p)), "%s pts (%s)" % (fe(100 * c_.mena_est, 1), fp(c_.mena_p))]])
    + "<p><b>Result.</b> The WPME share falls from %s where under 0.25%% of residents have Middle Eastern ancestry to %s where over 2%% do. "
      "Trump share predicts broad positioning on its own, but not once county size is held fixed.</p>" % (pct(bins.share_wpme.iloc[0]), pct(bins.share_wpme.iloc[-1]))
    + img("figure1_label_choice.png", "Share WPME by county Middle Eastern ancestry share and by Trump share")
    + "<p><b>How solid.</b> The ancestry result is stable across every control set and both ME lists. It is cross-sectional: community size also tracks things we cannot see, such as owner background.</p>"
    + "<p class='rec'><b>Recommendation: main text.</b> This is Step 1. Report the Trump-share columns too, so readers see it is the community, not politics.</p>"))
# ---------------- 4
pt = pairs[pairs.trump_share > .5]
parts.append(sec(4, "Matched pairs in the same county", "Main text",
    "<p><b>What we did.</b> Listed pairs of one WPME and one ME restaurant in the same county, both with a baba mention and 50 or more reviews, within 10 km and with similar review counts.</p>"
    + "<p><b>Result.</b> %d candidate pairs, %d of them in Trump-majority counties. Several sit within a few hundred meters of each other with near-identical ratings. "
      "The full list with names and addresses is in <code>outputs/desc_example_pairs.csv</code>.</p>" % (len(pairs), len(pt))
    + "<p><b>How solid.</b> Anecdote, not evidence. We have not verified menus or ownership.</p>"
    + "<p class='rec'><b>Recommendation: main text, one pair</b> as an opening illustration, after checking it by hand.</p>"))
# ---------------- 5
e1, e2, pool, avg = E("2016 election"), E("Travel ban"), E("POOLED: election and travel ban"), S("delta: average of the two")
parts.append(sec(5, "The rating gap shifts after the election and the travel ban", "Main text",
    "<p><b>What we did.</b> For each event, compared each restaurant's ratings in the six weeks after with the 210 days before, and asked whether the WPME-minus-ME gap changed more in counties with higher Trump share.</p>"
    + table(["", "Change in gap per 10 pts of Trump share", "", "Weeks 7–18", "Using share above 50%"],
            [["2016 election (Nov 8, 2016)", fe(e1.est), fp(e1.p), fe(E("2016 election", w="weeks 7-18").est), "%s (%s)" % (fe(E("2016 election", "majority").est), fp(E("2016 election", "majority").p))],
             ["Travel ban (Jan 27, 2017)", fe(e2.est), fp(e2.p), fe(E("Travel ban", w="weeks 7-18").est), "%s (%s)" % (fe(E("Travel ban", "majority").est), fp(E("Travel ban", "majority").p))],
             ["Both pooled", fe(pool.est), fp(pool.p), fe(E("POOLED: election and travel ban", w="weeks 7-18").est), "%s (%s)" % (fe(E("POOLED: election and travel ban", "majority").est), fp(E("POOLED: election and travel ban", "majority").p))],
             ["Both, one shared pre-election baseline", fe(avg.est), fp(avg.p), "", "%s (%s)" % (fe(S("delta: average of the two", "majority").est), fp(S("delta: average of the two", "majority").p))]])
    + "<p><b>Result.</b> After both events the gap moves toward WPME as Trump share rises, by about %s stars per 10 points. Going from a county at 30%% to one at 60%% is about %s stars. It is gone by weeks 7–18. "
      "On %d ordinary dates with no event the same estimate averages %s and never exceeds %s.</p>" % (fe(pool.est), fe(3 * pool.est, 2), len(od), fe(od.est.mean()), fe(od.est.max()))
    + img("figure2_events.png", "Event estimates for the election and the travel ban, with ordinary dates")
    + "<p><b>How solid.</b></p><ul><li>Significant with continuous Trump share; not with the over-50%% split.</li>"
      "<li>The travel-ban estimate depends on starting the window on Jan 27; starting three days later roughly halves it.</li>"
      "<li>The pre-period test passes for the election (%s) and is borderline for the ban (%s), whose pre-period contains the election.</li></ul>" % (fp(e1.pretrend_p), fp(e2.pretrend_p))
    + "<ul><li>The gap is weaker once reviewer leniency is accounted for (see result 8).</li></ul>"
    + "<p class='rec'><b>Recommendation: main text, as the comparison with WPME.</b> The lead estimate for Step 2 is result 7."
      "Report the pooled or shared-baseline gap after it, with all four cautions.</p>"))
# ---------------- 6
g = f6.set_index("period")
t7 = lambda series: [G7(series, k) for k in [5, 6, 7, "average of the three later periods"]]
parts.append(sec(6, "Each group and the gap over time", "Main text",
    "<p><b>What we did.</b> Estimated the Trump-share gradient in each six-week period from April 2016 to July 2017, relative to the pre-election average. "
    "First for each group against American-first restaurants in the same county (new, figure 7), then for the WPME-minus-ME gap (figure 6).</p>"
    + table(["Per 10 pts of Trump share", "After the election", "Between the events", "After the travel ban", "Three later periods"],
            [[lab_] + ["%s (%s)" % (fe(x_.est), fp(x_.p)) for x_ in t7(ser_)] for lab_, ser_ in [("ME, relative to American", "ME vs American"), ("WPME, relative to American", "WPME vs American")]])
    + "<p><b>Result, each group.</b> ME ratings dip after the election, recover, fall after the travel ban, and are back to baseline afterwards. Only the travel-ban dip is significant on its own. "
      "WPME does not fall in either event window; its one dip is in the weeks between them.</p>"
    + img("figure7_each_group_over_time.png", "Each group's rating over time relative to American-first restaurants")
    + "<p><b>Result, the gap.</b> %s after the election (%s), %s in the weeks between the two events (%s), %s after the travel ban (%s), then about %s in each later period.</p>" % (
        fe(g.loc[5, "est"]), fp(g.loc[5, "p"]), fe(g.loc[6, "est"]), fp(g.loc[6, "p"]), fe(g.loc[7, "est"]), fp(g.loc[7, "p"]), fe(g.loc[[8, 9, 10], "est"].mean(), 2))
    + img("figure6_gap_over_time.png", "The WPME-minus-ME gap over time")
    + "<p><b>How solid.</b> The movements are small next to the period-to-period noise. One pre-election period has an ME swing as large as the travel-ban dip, in the other direction; "
      "the joint test of pre-election movement passes for ME (%s) and is borderline for WPME (%s). In the gap figure the two spikes are matched by an equally large fall between them, so a skeptical reader can see an oscillation. "
      "The right panel of figure 6 (Trump-majority counties) shows no clear spike; that group has under 200 restaurants of each type.</p>" % (
        fp(G7("ME vs American", "pre-period joint test (p only)").p), fp(G7("WPME vs American", "pre-period joint test (p only)").p))
    + "<p class='rec'><b>Recommendation: main text, figure 7.</b> It shows the travel-ban dip and how brief it is. Move figure 6 to the appendix.</p>"))
# ---------------- 7
me_s, wp_s = wg.loc["ME vs American: average, per 10 pts"], wg.loc["WPME vs American: average, per 10 pts"]
b5 = f5[~f5.trump_share_bin.str.startswith("slope")]
parts.append(sec(7, "Which group moves", "Main text",
    "<p><b>What we did.</b> Added American-first restaurants in the same county as a reference group (%d of them), so each group's change can be seen on its own.</p>" % wg.n_american.iloc[0]
    + table(["Group, relative to American restaurants", "Change per 10 pts of Trump share", "", "Change at 60% Trump share"],
            [["Explicitly Middle Eastern (ME)", fe(me_s.est), fp(me_s.p), "%s (%s)" % (fe(wg.loc["ME vs American: average change at 60% Trump share", "est"]), fp(wg.loc["ME vs American: average change at 60% Trump share", "p"]))],
             ["Broadly positioned (WPME)", fe(wp_s.est), fp(wp_s.p), "%s (%s)" % (fe(wg.loc["WPME vs American: average change at 60% Trump share", "est"]), fp(wg.loc["WPME vs American: average change at 60% Trump share", "p"]))]])
    + "<p><b>Result.</b> ME ratings fall as Trump share rises. WPME ratings show no gradient. For ME the two events separately are %s after the election (%s) and %s after the travel ban (%s).</p>" % (
        fe(_me("after election, per 10 pts").est), fp(_me("after election, per 10 pts").p), fe(_me("after travel ban, per 10 pts").est), fp(_me("after travel ban, per 10 pts").p))
    + img("figure5_which_group_moves_by_trump_share.png", "Each group's rating change by county Trump share")
    + "<p><b>How solid.</b> Both lines sit below zero through most of the range: at 40%% Trump share WPME is %s (%s) and ME %s (%s) relative to American-first restaurants. Neither group was untouched; ME differs in its slope. "
      "The straight line is also a summary. Estimated separately for five groups of counties, the pattern is uneven:</p>" % (
        fe(_wp("average change at 40% Trump share").est), fp(_wp("average change at 40% Trump share").p), fe(_me("average change at 40% Trump share").est), fp(_me("average change at 40% Trump share").p))
    + table(["County Trump share", "ME", "WPME"], [[bn, "%s (%s, %d restaurants)" % (fe(m_.est), fp(m_.p), m_.restaurants), "%s (%s, %d)" % (fe(w_.est), fp(w_.p), w_.restaurants)]
            for bn in b5.trump_share_bin.unique() for m_ in [b5[(b5.trump_share_bin == bn) & b5.group.str.contains("ME\\)") & b5.group.str.startswith("Explicitly")].iloc[0]]
            for w_ in [b5[(b5.trump_share_bin == bn) & b5.group.str.startswith("Broadly")].iloc[0]]])
    + "<p>The ME decline sits mostly in counties at 50–60%%; above 60%% there are only %d ME restaurants and no decline. In counties under 30%%, WPME fell while ME held.</p>" % int(b5[(b5.trump_share_bin == "over 60%") & b5.group.str.startswith("Explicitly")].restaurants.iloc[0])
    + "<p class='rec'><b>Recommendation: main text, the line figure, as the lead estimate for Step 2.</b> Lead with the travel ban, report the election as a smaller dip in the same direction, and put the five-group table in the appendix.</p>"))
# ---------------- 8
s1 = st[(st.quantity == "per 10 pts Trump share") & (st.outcome == "share 1-star")].set_index("group")
parts.append(sec(8, "Star breakdown and reviewer leniency", "Main text",
    "<p><b>What we did.</b> Repeated result 7 with the share of reviews at each star level as the outcome. Then accounted for who is reviewing, using each reviewer's history on every other review they wrote (94% of reviews come from people with other reviews).</p>"
    + "<p><b>On restaurant quality.</b> Every model compares a restaurant with itself before and after, so fixed quality is already removed. The leniency check addresses the remaining worry that harsher reviewers happened to show up.</p>"
    + table(["ME restaurants, per 10 pts of Trump share", "As estimated", "Controlling for reviewer leniency", "Relative to each reviewer's usual"],
            [["Mean rating", "%s (%s)" % (fe(L("baseline", "mean rating", "ME").est), fp(L("baseline", "mean rating", "ME").p)),
              "%s (%s)" % (fe(L("+ leniency control", "mean rating", "ME").est), fp(L("+ leniency control", "mean rating", "ME").p)),
              "%s (%s)" % (fe(L("relative to the reviewer's usual", "mean rating", "ME").est), fp(L("relative to the reviewer's usual", "mean rating", "ME").p))],
             ["Share of 1-star reviews", "%s pts (%s)" % (fe(100 * L("baseline", "share 1-star", "ME").est, 2), fp(L("baseline", "share 1-star", "ME").p)),
              "%s pts (%s)" % (fe(100 * L("+ leniency control", "share 1-star", "ME").est, 2), fp(L("+ leniency control", "share 1-star", "ME").p)),
              "%s pts (%s)" % (fe(100 * L("relative to the reviewer's usual", "share 1-star", "ME").est, 2), fp(L("relative to the reviewer's usual", "share 1-star", "ME").p))]])
    + "<p><b>Result.</b> The ME decline is a rise in one-star reviews (%s points per 10 points of Trump share, %s); WPME shows none (%s). It survives both leniency adjustments: reviewers gave ME restaurants more one-star reviews than those same reviewers usually give.</p>" % (
        fe(100 * s1.loc["ME", "est"], 2), fp(s1.loc["ME", "p"]), fe(100 * s1.loc["WPME", "est"], 2))
    + img("desc_star_breakdown.png", "Change in the share of reviews at each star level")
    + "<p><b>How solid.</b> The ME result is robust. The contrast with WPME is less so:</p>"
    + table(["WPME minus ME, mean rating, per 10 pts", "As estimated", "Controlling for reviewer leniency", "Relative to each reviewer's usual"],
            [["", "%s (%s)" % (fe(L("baseline", "mean rating", "WPME minus ME").est), fp(L("baseline", "mean rating", "WPME minus ME").p)),
              "%s (%s)" % (fe(L("+ leniency control", "mean rating", "WPME minus ME").est), fp(L("+ leniency control", "mean rating", "WPME minus ME").p)),
              "%s (%s)" % (fe(L("relative to the reviewer's usual", "mean rating", "WPME minus ME").est), fp(L("relative to the reviewer's usual", "mean rating", "WPME minus ME").p))]])
    + "<p>WPME restaurants in more Trump-leaning counties drew somewhat more lenient reviewers after the events. Measured against each reviewer's own usual rating, WPME also dips a little (%s, %s), and the WPME-minus-ME difference is no longer significant.</p>" % (
        fe(L("relative to the reviewer's usual", "mean rating", "WPME").est), fp(L("relative to the reviewer's usual", "mean rating", "WPME").p))
    + "<p class='rec'><b>Recommendation: main text</b> for the star figure and the ME leniency result. This is why Step 2 is stated for ME ratings: that they fell is the clean result; whether WPME was spared is less certain.</p>"))
# ---------------- 9
oth = [("Travel ban 2.0", "Travel ban 2.0 (Mar 6, 2017)"), ("Travel ban 3.0", "Travel ban 3.0 (Sep 24, 2017)"), ("Supreme Court ruling", "Supreme Court ruling (Jun 26, 2018)"),
       ("Soleimani strike", "Soleimani strike (Jan 3, 2020)"), ("POOLED: all six events", "All six events pooled")]
parts.append(sec(9, "Other events examined", "Appendix",
    "<p><b>What we did.</b> We examined a few other events as well, with the same model.</p>" + table(["Event", "Change in gap per 10 pts of Trump share", ""], [[l_, fe(E(n_).est), fp(E(n_).p)] for n_, l_ in oth])
    + "<p><b>Result.</b> All are positive and none is significant alone.</p>"
    + "<p class='rec'><b>Recommendation: appendix, and one sentence in the text.</b></p>"))
# ---------------- 10
ov, tr = x4[x4.model == "overall: After"].iloc[0], x4[x4.model == "by Trump: After x continuous"].iloc[0]
parts.append(sec(10, "Positioning over time", "Appendix",
    "<p><b>What we did.</b> Google's categories are a 2021 snapshot, so relabeling cannot be seen. Using each restaurant's first review date as a stand-in for opening, compared the WPME share among restaurants first reviewed in the two years before and after the election.</p>"
    + "<p><b>Result.</b> %s before, %s after (%s points, %s). No extra shift in Trump-leaning counties (%s points per 10, %s).</p>" % (pct(ov.share_before), pct(ov.share_after), fe(100 * ov.est, 1), fp(ov.p), fe(100 * tr.est, 1), fp(tr.p))
    + img("figure4_positioning_over_time.png", "Share WPME by year of first review")
    + "<p><b>How solid.</b> A weak test: first review date is a noisy proxy, and Trump-majority counties add only 37–62 new restaurants a year.</p>"
    + "<p class='rec'><b>Recommendation: appendix or a footnote.</b> It answers an obvious reader question (did restaurants respond by positioning more broadly?) with \"not detectably\".</p>"))
# ---------------- 11
lowme, lowwp = idm[(idm.stars == "1-2 stars") & (idm.group == "ME")].iloc[0], idm[(idm.stars == "1-2 stars") & (idm.group == "WPME")].iloc[0]
hime = idm[(idm.stars == "4-5 stars") & (idm.group == "ME")].iloc[0]
quotes_html = ""
qp = BUILT / "desc_political_mention_reviews.csv"
if qp.exists():
    q = pd.read_csv(qp, dtype={"county_fips": str})
    el = pd.read_csv(INPUTS / "medsl-countypres-2000-2016.csv", low_memory=False)
    el = el[el.year.eq(2016) & el.FIPS.notna()].copy()
    el["county_fips"] = el.FIPS.astype(int).astype(str).str.zfill(5)
    names = el.drop_duplicates("county_fips").set_index("county_fips")[["county", "state_po"]]
    info = rest.set_index("gmap_id")
    # the excerpts to show are listed one per line in built/summary_excerpts.txt (local; review text is not kept in the repository)
    xp = BUILT / "summary_excerpts.txt"
    picks = [ln.strip() for ln in xp.read_text(encoding="utf-8").splitlines() if ln.strip()] if xp.exists() else []
    rowsq = []
    for ex in picks:
        m_ = q[q.text.str.startswith(ex[:40])]
        if len(m_) == 0:
            continue
        x = m_.iloc[0]
        assert ex in x.text
        ri = info.loc[x.gmap_id]
        cn = names.loc[x.county_fips] if x.county_fips in names.index else None
        where = "%s County, %s" % (cn.county, cn.state_po) if cn is not None else x.county_fips
        rowsq.append("<blockquote>&ldquo;%s&rdquo;<footer>%d-star review, %s, %s. Restaurant: first category &ldquo;%s&rdquo; (ME); %s; county Trump share %.0f%%, Middle Eastern ancestry %.1f%%; "
                     "the restaurant averages %.2f stars over %d reviews; this reviewer has %d reviews in the data.%s</footer></blockquote>" % (
                         html.escape(ex), x.rating, str(x["dt"])[:10], x["window"], html.escape(str(ri.first_category)), where, 100 * x.trump_share, ri.mena, ri.mean_rating, ri.n_reviews, x.reviews_total,
                         " This is the opening of a longer review." if len(x.text) > len(ex) + 20 else ""))
    quotes_html = "<p><b>Three examples.</b> Restaurant names are withheld here; they are in the local data.</p>" + "".join(rowsq)
pol_after = pm[pm.window != "before"].political.sum()
parts.append(sec(11, "What reviewers write: identity as the lens", "Main text",
    "<p><b>What we did.</b> Read the text of %d reviews with text from April 2016 to July 2017 and counted references to identity (Muslim, Islamic, racist, foreigner, immigrant, refugee and similar).</p>" % idm.text_reviews.sum()
    + table(["Reviews with text", "ME: identity mentions per 1,000", "WPME: identity mentions per 1,000"],
            [[s_, "%.1f (%d of %d)" % (a_.strict_per_1000, a_.strict, a_.text_reviews), "%.1f (%d of %d)" % (b2.strict_per_1000, b2.strict, b2.text_reviews)]
             for s_ in ["1-2 stars", "3 stars", "4-5 stars"] for a_ in [idm[(idm.stars == s_) & (idm.group == "ME")].iloc[0]] for b2 in [idm[(idm.stars == s_) & (idm.group == "WPME")].iloc[0]]])
    + "<p><b>Result.</b> Identity references are about %d times more common in one- and two-star reviews than in positive ones. They are no more common at ME restaurants than at WPME ones (%.1f versus %.1f per 1,000, %s). "
      "Explicit political language is nearly absent: %d reviews in the six weeks after either event.</p>" % (round(lowme.strict_per_1000 / hime.strict_per_1000), lowme.strict_per_1000, lowwp.strict_per_1000, fp(idt.loc["strict", "fisher_p"]), pol_after)
    + quotes_html
    + "<h3>Where the experiment comes in</h3>"
      "<p>Whether the explicit label is what makes identity the lens is a clean thing to test: give participants the same mediocre service scenario at a restaurant labeled &ldquo;Mediterranean&rdquo; or &ldquo;Middle Eastern&rdquo;, and measure both the rating and how much they attribute the experience to who runs the place. "
      "Social dominance orientation and food familiarity are the planned moderators.</p>"
    + "<p><b>How solid.</b> The excerpts are illustrations. Accusations of racism appear at WPME restaurants too, most are complaints that staff favor their own community, and they did not become more common after the events.</p>"
    + "<p class='rec'><b>Recommendation: main text, as the bridge to the experiment.</b> Avoid the term &ldquo;reverse racism&rdquo;.</p>"))
# ---------------- 12
r1 = rt[rt["sample"].str.startswith("one-time") & (rt.outcome == "rating")].iloc[0]
r2 = rt[rt.outcome.str.startswith("share")].iloc[0]
parts.append(sec(12, "Who the reviewers are", "One sentence",
    "<p><b>What we did.</b> Counted every reviewer's total reviews in the data and reran the event model by reviewer type.</p>"
    + "<p><b>Result.</b> One-time reviewers write 7%% of reviews. The effect is not concentrated among them (%s, %s, on %d reviews), and their share does not change (%s points, %s).</p>" % (fe(r1.est), fp(r1.p), r1.reviews_after, fe(100 * r2.est, 1), fp(r2.p))
    + "<p class='rec'><b>Recommendation: one sentence.</b> It rules out drive-by review bombing as the story.</p>"))
# ---------------- how the experiment builds on this
parts.append("""<h2 class='plain'>How the experiment builds on these findings</h2>
<p>The archival study shows where the phenomenon lives and how large it is in the field. The experiment can take each piece and make it sharp.</p>
<ol>
<li><b>It isolates the label.</b> In the field, restaurants that lead with "Mediterranean" differ from those that lead with "Middle Eastern" in many ways. The experiment shows the same restaurant, menu and photos and changes only the label, so the rating penalty we see after the travel ban becomes a causal effect of positioning.</li>
<li><b>It tests the protection claim directly.</b> The archival data establish the penalty for the explicit label. The experiment can show that the identical restaurant under the broad label escapes it, which is the paper's core claim: hiding identity through broader positioning can pay, counter to the authenticity literature.</li>
<li><b>It separates animus from unfamiliarity.</b> County Trump share is the field's stand-in for animus, and local Middle Eastern community size is its stand-in for familiarity. Measuring social dominance orientation and food familiarity for each participant turns both into individual-level moderators, and the two accounts predict different patterns: animus penalizes the explicit label most among high-SDO participants, while unfamiliarity predicts that "Mediterranean" simply is not read as Middle Eastern by people who do not know the food.</li>
<li><b>It recreates the stigma event.</b> The archival penalty appears in the weeks after the travel ban and fades. Having participants read a travel-ban news story or a neutral one before rating lets us switch that context on and off, and shows that threat salience is what activates the penalty.</li>
<li><b>It shows identity becoming the lens.</b> In the field the decline is a rise in one-star reviews, and negative reviews are where identity gets mentioned. Holding a mediocre service experience fixed and varying only the label lets us measure both the rating and how much participants attribute the experience to who runs the place.</li>
<li><b>It captures who never walks in.</b> Google ratings come only from people who chose to eat there. The experiment can measure choice and willingness to visit, the margin where a stigmatized label plausibly costs the most and which reviews cannot see.</li>
<li><b>It maps when authenticity wins.</b> Measuring perceived authenticity alongside ratings shows when the explicit label earns its premium (familiar, low-SDO, no salient threat) and when broad positioning does better. That turns the paper from a challenge to authenticity research into a boundary condition for it.</li>
</ol>
<p>Together the two studies cover each other: the archival evidence shows the pattern is real, national and tied to actual events, and the experiment shows what causes it and why.</p>""")

css = """
:root{--ink:#16242c;--muted:#52606a;--line:#dfe5e8;--bg:#fbfbfa;--main:#0f6b4f;--app:#8a5a00;--out:#9a2c2c}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:940px;margin:0 auto;padding:36px 20px 80px}h1{font-size:1.9rem;line-height:1.2;margin:0 0 6px}
.sub{color:var(--muted);margin:0 0 26px}h2{font-size:1.28rem;line-height:1.3;margin:54px 0 12px;padding-top:18px;border-top:1px solid var(--line)}
h2.plain{border-top:0;padding-top:0;margin-top:34px}h3{font-size:1.02rem;margin:22px 0 4px}
.n{display:inline-block;min-width:1.7em;height:1.7em;line-height:1.7em;text-align:center;border-radius:50%;background:var(--ink);color:#fff;font-size:.85rem;margin-right:8px;vertical-align:2px}
.tag{font-size:.74rem;font-weight:650;padding:3px 9px;border-radius:999px;white-space:nowrap;vertical-align:2px;margin-left:6px;border:1px solid}
.tag.main{color:var(--main);border-color:var(--main)}.tag.app{color:var(--app);border-color:var(--app)}.tag.out{color:var(--out);border-color:var(--out)}
.tw{overflow-x:auto;margin:12px 0 16px}table{border-collapse:collapse;width:100%;font-size:.92rem;font-variant-numeric:tabular-nums}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}th{color:var(--muted);font-weight:600;background:#f1f4f5}
figure{margin:18px 0}img{display:block;width:100%;height:auto;border:1px solid var(--line);border-radius:6px}figcaption{font-size:.78rem;color:var(--muted);margin-top:4px}
.rec{background:#eef5f2;border-left:4px solid var(--main);padding:10px 14px;border-radius:0 6px 6px 0}
blockquote{margin:12px 0;padding:10px 16px;border-left:4px solid var(--line);background:#f4f6f7;border-radius:0 6px 6px 0}blockquote footer{font-size:.84rem;color:var(--muted);margin-top:6px}
code{font-size:.88em;background:#eef1f2;padding:1px 5px;border-radius:4px}a{color:#0b5c8a}ul,ol{padding-left:22px}li{margin:4px 0}
@media print{h2{break-after:avoid}figure,table{break-inside:avoid}}
"""
doc = "<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Archival results summary</title><style>%s</style></head><body><main>" % css
doc += "<h1>Archival results: what we found and what to include</h1><p class='sub'>Hiding Their True Colors (Heshmati, Choe) &middot; working summary, updated November 24, 2026 &middot; contains three verbatim review excerpts; not for public posting</p>"
doc += "".join(parts) + "</main></body></html>"
(HERE / "RESULTS_SUMMARY.html").write_text(doc, encoding="utf-8")
print("RESULTS_SUMMARY.html written: %.1f MB, %d sections" % (len(doc) / 1e6, 12))
