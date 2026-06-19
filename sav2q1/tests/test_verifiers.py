"""Anti-halüsinasyon kapıları: verify-numeric ve verify-citations pass/fail."""

import json

from sav2q1.tools import verify_numeric, verify_citations


def _load(p):
    return json.loads(p.read_text(encoding="utf-8"))


def test_numeric_pass(demo_run):
    section = _load(demo_run / "sections" / "results.json")
    ledger = _load(demo_run / "results_ledger.json")
    rep = verify_numeric.verify(section, ledger)
    assert rep["status"] == "PASS", rep["violations"]


def test_numeric_fail_catches_fabricated(demo_run):
    section = _load(demo_run / "sections" / "results_tampered.json")
    ledger = _load(demo_run / "results_ledger.json")
    rep = verify_numeric.verify(section, ledger)
    assert rep["status"] == "FAIL"
    offenders = {v.get("offending_number") for v in rep["violations"]}
    assert {"9999,9", "0,55"} <= offenders


def test_citation_pass_real_source(demo_run):
    section = _load(demo_run / "sections" / "discussion.json")
    evidence = _load(demo_run / "evidence_store.json")
    assert verify_citations.verify(section, evidence)["status"] == "PASS"


def test_citation_fail_fake_ref(demo_run):
    section = _load(demo_run / "sections" / "discussion_tampered.json")
    evidence = _load(demo_run / "evidence_store.json")
    rep = verify_citations.verify(section, evidence)
    assert rep["status"] == "FAIL"


def test_citation_fail_fabricated_quote(demo_run):
    section = _load(demo_run / "sections" / "discussion.json")
    evidence = _load(demo_run / "evidence_store_badquote.json")
    rep = verify_citations.verify(section, evidence)
    assert rep["status"] == "FAIL"
    assert any("birebir bulunamadı" in v["reason"] for v in rep["violations"])
