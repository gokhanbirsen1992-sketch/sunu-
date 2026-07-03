"""Etki büyüklüğü hesapları."""
from __future__ import annotations

import math

import numpy as np


def cohen_d(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = len(a), len(b)
    va, vb = np.var(a, ddof=1), np.var(b, ddof=1)
    pooled = ((na - 1) * va + (nb - 1) * vb) / (na + nb - 2)
    if pooled <= 0:
        return 0.0
    return float((np.mean(a) - np.mean(b)) / math.sqrt(pooled))


def rank_biserial_from_u(u: float, n1: int, n2: int) -> float:
    return float(1 - (2 * u) / (n1 * n2))


def eta_squared_anova(groups: list[np.ndarray]) -> float:
    all_vals = np.concatenate(groups)
    grand = all_vals.mean()
    ss_between = sum(len(g) * (g.mean() - grand) ** 2 for g in groups)
    ss_total = float(((all_vals - grand) ** 2).sum())
    return float(ss_between / ss_total) if ss_total > 0 else 0.0


def epsilon_squared_kruskal(h: float, n: int, k: int) -> float:
    if n <= k:
        return 0.0
    return float((h - k + 1) / (n - k))


def cramers_v(chi2: float, n: int, shape: tuple[int, int]) -> float:
    r, c = shape
    denom = n * (min(r, c) - 1)
    return float(math.sqrt(chi2 / denom)) if denom > 0 else 0.0
