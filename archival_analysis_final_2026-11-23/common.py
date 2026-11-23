"""Shared definitions and estimators for the consolidated archival analysis (2026-11-23)."""
import pathlib
import numpy as np, pandas as pd
from scipy import stats

HERE = pathlib.Path(__file__).resolve().parent
INPUTS, BUILT, FROZEN, OUT = HERE / "inputs", HERE / "built", HERE / "frozen", HERE / "outputs"

# ---- group definitions (first Google category, 2021 snapshot)
ME_NATIONAL = r"\b(?:middle eastern|lebanese|persian|iranian|syrian|iraqi|turkish|yemeni|yemenite|palestinian|jordanian|egyptian|moroccan|north african|kuwaiti|qatari|bahraini|omani|saudi|armenian|afghan|afghani)\b"
ME_ORIGINAL = ["middle eastern restaurant", "north african restaurant", "armenian restaurant", "halal restaurant", "egyptian restaurant",
               "moroccan restaurant", "persian restaurant", "kebab shop", "lebanese restaurant", "syrian restaurant", "afghani restaurant",
               "yemenite restaurant", "iraqi restaurant", "palestinian restaurant", "jordanian restaurant", "kuwaiti restaurant",
               "qatari restaurant", "bahraini restaurant", "omani restaurant", "shawarma restaurant"]
ME_LISTS = {"national": "me_national", "original": "me_original"}

# ---- events (start of day, UTC)
FOCUS = [("2016 election", "2016-11-08"), ("Travel ban", "2017-01-27")]
OTHER = [("Travel ban 2.0", "2017-03-06"), ("Travel ban 3.0", "2017-09-24"), ("Supreme Court ruling", "2018-06-26"), ("Soleimani strike", "2020-01-03")]
EVENTS = FOCUS + OTHER
BIN_DAYS, PRE_BINS, POST_BINS = 42, 5, 3
ORDINARY_START, ORDINARY_END = "2016-06-06", "2020-01-06"
MIN_REVIEWS_LEVEL = 10
CONTROLS = ["log_pop", "log_density", "mena", "college", "foreign"]


def trump_share():
    """2016 Trump votes / all candidate votes by county (MEDSL 20190722); Kansas City, MO folded into Jackson County."""
    el = pd.read_csv(INPUTS / "medsl-countypres-2000-2016.csv", low_memory=False)
    el = el[el.year.eq(2016) & el.FIPS.notna()].copy()
    el["county_fips"] = el.FIPS.astype(int).astype(str).str.zfill(5).replace({"36000": "29095"})
    return (el[el.candidate.eq("Donald Trump")].groupby("county_fips").candidatevotes.sum() / el.groupby("county_fips").candidatevotes.sum()).rename("trump_share").dropna()


def census():
    """County controls from ACS 2017-2021 five-year tables (county rows) and 2018 county land area."""
    def acs(t):
        d = pd.read_csv(INPUTS / "census" / ("acs5_2021_%s_county.psv" % t), sep="|", dtype={"GEO_ID": str})
        d["county_fips"] = d.GEO_ID.str[-5:]
        return d.set_index("county_fips")
    pop, anc, edu, nat = acs("b01003"), acs("b04006"), acs("b15003"), acs("b05002")
    cv = pd.DataFrame({"population": pop.B01003_E001})
    cv["mena"] = 100 * anc[["B04006_E002", "B04006_E006", "B04006_E016", "B04006_E017", "B04006_E048", "B04006_E091"]].sum(axis=1) / pop.B01003_E001
    cv["college"] = 100 * edu[["B15003_E022", "B15003_E023", "B15003_E024", "B15003_E025"]].sum(axis=1) / edu.B15003_E001
    cv["foreign"] = 100 * nat.B05002_E013 / nat.B05002_E001
    land = pd.read_csv(INPUTS / "census" / "county_land_area.csv", dtype={"GEOID": str}).set_index("GEOID").ALAND / 1e6
    cv["log_pop"] = np.log(cv.population)
    cv["log_density"] = np.log(cv.population / land.reindex(cv.index))
    return cv


def absorb(v, fs, tol=1e-9, it=3000):
    """Remove fixed effects by alternating projections."""
    v = np.asarray(v, float).copy()
    cnt = [np.bincount(f).astype(float) for f in fs]
    for _ in range(it if len(fs) > 1 else 1):
        old = v.copy()
        for f, n in zip(fs, cnt):
            acc = np.zeros((len(n),) + v.shape[1:])
            np.add.at(acc, f, v)
            v -= (acc / (n[:, None] if v.ndim > 1 else n))[f]
        if np.abs(v - old).max() < tol:
            break
    return v


class Fit:
    """OLS with absorbed fixed effects and county-clustered standard errors.
    dof_adjust=False: sandwich x G/(G-1) (event models). dof_adjust=True: also x (N-1)/(N-K-#FE) (cross-sectional models)."""

    def __init__(self, d, y, cols, fes, cluster="county_fips", dof_adjust=False):
        fs = [pd.factorize(d[f])[0] for f in fes]
        g = pd.factorize(d[cluster])[0]
        self.G, self.n, self.cols = g.max() + 1, len(d), list(cols)
        X, yy = absorb(d[cols].to_numpy(float), fs), absorb(d[y].to_numpy(float), fs)
        self.b = np.linalg.lstsq(X, yy, rcond=None)[0]
        u = yy - X @ self.b
        bread = np.linalg.pinv(X.T @ X)
        sc = np.zeros((self.G, len(cols)))
        np.add.at(sc, g, X * u[:, None])
        self.vc = bread @ (sc.T @ sc) @ bread * self.G / (self.G - 1)
        if dof_adjust:
            nfe = sum(f.max() + 1 for f in fs)
            self.vc *= (self.n - 1) / max(self.n - len(cols) - nfe, 1)

    def lin(self, **terms):
        h = np.array([terms.get(c, 0.0) for c in self.cols])
        est, se = h @ self.b, np.sqrt(h @ self.vc @ h)
        return dict(est=est, se=se, p=2 * stats.t.sf(abs(est / se), self.G - 1))

    def joint(self, names):
        idx = [self.cols.index(k) for k in names]
        W = self.b[idx] @ np.linalg.pinv(self.vc[np.ix_(idx, idx)]) @ self.b[idx]
        return stats.f.sf(W / len(idx), len(idx), self.G - 1)


def zscore(share, measure):
    """County Trump measure: 'continuous' = per 10 points centered at 40%; 'majority' = share above 50%."""
    return (share - .4) / .1 if measure == "continuous" else (share > .5).astype(float)
