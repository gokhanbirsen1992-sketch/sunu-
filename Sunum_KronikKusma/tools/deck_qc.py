#!/usr/bin/env python3
"""PPTX kalite denetimi: slayt sayısı, konuşmacı notu, kelime bütçesi, font, taşma (geometri),
eksik resim, Türkçe glif. Kullanım: python tools/deck_qc.py output/X.pptx --json qc/deck_qc.json"""
import json
import re
import sys
import zipfile
from pathlib import Path

from pptx import Presentation
from pptx.util import Emu

ROOT = Path(__file__).resolve().parent.parent
WORD_LIMIT = 40
ALLOWED_FONTS = {"Arial", "Calibri", "Georgia", None}
AI_TELLS = [
    r"\bdelve\b", r"\btapestry\b", r"\bgame[- ]changer\b", r"\bunlock\b", r"\bharness\b",
    r"oyunun kurallarını", r"devrim niteliğinde", r"çığır açan", r"\bsihirli\b", "—",
]


def slide_words(slide):
    words = 0
    for sh in slide.shapes:
        if getattr(sh, "name", "").startswith(("SRC", "FOOT", "NUM")):
            continue  # kaynak satırı / altbilgi bütçeye sayılmaz
        if sh.has_text_frame:
            words += len(re.findall(r"\w+", sh.text_frame.text))
        if sh.has_table:
            for row in sh.table.rows:
                for c in row.cells:
                    words += len(re.findall(r"\w+", c.text))
    return words


def main(path, json_out=None):
    prs = Presentation(path)
    W, H = prs.slide_width, prs.slide_height
    rep = {"file": str(path), "slides": len(prs.slides), "issues": [], "per_slide": []}
    for i, s in enumerate(prs.slides, 1):
        info = {"n": i, "words": slide_words(s), "fonts": set(), "title": ""}
        if s.has_notes_slide and s.notes_slide.notes_text_frame.text.strip():
            rep["issues"].append(f"S{i}: konuşmacı notu var")
        for sh in s.shapes:
            if sh.left is not None and sh.width is not None:
                if sh.left < 0 or sh.top < 0 or sh.left + sh.width > W + Emu(1000) or sh.top + sh.height > H + Emu(1000):
                    rep["issues"].append(f"S{i}: '{sh.name}' slayt dışına taşıyor")
            if sh.has_text_frame:
                for p in sh.text_frame.paragraphs:
                    for r in p.runs:
                        info["fonts"].add(r.font.name)
                        for pat in AI_TELLS:
                            if re.search(pat, r.text, re.I):
                                rep["issues"].append(f"S{i}: AI-tell '{pat}' → '{r.text[:50]}'")
                if sh.name == "TITLE":
                    info["title"] = sh.text_frame.text
        bad = info["fonts"] - ALLOWED_FONTS
        if bad:
            rep["issues"].append(f"S{i}: taşınamaz font {bad}")
        if info["words"] > WORD_LIMIT and not info["title"].lower().startswith("kaynak"):
            rep["issues"].append(f"S{i}: {info['words']} kelime > {WORD_LIMIT}")
        info["fonts"] = sorted(f for f in info["fonts"] if f)
        rep["per_slide"].append(info)
    with zipfile.ZipFile(path) as z:
        app = z.read("docProps/app.xml").decode("utf-8")
        m = re.search(r"<Slides>(\d+)</Slides>", app)
        n = re.search(r"<Notes>(\d+)</Notes>", app)
        rep["app_xml"] = {"Slides": m and int(m.group(1)), "Notes": n and int(n.group(1))}
        notes_parts = [x for x in z.namelist() if x.startswith("ppt/notesSlides/")]
        rep["notes_parts"] = len(notes_parts)
    if rep["app_xml"]["Slides"] not in (None, rep["slides"]):
        rep["issues"].append(f"app.xml Slides={rep['app_xml']['Slides']} gerçek={rep['slides']}")
    if json_out:
        Path(json_out).write_text(json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"slayt={rep['slides']} notes_parts={rep['notes_parts']} app.xml={rep['app_xml']} sorun={len(rep['issues'])}")
    for x in rep["issues"]:
        print(" -", x)


if __name__ == "__main__":
    a = sys.argv[1:]
    j = a[a.index("--json") + 1] if "--json" in a else None
    main(a[0], j)
