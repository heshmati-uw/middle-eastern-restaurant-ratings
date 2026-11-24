"""Descriptive: do reviewers describe WPME ("Mediterranean"-first) restaurants as authentic Middle Eastern food?

Usage: python 23_authentic_mentions.py
Reads built/authentic_reviews/*.csv.gz and built/authentic_review_totals.csv (from 22_scan_authentic_reviews.py).
A review counts when "authentic" is followed within 40 characters (same sentence) by a cuisine word, e.g. "authentic Lebanese food".
Cuisine words: Middle Eastern nationalities/regions (Lebanese, Persian, Turkish, ...), and for comparison Mediterranean and Greek.
Writes outputs/desc_authentic_mentions.csv (counts; no text) and built/desc_authentic_review_examples.csv (text; local only).
"""
import glob, re
import pandas as pd
from common import BUILT, FROZEN, OUT

ME_WORDS = {"Lebanese": r"lebanese|lebanon", "Persian / Iranian": r"persian|iranian", "Turkish": r"turkish", "Syrian": r"syrian", "Palestinian": r"palestinian",
            "Egyptian": r"egyptian", "Iraqi": r"iraqi", "Jordanian": r"jordanian", "Yemeni": r"yemeni|yemenite", "Armenian": r"armenian", "Afghan": r"afghani?",
            "Moroccan": r"moroccan", "Israeli": r"israeli", "Arab / Arabic": r"arab(?:ic|ian)?", "Middle Eastern": r"middle[- ]eastern?"}
OTHER = {"Mediterranean": r"mediterr?anean", "Greek": r"greek"}
pat = lambda w: re.compile(r"authentic(?:ally)?\b[^.!?\n]{0,40}?\b(?:%s)\b" % w, re.I)
PATS = {k: pat(v) for k, v in {**ME_WORDS, **OTHER}.items()}
ANY_ME = pat("|".join(ME_WORDS.values()))

s = pd.read_csv(FROZEN / "restaurants.csv", dtype={"county_fips": str})
s["group"] = s.wpme.map({True: "WPME"}).fillna(s.me_national.map({True: "ME"}))
s = s[s.group.notna()]
r = pd.concat([pd.read_csv(f, dtype={"user_id": str}) for f in sorted(glob.glob(str(BUILT / "authentic_reviews" / "*.csv.gz")))], ignore_index=True)
r = r.merge(s[["gmap_id", "group", "first_category", "county_fips", "trump_share", "mena", "mean_rating", "n_reviews"]], on="gmap_id")
r["text"] = r.text.fillna("")
# leave out negated uses ("not authentic Lebanese", "isn't authentic ...")
NEG = re.compile(r"(?:\bnot\b|\bisn.?t\b|\bno\b|\bnothing\b|\bfar from\b|\bhardly\b|\bless\b|\bnever\b)[^.!?]{0,25}authentic", re.I)
neg = r.text.str.contains(NEG)
for k, p in PATS.items():
    r[k] = r.text.str.contains(p) & ~neg
r["any_me"] = r.text.str.contains(ANY_ME) & ~neg
print("negated uses left out: %d" % (r.text.str.contains(ANY_ME) & neg).sum())
tot = pd.read_csv(BUILT / "authentic_review_totals.csv").merge(s[["gmap_id", "group"]], on="gmap_id")

rows = []
for g in ["WPME", "ME"]:
    n_rest, n_text = int((s.group == g).sum()), int(tot[tot.group == g].text_reviews.sum())
    d = r[r.group == g]
    for k in ["any_me"] + list(PATS):
        m = d[d[k]]
        rows.append(dict(group=g, phrase="authentic + any Middle Eastern cuisine word" if k == "any_me" else "authentic + " + k, reviews=len(m), per_1000_text_reviews=1000 * len(m) / n_text,
                         restaurants=m.gmap_id.nunique(), share_of_restaurants=m.gmap_id.nunique() / n_rest, restaurants_in_group=n_rest, text_reviews_in_group=n_text))
res = pd.DataFrame(rows)
res.to_csv(OUT / "desc_authentic_mentions.csv", index=False)
pd.set_option("display.width", 220)
print(res[["group", "phrase", "reviews", "per_1000_text_reviews", "restaurants", "share_of_restaurants"]].round(3).to_string(index=False))

w = r[(r.group == "WPME") & r.any_me].copy()
w["date"] = pd.to_datetime(w.time_ms, unit="ms").dt.date
w["cuisine"] = w.apply(lambda x: "; ".join(k for k in ME_WORDS if x[k]), axis=1)
w["match"] = w.text.str.extract("(" + ANY_ME.pattern + ")", flags=re.I)[0]
w["mentions_at_restaurant"] = w.groupby("gmap_id").gmap_id.transform("size")
w = w.sort_values(["mentions_at_restaurant", "gmap_id", "time_ms"], ascending=[False, True, True])
w[["gmap_id", "first_category", "county_fips", "trump_share", "mena", "mean_rating", "n_reviews", "mentions_at_restaurant", "date", "rating", "cuisine", "match", "text", "user_id"]].to_csv(
    BUILT / "desc_authentic_review_examples.csv", index=False)
k = w.drop_duplicates("gmap_id").mentions_at_restaurant
print("\nWPME restaurants with at least 1 / 3 / 10 such reviews: %d / %d / %d" % ((k >= 1).sum(), (k >= 3).sum(), (k >= 10).sum()))
print("star ratings of these reviews:", w.rating.value_counts(normalize=True).sort_index().round(3).to_dict())
print("length of matching reviews (characters): median %d; under 120: %d" % (w.text.str.len().median(), (w.text.str.len() < 120).sum()))
