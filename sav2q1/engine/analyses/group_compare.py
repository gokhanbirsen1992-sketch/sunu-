"""Grup karşılaştırma ailesi (sürekli sonuç × kategorik grup).

M0 kapsamı: 2 bağımsız grup (t / Welch / Mann-Whitney) tam; ikiden çok grup için
tek yönlü ANOVA / Kruskal-Wallis temel destek. Test seçimi `decision_tree`'den
gelir; varsayım sonuçları ve gerekçe ledger'a yazılır.
"""

from __future__ import annotations

import numpy as np
from scipy import stats

from .. import assumptions, decision_tree, effects, posthoc
from ..fmt import fmt_num, fmt_p, fmt_ci


def _p_segment(p: float) -> str:
    s = fmt_p(p)
    return f"p {s}" if s.startswith("<") else f"p = {s}"


def _group_label(value_labels: dict | None, code) -> str:
    if value_labels:
        for k, v in value_labels.items():
            try:
                if float(k) == float(code):
                    return str(v)
            except (TypeError, ValueError):
                if k == code:
                    return str(v)
    return str(code)


def _group_desc(arr: np.ndarray) -> dict:
    return {
        "n": int(arr.size),
        "mean": float(np.mean(arr)), "sd": float(np.std(arr, ddof=1)),
        "median": float(np.median(arr)),
        "q1": float(np.percentile(arr, 25)), "q3": float(np.percentile(arr, 75)),
    }


def compare_two_groups(df, outcome: str, group: str, *, value_labels=None,
                       paired: bool = False, result_id: str = "R1",
                       question_ref: str | None = None) -> dict:
    sub = df[[outcome, group]].dropna()
    codes = sorted(sub[group].unique())
    if len(codes) != 2:
        raise ValueError(f"compare_two_groups: {group} 2 grup değil ({len(codes)})")
    a = sub.loc[sub[group] == codes[0], outcome].to_numpy(float)
    b = sub.loc[sub[group] == codes[1], outcome].to_numpy(float)
    la, lb = _group_label(value_labels, codes[0]), _group_label(value_labels, codes[1])

    norm = assumptions.normality_by_group(sub[outcome].to_numpy(float), sub[group].to_numpy())
    lev = assumptions.levene(a, b)
    test_id, reason = decision_tree.choose_two_group_test(
        all_normal=norm["all_normal"], equal_variance=lev["equal_variance"], paired=paired)

    display: list[str] = []
    ga = _group_desc(a); gb = _group_desc(b)

    if test_id in ("student_t", "welch_t"):
        equal_var = (test_id == "student_t")
        t, p = stats.ttest_ind(a, b, equal_var=equal_var)
        if equal_var:
            dfree = len(a) + len(b) - 2
        else:  # Welch-Satterthwaite
            va, vb, na, nb = np.var(a, ddof=1), np.var(b, ddof=1), len(a), len(b)
            dfree = (va/na + vb/nb) ** 2 / ((va/na)**2/(na-1) + (vb/nb)**2/(nb-1))
        g = effects.hedges_g(a, b)
        lo, hi = effects.smd_ci(g, len(a), len(b))
        stat_name, stat_val = "t", float(t)
        eff = {"name": "Hedges g", "value": g, "ci": [lo, hi]}
        df_s = fmt_num(dfree, 0 if equal_var else 1)
        apa = f"t({df_s}) = {fmt_num(stat_val)}, {_p_segment(p)}, g = {fmt_num(g)} (%95 GA: {fmt_ci(lo, hi)})"
        display = [apa,
                   f"{fmt_num(ga['mean'])} ± {fmt_num(ga['sd'])}",
                   f"{fmt_num(gb['mean'])} ± {fmt_num(gb['sd'])}"]
        rep = "mean_sd"
    else:  # mann_whitney_u
        U, p = stats.mannwhitneyu(a, b, alternative="two-sided")
        rb = effects.rank_biserial_mwu(U, len(a), len(b))
        lo, hi = effects.rank_biserial_ci(a, b)
        stat_name, stat_val = "U", float(U)
        eff = {"name": "rank-biserial r", "value": rb, "ci": [lo, hi]}
        apa = f"U = {fmt_num(stat_val, 1)}, {_p_segment(p)}, r = {fmt_num(rb)} (%95 GA: {fmt_ci(lo, hi)})"
        display = [apa,
                   f"{fmt_num(ga['median'])} ({fmt_num(ga['q1'])}–{fmt_num(ga['q3'])})",
                   f"{fmt_num(gb['median'])} ({fmt_num(gb['q1'])}–{fmt_num(gb['q3'])})"]
        rep = "median_iqr"

    return {
        "id": result_id,
        "question_ref": question_ref,
        "family": "group_compare",
        "test": test_id,
        "reason": reason,
        "variables": {"outcome": outcome, "group": group},
        "groups": [
            {"code": (int(codes[0]) if float(codes[0]).is_integer() else codes[0]), "label": la, **ga},
            {"code": (int(codes[1]) if float(codes[1]).is_integer() else codes[1]), "label": lb, **gb},
        ],
        "report_style": rep,
        "statistic": {"name": stat_name, "value": stat_val},
        "p_value": float(p),
        "effect": eff,
        "assumptions": {"normality": norm, "levene": lev},
        "n_analyzed": int(sub.shape[0]),
        "apa": apa,
        "_display": display,
        "_global": [str(ga["n"]), str(gb["n"]), str(int(sub.shape[0])), la, lb],
    }


def _ph_p(p: float) -> str:
    s = fmt_p(p)
    return s if s.startswith("<") else s


def compare_multi_groups(df, outcome: str, group: str, *, value_labels=None,
                         result_id: str = "R", question_ref: str | None = None,
                         confirmatory: bool = False) -> dict:
    """İkiden çok bağımsız grup karşılaştırması: ANOVA/Welch/Kruskal-Wallis + post-hoc + η²."""
    sub = df[[outcome, group]].dropna()
    codes = sorted(sub[group].unique())
    arrays = [sub.loc[sub[group] == g, outcome].to_numpy(float) for g in codes]
    labels = [_group_label(value_labels, g) for g in codes]
    k = len(codes)
    n_total = int(sub.shape[0])

    norm = assumptions.normality_by_group(sub[outcome].to_numpy(float), sub[group].to_numpy())
    lev = assumptions.levene(*arrays)
    test_id, reason = decision_tree.choose_multi_group_test(
        all_normal=norm["all_normal"], equal_variance=lev["equal_variance"], repeated=False)

    groups_desc = []
    display: list[str] = []
    glob: list[str] = [str(n_total)]
    for code, lab, a in zip(codes, labels, arrays):
        gd = _group_desc(a)
        groups_desc.append({"code": (int(code) if float(code).is_integer() else code), "label": lab, **gd})
        display.append(f"{fmt_num(gd['mean'])} ± {fmt_num(gd['sd'])}")
        display.append(f"{fmt_num(gd['median'])} ({fmt_num(gd['q1'])}–{fmt_num(gd['q3'])})")
        glob.append(str(gd["n"]))

    ph_list: list[dict] = []
    out_vals = sub[outcome].to_numpy(float)
    grp_vals = sub[group].to_numpy()

    if test_id in ("oneway_anova", "welch_anova"):
        if test_id == "oneway_anova":
            F, p = stats.f_oneway(*arrays)
            dfb, dfw = float(k - 1), float(n_total - k)
            ph_pairs = posthoc.tukey_hsd(out_vals, grp_vals, codes)
        else:
            F, p, dfb, dfw = posthoc.welch_anova(arrays)
            ph_pairs = posthoc.games_howell(arrays, codes)
        eta2 = effects.eta_squared_oneway(arrays)
        lo, hi = effects.eta_squared_ci_boot(arrays, kind="anova")
        dfb_s = fmt_num(dfb, 0 if test_id == "oneway_anova" else 1)
        dfw_s = fmt_num(dfw, 0 if test_id == "oneway_anova" else 1)
        apa = f"F({dfb_s}, {dfw_s}) = {fmt_num(F)}, {_p_segment(p)}, η² = {fmt_num(eta2)} (%95 GA: {fmt_ci(lo, hi)})"
        stat = {"name": "F", "value": float(F), "df1": dfb, "df2": dfw}
        eff = {"name": "η²", "value": float(eta2), "ci": [lo, hi]}
        rep = "mean_sd"
    else:  # kruskal_wallis
        H, p = stats.kruskal(*arrays)
        eta2 = effects.eta_squared_h(float(H), n_total, k)
        lo, hi = effects.eta_squared_ci_boot(arrays, kind="kw")
        apa = f"H({k - 1}) = {fmt_num(float(H))}, {_p_segment(p)}, η² = {fmt_num(eta2)} (%95 GA: {fmt_ci(lo, hi)})"
        stat = {"name": "H", "value": float(H), "df": k - 1}
        eff = {"name": "η²(H)", "value": float(eta2), "ci": [lo, hi]}
        rep = "median_iqr"
        ph_pairs = posthoc.dunn(out_vals, grp_vals, codes)

    for ca, cb, pv in ph_pairs:
        ph_list.append({"a": _group_label(value_labels, ca), "b": _group_label(value_labels, cb),
                        "p": float(pv), "p_str": _ph_p(float(pv))})

    display.append(apa)
    for ph_item in ph_list:
        display.append(ph_item["p_str"])

    return {
        "id": result_id,
        "question_ref": question_ref,
        "family": "multi_group_compare",
        "test": test_id,
        "reason": reason,
        "confirmatory": confirmatory,
        "variables": {"outcome": outcome, "group": group},
        "groups": groups_desc,
        "report_style": rep,
        "statistic": stat,
        "p_value": float(p),
        "effect": eff,
        "posthoc": ph_list,
        "assumptions": {"normality": norm, "levene": lev},
        "n_analyzed": n_total,
        "apa": apa,
        "_display": display,
        "_global": glob + [str(lbl) for lbl in labels],   # grup etiketleri (rakam içerebilir)
    }
