from __future__ import annotations

import warnings

import numpy as np
import pandas as pd

from .auto_typer import VarType
from .multivariate import _design_matrix


def run_kaplan_meier(
    df: pd.DataFrame,
    time_col: str,
    event_col: str,
    group_col: str | None = None,
) -> dict:
    from lifelines import KaplanMeierFitter
    from lifelines.statistics import logrank_test, multivariate_logrank_test

    data = df[[time_col, event_col] + ([group_col] if group_col else [])].dropna()
    data[time_col] = pd.to_numeric(data[time_col], errors="coerce")
    data[event_col] = pd.to_numeric(data[event_col], errors="coerce")
    data = data.dropna()

    curves: dict[str, dict] = {}
    if group_col is None:
        kmf = KaplanMeierFitter()
        kmf.fit(data[time_col], data[event_col], label="all")
        curves["all"] = {
            "timeline": kmf.timeline.tolist(),
            "survival": kmf.survival_function_.iloc[:, 0].tolist(),
            "median": float(kmf.median_survival_time_) if not np.isnan(kmf.median_survival_time_) else None,
        }
        return {"curves": curves, "logrank_p": None, "n": len(data)}

    groups = data[group_col].unique()
    for g in groups:
        sub = data[data[group_col] == g]
        if sub.empty:
            continue
        kmf = KaplanMeierFitter()
        kmf.fit(sub[time_col], sub[event_col], label=str(g))
        curves[str(g)] = {
            "timeline": kmf.timeline.tolist(),
            "survival": kmf.survival_function_.iloc[:, 0].tolist(),
            "median": float(kmf.median_survival_time_) if not np.isnan(kmf.median_survival_time_) else None,
            "n": int(len(sub)),
            "events": int(sub[event_col].sum()),
        }

    if len(groups) == 2:
        a, b = groups
        res = logrank_test(
            data.loc[data[group_col] == a, time_col], data.loc[data[group_col] == b, time_col],
            data.loc[data[group_col] == a, event_col], data.loc[data[group_col] == b, event_col],
        )
        p = float(res.p_value)
    else:
        res = multivariate_logrank_test(data[time_col], data[group_col], data[event_col])
        p = float(res.p_value)

    return {"curves": curves, "logrank_p": p, "n": len(data)}


def run_cox(
    df: pd.DataFrame,
    time_col: str,
    event_col: str,
    features: list[str],
    types: dict[str, VarType],
) -> dict:
    from lifelines import CoxPHFitter

    X = _design_matrix(df, features, types)
    base = pd.DataFrame({
        time_col: pd.to_numeric(df[time_col], errors="coerce"),
        event_col: pd.to_numeric(df[event_col], errors="coerce"),
    })
    data = pd.concat([base, X], axis=1).dropna()
    if len(data) < len(X.columns) + 10 or data[event_col].sum() < len(X.columns) + 5:
        return {"error": f"Yetersiz olay sayısı: {int(data[event_col].sum())} olay, {len(X.columns)} öznitelik"}

    cph = CoxPHFitter()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            cph.fit(data, duration_col=time_col, event_col=event_col)
        except Exception as e:
            return {"error": f"Cox regresyon başarısız: {e}"}

    s = cph.summary
    coef = pd.DataFrame({
        "variable": s.index,
        "HR": s["exp(coef)"].values,
        "HR_ci_low": s["exp(coef) lower 95%"].values,
        "HR_ci_high": s["exp(coef) upper 95%"].values,
        "p": s["p"].values,
    })
    return {
        "type": "cox",
        "n": int(len(data)),
        "events": int(data[event_col].sum()),
        "concordance": float(cph.concordance_index_),
        "log_likelihood_ratio_p": float(cph.log_likelihood_ratio_test().p_value),
        "coefficients": coef,
        "summary": str(cph.summary),
    }
