"""Word (.docx) derleyici — onaylı bölümler + ledger tabloları + doğrulanmış
kaynakça + ICMJE → tek dosya. Saf python-docx, deterministik, LLM YOK.

Kullanım:
  python -m sav2q1.docx.assemble --rundir runs/<id> [--out runs/<id>/output/article_tr.docx]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt

from .references_docx import format_vancouver, format_apa7
from .styles import apply_base_styles


def _load(p: Path) -> dict:
    return json.loads(Path(p).read_text(encoding="utf-8"))


def _block_text(block: dict) -> str:
    return " ".join(s.get("text", "") for s in block.get("sentences", []))


def _collect_cited_refs(sections: list[dict]) -> list[str]:
    """Bölümlerde ilk görülme sırasına göre atıf anahtarlarını topla (tekilleştir)."""
    order: list[str] = []
    for sec in sections:
        for block in sec.get("blocks", []):
            for sent in block.get("sentences", []):
                b = sent.get("binding") or {}
                if b.get("kind") == "citation":
                    ref = b.get("ref") or b.get("result_id")
                    if ref and ref not in order:
                        order.append(ref)
    return order


def _add_title_page(doc: Document, m: dict) -> None:
    t = doc.add_paragraph()
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = t.add_run(m.get("title", ""))
    run.bold = True
    run.font.size = Pt(16)

    for a in m.get("authors", []):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run(a.get("name", "")).bold = True
        if a.get("affiliation"):
            p.add_run(f"\n{a['affiliation']}").font.size = Pt(10)

    if m.get("corresponding"):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run(f"Sorumlu yazar: {m['corresponding']}").font.size = Pt(10)


def _add_abstract(doc: Document, m: dict) -> None:
    doc.add_heading("Öz", level=1)
    for label, text in (m.get("abstract") or {}).items():
        p = doc.add_paragraph()
        p.add_run(f"{label}: ").bold = True
        p.add_run(text)
    if m.get("keywords"):
        p = doc.add_paragraph()
        p.add_run("Anahtar Kelimeler: ").bold = True
        p.add_run(", ".join(m["keywords"]))


def _add_table1(doc: Document, ledger: dict, spec: dict) -> None:
    descs = {d["var"]: d for d in ledger.get("descriptives", [])}
    cap = doc.add_paragraph()
    cap.add_run(spec.get("title", "Tablo 1")).bold = True

    table = doc.add_table(rows=1, cols=2)
    table.style = "Table Grid"
    hdr = table.rows[0].cells
    hdr[0].paragraphs[0].add_run("Değişken").bold = True
    hdr[1].paragraphs[0].add_run("Değer").bold = True

    for var in spec.get("include", []):
        d = descs.get(var)
        if not d:
            continue
        if d["type"] == "continuous":
            cells = table.add_row().cells
            cells[0].text = f"{d['label']} (Ort. ± SS)"
            cells[1].text = d["apa_mean_sd"]
        else:
            for i, c in enumerate(d["categories"]):
                cells = table.add_row().cells
                cells[0].text = f"{d['label']} – {c['label']}" if i == 0 else f"  {c['label']}"
                cells[1].text = c["apa"]


def _render_table_json(doc: Document, tjson: dict) -> None:
    """Ledger tablo JSON'unu (group_table1 / correlation_table) Word tablosu yapar."""
    cap = doc.add_paragraph()
    cap.add_run(tjson.get("title", "Tablo")).bold = True
    cols = tjson["columns"]
    table = doc.add_table(rows=1, cols=len(cols))
    table.style = "Table Grid"
    for j, c in enumerate(cols):
        table.rows[0].cells[j].paragraphs[0].add_run(str(c)).bold = True
    for row in tjson.get("rows", []):
        cells = table.add_row().cells
        cells[0].text = str(row["label"])
        vals = list(row.get("values", []))
        if "p" in row:
            vals = vals + [row["p"]]
        for j, v in enumerate(vals, start=1):
            if j < len(cols):
                cells[j].text = str(v)
    if tjson.get("footnote"):
        fp = doc.add_paragraph()
        fr = fp.add_run(tjson["footnote"]); fr.italic = True; fr.font.size = Pt(9)


def _render_ledger_tables(doc: Document, ledger: dict, rundir: Path) -> bool:
    tabs = ledger.get("tables", [])
    if not tabs:
        return False
    for t in tabs:
        fpath = rundir / t["file"]
        if fpath.exists():
            _render_table_json(doc, json.loads(fpath.read_text(encoding="utf-8")))
    return True


def _add_figures(doc: Document, ledger: dict, rundir: Path) -> None:
    for f in ledger.get("figures", []):
        fpath = rundir / f["file"]
        if not fpath.exists():
            continue
        doc.add_picture(str(fpath), width=Inches(6))
        cap = doc.add_paragraph()
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = cap.add_run(f.get("title", f["id"])); r.italic = True; r.font.size = Pt(10)


def _add_references(doc: Document, refs: list[str], evidence: dict, style: str) -> None:
    by_key = {e["key"]: e for e in evidence.get("entries", [])}
    doc.add_heading("Kaynaklar", level=1)
    fmt = format_apa7 if style == "apa7" else format_vancouver
    for i, key in enumerate(refs, start=1):
        e = by_key.get(key)
        if not e:
            continue
        doc.add_paragraph(fmt(e, i))


def _add_icmje(doc: Document, icmje: dict) -> None:
    if not icmje:
        return
    labels = {
        "ethics": "Etik Kurul Onayı", "informed_consent": "Bilgilendirilmiş Onam",
        "registration": "Çalışma Kaydı", "funding": "Finansman",
        "coi": "Çıkar Çatışması", "data_availability": "Veri Erişilebilirliği",
        "authors_contributions": "Yazar Katkıları",
    }
    doc.add_heading("Beyanlar", level=1)
    for key, label in labels.items():
        if icmje.get(key):
            p = doc.add_paragraph()
            p.add_run(f"{label}: ").bold = True
            val = icmje[key]
            p.add_run("Evet" if val is True else str(val))


def build_docx(rundir: str, out: str | None = None) -> str:
    rundir = Path(rundir)
    m = _load(rundir / "manuscript.json")
    ledger = _load(rundir / "results_ledger.json")
    evidence_path = rundir / "evidence_store.json"
    evidence = _load(evidence_path) if evidence_path.exists() else {"entries": []}

    sections = []
    for sec_spec in m.get("sections", []):
        sec = _load(rundir / sec_spec["file"])
        sec["_heading"] = sec_spec["heading"]
        sections.append(sec)
    cited = _collect_cited_refs(sections)

    doc = Document()
    apply_base_styles(doc)
    _add_title_page(doc, m)
    _add_abstract(doc, m)

    for sec in sections:
        doc.add_heading(sec["_heading"], level=1)
        for block in sec.get("blocks", []):
            doc.add_paragraph(_block_text(block))
        if sec["_heading"].lower().startswith("bulgu"):
            # Önce ledger tablolarını (gruplara göre Tablo 1 + korelasyon) dene; yoksa M0 tek-sütun Tablo 1.
            if not _render_ledger_tables(doc, ledger, rundir):
                if m.get("table1"):
                    _add_table1(doc, ledger, m["table1"])
            _add_figures(doc, ledger, rundir)

    _add_references(doc, cited, evidence, m.get("citation_style", "vancouver"))
    _add_icmje(doc, m.get("icmje", {}))

    out_path = Path(out) if out else (rundir / "output" / "article_tr.docx")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out_path))
    return str(out_path)


def main(argv=None) -> None:
    p = argparse.ArgumentParser(prog="sav2q1.docx.assemble")
    p.add_argument("--rundir", required=True)
    p.add_argument("--out", required=False)
    args = p.parse_args(argv)
    out = build_docx(args.rundir, args.out)
    print(f"[assemble] yazıldı: {out}")


if __name__ == "__main__":
    main()
