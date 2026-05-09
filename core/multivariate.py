from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor

from .auto_typer import VarType


def _design_matrix(df: pd.DataFrame, features: list[str], types: dict[str, VarType]) -> pd.DataFrame:
    parts = []
    for f in features:
        s = df[f]
        if types.get(f) in {"continuous", "ordinal"}:
            parts.append(pd.to_numeric(s, errors="coerce").rename(f).to_frame())
        else:
            d = pd.get_dummies(s, prefix=f, drop_first=True, dummy_na=False, dtype=float)
            parts.append(d)
    if not parts:
        return pd.DataFrame(index=df.index)
    X = pd.concat(parts, axis=1)
    return X.astype(float)


def _vif(X: pd.DataFrame) -> pd.DataFrame:
    Xn = X.dropna()
    if Xn.shape[1] < 2 or len(Xn) < Xn.shape[1] + 2:
        return pd.DataFrame({"variable": Xn.columns, "VIF": [np.nan] * Xn.shape[1]})
    Xn = sm.add_constant(Xn, has_constant="add")
    vifs = []
    for i, col in enumerate(Xn.columns):
        if col == "const":
            continue
        try:
            vifs.append({"variable": col, "VIF": float(variance_inflation_factor(Xn.values, i))})
        except Exception:
            vifs.append({"variable": col, "VIF": np.nan})
    return pd.DataFrame(vifs)


def run_linear(df: pd.DataFrame, outcome: str, features: list[str], types: dict[str, VarType]) -> dict:
    y = pd.to_numeric(df[outcome], errors="coerce")
    X = _design_matrix(df, features, types)
    data = pd.concat([y.rename(outcome), X], axis=1).dropna()
    if len(data) < len(X.columns) + 5:
        return {"error": f"Yetersiz örneklem: {len(data)} satır, {len(X.columns)} öznitelik"}
    Xc = sm.add_constant(data[X.columns], has_constant="add")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = sm.OLS(data[outcome], Xc).fit()
    coef = pd.DataFrame({
        "variable": model.params.index,
        "beta": model.params.values,
        "std_err": model.bse.values,
        "ci_low": model.conf_int().iloc[:, 0].values,
        "ci_high": model.conf_int().iloc[:, 1].values,
        "p": model.pvalues.values,
    })
    return {
        "type": "linear",
        "n": int(model.nobs),
        "r2": float(model.rsquared),
        "r2_adj": float(model.rsquared_adj),
        "f_p": float(model.f_pvalue) if model.f_pvalue is not None else np.nan,
        "coefficients": coef,
        "vif": _vif(data[X.columns]),
        "summary": str(model.summary()),
    }


def run_logistic(df: pd.DataFrame, outcome: str, features: list[str], types: dict[str, VarType]) -> dict:
    raw = df[outcome].dropna()
    if raw.nunique() != 2:
        return {"error": f"Lojistik için outcome 2 değerli olmalı, {raw.nunique()} bulundu"}
    levels = sorted(raw.unique().tolist())
    y = (df[outcome] == levels[1]).astype(float).where(df[outcome].notna())
    X = _design_matrix(df, features, types)
    data = pd.concat([y.rename(outcome), X], axis=1).dropna()
    if len(data) < len(X.columns) + 10:
        return {"error": f"Yetersiz örneklem: {len(data)} satır"}
    Xc = sm.add_constant(data[X.columns], has_constant="add")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            model = sm.Logit(data[outcome], Xc).fit(disp=0, maxiter=100)
        except Exception as e:
            return {"error": f"Lojistik regresyon başarısız: {e}"}
    params = model.params
    conf = model.conf_int()
    coef = pd.DataFrame({
        "variable": params.index,
        "beta": params.values,
        "OR": np.exp(params.values),
        "OR_ci_low": np.exp(conf.iloc[:, 0].values),
        "OR_ci_high": np.exp(conf.iloc[:, 1].values),
        "p": model.pvalues.values,
    })
    return {
        "type": "logistic",
        "n": int(model.nobs),
        "pseudo_r2": float(model.prsquared),
        "llr_p": float(model.llr_pvalue) if model.llr_pvalue is not None else np.nan,
        "outcome_levels": {"reference": levels[0], "event": levels[1]},
        "coefficients": coef,
        "vif": _vif(data[X.columns]),
        "summary": str(model.summary()),
    }


def auto_multivariate(
    df: pd.DataFrame,
    outcome: str,
    features: list[str],
    types: dict[str, VarType],
) -> dict:
    if types.get(outcome) == "binary":
        return run_logistic(df, outcome, features, types)
    if types.get(outcome) in {"continuous", "ordinal"}:
        return run_linear(df, outcome, features, types)
    return {"error": f"Outcome tipi desteklenmiyor: {types.get(outcome)}"}
