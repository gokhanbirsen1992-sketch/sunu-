"""Golden-value sayısal doğruluk testleri.

Motor sarmalayıcılarının (analyses/*) ürettiği istatistikleri, alttaki referans
kütüphanelere (scipy/statsmodels/pingouin) ve elle hesaplanmış sabitlere karşı
doğrular. Amaç: sarmalayıcının doğru sayıyı çıkardığını kanıtlamak.
"""

import numpy as np
import pandas as pd
import pytest
from scipy import stats

from sav2q1.engine import effects
from sav2q1.engine.analyses.group_compare import compare_multi_groups
from sav2q1.engine.analyses.categorical import crosstab_test
from sav2q1.engine.analyses.correlation import correlate
from sav2q1.engine.analyses.regression import linear_regression


@pytest.fixture(scope="module")
def df3():
    rng = np.random.default_rng(7)
    n = 60
    g = np.repeat([1, 2, 3], n // 3)
    # çarpık (KW yolu) ve normal (ANOVA yolu) sonuçlar
    skew = np.concatenate([rng.exponential(1, 20), rng.exponential(2, 20), rng.exponential(3, 20)])
    norm = np.concatenate([rng.normal(10, 2, 20), rng.normal(11, 2, 20), rng.normal(12, 2, 20)])
    x = rng.normal(0, 1, n); y = 2 * x + rng.normal(0, 1, n)
    cat = rng.integers(0, 2, n)
    return pd.DataFrame({"g": g, "skew": skew, "norm": norm, "x": x, "y": y, "cat": cat})


def test_cohens_d_known():
    # iki grup, bilinen d: ortalama farkı 2, pooled sd ~2 -> d ~1
    a = np.array([2, 4, 6, 8, 10], float)
    b = np.array([0, 2, 4, 6, 8], float)
    # fark=2, her grup sd=sqrt(10)=3.162 -> d=2/3.162=0.632
    assert effects.cohens_d(a, b) == pytest.approx(0.6325, abs=1e-3)


def test_multigroup_statistic_matches_reference(df3):
    for var in ["skew", "norm"]:
        r = compare_multi_groups(df3, var, "g", result_id="R")
        arrays = [df3.loc[df3.g == k, var].to_numpy() for k in [1, 2, 3]]
        if r["test"] == "kruskal_wallis":
            H, _ = stats.kruskal(*arrays)
            assert r["statistic"]["value"] == pytest.approx(float(H), rel=1e-6)
        elif r["test"] == "oneway_anova":
            F, _ = stats.f_oneway(*arrays)
            assert r["statistic"]["value"] == pytest.approx(float(F), rel=1e-6)
        else:  # welch_anova
            import pingouin as pg
            F = float(pg.welch_anova(data=df3, dv=var, between="g")["F"].iloc[0])
            assert r["statistic"]["value"] == pytest.approx(F, rel=1e-6)


def test_correlation_matches_scipy(df3):
    r = correlate(df3, "x", "y", result_id="K")
    if r["test"] == "pearson":
        rho, _ = stats.pearsonr(df3.x, df3.y)
    else:
        rho, _ = stats.spearmanr(df3.x, df3.y)
    assert r["coefficient"]["value"] == pytest.approx(float(rho), rel=1e-6)


def test_chi2_matches_scipy(df3):
    r = crosstab_test(df3, "cat", "g", result_id="C")
    ct = pd.crosstab(df3.cat, df3.g).to_numpy()
    # testin seçtiği düzeltmeye göre referans
    yates = (r["test"] == "chi_square_yates")
    if r["test"] in ("chi_square", "chi_square_yates"):
        chi2, _, _, _ = stats.chi2_contingency(ct, correction=yates)
        assert r["statistic"]["value"] == pytest.approx(float(chi2), rel=1e-6)


def test_regression_matches_statsmodels(df3):
    import statsmodels.api as sm
    r = linear_regression(df3, "y", ["x"], result_id="REG")
    sub = df3[["y", "x"]].dropna()
    m = sm.OLS(sub.y.to_numpy(float), sm.add_constant(sub.x.to_numpy(float))).fit(cov_type="HC3")
    assert r["coefficients"][0]["b"] == pytest.approx(float(m.params[1]), rel=1e-6)
    assert r["model"]["r2"] == pytest.approx(float(m.rsquared), rel=1e-6)
