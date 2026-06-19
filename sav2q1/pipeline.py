"""Başsız (headless) makale üretim denetleyicisi — LLM YOK, deterministik.

Hem web (PWA/FastAPI) hem masaüstü (Tkinter) arayüzleri bunu çağırır:
  .sav → planner → motor (ledger+tablo+şekil) → narrate (Yöntem/Bulgular/Öz)
  → verify-numeric → docx.assemble → .docx yolu.

Opsiyonel: with_pubmed=True ise ücretsiz NCBI ile gerçek atıflar + şablon
Giriş/Tartışma eklenir (internet gerekir).
"""

from __future__ import annotations

import json
from pathlib import Path

from .engine import narrate, planner
from .engine.io_sav import read_sav
from .engine.ledger import _NpEncoder
from .engine.profile import profile_dataset
from .engine.runner import cmd_run
from .docx.assemble import build_docx


def _dump(obj, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, cls=_NpEncoder), encoding="utf-8")


class _Args:
    def __init__(self, sav, plan, rundir):
        self.sav, self.plan, self.rundir = sav, plan, rundir


def generate_article(sav_path: str, rundir: str, *, brief: dict | None = None,
                     title: str | None = None, with_pubmed: bool = False, log=print) -> dict:
    rundir = Path(rundir)
    (rundir / "sections").mkdir(parents=True, exist_ok=True)

    log("Veri profilleniyor ve analiz planı oluşturuluyor…")
    sav = read_sav(sav_path)
    prof = profile_dataset(sav)
    plan = planner.build_plan(prof, brief)

    # En çok 3 sürekli değişken için gruplara göre kutu grafiği ekle
    cmp_outcomes = [s["outcome"] for s in plan["steps"]
                    if s["type"] in ("multi_group_compare", "group_compare")]
    if plan.get("group_var") and cmp_outcomes:
        plan["figures"] = {"group": plan["group_var"], "markers": cmp_outcomes[:3]}
    plan_path = rundir / "analysis_plan.json"
    _dump(plan, plan_path)

    log(f"İstatistik motoru çalışıyor (grup: {plan.get('group_var')})…")
    cmd_run(_Args(sav_path, str(plan_path), str(rundir)))
    ledger = json.loads((rundir / "results_ledger.json").read_text(encoding="utf-8"))

    log("Yöntem, Bulgular ve Öz bölümleri yazılıyor (deterministik)…")
    _dump(narrate.narrate_methods(ledger), rundir / "sections" / "methods.json")
    _dump(narrate.narrate_results(ledger), rundir / "sections" / "results.json")
    _dump(narrate.narrate_abstract(ledger), rundir / "sections" / "abstract.json")

    sections = [{"heading": "Yöntem", "file": "sections/methods.json"},
                {"heading": "Bulgular", "file": "sections/results.json"}]

    evidence = {"entries": []}
    if with_pubmed:
        try:
            from .lit import pubmed_http
            log("PubMed'den gerçek kaynaklar getiriliyor (ücretsiz NCBI)…")
            topic = (brief or {}).get("topic") or _infer_topic(ledger, plan)
            evidence, intro, disc = pubmed_http.build_literature(topic, ledger, plan)
            if evidence["entries"]:
                _dump(intro, rundir / "sections" / "intro.json")
                _dump(disc, rundir / "sections" / "discussion.json")
                sections = ([{"heading": "Giriş", "file": "sections/intro.json"}] + sections +
                            [{"heading": "Tartışma", "file": "sections/discussion.json"}])
        except Exception as e:  # noqa: BLE001 — literatür opsiyoneldir, başarısızsa atla
            log(f"Literatür adımı atlandı: {e}")
    _dump(evidence, rundir / "evidence_store.json")

    log("Sayı ve atıf doğrulama kapıları çalışıyor…")
    from .tools import verify_citations, verify_numeric
    gate = {"numeric": "PASS", "citations": "PASS", "violations": 0}
    for sec_file in sorted((rundir / "sections").glob("*.json")):
        section = json.loads(sec_file.read_text(encoding="utf-8"))
        rep = verify_numeric.verify(section, ledger)
        if rep["status"] != "PASS":
            gate.update(numeric="FAIL", violations=gate["violations"] + rep["n_violations"], section=sec_file.stem)
            log(f"  ⚠ sayı: {sec_file.stem}: {rep['n_violations']} ihlal")
        if evidence["entries"]:
            crep = verify_citations.verify(section, evidence)
            if crep["status"] != "PASS":
                gate.update(citations="FAIL")
                log(f"  ⚠ atıf: {sec_file.stem}: {crep['n_violations']} ihlal")

    manuscript = {
        "language": "tr", "citation_style": "vancouver",
        "title": title or _default_title(ledger, plan),
        "authors": [{"name": "[Yazar adı]", "affiliation": "[Kurum]"}],
        "corresponding": "[Sorumlu yazar / e-posta]",
        "keywords": _keywords(ledger, plan),
        "abstract": narrate.abstract_dict(ledger),
        "sections": sections,
        "table1": plan.get("table1", {"title": "Tablo 1. Gruplara göre özellikler"}),
        "icmje": {"ethics": "[Etik kurul adı ve no]", "informed_consent": "[Onam beyanı]",
                  "funding": "[Finansman]", "coi": "Yazarlar çıkar çatışması bildirmemiştir.",
                  "data_availability": "Veriler makul talep üzerine sorumlu yazardan edinilebilir."},
    }
    _dump(manuscript, rundir / "manuscript.json")

    log("Word belgesi derleniyor…")
    docx_path = build_docx(str(rundir))
    log("Tamamlandı.")
    return {"docx": docx_path, "ledger": str(rundir / "results_ledger.json"),
            "gate": gate, "group_var": plan.get("group_var"),
            "n_results": len(ledger.get("results", [])), "with_citations": bool(evidence["entries"])}


def _default_title(ledger: dict, plan: dict) -> str:
    g = plan.get("group_var")
    return (f"{narrate._lab(ledger, g)}'a Göre Klinik ve Laboratuvar Değişkenlerinin Karşılaştırılması"
            if g else "SPSS Veri Analizi Raporu")


def _keywords(ledger: dict, plan: dict) -> list[str]:
    kws = []
    g = plan.get("group_var")
    if g:
        kws.append(narrate._lab(ledger, g))
    kws += ["veri analizi", "tanımlayıcı istatistik", "grup karşılaştırması"]
    return kws[:6]


def _infer_topic(ledger: dict, plan: dict) -> str:
    g = plan.get("group_var")
    return narrate._lab(ledger, g) if g else "clinical study"
