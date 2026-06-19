"""Kategorik × kategorik analiz: ki-kare / Fisher / McNemar + Cramér's V."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from .. import decision_tree, effects
from ..fmt import fmt_num, fmt_p
from .group_compare import _group_label, _p_segment


def crosstab_test(df, row_var: str, col_var: str, *, value_labels_row=None,
                  value_labels_col=None, result_id: str = "C", question_ref: str | None = None,
                  confirmatory: bool = False) -> dict:
    sub = df[[row_var, col_var]].dropna()
    ct = pd.crosstab(sub[row_var], sub[col_var])
    table = ct.to_numpy(float)
    r, c = table.shape
    chi2, p, dof, expected = stats.chi2_contingency(table, correction=False)
    min_exp = float(expected.min())
    test_id, reason = decision_tree.choose_categorical_test(r, c, min_exp, paired=False)

    display: list[str] = []
    glob: list[str] = [str(int(table.sum()))]

    if test_id == "fisher_exact" and r == 2 and c == 2:
        _, p = stats.fisher_exact(table)
        v = effects.cramers_v(table)
        apa = f"Fisher kesin testi, {_p_segment(p)}, V = {fmt_num(v)}"
        stat = {"name": "fisher_exact"}
    else:
        yates = (test_id == "chi_square_yates")
        chi2, p, dof, _ = stats.chi2_contingency(table, correction=yates)
        v = effects.cramers_v(table)
        apa = f"χ²({dof}) = {fmt_num(chi2)}, {_p_segment(p)}, V = {fmt_num(v)}"
        stat = {"name": "chi_square", "value": float(chi2), "df": int(dof), "yates": yates}

    # hücreler (satır=row kategorisi, sütun=col kategorisi) — Tablo için
    cells = []
    for ri, ridx in enumerate(ct.index):
        rlab = _group_label(value_labels_row, ridx)
        for ci, cidx in enumerate(ct.columns):
            clab = _group_label(value_labels_col, cidx)
            n = int(ct.iloc[ri, ci])
            col_total = int(ct.iloc[:, ci].sum())
            pct = round(100.0 * n / col_total, 1) if col_total else 0.0
            cells.append({"row": rlab, "col": clab, "n": n, "col_pct": pct})
            display.append(f"{n} (%{fmt_num(pct, 1)})")

    display.append(apa)
    return {
        "id": result_id, "question_ref": question_ref, "family": "categorical",
        "test": test_id, "reason": reason, "confirmatory": confirmatory,
        "variables": {"row": row_var, "col": col_var},
        "table_shape": [r, c], "min_expected": min_exp,
        "cells": cells, "statistic": stat, "p_value": float(p),
        "effect": {"name": "Cramér's V", "value": float(v)},
        "n_analyzed": int(table.sum()), "apa": apa,
        "_display": display, "_global": glob,
    }
