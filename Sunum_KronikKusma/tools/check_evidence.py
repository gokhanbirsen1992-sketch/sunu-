#!/usr/bin/env python3
"""Deterministik kanıt denetimi (LLM'siz).

1. references/*.bib: zorunlu alan, verified bayrağı, PMID/DOI tekrarı.
2. research/A*_*.md kanıt tabloları: her satırın PMID'si bib'de mi, DOI bib ile aynı mı,
   iddiadaki her sayı verbatim alıntıda geçiyor mu (sayı sadakati).

Kullanım: python tools/check_evidence.py [--json qc/evidence_check.json]
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REQUIRED = ("author", "title", "journal", "year", "pmid", "verified")
NUM_RE = re.compile(r"\d+(?:[.,]\d+)?")


def parse_bib(text):
    entries = []
    for m in re.finditer(r"@(\w+)\s*\{\s*([^,\s]+)\s*,(.*?)\n\}", text, re.S):
        fields = {}
        for fm in re.finditer(r"(\w+)\s*=\s*[{\"](.*?)[}\"]\s*,?\s*$", m.group(3), re.M):
            fields[fm.group(1).lower()] = fm.group(2).strip()
        entries.append({"type": m.group(1), "key": m.group(2), **fields})
    return entries


def norm_num(s):
    s = s.replace(",", ".")
    try:
        f = float(s)
    except ValueError:
        return s
    return f"{f:g}"


UNITS = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90}
WORD_RE = re.compile(r"\b(" + "|".join(list(TENS) + UNITS) + r")(?:-(" + "|".join(UNITS[1:10]) + r"))?\b", re.I)


def numbers(text):
    found = {norm_num(n) for n in NUM_RE.findall(text)}
    for m in WORD_RE.finditer(text):  # İngilizce yazıyla sayı: "four", "Sixty-one"
        w = m.group(1).lower()
        v = TENS.get(w, UNITS.index(w) if w in UNITS else 0)
        if m.group(2):
            v += UNITS.index(m.group(2).lower())
        found.add(str(v))
    return found


def split_row(line):
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    return cells


def main():
    out = {"bib": {}, "claims": {}, "summary": {}}
    bib_entries = []
    for bf in sorted((ROOT / "references").glob("A*.bib")):
        for e in parse_bib(bf.read_text(encoding="utf-8")):
            e["_file"] = bf.name
            bib_entries.append(e)

    by_pmid = defaultdict(list)
    by_doi = defaultdict(list)
    bib_problems = []
    for e in bib_entries:
        missing = [f for f in REQUIRED if not e.get(f)]
        if missing:
            bib_problems.append(f"{e['_file']}:{e['key']} eksik alan {missing}")
        if e.get("verified", "").lower() != "true":
            bib_problems.append(f"{e['_file']}:{e['key']} verified != true")
        if e.get("pmid"):
            by_pmid[e["pmid"]].append(e)
        if e.get("doi"):
            by_doi[e["doi"].lower()].append(e)

    # Aynı PMID farklı dosyalarda normal (ajanlar ortak kaynak kullanır); çelişkili alan tekrarı sorun.
    conflicts = []
    for pmid, es in by_pmid.items():
        dois = {x.get("doi", "").lower() for x in es}
        years = {x.get("year") for x in es}
        if len(dois) > 1 or len(years) > 1:
            conflicts.append(f"PMID {pmid}: çelişkili DOI/yıl {dois} {years} ({[x['_file'] for x in es]})")
    for doi, es in by_doi.items():
        pmids = {x.get("pmid") for x in es}
        if len(pmids) > 1:
            conflicts.append(f"DOI {doi}: çelişkili PMID {pmids}")

    out["bib"] = {
        "entries": len(bib_entries),
        "unique_pmids": len(by_pmid),
        "problems": bib_problems,
        "conflicts": conflicts,
    }

    claim_issues = []
    n_claims = 0
    for md in sorted((ROOT / "research").glob("A[0-9]_*.md")):
        header = None
        for line in md.read_text(encoding="utf-8").splitlines():
            if not line.startswith("|"):
                header = None if not line.strip() else header
                continue
            cells = split_row(line)
            if cells and cells[0] == "ID":
                header = [c.replace("İ", "i").lower() for c in cells]
                continue
            if not header or not re.match(r"A\d-\d+", cells[0] if cells else ""):
                continue
            n_claims += 1
            row = dict(zip(header, cells))
            cid = cells[0]
            claim = next((v for k, v in row.items() if k.startswith("iddia")), "")
            quote = next((v for k, v in row.items() if "alıntı" in k or "alinti" in k), "")
            pmid = re.sub(r"\D", "", row.get("pmid", ""))
            doi = row.get("doi", "").strip().lower()
            issues = []
            if not pmid:
                issues.append("PMID yok")
            elif pmid not in by_pmid:
                issues.append(f"PMID {pmid} bib'de yok")
            elif doi and not doi.startswith("doi yok"):
                bdois = {x.get("doi", "").lower() for x in by_pmid[pmid]}
                if doi not in bdois:
                    issues.append(f"DOI uyuşmazlığı satır={doi} bib={bdois}")
            if not quote or len(quote) < 15:
                issues.append("verbatim alıntı yok/çok kısa")
            missing_nums = sorted(numbers(claim) - numbers(quote))
            if missing_nums:
                issues.append(f"iddiadaki sayılar alıntıda yok: {missing_nums}")
            if issues:
                claim_issues.append({"file": md.name, "id": cid, "issues": issues, "claim": claim[:160]})
    out["claims"] = {"n": n_claims, "issues": claim_issues}
    out["summary"] = {
        "bib_entries": len(bib_entries),
        "bib_problems": len(bib_problems),
        "bib_conflicts": len(conflicts),
        "claims": n_claims,
        "claims_with_issues": len(claim_issues),
    }
    if "--json" in sys.argv:
        p = ROOT / sys.argv[sys.argv.index("--json") + 1]
        p.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(out["summary"], ensure_ascii=False, indent=2))
    for x in bib_problems + conflicts:
        print("BIB:", x)
    for c in claim_issues:
        print(f"CLAIM {c['file']} {c['id']}: {'; '.join(c['issues'])}")


if __name__ == "__main__":
    main()
