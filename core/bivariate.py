from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests

from .auto_typer import VarType


def _normality_ok(s: pd.Series) -> bool:
    s = s.dropna()
    if len(s) < 8:
        return False
    if len(s) > 5000:
        s = s.sample(5000, random_state=0)
    try:
        _, p = stats.shapiro(s)
        return p > 0.05
    except Exception:
        return False


def _test_continuous_continuous(x: pd.Series, y: pd.Series) -> dict:
    df = pd.concat([x, y], axis=1).dropna()
    if len(df) < 3:
        return {"test": "pearson", "stat": np.nan, "p": np.nan, "n": len(df), "effect": np.nan}
    if _normality_ok(df.iloc[:, 0]) and _normality_ok(df.iloc[:, 1]):
        r, p = stats.pearsonr(df.iloc[:, 0], df.iloc[:, 1])
        return {"test": "Pearson r", "stat": float(r), "p": float(p), "n": len(df), "effect": float(r)}
    r, p = stats.spearmanr(df.iloc[:, 0], df.iloc[:, 1])
    return {"test": "Spearman ρ", "stat": float(r), "p": float(p), "n": len(df), "effect": float(r)}


def _test_continuous_binary(cont: pd.Series, binary: pd.Series) -> dict:
    df = pd.concat([cont, binary], axis=1).dropna()
    if df.iloc[:, 1].nunique() < 2 or len(df) < 4:
        return {"test": "t-test", "stat": np.nan, "p": np.nan, "n": len(df), "effect": np.nan}
    groups = [g.iloc[:, 0].values for _, g in df.groupby(df.columns[1])]
    if len(groups) != 2:
        return {"test": "t-test", "stat": np.nan, "p": np.nan, "n": len(df), "effect": np.nan}
    if all(_normality_ok(pd.Series(g)) for g in groups):
        t, p = stats.ttest_ind(groups[0], groups[1], equal_var=False)
        pooled_sd = np.sqrt((np.var(groups[0], ddof=1) + np.var(groups[1], ddof=1)) / 2)
        d = (np.mean(groups[0]) - np.mean(groups[1])) / pooled_sd if pooled_sd else np.nan
        return {"test": "Welch t", "stat": float(t), "p": float(p), "n": len(df), "effect": float(d)}
    u, p = stats.mannwhitneyu(groups[0], groups[1], alternative="two-sided")
    n1, n2 = len(groups[0]), len(groups[1])
    r_eff = 1 - (2 * u) / (n1 * n2)
    return {"test": "Mann-Whitney U", "stat": float(u), "p": float(p), "n": len(df), "effect": float(r_eff)}


def _test_continuous_categorical(cont: pd.Series, cat: pd.Series) -> dict:
    df = pd.concat([cont, cat], axis=1).dropna()
    groups = [g.iloc[:, 0].values for _, g in df.groupby(df.columns[1]) if len(g) >= 2]
    if len(groups) < 2:
        return {"test": "ANOVA", "stat": np.nan, "p": np.nan, "n": len(df), "effect": np.nan}
    if all(_normality_ok(pd.Series(g)) for g in groups):
        f, p = stats.f_oneway(*groups)
        ss_b = sum(len(g) * (np.mean(g) - np.mean(np.concatenate(groups))) ** 2 for g in groups)
        ss_t = sum(((np.concatenate(groups) - np.mean(np.concatenate(groups))) ** 2))
        eta2 = ss_b / ss_t if ss_t else np.nan
        return {"test": "ANOVA", "stat": float(f), "p": float(p), "n": len(df), "effect": float(eta2)}
    h, p = stats.kruskal(*groups)
    return {"test": "Kruskal-Wallis", "stat": float(h), "p": float(p), "n": len(df), "effect": np.nan}


def _test_categorical_categorical(a: pd.Series, b: pd.Series) -> dict:
    df = pd.concat([a, b], axis=1).dropna()
    if len(df) < 4:
        return {"test": "chi2", "stat": np.nan, "p": np.nan, "n": len(df), "effect": np.nan}
    table = pd.crosstab(df.iloc[:, 0], df.iloc[:, 1])
    if table.shape[0] < 2 or table.shape[1] < 2:
        return {"test": "chi2", "stat": np.nan, "p": np.nan, "n": len(df), "effect": np.nan}
    expected_min = (table.values.sum(axis=0, keepdims=True) * table.values.sum(axis=1, keepdims=True)
                    / table.values.sum()).min()
    use_fisher = table.shape == (2, 2) and expected_min < 5
    if use_fisher:
        odds, p = stats.fisher_exact(table.values)
        return {"test": "Fisher exact", "stat": float(odds), "p": float(p), "n": len(df), "effect": float(odds)}
    chi2, p, dof, _ = stats.chi2_contingency(table.values)
    n = table.values.sum()
    cramer = np.sqrt(chi2 / (n * (min(table.shape) - 1))) if n else np.nan
    return {"test": "Chi²", "stat": float(chi2), "p": float(p), "n": int(n), "effect": float(cramer)}


def run_bivariate(
    df: pd.DataFrame,
    outcome: str,
    types: dict[str, VarType],
    skip: set[str] | None = None,
) -> pd.DataFrame:
    skip = (skip or set()) | {outcome}
    out_type = types[outcome]
    rows: list[dict] = []

    for feat in df.columns:
        if feat in skip:
            continue
        ft = types.get(feat, "continuous")
        if ft == "id_or_text":
            continue
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            res = _dispatch(df[feat], df[outcome], ft, out_type)
        rows.append({"feature": feat, "feature_type": ft, "outcome_type": out_type, **res})

    if not rows:
        return pd.DataFrame(columns=["feature", "test", "p", "p_fdr", "significant"])

    res_df = pd.DataFrame(rows)
    valid = res_df["p"].notna()
    res_df["p_fdr"] = np.nan
    if valid.any():
        _, p_adj, _, _ = multipletests(res_df.loc[valid, "p"], method="fdr_bh")
        res_df.loc[valid, "p_fdr"] = p_adj
    res_df["significant"] = (res_df["p_fdr"] < 0.05).fillna(False)
    return res_df.sort_values("p", na_position="last").reset_index(drop=True)


def _dispatch(x: pd.Series, y: pd.Series, xt: VarType, yt: VarType) -> dict:
    cont = {"continuous", "ordinal"}
    if xt in cont and yt in cont:
        return _test_continuous_continuous(x, y)
    if xt in cont and yt == "binary":
        return _test_continuous_binary(x, y)
    if xt == "binary" and yt in cont:
        return _test_continuous_binary(y, x)
    if xt in cont and yt == "categorical":
        return _test_continuous_categorical(x, y)
    if xt == "categorical" and yt in cont:
        return _test_continuous_categorical(y, x)
    return _test_categorical_categorical(x, y)
