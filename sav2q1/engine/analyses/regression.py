"""Doğrusal regresyon (OLS): standartlaştırılmış β, %95 GA, VIF, Breusch-Pagan,
artık normalliği. Çok değişkenli model için.
"""

from __future__ import annotations

import numpy as np
import statsmodels.api as sm
from scipy import stats as scipy_stats
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.outliers_influence import variance_inflation_factor

from ..fmt import fmt_num, fmt_ci
from .group_compare import _p_segment


def linear_regression(df, outcome: str, predictors: list[str], *, labels=None,
                      result_id: str = "REG1", question_ref: str | None = None) -> dict:
    labels = labels or {}
    sub = df[[outcome] + predictors].dropna()
    n = int(sub.shape[0])
    y = sub[outcome].to_numpy(float)
    X = sub[predictors].to_numpy(float)
    Xc = sm.add_constant(X)
    # Heteroskedastisiteye karşı dayanıklı çıkarım (HC3 robust SE) — bu veride
    # Breusch-Pagan ihlali beklendiğinden GA/p robust hesaplanır.
    ols = sm.OLS(y, Xc)
    model = ols.fit(cov_type="HC3")
    bp_p = float(het_breuschpagan(model.resid, Xc)[1])

    # standartlaştırılmış katsayılar (z-skor), yine HC3
    yz = (y - y.mean()) / y.std(ddof=1)
    Xz = (X - X.mean(0)) / X.std(0, ddof=1)
    model_z = sm.OLS(yz, sm.add_constant(Xz)).fit(cov_type="HC3")

    vifs = [float(variance_inflation_factor(Xc, i + 1)) for i in range(len(predictors))]
    resid_w, resid_p = scipy_stats.shapiro(model.resid)
    ci = model.conf_int()

    display: list[str] = []
    coefs = []
    for i, pname in enumerate(predictors):
        b = float(model.params[i + 1]); lo = float(ci[i + 1][0]); hi = float(ci[i + 1][1])
        pv = float(model.pvalues[i + 1]); beta = float(model_z.params[i + 1])
        capa = f"β = {fmt_num(beta)}, {_p_segment(pv)} (B = {fmt_num(b)}; %95 GA: {fmt_ci(lo, hi)})"
        coefs.append({
            "predictor": pname, "label": labels.get(pname, pname),
            "b": b, "ci": [lo, hi], "beta": beta, "p": pv, "vif": vifs[i], "apa": capa,
        })
        display += [capa, fmt_num(vifs[i])]

    r2 = float(model.rsquared); r2adj = float(model.rsquared_adj)
    F = float(model.fvalue); Fp = float(model.f_pvalue)
    dfn = len(predictors); dfd = n - len(predictors) - 1
    apa = (f"R² = {fmt_num(r2)}, düzeltilmiş R² = {fmt_num(r2adj)}, "
           f"F({dfn}, {dfd}) = {fmt_num(F)}, {_p_segment(Fp)}")
    display.append(apa)

    return {
        "id": result_id, "question_ref": question_ref, "family": "linear_regression",
        "outcome": outcome, "outcome_label": labels.get(outcome, outcome),
        "n_analyzed": n, "coefficients": coefs,
        "model": {"r2": r2, "r2_adj": r2adj, "F": F, "df1": dfn, "df2": dfd, "p": Fp},
        "diagnostics": {"se_type": "HC3 (robust)", "breusch_pagan_p": bp_p,
                        "residual_shapiro_p": float(resid_p),
                        "homoscedastic": bool(bp_p > 0.05), "residuals_normal": bool(resid_p > 0.05),
                        "max_vif": max(vifs) if vifs else None},
        "apa": apa, "_display": display, "_global": [str(n)],
    }
