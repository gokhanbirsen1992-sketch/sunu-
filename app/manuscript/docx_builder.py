"""python-docx ile APA'ya yakın Word çıktısı."""
from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.shared import Cm, Pt

from app.literature.apa import format_reference_runs
from app.models import CleaningReport, Finding, Manuscript
from app.statistics.reporting import fmt_df, fmt_p, fmt_stat

LABELS = {
    "tr": {
        "intro": "Giriş", "methods": "Yöntem", "results": "Bulgular",
        "discussion": "Tartışma", "limitations": "Sınırlılıklar", "references": "Kaynakça",
        "appendix": "Ek: Veri Temizleme Raporu", "table_results": "Tablo 1. Analiz Sonuçları Özeti",
        "author": "Yazar Adı", "cols": ["Analiz", "Değişkenler", "İstatistik", "p", "Etki Büyüklüğü"],
    },
    "en": {
        "intro": "Introduction", "methods": "Method", "results": "Results",
        "discussion": "Discussion", "limitations": "Limitations", "references": "References",
        "appendix": "Appendix: Data Cleaning Report", "table_results": "Table 1. Summary of Analyses",
        "author": "Author Name", "cols": ["Analysis", "Variables", "Statistic", "p", "Effect Size"],
    },
}

TEST_NAMES = {
    "ttest_ind": {"tr": "Bağımsız t-testi", "en": "Independent t-test"},
    "welch_t": {"tr": "Welch t-testi", "en": "Welch's t-test"},
    "mannwhitney": {"tr": "Mann-Whitney U", "en": "Mann-Whitney U"},
    "anova": {"tr": "Tek yönlü ANOVA", "en": "One-way ANOVA"},
    "kruskal": {"tr": "Kruskal-Wallis H", "en": "Kruskal-Wallis H"},
    "chi2": {"tr": "Ki-kare", "en": "Chi-square"},
    "fisher": {"tr": "Fisher kesin testi", "en": "Fisher's exact test"},
    "pearson": {"tr": "Pearson korelasyonu", "en": "Pearson correlation"},
    "spearman": {"tr": "Spearman korelasyonu", "en": "Spearman correlation"},
    "linreg": {"tr": "Çoklu regresyon", "en": "Multiple regression"},
}


def _setup_styles(doc: Document) -> None:
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(12)
    pf = style.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.DOUBLE
    pf.space_after = Pt(0)
    for section in doc.sections:
        section.top_margin = section.bottom_margin = Cm(2.5)
        section.left_margin = section.right_margin = Cm(2.5)


def _heading(doc: Document, text: str, level: int = 1) -> None:
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.bold = True
    run.font.name = "Times New Roman"
    run.font.size = Pt(12)
    if level == 1:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER


def _body(doc: Document, text: str) -> None:
    for para in text.split("\n\n"):
        para = para.strip()
        if not para:
            continue
        p = doc.add_paragraph(para)
        p.paragraph_format.first_line_indent = Cm(1.25)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY


def build_docx(
    manuscript: Manuscript,
    findings: list[Finding],
    cleaning_report: CleaningReport | None,
    out_path: str | Path,
) -> Path:
    lang = manuscript.language
    L = LABELS[lang]
    doc = Document()
    _setup_styles(doc)

    # Başlık sayfası
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title_p.add_run(manuscript.title or ("Başlıksız Çalışma" if lang == "tr" else "Untitled Study"))
    run.bold = True
    for line in (L["author"], ""):
        p = doc.add_paragraph(line)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_page_break()

    for key in ("intro", "methods", "results"):
        if manuscript.sections.get(key):
            _heading(doc, L[key])
            _body(doc, manuscript.sections[key])

    # Sonuç tablosu
    valid = [f for f in findings if f.error is None]
    if valid:
        doc.add_paragraph()
        cap = doc.add_paragraph()
        cap.add_run(L["table_results"]).bold = True
        table = doc.add_table(rows=1, cols=5)
        table.style = "Table Grid"
        for i, col in enumerate(L["cols"]):
            cell_run = table.rows[0].cells[i].paragraphs[0].add_run(col)
            cell_run.bold = True
        for f in valid:
            row = table.add_row().cells
            row[0].text = TEST_NAMES.get(f.planned.test_id, {}).get(lang, f.planned.test_id)
            vars_text = " × ".join(x for x in [f.planned.dv, f.planned.iv] if x) or ", ".join(f.planned.extra_vars)
            row[1].text = vars_text
            df_part = f"({fmt_df(f.df)})" if f.df is not None else ""
            row[2].text = f"{f.statistic_name}{df_part} = {fmt_stat(f.statistic)}"
            p_final = f.p_adjusted if f.p_adjusted is not None else f.p_value
            row[3].text = fmt_p(p_final) + (" *" if f.significant else "")
            row[4].text = (
                f"{f.effect_size_name} = {fmt_stat(f.effect_size)}" if f.effect_size is not None else "—"
            )

    for key in ("discussion", "limitations"):
        if manuscript.sections.get(key):
            _heading(doc, L[key])
            _body(doc, manuscript.sections[key])

    # Kaynakça — asılı girinti, italik dergi adı
    if manuscript.references:
        doc.add_page_break()
        _heading(doc, L["references"])
        for ref in manuscript.references:
            p = doc.add_paragraph()
            pf = p.paragraph_format
            pf.left_indent = Cm(1.25)
            pf.first_line_indent = Cm(-1.25)
            for text, italic in format_reference_runs(ref):
                r = p.add_run(text)
                r.italic = italic

    # Ek: temizlik raporu
    if cleaning_report:
        doc.add_page_break()
        _heading(doc, L["appendix"])
        for action in cleaning_report.actions:
            doc.add_paragraph("• " + action)

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out_path))
    return out_path
