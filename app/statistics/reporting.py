"""Bulgular için APA biçiminde sonuç cümleleri (TR/EN)."""
from __future__ import annotations

from app.models import Finding, VariableInfo


def fmt_p(p: float | None) -> str:
    if p is None:
        return "p = ?"
    if p < 0.001:
        return "p < .001"
    return f"p = {p:.3f}".replace("0.", ".")


def fmt_stat(x: float | None, nd: int = 2) -> str:
    return "?" if x is None else f"{x:.{nd}f}"


def fmt_df(df) -> str:
    if df is None:
        return ""
    if isinstance(df, float):
        return f"{df:.1f}" if not df.is_integer() else str(int(df))
    if isinstance(df, (list, tuple)):
        return ", ".join(fmt_df(d) for d in df)
    return str(df)


_STAT_LETTER = {
    "ttest_ind": "t", "welch_t": "t", "mannwhitney": "U", "anova": "F",
    "kruskal": "H", "chi2": "χ²", "fisher": "OR", "pearson": "r", "spearman": "ρ",
    "linreg": "F",
}


def apa_result(finding: Finding, vmap: dict[str, VariableInfo], lang: str) -> str:
    p = finding.planned
    dv = _disp(vmap, p.dv)
    iv = _disp(vmap, p.iv) if p.iv else ""
    letter = _STAT_LETTER.get(p.test_id, "stat")
    df_part = f"({fmt_df(finding.df)})" if finding.df is not None else ""
    stat_part = f"{letter}{df_part} = {fmt_stat(finding.statistic)}, {fmt_p(finding.p_value)}"
    if finding.p_adjusted is not None and finding.p_adjusted != finding.p_value:
        adj = fmt_p(finding.p_adjusted).replace("p", "p-düz" if lang == "tr" else "p-adj")
        stat_part += f", {adj}"
    if finding.effect_size is not None and finding.effect_size_name:
        stat_part += f", {finding.effect_size_name} = {fmt_stat(finding.effect_size)}"

    sig = finding.significant
    if lang == "tr":
        if p.family == "group":
            verb = "anlamlı bir fark göstermiştir" if sig else "anlamlı bir fark göstermemiştir"
            return f"'{dv}', '{iv}' gruplarına göre {verb} ({stat_part})."
        if p.family == "correlation":
            verb = "anlamlı bir ilişki" if sig else "anlamlı olmayan bir ilişki"
            direction = ""
            if sig and finding.statistic is not None:
                direction = "pozitif yönde " if finding.statistic > 0 else "negatif yönde "
            return f"'{dv}' ile '{iv}' arasında {direction}{verb} bulunmuştur ({stat_part})."
        if p.family == "association":
            verb = "anlamlı bir ilişki bulunmuştur" if sig else "anlamlı bir ilişki bulunmamıştır"
            return f"'{dv}' ile '{iv}' arasında {verb} ({stat_part})."
        verb = "anlamlıdır" if sig else "anlamlı değildir"
        r2 = finding.group_stats[0].get("r_squared") if finding.group_stats else None
        r2_part = f", R² = {fmt_stat(r2)}" if r2 is not None else ""
        return f"'{dv}' için kurulan regresyon modeli {verb} ({stat_part}{r2_part})."
    # EN
    if p.family == "group":
        verb = "differed significantly" if sig else "did not differ significantly"
        return f"'{dv}' {verb} across '{iv}' groups ({stat_part})."
    if p.family == "correlation":
        if sig and finding.statistic is not None:
            direction = "positive" if finding.statistic > 0 else "negative"
            return f"A significant {direction} correlation was found between '{dv}' and '{iv}' ({stat_part})."
        return f"No significant correlation was found between '{dv}' and '{iv}' ({stat_part})."
    if p.family == "association":
        verb = "A significant association" if sig else "No significant association"
        return f"{verb} was found between '{dv}' and '{iv}' ({stat_part})."
    verb = "was significant" if sig else "was not significant"
    r2 = finding.group_stats[0].get("r_squared") if finding.group_stats else None
    r2_part = f", R² = {fmt_stat(r2)}" if r2 is not None else ""
    return f"The regression model for '{dv}' {verb} ({stat_part}{r2_part})."


def _disp(vmap: dict[str, VariableInfo], name: str | None) -> str:
    if not name:
        return ""
    v = vmap.get(name)
    return (v.label or v.name) if v else name
