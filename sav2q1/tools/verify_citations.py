"""verify-citations — atıf doğrulayıcı (anti-halüsinasyon kapısı, deterministik kısım).

Bir bölüm taslağındaki HER atıf için şunları zorunlu kılar:
  1) Atıf anahtarı evidence_store'da VAR.
  2) status == "VERIFIED" ve gerçek bir PMID veya DOI taşıyor.
  3) retracted == false (geri çekilmemiş).
  4) En az bir destek alıntısı (`supports_claims[].quote`) VAR ve bu alıntı
     saklanan GERÇEK abstract'ın BİREBİR alt dizesidir (uydurma alıntı imkânsız).

(İddianın abstract'ı gerçekten desteklediğine dair ANLAMSAL karar, citation
verifier ALT-AGENT'ının işidir; bu araç yapısal + birebir-alıntı bütünlüğünü
mekanik olarak güvence altına alır.)

Kullanım:
  python -m sav2q1.tools.verify_citations --section S.json --evidence E.json --out R.json
Çıkış kodu: PASS=0, FAIL=1.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def _norm_ws(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip().lower()


def _cited_refs(section: dict) -> list[str]:
    refs: list[str] = []
    for block in section.get("blocks", []):
        for sent in block.get("sentences", []):
            b = sent.get("binding") or {}
            if b.get("kind") == "citation":
                ref = b.get("ref") or b.get("result_id")
                if ref:
                    refs.append(ref)
    return refs


def verify(section: dict, evidence: dict) -> dict:
    by_key = {e["key"]: e for e in evidence.get("entries", [])}
    violations: list[dict] = []
    checked: list[str] = []

    for ref in _cited_refs(section):
        checked.append(ref)
        e = by_key.get(ref)
        if e is None:
            violations.append({"ref": ref, "reason": "evidence_store'da yok (uydurma atıf?)"})
            continue
        if e.get("status") != "VERIFIED":
            violations.append({"ref": ref, "reason": f"status VERIFIED değil ({e.get('status')})"})
        if not (e.get("pmid") or e.get("doi")):
            violations.append({"ref": ref, "reason": "gerçek PMID/DOI yok"})
        if e.get("retracted"):
            violations.append({"ref": ref, "reason": "kaynak geri çekilmiş (retracted)"})
        sc = e.get("supports_claims") or []
        if not sc:
            violations.append({"ref": ref, "reason": "destek alıntısı (supports_claims) yok"})
        else:
            abs = _norm_ws(e.get("abstract", ""))
            for c in sc:
                q = _norm_ws(c.get("quote", ""))
                if not q:
                    violations.append({"ref": ref, "reason": "boş destek alıntısı"})
                elif q not in abs:
                    violations.append({"ref": ref, "reason": "destek alıntısı abstract'ta birebir bulunamadı (uydurma alıntı)",
                                       "quote": c.get("quote")})

    status = "PASS" if not violations else "FAIL"
    return {
        "tool": "verify_citations",
        "section": section.get("section"),
        "status": status,
        "n_citations_checked": len(checked),
        "n_violations": len(violations),
        "violations": violations,
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="sav2q1.tools.verify_citations")
    p.add_argument("--section", required=True)
    p.add_argument("--evidence", required=True)
    p.add_argument("--out", required=False)
    args = p.parse_args(argv)

    section = json.loads(Path(args.section).read_text(encoding="utf-8"))
    evidence = json.loads(Path(args.evidence).read_text(encoding="utf-8"))
    report = verify(section, evidence)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    icon = "✓" if report["status"] == "PASS" else "✗"
    print(f"[verify-citations] {icon} {report['status']} — {report['section']}: "
          f"{report['n_citations_checked']} atıf, {report['n_violations']} ihlal")
    for v in report["violations"][:20]:
        print(f"   ✗ ref={v.get('ref','-')}: {v['reason']}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
