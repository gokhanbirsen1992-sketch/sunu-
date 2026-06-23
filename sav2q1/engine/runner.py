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

from . import missing, multiplicity, planner, tables as tables_mod, figures as figures_mod
from .fmt import fmt_p
from .io_sav import read_sav
from .ledger import LedgerBuilder, _NpEncoder
from .profile import profile_dataset
from .analyses.descriptives import build_descriptives
from .analyses.group_compare import compare_two_groups, compare_multi_groups
from .analyses.categorical import crosstab_test
from .analyses.correlation import correlate, correlation_matrix
from .analyses.regression import linear_regression


def _dump(obj, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, cls=_NpEncoder), encoding="utf-8")


def cmd_profile(args) -> None:
    sav = read_sav(args.sav)
    prof = profile_dataset(sav)
    _dump(prof, args.out)
    print(f"[profile] {args.out} yazıldı: {prof['n_rows']} satır, {prof['n_vars']} değişken")


def cmd_plan(args) -> None:
    import yaml
    sav = read_sav(args.sav)
    prof = profile_dataset(sav)
    brief = None
    if args.brief:
        brief = yaml.safe_load(Path(args.brief).read_text(encoding="utf-8"))
    plan = planner.build_plan(prof, brief)
    _dump(plan, args.out)
    n_cmp = sum(1 for s in plan["steps"] if s["type"] in ("group_compare", "multi_group_compare"))
    print(f"[plan] {args.out} yazıldı: grup değişkeni={plan['group_var']}, "
          f"{n_cmp} grup karşılaştırması, {len(plan['id_vars'])} kimlik değişkeni dışlandı "
          f"({', '.join(plan['id_vars'][:4])}{'…' if len(plan['id_vars'])>4 else ''})")


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

    id_vars = set(plan.get("id_vars", []))           # PII/kimlik — analiz dışı
    labels = sav.column_labels

    def vl(col):
        return sav.value_labels.get(col)

    for step in plan.get("steps", []):
        t = step["type"]
        if t == "descriptives":
            include = step.get("include")
            if include is None:
                include = [v["name"] for v in prof["variables"] if v["name"] not in id_vars]
            for d in build_descriptives(prof, include=include):
                lb.add_descriptive(d)
        elif t == "group_compare":
            lb.add_result(compare_two_groups(
                sav.df, step["outcome"], step["group"], value_labels=vl(step["group"]),
                paired=step.get("paired", False), result_id=step["id"],
                question_ref=step.get("question_ref")))
        elif t == "multi_group_compare":
            lb.add_result(compare_multi_groups(
                sav.df, step["outcome"], step["group"], value_labels=vl(step["group"]),
                result_id=step["id"], question_ref=step.get("question_ref"),
                confirmatory=step.get("confirmatory", False)))
        elif t == "categorical":
            lb.add_result(crosstab_test(
                sav.df, step["row"], step["col"], value_labels_row=vl(step["row"]),
                value_labels_col=vl(step["col"]), result_id=step["id"],
                question_ref=step.get("question_ref"), confirmatory=step.get("confirmatory", False)))
        elif t == "correlation":
            lb.add_result(correlate(
                sav.df, step["x"], step["y"], label_x=labels.get(step["x"], step["x"]),
                label_y=labels.get(step["y"], step["y"]), result_id=step["id"],
                question_ref=step.get("question_ref"), confirmatory=step.get("confirmatory", False)))
        elif t == "correlation_matrix":
            lb.add_result(correlation_matrix(
                sav.df, step["x_vars"], step["y_vars"], labels=labels,
                result_id=step["id"], question_ref=step.get("question_ref")))
        elif t == "regression_linear":
            lb.add_result(linear_regression(
                sav.df, step["outcome"], step["predictors"], labels=labels,
                result_id=step["id"], question_ref=step.get("question_ref")))
        else:
            raise SystemExit(f"[run] bilinmeyen adım tipi: {t}")

    # Eksik veri raporu
    analysis_vars = [v["name"] for v in prof["variables"] if v["name"] not in id_vars]
    lb.ledger["missingness"] = missing.missingness_report(sav.df, analysis_vars)

    # Çokluluk düzeltmesi: keşifsel grup karşılaştırmaları
    policy = plan.get("multiplicity_policy", "bh")
    expl = [r for r in lb.ledger["results"]
            if r.get("family") == "multi_group_compare" and not r.get("confirmatory")]
    if expl and policy != "none":
        padj = multiplicity.adjust_pvalues([r["p_value"] for r in expl], policy)
        for r, pa in zip(expl, padj):
            r["p_adjusted"] = pa
            r["p_adjusted_str"] = fmt_p(pa)
            lb._register(r["id"], [fmt_p(pa)])
        lb.ledger["multiplicity"] = {"method": policy, "n_tests": len(expl),
                                     "family": "exploratory_group_comparisons"}

    # Tablolar (gruplara göre Tablo 1 + korelasyon tablosu)
    t1spec = plan.get("table1")
    if t1spec:
        t1 = tables_mod.build_group_table1(lb.ledger, labels,
                                           title=t1spec.get("title", "Tablo 1. Gruplara göre özellikler"))
        if t1:
            _dump(t1, rundir / "tables" / "T1.json")
            lb.add_table({"id": "T1", "title": t1["title"], "file": "tables/T1.json"})
        t2 = tables_mod.build_correlation_table(lb.ledger, labels,
                                                title=t1spec.get("corr_title", "Tablo 2. Belirteç korelasyonları"))
        if t2:
            _dump(t2, rundir / "tables" / "T2.json")
            lb.add_table({"id": "T2", "title": t2["title"], "file": "tables/T2.json"})

    # Şekiller
    figspec = plan.get("figures")
    if figspec:
        try:
            fdir = rundir / "figures"
            lb.add_figure(figures_mod.make_marker_boxplots(
                sav.df, figspec["group"], figspec["markers"], vl(figspec["group"]), labels, fdir))
            if figspec.get("scatter"):
                sx, sy = figspec["scatter"]
                lb.add_figure(figures_mod.make_scatter(sav.df, sx, sy, labels, fdir))
        except Exception as e:  # noqa: BLE001 — şekil hatası tüm koşuyu düşürmesin
            print(f"[run] şekil üretimi atlandı: {e}")

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

    pl = sub.add_parser("plan", help="Profilden (+brief) analiz planını OTOMATİK üret")
    pl.add_argument("--sav", required=True)
    pl.add_argument("--out", required=True)
    pl.add_argument("--brief", required=False)
    pl.set_defaults(func=cmd_plan)

    pr = sub.add_parser("run", help="Analiz planını yürüt, ledger üret")
    pr.add_argument("--sav", required=True)
    pr.add_argument("--plan", required=True)
    pr.add_argument("--rundir", required=True)
    pr.set_defaults(func=cmd_run)

    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
