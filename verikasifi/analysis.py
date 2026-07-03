"""Veri Kâşifi — bağımsız istatistik + örüntü keşif motoru.

Herhangi bir CSV/Excel/SPSS dosyasını analiz eder: betimsel istatistikler, klasik anlamlılık
testleri (t-testi/ANOVA/korelasyon/ki-kare), gizli grup keşfi (PCA+K-Means kümeleme), sıra dışı
vaka tespiti (Isolation Forest), klasik korelasyonun kaçırdığı gizli ilişkiler (Mutual
Information) ve isteğe bağlı risk skoru (Lojistik Regresyon + Random Forest).

Tüm hesaplamalar deterministiktir (sabit random_state); yapay zekâ hiçbir sayı üretmez.
Bu modül, PaperForge (app/) koduyla hiçbir şey paylaşmaz — tamamen bağımsızdır.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.feature_selection import mutual_info_regression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, silhouette_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.preprocessing import StandardScaler

RANDOM_STATE = 42
MAX_CATEGORICAL_LEVELS = 30
MIN_NUMERIC_UNIQUE = 10
MAX_TESTS = 60
MIN_ROWS_FOR_DISCOVERY = 15
MIN_ROWS_FOR_MI_PAIR = 20
MIN_CLASS_N_FOR_RISK = 10


def load_dataset(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix in (".xlsx", ".xls"):
        return pd.read_excel(path)
    if suffix in (".sav", ".zsav"):
        import pyreadstat

        df, _ = pyreadstat.read_sav(str(path), apply_value_formats=True)
        return df
    raise ValueError(f"Desteklenmeyen dosya türü: {suffix} (.csv, .xlsx, .xls veya .sav kullanın)")


@dataclass
class ColumnInfo:
    name: str
    kind: str  # "numeric" | "categorical"
    n_missing: int
    n_unique: int


def detect_columns(df: pd.DataFrame) -> list[ColumnInfo]:
    cols: list[ColumnInfo] = []
    for name in df.columns:
        s = df[name]
        n_missing = int(s.isna().sum())
        n_unique = int(s.dropna().nunique())
        if n_unique <= 1:
            continue
        numeric = pd.api.types.is_numeric_dtype(s)
        if numeric and n_unique > MIN_NUMERIC_UNIQUE:
            kind = "numeric"
        elif n_unique <= MAX_CATEGORICAL_LEVELS:
            kind = "categorical"
        else:
            continue  # muhtemelen serbest metin veya kimlik sütunu
        cols.append(ColumnInfo(name=name, kind=kind, n_missing=n_missing, n_unique=n_unique))
    return cols


@dataclass
class TestResult:
    kind: str  # "correlation" | "group_test" | "chi_square"
    variables: list[str]
    statistic: float
    p_value: float
    significant: bool
    description: str


def run_classic_tests(df: pd.DataFrame, columns: list[ColumnInfo], alpha: float = 0.05) -> tuple[list[TestResult], bool]:
    numeric = [c.name for c in columns if c.kind == "numeric"]
    categorical = [c.name for c in columns if c.kind == "categorical"]
    results: list[TestResult] = []

    for i, a in enumerate(numeric):
        for b in numeric[i + 1:]:
            sub = df[[a, b]].apply(pd.to_numeric, errors="coerce").dropna()
            if len(sub) < 5:
                continue
            r, p = stats.pearsonr(sub[a], sub[b])
            sig = p < alpha
            results.append(TestResult(
                kind="correlation", variables=[a, b], statistic=float(r), p_value=float(p), significant=sig,
                description=f"'{a}' ile '{b}' arasında {'anlamlı' if sig else 'anlamsız'} korelasyon (r={r:.2f}, p={p:.3f}).",
            ))

    for cat in categorical:
        level_count = df[cat].dropna().nunique()
        if not (2 <= level_count <= 8):
            continue
        for num in numeric:
            sub = df[[cat, num]].copy()
            sub[num] = pd.to_numeric(sub[num], errors="coerce")
            sub = sub.dropna()
            grouped = [g[num].to_numpy(dtype=float) for _, g in sub.groupby(cat, observed=True) if len(g) >= 3]
            if len(grouped) < 2:
                continue
            if len(grouped) == 2:
                stat, p = stats.ttest_ind(grouped[0], grouped[1], equal_var=False)
                test_name = "t-testi"
            else:
                stat, p = stats.f_oneway(*grouped)
                test_name = "ANOVA"
            sig = p < alpha
            results.append(TestResult(
                kind="group_test", variables=[cat, num], statistic=float(stat), p_value=float(p), significant=sig,
                description=f"'{num}', '{cat}' gruplarına göre {test_name} ile {'anlamlı' if sig else 'anlamsız'} farklılık gösterdi (p={p:.3f}).",
            ))

    for i, a in enumerate(categorical):
        for b in categorical[i + 1:]:
            sub = df[[a, b]].dropna()
            if len(sub) < 10:
                continue
            table = pd.crosstab(sub[a], sub[b])
            if table.shape[0] < 2 or table.shape[1] < 2:
                continue
            chi2, p, _, _ = stats.chi2_contingency(table.values)
            sig = p < alpha
            results.append(TestResult(
                kind="chi_square", variables=[a, b], statistic=float(chi2), p_value=float(p), significant=sig,
                description=f"'{a}' ile '{b}' arasında {'anlamlı' if sig else 'anlamsız'} ilişki (χ²={chi2:.2f}, p={p:.3f}).",
            ))

    truncated = len(results) > MAX_TESTS
    results = results[:MAX_TESTS]
    return results, truncated


@dataclass
class ClusterInfo:
    cluster_id: int
    size: int
    share: float
    top_variables: list[str]


@dataclass
class DiscoveryResult:
    clustering_k: Optional[int] = None
    clustering_silhouette: Optional[float] = None
    clusters: list[ClusterInfo] = field(default_factory=list)
    n_anomalies: Optional[int] = None
    anomaly_contamination: float = 0.05
    hidden_relationships: list[dict[str, Any]] = field(default_factory=list)
    risk_score: Optional[dict[str, Any]] = None
    notes: list[str] = field(default_factory=list)


def _encode_categorical(series: pd.Series) -> pd.Series:
    codes, _ = pd.factorize(series, sort=True)
    return pd.Series(codes, index=series.index, dtype=float).replace(-1.0, np.nan)


def run_discovery(df: pd.DataFrame, columns: list[ColumnInfo], target: Optional[str] = None) -> DiscoveryResult:
    result = DiscoveryResult()
    col_map = {c.name: c for c in columns}
    numeric = [c.name for c in columns if c.kind == "numeric"]
    categorical = [c.name for c in columns if c.kind == "categorical"]

    if len(numeric) < 3:
        result.notes.append("Gizli grup/anomali keşfi için en az 3 sayısal değişken gerekir.")
    else:
        sub = df[numeric].apply(pd.to_numeric, errors="coerce").dropna()
        if len(sub) < MIN_ROWS_FOR_DISCOVERY:
            result.notes.append(f"Gizli grup/anomali keşfi için en az {MIN_ROWS_FOR_DISCOVERY} eksiksiz satır gerekir (mevcut: {len(sub)}).")
        else:
            X = StandardScaler().fit_transform(sub.to_numpy(dtype=float))

            best = None
            max_k = min(6, len(sub) // 5)
            for k in range(2, max(3, max_k + 1)):
                if k >= len(sub):
                    break
                labels = KMeans(n_clusters=k, n_init=10, random_state=RANDOM_STATE).fit_predict(X)
                if len(set(labels)) < 2:
                    continue
                score = float(silhouette_score(X, labels))
                if best is None or score > best[0]:
                    best = (score, k, labels)
            if best is None:
                result.notes.append("Belirgin bir gizli grup yapısı bulunamadı.")
            else:
                score, k, labels = best
                result.clustering_k, result.clustering_silhouette = k, score
                for cid in range(k):
                    mask = labels == cid
                    size = int(mask.sum())
                    means = X[mask].mean(axis=0)
                    order = np.argsort(-np.abs(means))[:4]
                    result.clusters.append(ClusterInfo(
                        cluster_id=cid + 1, size=size, share=size / len(sub),
                        top_variables=[sub.columns[i] for i in order],
                    ))

            iso = IsolationForest(contamination=0.05, random_state=RANDOM_STATE)
            pred = iso.fit_predict(X)
            result.n_anomalies = int((pred == -1).sum())

    mixed = numeric + categorical
    pairs: list[dict[str, Any]] = []
    for i, a in enumerate(mixed):
        for b in mixed[i + 1:]:
            xa = pd.to_numeric(df[a], errors="coerce") if col_map[a].kind == "numeric" else _encode_categorical(df[a])
            xb = pd.to_numeric(df[b], errors="coerce") if col_map[b].kind == "numeric" else _encode_categorical(df[b])
            merged = pd.concat([xa.rename("a"), xb.rename("b")], axis=1).dropna()
            if len(merged) < MIN_ROWS_FOR_MI_PAIR:
                continue
            discrete = col_map[a].kind == "categorical"
            try:
                mi = float(mutual_info_regression(
                    merged[["a"]].to_numpy(), merged["b"].to_numpy(),
                    discrete_features=[discrete], random_state=RANDOM_STATE,
                )[0])
            except ValueError:
                continue
            r = None
            if col_map[a].kind == "numeric" and col_map[b].kind == "numeric":
                r, _ = stats.pearsonr(merged["a"], merged["b"])
                r = float(r)
            pairs.append({"a": a, "b": b, "mi": mi, "r": r})

    if pairs:
        threshold = float(np.quantile([p["mi"] for p in pairs], 0.75))
        for p in pairs:
            p["hidden"] = p["mi"] >= threshold and (p["r"] is None or abs(p["r"]) < 0.3)
        pairs.sort(key=lambda p: -p["mi"])
    result.hidden_relationships = [p for p in pairs if p["hidden"]][:10]

    if target:
        result.risk_score = _run_risk_score(df, columns, target, result.notes)

    return result


def _run_risk_score(df: pd.DataFrame, columns: list[ColumnInfo], target: str, notes: list[str]) -> Optional[dict[str, Any]]:
    col_map = {c.name: c for c in columns}
    if target not in col_map:
        notes.append(f"'{target}' sütunu bulunamadı; risk skoru hesaplanamadı.")
        return None

    predictors = [c for c in columns if c.name != target]
    if len(predictors) < 2:
        notes.append(f"'{target}' için risk skoru hesaplanamadı: yeterli yordayıcı değişken yok.")
        return None

    numeric_cols = [c.name for c in predictors if c.kind == "numeric"]
    cat_cols = [c.name for c in predictors if c.kind == "categorical"]
    parts = {target: df[target]}
    for c in numeric_cols:
        parts[c] = pd.to_numeric(df[c], errors="coerce")
    for c in cat_cols:
        parts[c] = df[c]
    sub = pd.DataFrame(parts).dropna()

    y_series = sub[target]
    classes, counts = np.unique(y_series.to_numpy(dtype=object), return_counts=True)
    if len(classes) != 2 or counts.min() < MIN_CLASS_N_FOR_RISK:
        notes.append(f"'{target}' için risk skoru hesaplanamadı: ikili değil veya sınıflardan biri çok küçük (n<{MIN_CLASS_N_FOR_RISK}).")
        return None

    pos_label = classes.max()
    y = (y_series == pos_label).astype(int).to_numpy()

    X_df = sub[numeric_cols + cat_cols].copy()
    if cat_cols:
        X_df = pd.get_dummies(X_df, columns=cat_cols, drop_first=True)
    feature_names = list(X_df.columns)
    X = StandardScaler().fit_transform(X_df.to_numpy(dtype=float))

    n_splits = min(5, int(counts.min()))
    if n_splits < 2:
        notes.append(f"'{target}' için risk skoru hesaplanamadı: çapraz doğrulama için yeterli örneklem yok.")
        return None
    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=RANDOM_STATE)

    logreg = LogisticRegression(max_iter=1000)
    rf = RandomForestClassifier(n_estimators=300, random_state=RANDOM_STATE)

    auc_lr = auc_rf = None
    try:
        proba = cross_val_predict(logreg, X, y, cv=cv, method="predict_proba")[:, 1]
        auc_lr = float(roc_auc_score(y, proba))
    except ValueError:
        pass
    try:
        proba = cross_val_predict(rf, X, y, cv=cv, method="predict_proba")[:, 1]
        auc_rf = float(roc_auc_score(y, proba))
    except ValueError:
        pass

    rf.fit(X, y)
    predictors_out = sorted(
        [{"name": n, "importance": float(imp)} for n, imp in zip(feature_names, rf.feature_importances_)],
        key=lambda d: -d["importance"],
    )[:10]

    return {
        "target": target, "positive_class": str(pos_label), "n": len(sub), "n_positive": int(y.sum()),
        "auc_logreg": auc_lr, "auc_rf": auc_rf, "predictors": predictors_out,
    }
