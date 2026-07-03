"""Keşifsel örüntü ve risk analizi: kümeleme, anomali, bilgi teorisi, risk skoru."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from app.models import JobConfig, VariableInfo
from app.statistics.decision import plan_tests
from app.statistics.discovery import (
    MIN_ROWS_FOR_DISCOVERY,
    _run_anomaly,
    _run_clustering,
    _run_mutual_info,
    _run_risk_score,
    run_discovery,
)
from app.statistics.loader import load_dataset
from app.statistics.tests_runner import run_tests
from app.statistics.vartypes import infer_types
from sklearn.preprocessing import StandardScaler


def _vars(*specs) -> list[VariableInfo]:
    return [VariableInfo(name=n, kind=k, role=r) for n, k, r in specs]


def test_clustering_finds_two_groups():
    rng = np.random.default_rng(0)
    n = 40
    group_a = rng.normal(0, 0.5, size=(n, 3))
    group_b = rng.normal(10, 0.5, size=(n, 3))
    df = pd.DataFrame(np.vstack([group_a, group_b]), columns=["v1", "v2", "v3"])
    variables = _vars(("v1", "continuous", "auto"), ("v2", "continuous", "auto"), ("v3", "continuous", "auto"))

    sub = df[["v1", "v2", "v3"]]
    X = StandardScaler().fit_transform(sub.to_numpy(dtype=float))
    result = _run_clustering(sub, X)

    assert result is not None
    assert result.k == 2
    assert result.silhouette > 0.8
    sizes = sorted(c.size for c in result.clusters)
    assert sizes == [n, n]


def test_anomaly_detection_flags_injected_outliers():
    rng = np.random.default_rng(1)
    n = 60
    normal = rng.normal(0, 1, size=(n, 4))
    outliers = np.array([[50, 50, 50, 50], [-50, -50, -50, -50]])
    df = pd.DataFrame(np.vstack([normal, outliers]), columns=["a", "b", "c", "d"])
    sub = df[["a", "b", "c", "d"]]
    X = StandardScaler().fit_transform(sub.to_numpy(dtype=float))

    result = _run_anomaly(sub, X)

    assert result is not None
    flagged_idx = {r["row_index"] for r in result.flagged_rows}
    assert (n) in flagged_idx  # ilk enjekte edilen aykırı satır
    assert (n + 1) in flagged_idx  # ikinci enjekte edilen aykırı satır


def test_mutual_info_flags_nonlinear_hidden_relationship():
    rng = np.random.default_rng(2)
    n = 300
    x = rng.uniform(-3 * np.pi, 3 * np.pi, n)
    nonlinear = np.sin(x) + rng.normal(0, 0.05, n)  # doğrusal korelasyonu zayıf, ama güçlü bağımlılık
    linear = 2 * x + rng.normal(0, 1, n)  # klasik korelasyonla zaten yakalanır
    data = {"x": x, "nonlinear": nonlinear, "linear": linear}
    # birbirinden ve x'ten bağımsız gürültü değişkenleri: MI dağılımının 75. yüzdeliğini
    # gerçekçi (düşük) bir seviyede tutar, aksi halde yalnızca 2 çiftle eşik anlamsızlaşır
    for i in range(8):
        data[f"noise{i}"] = rng.normal(0, 1, n)
    df = pd.DataFrame(data)
    variables = _vars(*[(name, "continuous", "auto") for name in data])

    r_nonlinear = float(np.corrcoef(x, nonlinear)[0, 1])
    r_linear = float(np.corrcoef(x, linear)[0, 1])
    from app.models import Finding, PlannedTest

    correlation_findings = [
        Finding(id="F1", planned=PlannedTest(test_id="pearson", family="correlation", dv="x", iv="nonlinear"),
                statistic=r_nonlinear, error=None),
        Finding(id="F2", planned=PlannedTest(test_id="pearson", family="correlation", dv="x", iv="linear"),
                statistic=r_linear, error=None),
    ]

    pairs = _run_mutual_info(df, variables, correlation_findings)
    by_pair = {frozenset((p.var_a, p.var_b)): p for p in pairs}

    nonlinear_pair = by_pair[frozenset(("x", "nonlinear"))]
    linear_pair = by_pair[frozenset(("x", "linear"))]
    assert nonlinear_pair.hidden is True
    assert linear_pair.hidden is False


@pytest.fixture()
def loaded(sav_path):
    df, meta = load_dataset(sav_path)
    variables = infer_types(df, meta)
    return df, meta, variables


def test_risk_score_with_binary_dv(loaded):
    df, _, variables = loaded
    for v in variables:
        if v.name == "cinsiyet":
            v.role = "dv"
    assert next(v for v in variables if v.name == "cinsiyet").kind == "binary"

    result, skip_reason = _run_risk_score(df, variables)

    assert skip_reason is None
    assert result is not None
    assert result.dv == "cinsiyet"
    assert result.n > 0
    assert 0 <= result.n_positive <= result.n
    assert result.auc_logreg is not None and 0.0 <= result.auc_logreg <= 1.0
    assert len(result.predictors) > 0


def test_run_discovery_end_to_end(loaded):
    df, _, variables = loaded
    for v in variables:
        if v.name == "cinsiyet":
            v.role = "dv"
    plans, _ = plan_tests(df, variables)
    findings = run_tests(df, plans, variables, JobConfig())

    report = run_discovery(df, variables, JobConfig(), findings)

    assert report.risk_score is not None
    assert report.clustering is not None or report.skipped_reasons


def test_graceful_skip_on_insufficient_data():
    df = pd.DataFrame({"a": [1.0, 2.0, 3.0], "b": [2.0, 4.0, 6.0]})
    variables = _vars(("a", "continuous", "auto"), ("b", "continuous", "auto"))
    assert len(df) < MIN_ROWS_FOR_DISCOVERY

    report = run_discovery(df, variables, JobConfig(), [])

    assert report.clustering is None
    assert report.anomalies is None
    assert report.risk_score is None
    assert report.skipped_reasons  # nedenler kaydedilmiş, hata fırlatılmamış
