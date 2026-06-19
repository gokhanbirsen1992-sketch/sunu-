"""verify-numeric — BİNDİNG-BAZLI sayı doğrulayıcı (anti-halüsinasyon kapısı).

Bir bölüm taslağındaki (section_draft.json) HER cümlenin içerdiği sayıların,
yalnızca o cümlenin `binding`'inde gösterilen ledger id'sine ait token kümesinde
(+ örneklem sayıları + istatistik-dışı whitelist + yıllar) bulunmasını şart koşar.

Böylece iki hata yakalanır:
  1) Uydurma sayı (defterde hiç yok).
  2) DOĞRU sayı / YANLIŞ bağlam (sayı var ama bu sonucun değil).

Kullanım:
  python -m sav2q1.tools.verify_numeric --section S.json --ledger L.json --out R.json
Çıkış kodu: PASS=0, FAIL=1.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from sav2q1.engine.numbers import extract_tokens, is_year, GLOBAL_WHITELIST


def _binding_id(binding: dict) -> str | None:
    return binding.get("result_id") or binding.get("ref")


def verify(section: dict, ledger: dict) -> dict:
    number_index = ledger.get("number_index", {})
    global_allowed = set(ledger.get("global_index", [])) | GLOBAL_WHITELIST

    violations: list[dict] = []
    n_sentences = 0
    n_numbers = 0

    for bi, block in enumerate(section.get("blocks", [])):
        for si, sent in enumerate(block.get("sentences", [])):
            n_sentences += 1
            text = sent.get("text", "")
            binding = sent.get("binding") or {"kind": "narrative"}
            kind = binding.get("kind", "narrative")

            allowed = set(global_allowed)
            idkey = None
            if kind == "ledger":
                idkey = _binding_id(binding)
                if idkey is None:
                    violations.append({"block": bi, "sentence": si, "text": text,
                                       "reason": "ledger binding'inde result_id/ref yok"})
                    continue
                if idkey not in number_index:
                    violations.append({"block": bi, "sentence": si, "text": text,
                                       "reason": f"binding id '{idkey}' ledger'da yok"})
                    continue
                allowed |= set(number_index[idkey])

            for tok in extract_tokens(text):
                n_numbers += 1
                if tok in allowed or is_year(tok):
                    continue
                violations.append({
                    "block": bi, "sentence": si, "binding_kind": kind,
                    "binding_id": idkey, "offending_number": tok, "text": text,
                    "reason": ("istatistik-dışı cümlede izinsiz sayı"
                               if kind != "ledger" else
                               f"'{tok}' sayısı '{idkey}' sonucunun token kümesinde yok"),
                })

    status = "PASS" if not violations else "FAIL"
    return {
        "tool": "verify_numeric",
        "section": section.get("section"),
        "status": status,
        "n_sentences": n_sentences,
        "n_numbers_checked": n_numbers,
        "n_violations": len(violations),
        "violations": violations,
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="sav2q1.tools.verify_numeric")
    p.add_argument("--section", required=True)
    p.add_argument("--ledger", required=True)
    p.add_argument("--out", required=False)
    args = p.parse_args(argv)

    section = json.loads(Path(args.section).read_text(encoding="utf-8"))
    ledger = json.loads(Path(args.ledger).read_text(encoding="utf-8"))
    report = verify(section, ledger)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    icon = "✓" if report["status"] == "PASS" else "✗"
    print(f"[verify-numeric] {icon} {report['status']} — {report['section']}: "
          f"{report['n_numbers_checked']} sayı, {report['n_violations']} ihlal")
    for v in report["violations"][:20]:
        print(f"   ✗ sayı={v.get('offending_number','-')} id={v.get('binding_id','-')}: {v['reason']}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
