"""Etki büyüklükleri ve %95 güven aralıkları.

Q1 şartı: HER çıkarımsal test bir etki büyüklüğü + GA raporlamalıdır.
GA'lar mümkün olduğunda analitik, değilse sabit-seed bootstrap ile hesaplanır.
"""

from __future__ import annotations

import numpy as np
from scipy import stats

from . import GLOBAL_SEED


def cohens_d(x, y) -> float:
    """Bağımsız iki grup için Cohen's d (pooled SD)."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    x = x[~np.isnan(x)]; y = y[~np.isnan(y)]
    nx, ny = len(x), len(y)
    sx2, sy2 = np.var(x, ddof=1), np.var(y, ddof=1)
    sp = np.sqrt(((nx - 1) * sx2 + (ny - 1) * sy2) / (nx + ny - 2))
    if sp == 0:
        return 0.0
    return float((np.mean(x) - np.mean(y)) / sp)


def hedges_g(x, y) -> float:
    """Küçük örneklem düzeltmeli Hedges' g."""
    d = cohens_d(x, y)
    nx = len(np.asarray(x, float)[~np.isnan(np.asarray(x, float))])
    ny = len(np.asarray(y, float)[~np.isnan(np.asarray(y, float))])
    dfree = nx + ny - 2
    J = 1.0 - 3.0 / (4.0 * dfree - 1.0) if dfree > 0 else 1.0
    return float(d * J)


def smd_ci(d: float, nx: int, ny: int, conf: float = 0.95) -> tuple[float, float]:
    """Standartlaştırılmış ortalama farkı (d/g) için yaklaşık GA (büyük örneklem)."""
    se = np.sqrt((nx + ny) / (nx * ny) + d ** 2 / (2.0 * (nx + ny)))
    z = stats.norm.ppf(1 - (1 - conf) / 2)
    return (float(d - z * se), float(d + z * se))


def rank_biserial_mwu(U: float, nx: int, ny: int) -> float:
    """Mann-Whitney U için sıralama-çift seri korelasyonu (etki büyüklüğü)."""
    return float(1.0 - (2.0 * U) / (nx * ny))


def rank_biserial_ci(x, y, conf: float = 0.95, n_boot: int = 5000) -> tuple[float, float]:
    """Sıralama-çift seri korelasyonu için sabit-seed bootstrap GA."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    x = x[~np.isnan(x)]; y = y[~np.isnan(y)]
    rng = np.random.default_rng(GLOBAL_SEED)

    def stat(a, b):
        U, _ = stats.mannwhitneyu(a, b, alternative="two-sided")
        return rank_biserial_mwu(U, len(a), len(b))

    boots = np.empty(n_boot)
    for i in range(n_boot):
        a = rng.choice(x, size=len(x), replace=True)
        b = rng.choice(y, size=len(y), replace=True)
        boots[i] = stat(a, b)
    lo = float(np.percentile(boots, 100 * (1 - conf) / 2))
    hi = float(np.percentile(boots, 100 * (1 - (1 - conf) / 2)))
    return (lo, hi)


def eta_squared_oneway(groups: list) -> float:
    """Tek yönlü ANOVA için eta-kare (SS_between / SS_total)."""
    arrs = [np.asarray(g, float) for g in groups]
    arrs = [a[~np.isnan(a)] for a in arrs]
    grand = np.concatenate(arrs)
    grand_mean = grand.mean()
    ss_between = sum(len(a) * (a.mean() - grand_mean) ** 2 for a in arrs)
    ss_total = ((grand - grand_mean) ** 2).sum()
    return float(ss_between / ss_total) if ss_total else 0.0


def cramers_v(table: np.ndarray) -> float:
    """Ki-kare bağımsızlık için Cramér's V."""
    table = np.asarray(table, float)
    chi2 = stats.chi2_contingency(table, correction=False)[0]
    n = table.sum()
    k = min(table.shape) - 1
    return float(np.sqrt(chi2 / (n * k))) if n and k else 0.0


def eta_squared_h(H: float, n: int, k: int) -> float:
    """Kruskal-Wallis için η² (eta-kare-H): (H - k + 1)/(n - k). 0–1 sınırlı."""
    denom = (n - k)
    return float((H - k + 1) / denom) if denom > 0 else 0.0


def eta_squared_ci_boot(arrays: list, n_boot: int = 1000, conf: float = 0.95,
                        kind: str = "anova") -> tuple[float, float]:
    """Tek yönlü η² (ANOVA) veya η²_H (KW) için katmanlı, sabit-seed bootstrap GA."""
    arrays = [np.asarray(a, float) for a in arrays]
    arrays = [a[~np.isnan(a)] for a in arrays]
    rng = np.random.default_rng(GLOBAL_SEED)
    k = len(arrays)
    boots = np.empty(n_boot)
    for i in range(n_boot):
        res = [rng.choice(a, size=len(a), replace=True) for a in arrays]
        if kind == "kw":
            H, _ = stats.kruskal(*res)
            n = sum(len(a) for a in res)
            boots[i] = eta_squared_h(H, n, k)
        else:
            boots[i] = eta_squared_oneway(res)
    lo = float(np.percentile(boots, 100 * (1 - conf) / 2))
    hi = float(np.percentile(boots, 100 * (1 - (1 - conf) / 2)))
    return (lo, hi)


def correlation_ci(r: float, n: int, conf: float = 0.95, spearman: bool = False) -> tuple[float, float]:
    """Pearson/Spearman korelasyonu için Fisher-z GA."""
    if n < 4 or abs(r) >= 1:
        return (float("nan"), float("nan"))
    z = np.arctanh(r)
    se = (1.03 if spearman else 1.0) / np.sqrt(n - 3)
    zc = stats.norm.ppf(1 - (1 - conf) / 2)
    return (float(np.tanh(z - zc * se)), float(np.tanh(z + zc * se)))
