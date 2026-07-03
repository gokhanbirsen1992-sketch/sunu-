"""Keşifsel örüntü ve risk analizi: kümeleme, PCA, anomali, bilgi teorisi, risk skoru.

Klasik hipotez testlerinin (decision.py/tests_runner.py) aksine bu modülün ürettiği bulgular
"anlamlı/anlamlı değil" değil, **keşifsel/hipotez üreticidir** — doğrulayıcı sonuçlarla
karıştırılmamalıdır. Tüm hesaplamalar scikit-learn/numpy ile deterministiktir (sabit
random_state); hiçbir sayı yapay zekâya hesaplatılmaz.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.feature_selection import mutual_info_regression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, silhouette_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.preprocessing import StandardScaler

from app.models import (
    AnomalyResult,
    ClusterProfile,
    ClusteringResult,
    DiscoveryReport,
    Finding,
    JobConfig,
    MutualInfoPair,
    RiskScoreResult,
    VariableInfo,
)

RANDOM_STATE = 42
MIN_ROWS_FOR_DISCOVERY = 15
MIN_VARS_FOR_DISCOVERY = 3
MIN_ROWS_FOR_ANOMALY = 20
MIN_ROWS_FOR_MI_PAIR = 20
MIN_CLASS_N_FOR_RISK = 10


def _label(v: VariableInfo) -> str:
    return v.label or v.name


def _encode_column(df: pd.DataFrame, name: str, kind: str) -> pd.Series:
    """Sürekli/sıralı değişkeni sayısala çevirir; nominal/binary değişkeni tamsayı koduna çevirir.

    Veri Temizleme aşaması (`s1_clean._apply_value_labels`) nominal/binary sütunların ham SPSS
    kodlarını (1.0/2.0) okunabilir etiketlere ("Kadın"/"Erkek") çevirdiği için bu sütunlar
    `pd.to_numeric` ile işlenemez; bunun yerine kategori kodlanır.
    """
    if kind in ("continuous", "ordinal"):
        return pd.to_numeric(df[name], errors="coerce")
    codes, _ = pd.factorize(df[name], sort=True)
    return pd.Series(codes, index=df.index, dtype=float).replace(-1.0, np.nan)


def _numeric_frame(df: pd.DataFrame, variables: list[VariableInfo]) -> tuple[pd.DataFrame | None, str | None]:
    """Kümeleme/PCA/anomali için uygun sürekli/sıralı değişkenleri seçip sayısala çevirir."""
    usable = [v for v in variables if v.role != "exclude" and v.kind in ("continuous", "ordinal")]
    if len(usable) < MIN_VARS_FOR_DISCOVERY:
        return None, "Kümeleme/PCA/anomali analizi için en az 3 sürekli/sıralı değişken gerekir."
    cols = [v.name for v in usable]
    sub = df[cols].apply(pd.to_numeric, errors="coerce").dropna()
    if len(sub) < MIN_ROWS_FOR_DISCOVERY:
        return None, (
            f"Kümeleme/PCA/anomali analizi için en az {MIN_ROWS_FOR_DISCOVERY} eksiksiz gözlem "
            f"gerekir (mevcut: {len(sub)})."
        )
    return sub, None


def _run_clustering(sub: pd.DataFrame, X: np.ndarray) -> ClusteringResult | None:
    n_comp = min(5, X.shape[1])
    pca = PCA(n_components=n_comp, random_state=RANDOM_STATE)
    pca.fit(X)
    loadings: list[dict] = []
    for ci in range(pca.n_components_):
        comp = pca.components_[ci]
        top = np.argsort(-np.abs(comp))[:3]
        for idx in top:
            loadings.append({"component": ci + 1, "variable": sub.columns[idx], "loading": float(comp[idx])})

    max_k = min(6, len(sub) // 5)
    best_k, best_score, best_labels = None, -1.0, None
    for k in range(2, max(3, max_k + 1)):
        if k >= len(sub):
            break
        labels = KMeans(n_clusters=k, n_init=10, random_state=RANDOM_STATE).fit_predict(X)
        if len(set(labels)) < 2:
            continue
        score = float(silhouette_score(X, labels))
        if score > best_score:
            best_k, best_score, best_labels = k, score, labels
    if best_labels is None:
        return None

    clusters: list[ClusterProfile] = []
    for cid in range(best_k):
        mask = best_labels == cid
        size = int(mask.sum())
        means = X[mask].mean(axis=0)
        order = np.argsort(-np.abs(means))[:5]
        top_vars = [{"name": sub.columns[i], "mean_z": float(means[i])} for i in order]
        clusters.append(ClusterProfile(cluster_id=cid + 1, size=size, share=size / len(sub), top_variables=top_vars))

    return ClusteringResult(
        k=best_k,
        silhouette=best_score,
        variables_used=list(sub.columns),
        clusters=clusters,
        pca_explained_variance=[float(v) for v in pca.explained_variance_ratio_],
        pca_top_loadings=loadings,
    )


def _run_anomaly(sub: pd.DataFrame, X: np.ndarray) -> AnomalyResult | None:
    if len(sub) < MIN_ROWS_FOR_ANOMALY:
        return None
    contamination = 0.05
    model = IsolationForest(contamination=contamination, random_state=RANDOM_STATE)
    pred = model.fit_predict(X)
    scores = model.score_samples(X)
    flagged = [
        {"row_index": int(sub.index[i]), "score": float(scores[i])}
        for i in np.where(pred == -1)[0]
    ]
    flagged.sort(key=lambda r: r["score"])
    return AnomalyResult(
        n_flagged=len(flagged), contamination=contamination,
        variables_used=list(sub.columns), flagged_rows=flagged[:30],
    )


def _run_mutual_info(
    df: pd.DataFrame, variables: list[VariableInfo], correlation_findings: list[Finding]
) -> list[MutualInfoPair]:
    usable = [v for v in variables if v.role != "exclude" and v.kind in ("continuous", "ordinal", "nominal", "binary")]
    vmap = {v.name: v for v in usable}
    corr_lookup: dict[frozenset, float] = {}
    for f in correlation_findings:
        if f.planned.family == "correlation" and f.error is None and f.statistic is not None and f.planned.iv:
            corr_lookup[frozenset((f.planned.dv, f.planned.iv))] = f.statistic

    pairs: list[MutualInfoPair] = []
    names = [v.name for v in usable]
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            xa = _encode_column(df, a, vmap[a].kind)
            xb = _encode_column(df, b, vmap[b].kind)
            sub = pd.concat([xa.rename("a"), xb.rename("b")], axis=1).dropna()
            if len(sub) < MIN_ROWS_FOR_MI_PAIR:
                continue
            x = sub[["a"]].to_numpy(dtype=float)
            y = sub["b"].to_numpy(dtype=float)
            discrete = vmap[a].kind in ("nominal", "binary")
            try:
                mi = float(mutual_info_regression(x, y, discrete_features=[discrete], random_state=RANDOM_STATE)[0])
            except ValueError:
                continue
            pairs.append(MutualInfoPair(var_a=a, var_b=b, mi=mi, correlation=corr_lookup.get(frozenset((a, b)))))

    if not pairs:
        return []
    threshold = float(np.quantile([p.mi for p in pairs], 0.75))
    for p in pairs:
        p.hidden = p.mi >= threshold and (p.correlation is None or abs(p.correlation) < 0.3)
    pairs.sort(key=lambda p: -p.mi)
    return pairs[:15]


def _run_risk_score(df: pd.DataFrame, variables: list[VariableInfo]) -> tuple[RiskScoreResult | None, str | None]:
    dv_candidates = [v for v in variables if v.role == "dv" and v.kind == "binary"]
    if not dv_candidates:
        return None, None  # kullanıcı ikili bir bağımlı değişken işaretlemedi; sessizce atla
    dv = dv_candidates[0]

    predictor_vars = [
        v for v in variables
        if v.name != dv.name and v.role != "exclude" and v.kind in ("continuous", "ordinal", "binary", "nominal")
    ]
    if len(predictor_vars) < 2:
        return None, f"'{_label(dv)}' için risk skoru hesaplanamadı: yeterli yordayıcı değişken yok."

    # DV değeri (Veri Temizleme'de nominal/binary sütunlar "Kadın"/"Erkek" gibi etiketlere
    # çevrildiği için) kategorik ham değer olarak ele alınır — pd.to_numeric UYGULANMAZ.
    numeric_cols = [v.name for v in predictor_vars if v.kind in ("continuous", "ordinal")]
    cat_cols = [v.name for v in predictor_vars if v.kind in ("nominal", "binary")]
    parts = {dv.name: df[dv.name]}
    for c in numeric_cols:
        parts[c] = pd.to_numeric(df[c], errors="coerce")
    for c in cat_cols:
        parts[c] = df[c]
    sub = pd.DataFrame(parts).dropna()

    y_series = sub[dv.name]
    classes, counts = np.unique(y_series.to_numpy(dtype=object), return_counts=True)
    if len(classes) != 2 or counts.min() < MIN_CLASS_N_FOR_RISK:
        return None, (
            f"'{_label(dv)}' için risk skoru hesaplanamadı: sınıflardan biri çok küçük "
            f"(n<{MIN_CLASS_N_FOR_RISK}) veya değişken ikili değil."
        )

    pos_label = classes.max()
    y = (y_series == pos_label).astype(int).to_numpy()
    pos_display = str(pos_label)

    X_df = sub[numeric_cols + cat_cols].copy()
    if cat_cols:
        X_df = pd.get_dummies(X_df, columns=cat_cols, drop_first=True)
    feature_names = list(X_df.columns)
    X = StandardScaler().fit_transform(X_df.to_numpy(dtype=float))

    n_splits = min(5, int(counts.min()))
    if n_splits < 2:
        return None, f"'{_label(dv)}' için risk skoru hesaplanamadı: çapraz doğrulama için yeterli örneklem yok."
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

    logreg.fit(X, y)
    rf.fit(X, y)
    predictors_out = [
        {
            "name": name,
            "odds_ratio": float(np.exp(logreg.coef_[0][i])),
            "rf_importance": float(rf.feature_importances_[i]),
        }
        for i, name in enumerate(feature_names)
    ]
    predictors_out.sort(key=lambda d: -d["rf_importance"])

    result = RiskScoreResult(
        dv=dv.name, n=len(sub), n_positive=int(y.sum()), positive_class=str(pos_display),
        auc_logreg=auc_lr, auc_rf=auc_rf, predictors=predictors_out[:10],
    )
    return result, None


def run_discovery(
    df: pd.DataFrame,
    variables: list[VariableInfo],
    config: JobConfig,
    correlation_findings: list[Finding],
) -> DiscoveryReport:
    report = DiscoveryReport()

    sub, skip_msg = _numeric_frame(df, variables)
    if sub is None:
        report.skipped_reasons.append(skip_msg)
    else:
        try:
            X = StandardScaler().fit_transform(sub.to_numpy(dtype=float))
        except Exception as exc:  # tekil analizin çökmesi tüm aşamayı düşürmesin
            X = None
            report.skipped_reasons.append(f"Veri standardizasyonu başarısız: {exc}")
        if X is not None:
            try:
                report.clustering = _run_clustering(sub, X)
                if report.clustering is None:
                    report.skipped_reasons.append("Belirgin bir gizli küme yapısı bulunamadı.")
            except Exception as exc:
                report.skipped_reasons.append(f"Kümeleme/PCA hesaplanamadı: {exc}")
            try:
                report.anomalies = _run_anomaly(sub, X)
                if report.anomalies is None:
                    report.skipped_reasons.append(
                        f"Anomali tespiti için yeterli gözlem yok (n<{MIN_ROWS_FOR_ANOMALY})."
                    )
            except Exception as exc:
                report.skipped_reasons.append(f"Anomali tespiti hesaplanamadı: {exc}")

    try:
        report.mutual_info = _run_mutual_info(df, variables, correlation_findings)
    except Exception as exc:
        report.skipped_reasons.append(f"Bilgi teorisi (mutual information) analizi hesaplanamadı: {exc}")

    try:
        risk, skip_reason = _run_risk_score(df, variables)
        report.risk_score = risk
        if skip_reason:
            report.skipped_reasons.append(skip_reason)
    except Exception as exc:
        report.skipped_reasons.append(f"Risk skoru hesaplanamadı: {exc}")

    return report
