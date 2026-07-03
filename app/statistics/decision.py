"""Test seçim kural motoru: hangi istatistiksel test, neden?"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from app.models import NormalityResult, PlannedTest, VariableInfo

MAX_TESTS = 40
MIN_GROUP_N = 3


def assess_normality(series: pd.Series) -> NormalityResult:
    vals = pd.to_numeric(series, errors="coerce").dropna().astype(float)
    n = len(vals)
    res = NormalityResult(n=n)
    if n < MIN_GROUP_N:
        res.basis = "n çok küçük"
        return res
    res.skew = float(stats.skew(vals)) if n > 2 else None
    res.kurtosis = float(stats.kurtosis(vals)) if n > 3 else None
    shape_loose = (res.skew is None or abs(res.skew) < 2) and (res.kurtosis is None or abs(res.kurtosis) < 7)
    shape_mild = (res.skew is None or abs(res.skew) < 1) and (res.kurtosis is None or abs(res.kurtosis) < 3)
    if n <= 5000:
        try:
            w, p = stats.shapiro(vals)
            res.shapiro_w, res.shapiro_p = float(w), float(p)
        except ValueError:
            pass
    if res.shapiro_p is not None:
        if n <= 50:
            res.normal = bool(res.shapiro_p > 0.05 and shape_loose)
            res.basis = "Shapiro-Wilk + çarpıklık/basıklık"
        else:
            # büyük n'de Shapiro önemsiz sapmaları da reddeder; ılımlı şekil ölçütüyle dengele
            res.normal = bool(shape_mild or (res.shapiro_p > 0.05 and shape_loose))
            res.basis = "Shapiro-Wilk + çarpıklık/basıklık (n>50 dengeli)"
    else:
        res.normal = shape_mild
        res.basis = "çarpıklık/basıklık"
    return res


def _groups(df: pd.DataFrame, dv: str, iv: str) -> list[tuple[str, pd.Series]]:
    sub = df[[dv, iv]].dropna()
    out = []
    for level, grp in sub.groupby(iv, observed=True):
        vals = pd.to_numeric(grp[dv], errors="coerce").dropna()
        if len(vals) >= MIN_GROUP_N:
            out.append((str(level), vals))
    return out


def _label(variables: dict[str, VariableInfo], name: str) -> str:
    v = variables.get(name)
    return (v.label or v.name) if v else name


def plan_tests(
    df: pd.DataFrame, variables: list[VariableInfo]
) -> tuple[list[PlannedTest], list[str]]:
    """PlannedTest listesi + genel notlar (TR) döndürür."""
    notes: list[str] = []
    plans: list[PlannedTest] = []
    vmap = {v.name: v for v in variables}

    active = [v for v in variables if v.role != "exclude" and v.kind in ("continuous", "ordinal", "nominal", "binary")]
    cat_vars = [v for v in active if v.kind in ("nominal", "binary")]
    num_vars = [v for v in active if v.kind in ("continuous", "ordinal")]
    cont_vars = [v for v in active if v.kind == "continuous"]

    # --- Grup karşılaştırmaları ---
    for iv in cat_vars:
        for dv in num_vars:
            groups = _groups(df, dv.name, iv.name)
            if len(groups) < 2:
                continue
            norms = {name: assess_normality(vals) for name, vals in groups}
            all_normal = dv.kind == "continuous" and all(nr.normal for nr in norms.values())
            checks: dict = {
                "groups": {name: len(vals) for name, vals in groups},
                "normality": {name: nr.model_dump() for name, nr in norms.items()},
            }
            dv_l, iv_l = _label(vmap, dv.name), _label(vmap, iv.name)

            if len(groups) == 2:
                if all_normal:
                    lev_p = float(stats.levene(*[g[1] for g in groups]).pvalue)
                    checks["levene_p"] = lev_p
                    if lev_p > 0.05:
                        test_id, name_tr, name_en = "ttest_ind", "bağımsız örneklem t-testi", "independent-samples t-test"
                        extra_tr = "ve varyanslar homojen olduğundan (Levene p>.05)"
                        extra_en = "and variances were homogeneous (Levene p>.05)"
                    else:
                        test_id, name_tr, name_en = "welch_t", "Welch t-testi", "Welch's t-test"
                        extra_tr = "ancak varyans homojenliği sağlanmadığından (Levene p≤.05)"
                        extra_en = "but homogeneity of variance was violated (Levene p≤.05)"
                    rat_tr = (
                        f"'{dv_l}' her iki '{iv_l}' grubunda normal dağıldığından {extra_tr} {name_tr} kullanıldı."
                    )
                    rat_en = f"As '{dv_l}' was normally distributed in both '{iv_l}' groups {extra_en}, the {name_en} was used."
                else:
                    test_id = "mannwhitney"
                    why_tr = "sıralayıcı (ordinal) olduğundan" if dv.kind == "ordinal" else "en az bir grupta normal dağılmadığından"
                    why_en = "is ordinal" if dv.kind == "ordinal" else "was not normally distributed in at least one group"
                    rat_tr = f"'{dv_l}' {why_tr} parametrik olmayan Mann-Whitney U testi kullanıldı."
                    rat_en = f"Because '{dv_l}' {why_en}, the non-parametric Mann-Whitney U test was used."
            else:
                if all_normal:
                    lev_p = float(stats.levene(*[g[1] for g in groups]).pvalue)
                    checks["levene_p"] = lev_p
                    if lev_p > 0.05:
                        test_id = "anova"
                        rat_tr = f"'{dv_l}' tüm '{iv_l}' gruplarında normal dağıldığı ve varyanslar homojen olduğu için tek yönlü ANOVA kullanıldı."
                        rat_en = f"One-way ANOVA was used as '{dv_l}' was normally distributed in all '{iv_l}' groups with homogeneous variances."
                    else:
                        test_id = "kruskal"
                        rat_tr = f"Varyans homojenliği sağlanmadığından (Levene p≤.05) '{dv_l}' için Kruskal-Wallis H testi kullanıldı."
                        rat_en = f"As homogeneity of variance was violated (Levene p≤.05), the Kruskal-Wallis H test was used for '{dv_l}'."
                else:
                    test_id = "kruskal"
                    why_tr = "sıralayıcı olduğundan" if dv.kind == "ordinal" else "normallik varsayımı sağlanmadığından"
                    why_en = "is ordinal" if dv.kind == "ordinal" else "violated the normality assumption"
                    rat_tr = f"'{dv_l}' {why_tr} parametrik olmayan Kruskal-Wallis H testi kullanıldı."
                    rat_en = f"Because '{dv_l}' {why_en}, the non-parametric Kruskal-Wallis H test was used."
            plans.append(
                PlannedTest(
                    test_id=test_id, family="group", dv=dv.name, iv=iv.name,
                    rationale_tr=rat_tr, rationale_en=rat_en, checks=checks,
                )
            )

    # --- Korelasyonlar ---
    for i, a in enumerate(num_vars):
        for b in num_vars[i + 1:]:
            sub = df[[a.name, b.name]].dropna()
            if len(sub) < 5:
                continue
            a_l, b_l = _label(vmap, a.name), _label(vmap, b.name)
            checks = {"n": len(sub)}
            if a.kind == "continuous" and b.kind == "continuous":
                na, nb = assess_normality(sub[a.name]), assess_normality(sub[b.name])
                checks["normality"] = {a.name: na.model_dump(), b.name: nb.model_dump()}
                if na.normal and nb.normal:
                    test_id = "pearson"
                    rat_tr = f"'{a_l}' ve '{b_l}' normal dağıldığından Pearson korelasyonu kullanıldı."
                    rat_en = f"Pearson correlation was used as '{a_l}' and '{b_l}' were normally distributed."
                else:
                    test_id = "spearman"
                    rat_tr = f"Normallik sağlanmadığından '{a_l}' ile '{b_l}' arasında Spearman sıra korelasyonu kullanıldı."
                    rat_en = f"Spearman's rank correlation was used between '{a_l}' and '{b_l}' due to non-normality."
            else:
                test_id = "spearman"
                rat_tr = f"En az bir değişken sıralayıcı olduğundan '{a_l}' ile '{b_l}' arasında Spearman korelasyonu kullanıldı."
                rat_en = f"Spearman's correlation was used between '{a_l}' and '{b_l}' as at least one variable is ordinal."
            plans.append(
                PlannedTest(
                    test_id=test_id, family="correlation", dv=a.name, iv=b.name,
                    rationale_tr=rat_tr, rationale_en=rat_en, checks=checks,
                )
            )

    # --- Kategorik ilişkiler ---
    for i, a in enumerate(cat_vars):
        for b in cat_vars[i + 1:]:
            sub = df[[a.name, b.name]].dropna()
            if len(sub) < 10:
                continue
            table = pd.crosstab(sub[a.name], sub[b.name])
            if table.shape[0] < 2 or table.shape[1] < 2 or table.shape[0] > 10 or table.shape[1] > 10:
                continue
            expected = stats.contingency.expected_freq(table.values)
            min_exp = float(expected.min())
            a_l, b_l = _label(vmap, a.name), _label(vmap, b.name)
            checks = {"table_shape": list(table.shape), "min_expected": min_exp, "n": len(sub)}
            if table.shape == (2, 2) and min_exp < 5:
                test_id = "fisher"
                rat_tr = f"2×2 tabloda beklenen frekans 5'in altında kaldığından '{a_l}' × '{b_l}' için Fisher kesin testi kullanıldı."
                rat_en = f"Fisher's exact test was used for '{a_l}' × '{b_l}' because an expected count fell below 5 in the 2×2 table."
            else:
                test_id = "chi2"
                warn = "" if min_exp >= 5 else " (bazı beklenen frekanslar <5, sonuç ihtiyatla yorumlanmalıdır)"
                warn_en = "" if min_exp >= 5 else " (some expected counts <5; interpret with caution)"
                rat_tr = f"'{a_l}' ile '{b_l}' arasındaki ilişki ki-kare bağımsızlık testiyle incelendi{warn}."
                rat_en = f"The association between '{a_l}' and '{b_l}' was examined with the chi-square test of independence{warn_en}."
            plans.append(
                PlannedTest(
                    test_id=test_id, family="association", dv=a.name, iv=b.name,
                    rationale_tr=rat_tr, rationale_en=rat_en, checks=checks,
                )
            )

    # --- Regresyon: kullanıcı bir DV işaretlediyse ---
    dv_marked = [v for v in active if v.role == "dv" and v.kind == "continuous"]
    for dv in dv_marked:
        predictors = [v.name for v in cont_vars if v.name != dv.name][:5]
        if len(predictors) >= 2:
            dv_l = _label(vmap, dv.name)
            plans.append(
                PlannedTest(
                    test_id="linreg", family="regression", dv=dv.name, iv=None, extra_vars=predictors,
                    rationale_tr=f"'{dv_l}' bağımlı değişkenini yordayan etmenler çoklu doğrusal regresyon ile incelendi.",
                    rationale_en=f"Predictors of '{dv_l}' were examined using multiple linear regression.",
                    checks={"predictors": predictors},
                )
            )

    if len(plans) > MAX_TESTS:
        notes.append(
            f"Olası {len(plans)} testten ilk {MAX_TESTS} tanesi çalıştırıldı (çoklu test enflasyonunu sınırlamak için)."
        )
        plans = plans[:MAX_TESTS]
    if not plans:
        notes.append("Uygun değişken çifti bulunamadı; test planlanamadı.")
    return plans, notes
