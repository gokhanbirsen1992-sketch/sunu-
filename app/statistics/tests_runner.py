"""Planlanan testleri deterministik olarak çalıştırır — sayıları asla LLM üretmez."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests

from app.models import Finding, JobConfig, PlannedTest, VariableInfo
from app.statistics import effect_sizes as es
from app.statistics.reporting import apa_result


def run_tests(
    df: pd.DataFrame,
    plans: list[PlannedTest],
    variables: list[VariableInfo],
    config: JobConfig,
) -> list[Finding]:
    vmap = {v.name: v for v in variables}
    findings: list[Finding] = []
    for i, plan in enumerate(plans, start=1):
        f = Finding(id=f"F{i}", planned=plan)
        try:
            _run_single(df, plan, f)
        except Exception as exc:  # tek testin çökmesi pipeline'ı durdurmasın
            f.error = f"{type(exc).__name__}: {exc}"
        findings.append(f)

    _adjust_pvalues(findings, config)

    for f in findings:
        p_final = f.p_adjusted if f.p_adjusted is not None else f.p_value
        f.significant = bool(p_final is not None and p_final < config.alpha and f.error is None)
        f.keywords = _keywords(f, vmap)
        if f.error is None:
            f.apa_tr = apa_result(f, vmap, "tr")
            f.apa_en = apa_result(f, vmap, "en")
    return findings


def _adjust_pvalues(findings: list[Finding], config: JobConfig) -> None:
    if config.p_adjust == "none":
        return
    method = {"holm": "holm", "fdr_bh": "fdr_bh"}[config.p_adjust]
    for family in ("group", "correlation", "association", "regression"):
        fam = [f for f in findings if f.planned.family == family and f.p_value is not None and f.error is None]
        if len(fam) < 2:
            for f in fam:
                f.p_adjusted = f.p_value
            continue
        _, adj, _, _ = multipletests([f.p_value for f in fam], method=method)
        for f, p in zip(fam, adj):
            f.p_adjusted = float(p)


def _group_arrays(df: pd.DataFrame, plan: PlannedTest) -> list[tuple[str, np.ndarray]]:
    sub = df[[plan.dv, plan.iv]].dropna()
    out = []
    for level, grp in sub.groupby(plan.iv, observed=True):
        vals = pd.to_numeric(grp[plan.dv], errors="coerce").dropna().to_numpy(dtype=float)
        if len(vals) >= 3:
            out.append((str(level), vals))
    return out


def _gstats(groups: list[tuple[str, np.ndarray]]) -> list[dict]:
    return [
        {
            "group": name, "n": int(len(v)), "mean": float(np.mean(v)),
            "sd": float(np.std(v, ddof=1)) if len(v) > 1 else 0.0,
            "median": float(np.median(v)),
        }
        for name, v in groups
    ]


def _run_single(df: pd.DataFrame, plan: PlannedTest, f: Finding) -> None:
    t = plan.test_id
    if t in ("ttest_ind", "welch_t", "mannwhitney", "anova", "kruskal"):
        groups = _group_arrays(df, plan)
        if len(groups) < 2:
            raise ValueError("yeterli grup yok")
        arrays = [g[1] for g in groups]
        f.group_stats = _gstats(groups)
        if t in ("ttest_ind", "welch_t"):
            equal_var = t == "ttest_ind"
            res = stats.ttest_ind(arrays[0], arrays[1], equal_var=equal_var)
            f.statistic_name, f.statistic, f.p_value = "t", float(res.statistic), float(res.pvalue)
            f.df = float(getattr(res, "df", len(arrays[0]) + len(arrays[1]) - 2))
            f.effect_size_name, f.effect_size = "d", es.cohen_d(arrays[0], arrays[1])
        elif t == "mannwhitney":
            res = stats.mannwhitneyu(arrays[0], arrays[1], alternative="two-sided")
            f.statistic_name, f.statistic, f.p_value = "U", float(res.statistic), float(res.pvalue)
            f.effect_size_name = "r_rb"
            f.effect_size = es.rank_biserial_from_u(float(res.statistic), len(arrays[0]), len(arrays[1]))
        elif t == "anova":
            res = stats.f_oneway(*arrays)
            f.statistic_name, f.statistic, f.p_value = "F", float(res.statistic), float(res.pvalue)
            k, n = len(arrays), sum(len(a) for a in arrays)
            f.df = [k - 1, n - k]
            f.effect_size_name, f.effect_size = "η²", es.eta_squared_anova(arrays)
            _tukey_posthoc(f, groups)
        else:  # kruskal
            res = stats.kruskal(*arrays)
            f.statistic_name, f.statistic, f.p_value = "H", float(res.statistic), float(res.pvalue)
            k, n = len(arrays), sum(len(a) for a in arrays)
            f.df = k - 1
            f.effect_size_name, f.effect_size = "ε²", es.epsilon_squared_kruskal(float(res.statistic), n, k)
            _pairwise_mwu_posthoc(f, groups)
        return

    if t in ("pearson", "spearman"):
        sub = df[[plan.dv, plan.iv]].dropna()
        a = pd.to_numeric(sub[plan.dv], errors="coerce")
        b = pd.to_numeric(sub[plan.iv], errors="coerce")
        mask = a.notna() & b.notna()
        a, b = a[mask].to_numpy(float), b[mask].to_numpy(float)
        if len(a) < 5:
            raise ValueError("yeterli veri yok")
        if t == "pearson":
            res = stats.pearsonr(a, b)
            f.statistic_name = "r"
        else:
            res = stats.spearmanr(a, b)
            f.statistic_name = "ρ"
        f.statistic, f.p_value = float(res.statistic), float(res.pvalue)
        f.df = len(a) - 2
        f.effect_size_name, f.effect_size = f.statistic_name, f.statistic
        f.group_stats = [{"n": int(len(a))}]
        return

    if t in ("chi2", "fisher"):
        sub = df[[plan.dv, plan.iv]].dropna()
        table = pd.crosstab(sub[plan.dv], sub[plan.iv])
        n = int(table.values.sum())
        f.group_stats = [{"crosstab": {str(k): {str(c): int(x) for c, x in row.items()} for k, row in table.to_dict("index").items()}, "n": n}]
        if t == "chi2":
            chi2, p, dof, _ = stats.chi2_contingency(table.values)
            f.statistic_name, f.statistic, f.p_value, f.df = "χ²", float(chi2), float(p), int(dof)
            f.effect_size_name = "V"
            f.effect_size = es.cramers_v(float(chi2), n, table.shape)
        else:
            odds, p = stats.fisher_exact(table.values)
            f.statistic_name, f.statistic, f.p_value = "OR", float(odds), float(p)
        return

    if t == "linreg":
        import statsmodels.api as sm

        cols = [plan.dv] + plan.extra_vars
        sub = df[cols].apply(pd.to_numeric, errors="coerce").dropna()
        if len(sub) < len(plan.extra_vars) + 10:
            raise ValueError("regresyon için yeterli veri yok")
        X = sm.add_constant(sub[plan.extra_vars])
        model = sm.OLS(sub[plan.dv], X).fit()
        f.statistic_name, f.statistic = "F", float(model.fvalue)
        f.p_value = float(model.f_pvalue)
        f.df = [int(model.df_model), int(model.df_resid)]
        f.effect_size_name, f.effect_size = "R²", float(model.rsquared)
        f.group_stats = [
            {
                "r_squared": float(model.rsquared),
                "adj_r_squared": float(model.rsquared_adj),
                "n": int(model.nobs),
                "coefficients": [
                    {
                        "term": term,
                        "b": float(model.params[term]),
                        "se": float(model.bse[term]),
                        "t": float(model.tvalues[term]),
                        "p": float(model.pvalues[term]),
                    }
                    for term in model.params.index
                ],
            }
        ]
        return

    raise ValueError(f"bilinmeyen test: {t}")


def _tukey_posthoc(f: Finding, groups: list[tuple[str, np.ndarray]]) -> None:
    if f.p_value is None or f.p_value >= 0.05:
        return
    try:
        from statsmodels.stats.multicomp import pairwise_tukeyhsd

        values = np.concatenate([g[1] for g in groups])
        labels = np.concatenate([[g[0]] * len(g[1]) for g in groups])
        res = pairwise_tukeyhsd(values, labels)
        for row in res.summary().data[1:]:
            f.posthoc.append(
                {"method": "Tukey HSD", "a": str(row[0]), "b": str(row[1]),
                 "p": float(row[3]), "significant": bool(row[6])}
            )
    except Exception:
        pass


def _pairwise_mwu_posthoc(f: Finding, groups: list[tuple[str, np.ndarray]]) -> None:
    if f.p_value is None or f.p_value >= 0.05:
        return
    pairs, ps = [], []
    for i in range(len(groups)):
        for j in range(i + 1, len(groups)):
            res = stats.mannwhitneyu(groups[i][1], groups[j][1], alternative="two-sided")
            pairs.append((groups[i][0], groups[j][0]))
            ps.append(float(res.pvalue))
    if not ps:
        return
    _, adj, _, _ = multipletests(ps, method="holm")
    for (a, b), p in zip(pairs, adj):
        f.posthoc.append({"method": "Mann-Whitney (Holm)", "a": a, "b": b, "p": float(p), "significant": bool(p < 0.05)})


def _keywords(f: Finding, vmap: dict[str, VariableInfo]) -> list[str]:
    words: list[str] = []
    for name in [f.planned.dv, f.planned.iv, *f.planned.extra_vars]:
        if not name:
            continue
        v = vmap.get(name)
        words.append((v.label or v.name) if v else name)
    return words
