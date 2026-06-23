"""posthoc.py (scipy/statsmodels) çıktıları referansa (pingouin/scikit_posthocs)
karşı doğrulanır. pingouin/scikit_posthocs YALNIZ test bağımlılığıdır — motor
bunları artık import etmez (Windows .exe küçük ve güvenilir olsun diye)."""

import numpy as np
import pandas as pd
import pytest

pg = pytest.importorskip("pingouin")
sp = pytest.importorskip("scikit_posthocs")

from sav2q1.engine import posthoc


@pytest.fixture
def d():
    rng = np.random.default_rng(3)
    g = np.repeat([0, 1, 2], [40, 45, 35])
    y = np.concatenate([rng.normal(10, 2, 40), rng.normal(12, 4, 45), rng.normal(11, 6, 35)])
    return g, y, [0, 1, 2]


def test_welch_anova_matches_pingouin(d):
    g, y, codes = d
    F, p, _, _ = posthoc.welch_anova([y[g == c] for c in codes])
    ref = pg.welch_anova(data=pd.DataFrame({"y": y, "g": g}), dv="y", between="g")
    assert F == pytest.approx(float(ref["F"].iloc[0]), rel=1e-6)
    assert p == pytest.approx(float(ref["p_unc"].iloc[0]), rel=1e-6)


def test_tukey_matches_pingouin(d):
    g, y, codes = d
    mine = [x[2] for x in posthoc.tukey_hsd(y, g, codes)]
    ref = list(pg.pairwise_tukey(data=pd.DataFrame({"y": y, "g": g}), dv="y", between="g")["p_tukey"])
    assert mine == pytest.approx(ref, abs=1e-4)


def test_gameshowell_matches_pingouin(d):
    g, y, codes = d
    mine = [x[2] for x in posthoc.games_howell([y[g == c] for c in codes], codes)]
    ref = list(pg.pairwise_gameshowell(data=pd.DataFrame({"y": y, "g": g}), dv="y", between="g")["pval"])
    assert mine == pytest.approx(ref, abs=1e-4)


def test_dunn_matches_scikit():
    rng = np.random.default_rng(5)
    g = np.repeat([0, 1, 2], [40, 45, 35])
    y = np.concatenate([rng.exponential(1, 40), rng.exponential(2, 45), rng.exponential(3, 35)])
    codes = [0, 1, 2]
    mine = [x[2] for x in posthoc.dunn(y, g, codes)]
    dd = sp.posthoc_dunn(pd.DataFrame({"y": y, "g": g}), val_col="y", group_col="g", p_adjust="bonferroni")
    ref = [dd.loc[codes[i], codes[j]] for i in range(3) for j in range(i + 1, 3)]
    assert mine == pytest.approx(ref, abs=1e-6)
