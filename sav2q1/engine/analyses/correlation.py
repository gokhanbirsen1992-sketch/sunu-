"""Korelasyon analizi: Pearson/Spearman + GA + korelasyon matrisi.

Normallik durumuna göre test seçilir (decision_tree). Her korelasyon etki
büyüklüğüdür ve Fisher-z GA ile raporlanır.
"""

from __future__ import annotations

import numpy as np
from scipy import stats

from .. import assumptions, decision_tree, effects
from ..fmt import fmt_num, fmt_ci
from .group_compare import _p_segment


def correlate(df, x: str, y: str, *, label_x: str = "", label_y: str = "",
              result_id: str = "K", question_ref: str | None = None,
              confirmatory: bool = False) -> dict:
    sub = df[[x, y]].dropna()
    a = sub[x].to_numpy(float); b = sub[y].to_numpy(float)
    n = int(sub.shape[0])
    both_normal = bool(assumptions.shapiro(a)["normal"] and assumptions.shapiro(b)["normal"])
    test_id, reason = decision_tree.choose_correlation_test(both_normal)

    if test_id == "pearson":
        r, p = stats.pearsonr(a, b); coef, spear = "r", False
    else:
        r, p = stats.spearmanr(a, b); coef, spear = "rho", True
    lo, hi = effects.correlation_ci(float(r), n, spearman=spear)
    apa = f"{coef} = {fmt_num(float(r))}, {_p_segment(p)} (%95 GA: {fmt_ci(lo, hi)}; n = {n})"

    return {
        "id": result_id, "question_ref": question_ref, "family": "correlation",
        "test": test_id, "reason": reason, "confirmatory": confirmatory,
        "variables": {"x": x, "y": y, "label_x": label_x, "label_y": label_y},
        "coefficient": {"name": coef, "value": float(r), "ci": [lo, hi]},
        "p_value": float(p), "n_analyzed": n, "apa": apa,
        "_display": [apa], "_global": [str(n)],
    }


def correlation_matrix(df, xs: list[str], ys: list[str], *, labels=None,
                       result_id: str = "KMAT", question_ref: str | None = None) -> dict:
    """xs (belirteçler) × ys (sonuçlar) korelasyon matrisi; her hücre bir korelasyon."""
    labels = labels or {}
    rows = []
    display: list[str] = []
    for xi, x in enumerate(xs):
        for yi, y in enumerate(ys):
            c = correlate(df, x, y, label_x=labels.get(x, x), label_y=labels.get(y, y),
                          result_id=f"{result_id}.{xi}.{yi}")
            rows.append({"x": x, "y": y, "test": c["test"],
                         "r": c["coefficient"]["value"], "ci": c["coefficient"]["ci"],
                         "p": c["p_value"], "n": c["n_analyzed"], "apa": c["apa"]})
            display.append(c["apa"])
    return {
        "id": result_id, "question_ref": question_ref, "family": "correlation_matrix",
        "x_vars": xs, "y_vars": ys, "cells": rows, "apa": f"{len(rows)} korelasyon",
        "_display": display, "_global": [],
    }
