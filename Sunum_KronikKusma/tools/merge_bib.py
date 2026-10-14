#!/usr/bin/env python3
"""references/A*.bib → references/library.bib (PMID başına tek kayıt, çakışmasız anahtar)
+ references/pmid_key_map.json (ajan anahtarı → nihai anahtar).

V1 bulguları: aynı anahtar iki farklı PMID'ye (Karrento2025), aynı PMID farklı anahtarlara gidiyor;
'DOI yok' serbest metni; kaçışsız '&'; note alanları. Hepsi burada normalize edilir."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from check_evidence import parse_bib  # noqa: E402

KEEP = ["author", "title", "journal", "year", "volume", "number", "pages", "doi", "pmid", "pmcid",
        "verified", "verified_by"]


def base_key(e):
    first = re.split(r"\s+and\s+", e.get("author", "Anon"))[0]
    last = first.split(",")[0].strip() if "," in first else first.split()[-1]
    last = re.sub(r"[^A-Za-z]", "", last.encode("ascii", "ignore").decode()) or "Anon"
    return f"{last}{e.get('year', '')}"


def main():
    by_pmid = {}
    agent_keys = {}
    for bf in sorted((ROOT / "references").glob("A*.bib")):
        for e in parse_bib(bf.read_text(encoding="utf-8")):
            pmid = re.sub(r"\D", "", e.get("pmid", ""))
            if not pmid:
                continue
            agent_keys.setdefault(pmid, set()).add(f"{bf.stem}:{e['key']}")
            by_pmid.setdefault(pmid, e)
    used = {}
    final = {}
    for pmid, e in sorted(by_pmid.items(), key=lambda kv: (base_key(kv[1]), kv[0])):
        k = base_key(e)
        n = used.get(k, 0)
        used[k] = n + 1
        final[pmid] = k if n == 0 else f"{k}{'abcdefghij'[n]}"
    # ilk kayıt da çakışıyorsa 'a' eki ver
    for k, n in used.items():
        if n > 1:
            for pmid, fk in final.items():
                if fk == k:
                    final[pmid] = k + "a"
                    break
    out = []
    for pmid, e in sorted(by_pmid.items(), key=lambda kv: final[kv[0]]):
        fields = []
        for f in KEEP:
            v = e.get(f, "")
            if f == "doi" and v.lower().startswith("doi yok"):
                v = ""
            if not v:
                continue
            v = re.sub(r"(?<!\\)&", r"\\&", v)
            fields.append(f"  {f} = {{{v}}}")
        out.append(f"@article{{{final[pmid]},\n" + ",\n".join(fields) + "\n}")
    (ROOT / "references" / "library.bib").write_text("\n\n".join(out) + "\n", encoding="utf-8")
    (ROOT / "references" / "pmid_key_map.json").write_text(json.dumps(
        {p: {"key": final[p], "agent_keys": sorted(agent_keys[p])} for p in sorted(final)},
        ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(out)} kayıt, {sum(1 for n in used.values() if n > 1)} anahtar ekle ayrıştırıldı")


if __name__ == "__main__":
    main()
