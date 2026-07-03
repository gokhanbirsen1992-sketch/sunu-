from analysis import detect_columns, run_classic_tests, run_discovery


def test_detect_columns_classifies_numeric_and_categorical(synthetic_df):
    columns = detect_columns(synthetic_df)
    kinds = {c.name: c.kind for c in columns}
    assert kinds["x1"] == "numeric"
    assert kinds["skor"] == "numeric"
    assert kinds["cinsiyet"] == "categorical"
    assert kinds["kategori"] == "categorical"
    assert kinds["sonuc"] == "categorical"


def test_classic_tests_find_group_difference(synthetic_df):
    columns = detect_columns(synthetic_df)
    tests, truncated = run_classic_tests(synthetic_df, columns, alpha=0.05)
    assert not truncated
    assert any(t.kind == "group_test" and set(t.variables) == {"cinsiyet", "skor"} and t.significant for t in tests)


def test_discovery_finds_two_hidden_clusters(synthetic_df):
    columns = detect_columns(synthetic_df)
    discovery = run_discovery(synthetic_df, columns)
    assert discovery.clustering_k == 2
    assert discovery.clustering_silhouette > 0.5
    assert discovery.n_anomalies is not None
    assert discovery.risk_score is None  # hedef belirtilmedi


def test_discovery_with_target_produces_risk_score(synthetic_df):
    columns = detect_columns(synthetic_df)
    discovery = run_discovery(synthetic_df, columns, target="sonuc")
    assert discovery.risk_score is not None
    assert discovery.risk_score["target"] == "sonuc"
    assert 0 <= discovery.risk_score["n_positive"] <= discovery.risk_score["n"]
    assert discovery.risk_score["auc_logreg"] is not None
    assert 0.0 <= discovery.risk_score["auc_logreg"] <= 1.0


def test_discovery_graceful_on_tiny_data():
    import pandas as pd

    df = pd.DataFrame({"a": [1.0, 2.0, 3.0], "b": [2.0, 4.0, 6.0], "c": ["x", "y", "x"]})
    columns = detect_columns(df)
    discovery = run_discovery(df, columns)
    assert discovery.clustering_k is None
    assert discovery.notes
