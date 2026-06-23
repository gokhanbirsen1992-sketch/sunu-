"""Post-hoc ve Welch-ANOVA — yalnız scipy/statsmodels/numpy (pingouin/seaborn YOK).

Bu modül, çok-gruplu karşılaştırmanın pingouin + scikit_posthocs bağımlılığını
ortadan kaldırır; böylece Windows .exe paketlemesi küçük ve güvenilir olur.
Doğruluk, golden testlerde pingouin/scikit_posthocs referansına karşı doğrulanır.
"""

from __future__ import annotations

import numpy as np
from scipy import stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd


def _clean(arrays):
    arrays = [np.asarray(a, float) for a in arrays]
    return [a[~np.isnan(a)] for a in arrays]


def welch_anova(arrays) -> tuple[float, float, float, float]:
    """Welch'in eşit-olmayan varyans ANOVA'sı → (F, p, df1, df2)."""
    arrays = _clean(arrays)
    k = len(arrays)
    n = np.array([len(a) for a in arrays], float)
    m = np.array([a.mean() for a in arrays])
    v = np.array([a.var(ddof=1) for a in arrays])
    w = n / v
    sw = w.sum()
    xbar = (w * m).sum() / sw
    num = (w * (m - xbar) ** 2).sum() / (k - 1)
    term = ((1 - w / sw) ** 2 / (n - 1)).sum()
    denom = 1 + (2 * (k - 2) / (k ** 2 - 1)) * term
    F = num / denom
    df1 = k - 1
    df2 = (k ** 2 - 1) / (3 * term)
    p = float(stats.f.sf(F, df1, df2))
    return float(F), p, float(df1), float(df2)


def tukey_hsd(values, groups, codes) -> list[tuple]:
    """Tukey HSD (statsmodels) → [(code_a, code_b, p_adj), ...] codes sırasında."""
    res = pairwise_tukeyhsd(np.asarray(values, float), np.asarray(groups))
    gu = list(res.groupsunique)
    idx = {g: i for i, g in enumerate(gu)}
    pvals = np.asarray(res.pvalues, float)
    out = []
    pos = 0
    for i in range(len(gu)):
        for j in range(i + 1, len(gu)):
            out.append((gu[i], gu[j], float(pvals[pos]))); pos += 1
    # codes (analizdeki sıralı kodlar) düzeninde döndür
    bymap = {(min(a, b), max(a, b)): p for a, b, p in out}
    res_list = []
    for a in range(len(codes)):
        for b in range(a + 1, len(codes)):
            key = (min(codes[a], codes[b]), max(codes[a], codes[b]))
            res_list.append((codes[a], codes[b], bymap.get(key, float("nan"))))
    return res_list


def games_howell(arrays, codes) -> list[tuple]:
    """Games-Howell post-hoc (eşit-olmayan varyans) → [(code_a, code_b, p), ...]."""
    arrays = _clean(arrays)
    k = len(arrays)
    n = [len(a) for a in arrays]
    m = [a.mean() for a in arrays]
    v = [a.var(ddof=1) for a in arrays]
    out = []
    for i in range(k):
        for j in range(i + 1, k):
            se = np.sqrt(v[i] / n[i] + v[j] / n[j])
            t = abs(m[i] - m[j]) / se if se > 0 else 0.0
            df = (v[i] / n[i] + v[j] / n[j]) ** 2 / (
                (v[i] / n[i]) ** 2 / (n[i] - 1) + (v[j] / n[j]) ** 2 / (n[j] - 1))
            q = np.sqrt(2) * t
            p = float(stats.studentized_range.sf(q, k, df))
            out.append((codes[i], codes[j], min(1.0, p)))
    return out


def dunn(values, groups, codes) -> list[tuple]:
    """Kruskal sonrası Dunn post-hoc (Bonferroni) → [(code_a, code_b, p_adj), ...]."""
    values = np.asarray(values, float)
    groups = np.asarray(groups)
    mask = ~np.isnan(values)
    values, groups = values[mask], groups[mask]
    N = len(values)
    ranks = stats.rankdata(values)
    _, counts = np.unique(values, return_counts=True)
    tie = float((counts ** 3 - counts).sum())
    sigma_fac = N * (N + 1) / 12 - tie / (12 * (N - 1))
    rbar = {c: ranks[groups == c].mean() for c in codes}
    nn = {c: int((groups == c).sum()) for c in codes}
    m = len(codes) * (len(codes) - 1) // 2
    out = []
    for i in range(len(codes)):
        for j in range(i + 1, len(codes)):
            ci, cj = codes[i], codes[j]
            se = np.sqrt(sigma_fac * (1 / nn[ci] + 1 / nn[cj]))
            z = (rbar[ci] - rbar[cj]) / se if se > 0 else 0.0
            p = 2 * float(stats.norm.sf(abs(z)))
            out.append((ci, cj, min(1.0, p * m)))
    return out
