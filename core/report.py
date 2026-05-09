from __future__ import annotations

import os
from datetime import datetime
from typing import Any

import pandas as pd

from .literature import Paper


def _fmt_p(p) -> str:
    if p is None or pd.isna(p):
        return "—"
    if p < 0.001:
        return "<0.001"
    return f"{p:.3f}"


def _bivariate_table(biv: pd.DataFrame, top_n: int = 30) -> str:
    if biv.empty:
        return "_(sonuç yok)_\n"
    show = biv.head(top_n).copy()
    lines = ["| Değişken | Tip | Test | n | İstatistik | Etki | p | p (FDR) | Anlamlı |",
             "|---|---|---|---|---|---|---|---|---|"]
    for _, r in show.iterrows():
        eff = "—" if pd.isna(r.get("effect")) else f"{r['effect']:.3f}"
        stat = "—" if pd.isna(r.get("stat")) else f"{r['stat']:.3f}"
        sig = "✅" if r.get("significant") else ""
        lines.append(
            f"| {r['feature']} | {r['feature_type']} | {r['test']} | {int(r['n'])} | "
            f"{stat} | {eff} | {_fmt_p(r['p'])} | {_fmt_p(r['p_fdr'])} | {sig} |"
        )
    return "\n".join(lines) + "\n"


def _multivariate_table(mv: dict) -> str:
    if "error" in mv:
        return f"⚠️ {mv['error']}\n"
    coef: pd.DataFrame = mv["coefficients"]
    if mv["type"] == "logistic":
        head = "| Değişken | OR | %95 GA | p |\n|---|---|---|---|\n"
        rows = "\n".join(
            f"| {r['variable']} | {r['OR']:.3f} | "
            f"({r['OR_ci_low']:.3f}–{r['OR_ci_high']:.3f}) | {_fmt_p(r['p'])} |"
            for _, r in coef.iterrows() if r["variable"] != "const"
        )
        meta = (f"**n={mv['n']}**, pseudo-R²={mv['pseudo_r2']:.3f}, "
                f"LLR p={_fmt_p(mv['llr_p'])} · "
                f"Olay: `{mv['outcome_levels']['event']}` (referans: `{mv['outcome_levels']['reference']}`)")
    elif mv["type"] == "cox":
        head = "| Değişken | HR | %95 GA | p |\n|---|---|---|---|\n"
        rows = "\n".join(
            f"| {r['variable']} | {r['HR']:.3f} | "
            f"({r['HR_ci_low']:.3f}–{r['HR_ci_high']:.3f}) | {_fmt_p(r['p'])} |"
            for _, r in coef.iterrows()
        )
        meta = (f"**n={mv['n']}**, olay={mv['events']}, "
                f"C-index={mv['concordance']:.3f}, "
                f"LR test p={_fmt_p(mv['log_likelihood_ratio_p'])}")
    else:
        head = "| Değişken | β | %95 GA | p |\n|---|---|---|---|\n"
        rows = "\n".join(
            f"| {r['variable']} | {r['beta']:.3f} | "
            f"({r['ci_low']:.3f}–{r['ci_high']:.3f}) | {_fmt_p(r['p'])} |"
            for _, r in coef.iterrows() if r["variable"] != "const"
        )
        meta = (f"**n={mv['n']}**, R²={mv['r2']:.3f}, "
                f"adj. R²={mv['r2_adj']:.3f}, F p={_fmt_p(mv['f_p'])}")
    return f"{meta}\n\n{head}{rows}\n"


def _literature_section(lit: dict[str, list[Paper]]) -> str:
    out_lines: list[str] = []
    for feature, papers in lit.items():
        if feature == "_errors":
            continue
        out_lines.append(f"### 🔍 `{feature}`")
        if not papers:
            out_lines.append("_Sonuç bulunamadı._\n")
            continue
        for p in papers:
            authors = ", ".join(p.authors[:3])
            if len(p.authors) > 3:
                authors += " et al."
            out_lines.append(f"- **{p.title}**  \n  {authors} · *{p.journal}* ({p.year})  \n"
                             f"  PMID: [{p.pmid}](https://pubmed.ncbi.nlm.nih.gov/{p.pmid}/)"
                             f"{' · DOI: [' + p.doi + '](' + p.url + ')' if p.doi else ''}")
            if p.abstract:
                out_lines.append(f"  > {p.abstract[:400]}{'...' if len(p.abstract) > 400 else ''}")
        out_lines.append("")
    if "_errors" in lit:
        out_lines.append("\n_Bazı sorgular başarısız:_ " + "; ".join(lit["_errors"]))
    return "\n".join(out_lines)


def build_markdown(
    meta: dict[str, Any],
    bivariate: pd.DataFrame,
    multivariate: dict | None,
    literature: dict[str, list[Paper]] | None,
    article_ideas: str | None = None,
) -> str:
    sig = bivariate[bivariate["significant"]] if not bivariate.empty else bivariate
    parts = [
        f"# İstatistiksel Analiz Raporu",
        f"_Oluşturulma: {datetime.now().strftime('%Y-%m-%d %H:%M')}_\n",
        "## 1. Çalışma Özeti",
        f"- **Outcome:** `{meta.get('outcome')}` ({meta.get('outcome_type')})",
        f"- **Çalışma tipi:** {meta.get('study_type', 'belirsiz')}",
        f"- **Örneklem:** n={meta.get('n_rows')} satır, {meta.get('n_cols')} sütun",
        f"- **Eksik veri stratejisi:** {meta.get('missing_strategy', 'yok')}\n",
        "## 2. Bivariate Analiz (FDR-Benjamini-Hochberg düzeltmeli)",
        f"Toplam **{len(bivariate)} test**, FDR<0.05 anlamlı: **{int(sig.shape[0])}**\n",
        _bivariate_table(bivariate),
        "## 3. Multivariate Model",
    ]
    if multivariate:
        parts.append(_multivariate_table(multivariate))
    else:
        parts.append("_(çalıştırılmadı)_\n")

    parts.append("## 4. Literatür Eşleşmesi (PubMed)")
    if literature:
        parts.append(_literature_section(literature))
    else:
        parts.append("_(literatür araması yapılmadı)_\n")

    parts.append("## 5. Makale Fikri / Kurgu Önerisi")
    if article_ideas:
        parts.append(article_ideas)
    else:
        parts.append(_default_article_ideas(meta, bivariate, multivariate))

    parts.append("\n## 6. Limitasyonlar")
    parts.append(_default_limitations(meta))

    return "\n".join(parts)


def _default_article_ideas(meta, biv, mv) -> str:
    if biv.empty or "significant" not in biv.columns:
        return "_Anlamlı bulgu olmadığı için fikir üretilemedi._"
    sig = biv[biv["significant"]].head(5)
    if sig.empty:
        return ("FDR-düzeltmeli p<0.05 bulgu yok. Örneklem büyütme, alt-grup analizi veya "
                "ön-kayıtlı hipotez ile yeniden değerlendirme önerilir.")
    feats = ", ".join(f"`{f}`" for f in sig["feature"].tolist())
    return (f"### Önerilen kurgu\n\n"
            f"**Başlık taslağı:** _\"{meta.get('outcome', 'outcome')} ile ilişkili faktörler: "
            f"{sig.iloc[0]['feature']} odaklı çok değişkenli analiz\"_\n\n"
            f"**Hipotez:** {feats} değişkenleri `{meta.get('outcome')}` ile bağımsız olarak "
            f"ilişkilidir.\n\n"
            f"**Novelty argümanı:** Literatür taraması bölümünde döndürülen makalelerle "
            f"çelişen/destekleyen bulguları karşılaştırın; gap varsa öne çıkarın.\n\n"
            f"**Hedef dergi tipi:** Bulguların klinik etki büyüklüğüne göre orta-üst impact "
            f"(IF 2–6) genel/spesifik dergiler.")


def _default_limitations(meta) -> str:
    items = [
        "- Gözlemsel/retrospektif tasarımda nedensellik çıkarılamaz.",
        "- FDR düzeltmesine rağmen çoklu test ile keşfedilen ilişkilerin doğrulanması için "
        "bağımsız kohort gereklidir.",
        f"- Eksik veri stratejisi ({meta.get('missing_strategy', 'yok')}) sonuçları etkilemiş "
        "olabilir; duyarlılık analizi önerilir.",
        "- Confounder kontrolü için propensity score eşleştirme veya IPTW düşünülmeli.",
    ]
    return "\n".join(items)


def llm_article_ideas(
    meta: dict, biv: pd.DataFrame, mv: dict | None, literature: dict | None,
    api_key: str | None = None, model: str = "claude-sonnet-4-6",
) -> str | None:
    api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
    except Exception:
        return None

    sig = biv[biv["significant"]].head(8) if not biv.empty else biv
    sig_txt = sig[["feature", "test", "p_fdr", "effect"]].to_string(index=False) if not sig.empty else "yok"
    mv_txt = ""
    if mv and "coefficients" in mv:
        mv_txt = mv["coefficients"].to_string(index=False)

    lit_txt = ""
    if literature:
        for k, papers in literature.items():
            if k == "_errors":
                continue
            lit_txt += f"\n## {k}\n"
            for p in papers[:3]:
                lit_txt += f"- {p.title} ({p.year}, {p.journal})\n"

    prompt = f"""Sen bir klinik araştırma metodolog uzmanısın. Aşağıdaki istatistik analiz çıktılarına bakıp Türkçe olarak şunları ver:
1) Hangi makale fikri en güçlü? Başlık önerisi
2) Hipotez (1 cümle)
3) Novelty argümanı (literatürle çelişen/destekleyen)
4) Hedef dergi tipi
5) Bir sonraki adımda yapılması gereken 2-3 ek analiz

## Çalışma
Outcome: {meta.get('outcome')} ({meta.get('outcome_type')})
Çalışma tipi: {meta.get('study_type')}
n={meta.get('n_rows')}

## FDR-anlamlı bivariate
{sig_txt}

## Multivariate
{mv_txt or 'çalıştırılmadı'}

## Literatür özeti
{lit_txt or 'aranmadı'}
"""
    try:
        resp = client.messages.create(
            model=model, max_tokens=1500,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.content[0].text
    except Exception as e:
        return f"_LLM çağrısı başarısız: {e}_"
