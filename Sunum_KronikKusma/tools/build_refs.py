#!/usr/bin/env python3
"""slides_content.md içindeki [@PMID] etiketlerini ilk görünme sırasına göre numaralandırır,
_kaynaklar.md (SSOT) ve references/ref_order.json üretir. Her PMID library.bib'de ve en az bir
kanıt satırında (research/A*_*.md) bulunmak zorunda; değilse hata verir."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from check_evidence import parse_bib  # noqa: E402

TAG = re.compile(r"\[@([\d;\s@]+)\]")


import unicodedata

ACC = {"'": "\u0301", '"': "\u0308", "`": "\u0300", "^": "\u0302", "~": "\u0303", "c": "\u0327", "v": "\u030c", "u": "\u0306"}


def delatex(t):
    """BibTeX aksanlarını ({\\'u}, {\\"a}, \\c{c}) Unicode'a çevirir, kalan süslü parantezleri siler."""
    t = re.sub(r"\{?\\([\'\"`^~cvu])\{?([A-Za-z])\}?\}?", lambda m: m.group(2) + ACC[m.group(1)], t)
    t = t.replace("{", "").replace("}", "").replace("\\&", "&")
    return unicodedata.normalize("NFC", t)


def short_authors(a):
    names = [n.strip() for n in re.split(r"\s+and\s+", a) if n.strip() and n.strip() != "others"]
    out = []
    for n in names[:3]:
        if "," in n:
            last, first = [x.strip() for x in n.split(",", 1)]
        else:
            parts = n.split()
            last, first = parts[-1], " ".join(parts[:-1])
        initials = "".join(w[0] for w in re.split(r"[\s\-]+", first) if w)
        out.append(f"{last} {initials}".strip())
    more = len(names) > 3 or "others" in a
    return ", ".join(out) + (", et al" if more else "")


def main():
    text = (ROOT / "research" / "slides_content.md").read_text(encoding="utf-8")
    order = []
    for m in TAG.finditer(text):
        for p in re.findall(r"\d+", m.group(1)):
            if p not in order:
                order.append(p)
    bib = {re.sub(r"\D", "", e.get("pmid", "")): e
           for e in parse_bib((ROOT / "references" / "library.bib").read_text(encoding="utf-8"))}
    evidence = "\n".join(f.read_text(encoding="utf-8") for f in (ROOT / "research").glob("A[0-9]_*.md"))
    missing_bib = [p for p in order if p not in bib]
    missing_ev = [p for p in order if f"| {p} |" not in evidence]
    if missing_bib or missing_ev:
        sys.exit(f"HATA: bib'de yok {missing_bib}; kanıt satırında yok {missing_ev}")
    lines = ["# Kaynaklar — Kronik Tekrarlayan Kusması Olan Çocuğa Yaklaşım", "",
             "Numaralar slayt sırasıyla `tools/build_refs.py` tarafından üretildi (elle düzenlemeyin). "
             "Tüm kayıtlar PubMed'de doğrulandı (qc/reference_audit.json).", ""]
    refs = []
    for i, p in enumerate(order, 1):
        e = {k: delatex(v) if isinstance(v, str) else v for k, v in bib[p].items()}
        vol = e.get("volume", "")
        num = f"({e['number']})" if e.get("number") else ""
        pages = ":" + re.sub(r"-+", "-", e["pages"]) if e.get("pages") else ""
        src = f"{e.get('journal','')}. {e.get('year','')}" + (f";{vol}{num}{pages}" if vol else "")
        doi = e.get("doi", "")
        title = e.get("title", "").rstrip(".")
        line = f"{i}. {short_authors(e.get('author',''))}. {title}. {src}. PMID {p}" + (f". doi:{doi}" if doi else "")
        lines.append(line.replace("\\&", "&"))
        refs.append({"n": i, "pmid": p, "short": f"{short_authors(e.get('author','')).split(',')[0]} {e.get('year','')}",
                     "text": line.split(". ", 1)[1].replace("\\&", "&"), "doi": doi})
    (ROOT / "_kaynaklar.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (ROOT / "references" / "ref_order.json").write_text(json.dumps(refs, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(order)} kaynak numaralandı; tümü bib'de ve kanıt satırında mevcut.")


if __name__ == "__main__":
    main()
