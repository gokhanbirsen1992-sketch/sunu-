"""Motor CLI: profil çıkarımı ve analiz planı yürütme.

Kullanım:
  python -m sav2q1.engine.runner profile --sav X.sav --out profile.json
  python -m sav2q1.engine.runner run --sav X.sav --plan plan.json --rundir runs/<id>

Plan (analysis_plan.json) — methodologist üretir, İNSAN KAPISI 1 onaylar:
  {
    "run_id": "...",
    "dataset": {...}, "design": {"kind": "...", "checklist": "STROBE"},
    "steps": [
      {"type": "descriptives", "include": ["age","sex",...]},
      {"type": "group_compare", "id": "R1", "outcome": "stress", "group": "sex",
       "paired": false, "question_ref": "RQ1"}
    ]
  }
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .io_sav import read_sav
from .ledger import LedgerBuilder, _NpEncoder
from .profile import profile_dataset
from .analyses.descriptives import build_descriptives
from .analyses.group_compare import compare_two_groups


def _dump(obj, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, cls=_NpEncoder), encoding="utf-8")


def cmd_profile(args) -> None:
    sav = read_sav(args.sav)
    prof = profile_dataset(sav)
    _dump(prof, args.out)
    print(f"[profile] {args.out} yazıldı: {prof['n_rows']} satır, {prof['n_vars']} değişken")


def cmd_run(args) -> None:
    sav = read_sav(args.sav)
    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    rundir = Path(args.rundir)
    prof = profile_dataset(sav)

    dataset = plan.get("dataset") or {
        "n_rows": prof["n_rows"], "n_vars": prof["n_vars"],
        "n_complete_cases": prof["n_complete_cases"], "source_file": sav.source_file,
    }
    lb = LedgerBuilder(run_id=plan.get("run_id", "run"), dataset=dataset,
                       design=plan.get("design", {"kind": "unknown", "checklist": "STROBE"}))

    for step in plan.get("steps", []):
        t = step["type"]
        if t == "descriptives":
            for d in build_descriptives(prof, include=step.get("include")):
                lb.add_descriptive(d)
        elif t == "group_compare":
            vlabels = sav.value_labels.get(step["group"])
            r = compare_two_groups(
                sav.df, step["outcome"], step["group"], value_labels=vlabels,
                paired=step.get("paired", False), result_id=step["id"],
                question_ref=step.get("question_ref"))
            lb.add_result(r)
        else:
            raise SystemExit(f"[run] bilinmeyen adım tipi: {t}")

    out = rundir / "results_ledger.json"
    lb.write(out)
    led = lb.to_dict()
    print(f"[run] {out} yazıldı: {len(led['descriptives'])} tanımlayıcı, "
          f"{len(led['results'])} sonuç, number_index anahtarları: {len(led['number_index'])}")


def main(argv=None) -> None:
    p = argparse.ArgumentParser(prog="sav2q1.engine.runner")
    sub = p.add_subparsers(dest="cmd", required=True)

    pp = sub.add_parser("profile", help="Değişken profili çıkar")
    pp.add_argument("--sav", required=True)
    pp.add_argument("--out", required=True)
    pp.set_defaults(func=cmd_profile)

    pr = sub.add_parser("run", help="Analiz planını yürüt, ledger üret")
    pr.add_argument("--sav", required=True)
    pr.add_argument("--plan", required=True)
    pr.add_argument("--rundir", required=True)
    pr.set_defaults(func=cmd_run)

    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
