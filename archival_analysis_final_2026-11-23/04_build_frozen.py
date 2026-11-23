"""Step 4 (from raw). Build the analysis-ready tables that steps 5-9 read. These contain no names, addresses or review text.

Usage: python 04_build_frozen.py
Writes:
  frozen/restaurants.csv       one row per sample restaurant: group flags, county, Trump share, county controls,
                               number of reviews, mean rating and year of first review (all years)
  frozen/event_cells.csv.gz    WPME and ME restaurants: mean rating and review count per 42-day period around each event
                               and each ordinary date (periods -5..2; period 0 starts on the date, UTC)
  frozen/timeline_cells.csv.gz WPME, ME and American restaurants on the shared election + travel-ban timeline:
                               periods -5..-1 = the 210 days before 2016-11-08; 100 = 2016-11-08 to 2016-12-19; 200 = 2017-01-27 to 2017-03-09
"""
import glob
import numpy as np, pandas as pd
from common import BUILT, FROZEN, EVENTS, BIN_DAYS, PRE_BINS, POST_BINS, ORDINARY_START, ORDINARY_END, trump_share, census

FROZEN.mkdir(exist_ok=True)
s = pd.read_csv(BUILT / "sample_restaurants.csv", low_memory=False).merge(pd.read_csv(BUILT / "county_fips.csv", dtype={"county_fips": str}), on="gmap_id", how="left")
s = s.merge(trump_share(), left_on="county_fips", right_index=True, how="left").merge(census(), left_on="county_fips", right_index=True, how="left")
r = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(str(BUILT / "reviews_exact" / "*.csv.gz")))], ignore_index=True).drop_duplicates()
r["dt"] = pd.to_datetime(r.time_ms, unit="ms")
agg = r.groupby("gmap_id").agg(n_reviews=("rating", "size"), mean_rating=("rating", "mean"), first_year=("dt", lambda x: x.min().year))
s = s.merge(agg, left_on="gmap_id", right_index=True, how="left")
s["state_fips"] = s.county_fips.str[:2]
cols = ["gmap_id", "first_category", "med_first", "baba", "wpme", "me_national", "me_original", "american", "county_fips", "state_fips", "trump_share",
        "population", "log_pop", "log_density", "mena", "college", "foreign", "n_reviews", "mean_rating", "first_year"]
s[cols].to_csv(FROZEN / "restaurants.csv", index=False)
print("restaurants: %d; with county and Trump share: %d; reviews: %d (%s to %s)" % (len(s), s.trump_share.notna().sum(), len(r), r.dt.min().date(), r.dt.max().date()))

focal = set(s[(s.wpme | s.me_national | s.me_original) & s.trump_share.notna()].gmap_id)
rf = r[r.gmap_id.isin(focal)]
span = pd.Timedelta(days=BIN_DAYS)
dates = [(n, d, "event") for n, d in EVENTS] + [("ordinary", d.strftime("%Y-%m-%d"), "ordinary") for d in pd.date_range(ORDINARY_START, ORDINARY_END, freq="%dD" % BIN_DAYS)]
parts = []
for name, date, kind in dates:
    e = pd.Timestamp(date)
    x = rf[(rf.dt >= e - PRE_BINS * span) & (rf.dt < e + POST_BINS * span)]
    b = np.floor((x.dt - e).dt.total_seconds() / (BIN_DAYS * 86400)).astype(int)
    c = x.assign(bin=b).groupby(["gmap_id", "bin"]).rating.agg(["mean", "size"]).reset_index().rename(columns={"size": "n"})
    parts.append(c.assign(event=name, date=date, kind=kind))
pd.concat(parts, ignore_index=True).to_csv(FROZEN / "event_cells.csv.gz", index=False)

e1, e2 = pd.Timestamp("2016-11-08"), pd.Timestamp("2017-01-27")
three = set(s[(s.wpme | s.me_national | s.me_original | s.american) & s.trump_share.notna()].gmap_id)
x = r[r.gmap_id.isin(three) & (r.dt >= e1 - PRE_BINS * span) & (r.dt < e2 + span)]
lab = np.where(x.dt < e1, np.floor((x.dt - e1).dt.total_seconds() / (BIN_DAYS * 86400)).astype(int),
               np.where(x.dt < e1 + span, 100, np.where(x.dt >= e2, 200, -999)))
c = x.assign(bin=lab)
c = c[c.bin.ne(-999)].groupby(["gmap_id", "bin"]).rating.agg(["mean", "size"]).reset_index().rename(columns={"size": "n"})
c.to_csv(FROZEN / "timeline_cells.csv.gz", index=False)
print("event cells: %d rows over %d dates; timeline cells: %d rows" % (sum(len(p) for p in parts), len(dates), len(c)))
