"""İstatistik çekirdeği: yükleme, tipleme, temizlik, karar tablosu, test koşumu."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from app.models import JobConfig
from app.statistics.cleaning import clean
from app.statistics.decision import assess_normality, plan_tests
from app.statistics.loader import load_dataset
from app.statistics.tests_runner import run_tests
from app.statistics.vartypes import infer_types


@pytest.fixture()
def loaded(sav_path):
    df, meta = load_dataset(sav_path)
    variables = infer_types(df, meta)
    return df, meta, variables


def _vmap(variables):
    return {v.name: v for v in variables}


def test_loader_reads_sav_metadata(loaded):
    df, meta, _ = loaded
    assert len(df) == 120
    assert meta["labels"]["kaygi"] == "Kaygı Puanı"
    assert meta["value_labels"]["cinsiyet"]["1.0"] == "Kadın"


def test_type_inference(loaded):
    _, _, variables = loaded
    kinds = {v.name: v.kind for v in variables}
    assert kinds["cinsiyet"] == "binary"
    assert kinds["grup"] == "nominal"
    assert kinds["kaygi"] == "continuous"
    assert kinds["memnuniyet"] == "ordinal"
    assert kinds["sigara"] == "binary"


def test_cleaning_removes_duplicates_and_outliers(loaded):
    df, _, variables = loaded
    cleaned, report = clean(df, variables)
    assert report.duplicates_removed >= 1
    assert "gelir" in report.outliers
    assert report.rows_after < report.rows_before
    assert cleaned["gelir"].max() < df["gelir"].max()


def test_normality_detects_skew():
    rng = np.random.default_rng(1)
    normal = pd.Series(rng.normal(0, 1, 200))
    skewed = pd.Series(np.exp(rng.normal(0, 1.5, 200)))
    assert assess_normality(normal).normal is True
    assert assess_normality(skewed).normal is False


def test_decision_rules(loaded):
    df, _, variables = loaded
    cleaned, _ = clean(df, variables)
    plans, _ = plan_tests(cleaned, variables)
    by_pair = {(p.dv, p.iv): p for p in plans}

    # çarpık 'gelir' × binary → Mann-Whitney
    assert by_pair[("gelir", "cinsiyet")].test_id == "mannwhitney"
    # Likert her korelasyonda Spearman
    corr = [p for p in plans if p.family == "correlation" and "memnuniyet" in (p.dv, p.iv)]
    assert corr and all(p.test_id == "spearman" for p in corr)
    # kategorik × kategorik → chi2/fisher
    assoc = [p for p in plans if p.family == "association"]
    assert assoc and all(p.test_id in ("chi2", "fisher") for p in assoc)
    # her planın gerekçesi iki dilde var
    assert all(p.rationale_tr and p.rationale_en for p in plans)
    # 3+ grup karşılaştırması ANOVA veya Kruskal olmalı
    g3 = [p for p in plans if p.iv == "grup" and p.family == "group"]
    assert g3 and all(p.test_id in ("anova", "kruskal") for p in g3)


def test_run_tests_produces_findings(loaded):
    df, _, variables = loaded
    cleaned, _ = clean(df, variables)
    plans, _ = plan_tests(cleaned, variables)
    findings = run_tests(cleaned, plans, variables, JobConfig())
    assert len(findings) == len(plans)
    ok = [f for f in findings if f.error is None]
    assert len(ok) >= len(plans) - 1
    for f in ok:
        assert f.p_value is not None and 0 <= f.p_value <= 1
        assert f.apa_tr and f.apa_en
    # enjekte edilen gerçek etki yakalanmalı: kaygı × cinsiyet anlamlı
    kc = next(f for f in findings if f.planned.dv == "kaygi" and f.planned.iv == "cinsiyet")
    assert kc.significant
    # negatif korelasyon: kaygı × doyum
    kd = next(f for f in findings if {f.planned.dv, f.planned.iv} == {"kaygi", "doyum"})
    assert kd.significant and kd.statistic < 0


def test_holm_adjustment_monotone(loaded):
    df, _, variables = loaded
    cleaned, _ = clean(df, variables)
    plans, _ = plan_tests(cleaned, variables)
    findings = run_tests(cleaned, plans, variables, JobConfig(p_adjust="holm"))
    for f in findings:
        if f.p_value is not None and f.p_adjusted is not None:
            assert f.p_adjusted >= f.p_value - 1e-12
