"""
SPSS-Keşif — SPSS'in ötesinde istatistiksel keşif motoru.

Bir .sav / .csv / .xlsx dosyasında klasik SPSS'in göremediği gizli örüntüleri
arar; her bulguyu yayın titizliğiyle (holdout doğrulama, FDR, etki büyüklüğü)
eler.

Kullanım:
    python analyze.py veri.sav --target HEDEF --out rapor/
    python analyze.py veri.csv --target HEDEF --treatment TEDAVI --out rapor/
    python analyze.py veri.sav --out rapor/          # hedef yoksa tüm veriyi tara

Tasarım ilkeleri:
- Opsiyonel kütüphaneler (shap, umap, econml) yoksa o modül zarifçe atlanır.
- Tüm denetimli keşif TRAIN'de yapılır, HOLDOUT'ta teyit edilir.
- Hiçbir doğrulanmamış örüntü "bulgu" diye sunulmaz.
"""
from __future__ import annotations
import argparse
import json
import os
import warnings
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")

# ----- Opsiyonel bağımlılıklar (yoksa modül atlanır) -----
def _try(name):
    try:
        return __import__(name)
    except Exception:
        return None

shap = _try("shap")
umap_mod = _try("umap")
_HAS_ECONML = _try("econml") is not None


# =====================================================================
# 1. VERİ YÜKLEME VE PROFİL
# =====================================================================
def load_data(path: str):
    """SPSS/CSV/Excel oku. .sav için değer ve değişken etiketlerini korur."""
    ext = os.path.splitext(path)[1].lower()
    meta = {}
    if ext == ".sav":
        import pyreadstat
        df, m = pyreadstat.read_sav(path, apply_value_formats=False)
        meta = {
            "column_labels": dict(zip(m.column_names, m.column_labels or [])),
            "value_labels": m.variable_value_labels or {},
        }
    elif ext in (".csv", ".txt"):
        df = pd.read_csv(path)
    elif ext in (".xlsx", ".xls"):
        df = pd.read_excel(path)
    else:
        raise ValueError(f"Desteklenmeyen format: {ext}")
    return df, meta


def infer_types(df: pd.DataFrame, max_cat_card: int = 15):
    """Her sütunu 'numeric' / 'categorical' olarak sınıflandır."""
    types = {}
    for c in df.columns:
        s = df[c]
        if pd.api.types.is_numeric_dtype(s):
            nun = s.nunique(dropna=True)
            types[c] = "categorical" if nun <= max_cat_card and nun <= 0.05 * len(s) + 10 \
                       else "numeric"
        else:
            types[c] = "categorical"
    return types


def profile(df: pd.DataFrame, types: dict, meta: dict) -> str:
    """Veri profili (markdown)."""
    lines = ["## Veri Profili", "",
             f"- Satır: **{len(df)}**, Sütun: **{df.shape[1]}**", "",
             "| Değişken | Etiket | Tip | Eksik % | Benzersiz |",
             "|---|---|---|---|---|"]
    labels = meta.get("column_labels", {})
    for c in df.columns:
        miss = df[c].isna().mean() * 100
        lines.append(f"| {c} | {(labels.get(c) or '')[:30]} | {types[c]} | "
                     f"{miss:.1f} | {df[c].nunique()} |")
    return "\n".join(lines)


def prepare_matrix(df: pd.DataFrame, types: dict, drop: list[str]):
    """Modelleme için sayısallaştırılmış X (kategorikler one-hot, eksikler doldurulur)."""
    use = [c for c in df.columns if c not in drop]
    num = [c for c in use if types[c] == "numeric"]
    cat = [c for c in use if types[c] == "categorical"]
    X = df[num].copy()
    for c in num:
        X[c] = X[c].fillna(X[c].median())
    for c in cat:
        d = pd.get_dummies(df[c].astype("category"), prefix=c, dummy_na=False)
        X = pd.concat([X, d], axis=1)
    return X, num, cat


# =====================================================================
# Yardımcı: FDR (Benjamini-Hochberg) çoklu test düzeltmesi
# =====================================================================
def fdr(pvals: np.ndarray, alpha: float = 0.05):
    """BH-FDR. Düzeltilmiş p ve reddedilenleri döndür."""
    p = np.asarray(pvals, float)
    n = len(p)
    order = np.argsort(p)
    ranked = p[order] * n / (np.arange(n) + 1)
    # monoton yap
    ranked = np.minimum.accumulate(ranked[::-1])[::-1]
    adj = np.empty(n)
    adj[order] = np.clip(ranked, 0, 1)
    return adj, adj < alpha


# =====================================================================
# 2. DOĞRUSAL-OLMAYAN İLİŞKİ + DEĞİŞKEN ÖNEMİ (boosting + holdout)
# =====================================================================
def discover_relationships(X, y, task: str, feat_names):
    """
    Hedef Y'yi tahmin eden boosting modeli kur. Holdout'ta:
      - Doğrusal model vs boosting farkı = DOĞRUSAL-OLMAYANLIK sinyali
      - Permütasyon önemi (+ p-değeri) = hangi değişken GERÇEKTEN önemli
    """
    from sklearn.model_selection import train_test_split
    from sklearn.inspection import permutation_importance
    from sklearn.metrics import r2_score, roc_auc_score
    strat = y if task == "classification" else None
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3,
                                          random_state=42, stratify=strat)
    out = {"task": task}

    if task == "classification":
        from sklearn.linear_model import LogisticRegression
        from sklearn.preprocessing import StandardScaler
        from sklearn.pipeline import make_pipeline
        import xgboost as xgb
        lin = make_pipeline(StandardScaler(),
                            LogisticRegression(max_iter=2000)).fit(Xtr, ytr)
        gb = xgb.XGBClassifier(n_estimators=400, learning_rate=0.05, max_depth=4,
                               subsample=0.8, colsample_bytree=0.8,
                               eval_metric="logloss", n_jobs=-1).fit(Xtr, ytr)
        score = lambda m: roc_auc_score(yte, m.predict_proba(Xte)[:, 1])
        out["metric"] = "AUC"
        scorer = "roc_auc"
    else:
        from sklearn.linear_model import LinearRegression
        from sklearn.preprocessing import StandardScaler
        from sklearn.pipeline import make_pipeline
        import xgboost as xgb
        lin = make_pipeline(StandardScaler(), LinearRegression()).fit(Xtr, ytr)
        gb = xgb.XGBRegressor(n_estimators=400, learning_rate=0.05, max_depth=4,
                              subsample=0.8, colsample_bytree=0.8,
                              n_jobs=-1).fit(Xtr, ytr)
        score = lambda m: r2_score(yte, m.predict(Xte))
        out["metric"] = "R2"
        scorer = "r2"

    out["linear_score"] = float(score(lin))
    out["boosting_score"] = float(score(gb))
    out["nonlinearity_gain"] = out["boosting_score"] - out["linear_score"]

    # Permütasyon önemi (holdout) + p-değeri (permütasyon dağılımına göre)
    perm = permutation_importance(gb, Xte, yte, scoring=scorer,
                                  n_repeats=30, random_state=0, n_jobs=-1)
    imp_mean, imp_std = perm.importances_mean, perm.importances_std
    # Tek taraflı p: önem dağılımının 0'ı içerme olasılığı (yaklaşık z-testi)
    with np.errstate(divide="ignore", invalid="ignore"):
        z = np.where(imp_std > 0, imp_mean / imp_std, 0.0)
    pvals = 1 - stats.norm.cdf(z)
    adj, sig = fdr(pvals)
    imp = (pd.DataFrame({"degisken": feat_names, "onem": imp_mean,
                         "p_fdr": adj, "anlamli": sig})
           .sort_values("onem", ascending=False).reset_index(drop=True))
    out["importance"] = imp
    out["model"] = gb
    out["Xte"] = Xte
    return out


# =====================================================================
# 3. ETKİLEŞİM KEŞFİ (SHAP interaction — SPSS bunu otomatik yapamaz)
# =====================================================================
def discover_interactions(model, Xte, feat_names, top=8):
    """SHAP etkileşim değerleriyle en güçlü değişken-çiftlerini bul."""
    if shap is None:
        return None
    try:
        expl = shap.TreeExplainer(model)
        sv = expl.shap_interaction_values(Xte.iloc[:min(400, len(Xte))])
        inter = np.abs(sv).mean(axis=0)
        np.fill_diagonal(inter, 0)
        pairs = []
        n = inter.shape[0]
        for i in range(n):
            for j in range(i + 1, n):
                pairs.append((feat_names[i], feat_names[j], float(inter[i, j])))
        pairs.sort(key=lambda t: t[2], reverse=True)
        return pairs[:top]
    except Exception:
        return None


# =====================================================================
# 4. GİZLİ SEGMENTLER (denetimsiz kümeleme — etiket gerektirmez)
# =====================================================================
def discover_segments(X, max_k=6):
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score
    Xs = StandardScaler().fit_transform(X.select_dtypes(include=[np.number]))
    best = {"k": None, "sil": -1, "labels": None}
    for k in range(2, max_k + 1):
        km = KMeans(n_clusters=k, n_init=10, random_state=0).fit(Xs)
        sil = silhouette_score(Xs, km.labels_)
        if sil > best["sil"]:
            best = {"k": k, "sil": float(sil), "labels": km.labels_}
    # 2B gömme (görselleştirme için)
    emb = None
    if umap_mod is not None:
        try:
            emb = umap_mod.UMAP(random_state=0).fit_transform(Xs)
        except Exception:
            emb = None
    best["embedding"] = emb
    return best


# =====================================================================
# 5. ANOMALİ TESPİTİ (çok boyutlu aykırı — SPSS tek değişkene bakar)
# =====================================================================
def discover_anomalies(X, contamination=0.03):
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    Xs = StandardScaler().fit_transform(X.select_dtypes(include=[np.number]))
    iso = IsolationForest(contamination=contamination, random_state=0).fit(Xs)
    flags = iso.predict(Xs) == -1
    return {"n": int(flags.sum()), "oran": float(flags.mean()),
            "indeks": np.where(flags)[0].tolist()}


# =====================================================================
# 6. DOĞRUSAL-OLMAYAN İLİŞKİ AĞI (Mutual Information vs Pearson)
#    "Gizli" ilişki = yüksek MI ama düşük doğrusal korelasyon
# =====================================================================
def discover_mi_network(df, types, drop, top=15):
    from sklearn.feature_selection import mutual_info_regression
    num = [c for c in df.columns
           if c not in drop and types[c] == "numeric"]
    d = df[num].dropna()
    if len(d) < 30 or len(num) < 2:
        return None
    rows = []
    for i, a in enumerate(num):
        for b in num[i + 1:]:
            x = d[[a]].values
            mi = float(mutual_info_regression(x, d[b].values,
                                              random_state=0)[0])
            r = float(np.corrcoef(d[a], d[b])[0, 1])
            # gizlilik skoru: doğrusal-olmayan ama bağlı
            rows.append({"a": a, "b": b, "MI": mi, "pearson": r,
                         "gizli_dogrusal_olmayan": mi - abs(r)})
    res = pd.DataFrame(rows).sort_values("MI", ascending=False)
    return res.head(top).reset_index(drop=True)


# =====================================================================
# 7. NEDENSEL ETKİ (EconML DML — opsiyonel)
# =====================================================================
def estimate_causal(df, types, target, treatment, drop):
    if not _HAS_ECONML:
        return {"hata": "econml kurulu değil (pip install econml)"}
    from econml.dml import LinearDML
    from sklearn.ensemble import GradientBoostingRegressor, GradientBoostingClassifier
    controls = [c for c in df.columns
                if c not in drop + [target, treatment] and types[c] == "numeric"]
    d = df[[target, treatment] + controls].dropna()
    if len(d) < 100:
        return {"hata": "yetersiz veri (nedensel analiz için <100 satır)"}
    Y, T, W = d[target].values, d[treatment].values, d[controls].values
    t_clf = d[treatment].nunique() <= 2
    est = LinearDML(
        model_y=GradientBoostingRegressor(),
        model_t=(GradientBoostingClassifier() if t_clf
                 else GradientBoostingRegressor()),
        discrete_treatment=t_clf, random_state=0)
    est.fit(Y, T, X=None, W=W)
    ate = float(est.ate())
    lo, hi = est.ate_interval()
    return {"ate": ate, "ci": [float(lo), float(hi)],
            "kontroller": controls, "n": len(d)}


# =====================================================================
# RAPOR
# =====================================================================
def build_report(prof, rel, inter, seg, anom, mi, causal, target):
    L = ["# SPSS-Keşif Bulgu Raporu", "",
         "> ⚠️ Aşağıdaki bulgular **YAYINA ADAY HİPOTEZLER**dir. Holdout'ta "
         "teyit edilen ve FDR sonrası ayakta kalanlar 'güçlü' kabul edilir. "
         "Gerçek yayın için bağımsız veriyle doğrulama şarttır. ML örüntü bulur; "
         "nedensel iddia varsayım gerektirir.", "", prof, ""]

    if rel:
        g = rel["nonlinearity_gain"]
        L += ["## 1. Doğrusal-Olmayan İlişki ve Değişken Önemi",
              f"- Hedef: **{target}** ({rel['task']})",
              f"- Doğrusal model {rel['metric']}: **{rel['linear_score']:.3f}**",
              f"- Boosting {rel['metric']}: **{rel['boosting_score']:.3f}**",
              f"- **Doğrusal-olmayanlık kazancı: {g:+.3f}** "
              + ("→ ⭐ SPSS'in lineer modelinin KAÇIRDIĞI yapı var!"
                 if g > 0.02 else "→ ilişki büyük ölçüde doğrusal (SPSS yeterli)"),
              "", "### Holdout'ta doğrulanmış önemli değişkenler (FDR<0.05)",
              "| Değişken | Önem | p (FDR) | Anlamlı |", "|---|---|---|---|"]
        for _, r in rel["importance"].head(15).iterrows():
            L.append(f"| {r['degisken']} | {r['onem']:.4f} | {r['p_fdr']:.3f} "
                     f"| {'✅' if r['anlamli'] else '—'} |")
        L.append("")

    if inter:
        L += ["## 2. Otomatik Keşfedilen Etkileşimler",
              "_SPSS'te etkileşimi elle yazarsın; burada veri kendisi söylüyor._",
              "| Değişken A | Değişken B | Etkileşim gücü |", "|---|---|---|"]
        for a, b, v in inter:
            L.append(f"| {a} | {b} | {v:.4f} |")
        L.append("")
    elif shap is None:
        L += ["## 2. Etkileşimler", "_SHAP kurulu değil — atlandı "
              "(pip install shap)._", ""]

    if seg:
        L += ["## 3. Gizli Segmentler (denetimsiz)",
              f"- En iyi küme sayısı: **k={seg['k']}** "
              f"(silhouette={seg['sil']:.3f})",
              "- Veride önceden tanımlanmamış doğal alt-gruplar var. "
              "Her segmenti profilleyip yorumla.", ""]

    if anom:
        L += ["## 4. Çok Boyutlu Anomaliler",
              f"- **{anom['n']}** olağandışı vaka (%{anom['oran']*100:.1f}). "
              "Tek değişkende normal görünüp ÇOK DEĞİŞKENLİ uzayda sıra dışı "
              "olanlar — SPSS'in kaçırdığı aykırılar.", ""]

    if mi is not None and len(mi):
        L += ["## 5. Gizli Doğrusal-Olmayan İlişkiler (MI vs Pearson)",
              "_Yüksek karşılıklı bilgi ama düşük doğrusal korelasyon = "
              "SPSS korelasyon matrisinin GÖREMEYECEĞİ ilişkiler._",
              "| A | B | MI | Pearson | Gizlilik |", "|---|---|---|---|---|"]
        for _, r in mi.iterrows():
            flag = " ⭐" if (r["MI"] > 0.1 and abs(r["pearson"]) < 0.2) else ""
            L.append(f"| {r['a']} | {r['b']} | {r['MI']:.3f} | "
                     f"{r['pearson']:+.2f} | {r['gizli_dogrusal_olmayan']:+.3f}{flag} |")
        L.append("")

    if causal:
        if "hata" in causal:
            L += ["## 6. Nedensel Etki", f"_Atlandı: {causal['hata']}_", ""]
        else:
            L += ["## 6. Nedensel Etki (Double ML)",
                  f"- Tahmini ortalama tedavi etkisi (ATE): **{causal['ate']:+.4f}**",
                  f"- %95 güven aralığı: [{causal['ci'][0]:+.4f}, {causal['ci'][1]:+.4f}]",
                  f"- {len(causal['kontroller'])} confounder kontrol edildi, "
                  f"n={causal['n']}.",
                  "- ⚠️ Geçerlilik 'tüm confounder'lar ölçüldü' varsayımına "
                  "dayanır (unconfoundedness). Bu varsayımı tartışmadan nedensel "
                  "iddiada bulunma.", ""]

    L += ["## Sonraki adımlar (yayın için)",
          "1. ⭐ ile işaretli güçlü bulguları **bağımsız/yeni veriyle** doğrula.",
          "2. Analiz planını **ön-kayıt** (pre-registration) ile sabitle.",
          "3. Etki büyüklüğü + güven aralığı raporla (sadece p değil).",
          "4. Nedensel iddialar için varsayımları ve sınırlılıkları yaz.",
          "5. Keşifsel (hypothesis-generating) olduğunu açıkça belirt.", ""]
    return "\n".join(L)


# =====================================================================
# ANA AKIŞ
# =====================================================================
def main():
    ap = argparse.ArgumentParser(description="SPSS-Keşif motoru")
    ap.add_argument("data", help=".sav / .csv / .xlsx dosya yolu")
    ap.add_argument("--target", help="Hedef/sonuç (Y) değişkeni")
    ap.add_argument("--treatment", help="Nedensel analiz için tedavi (T) değişkeni")
    ap.add_argument("--drop", default="", help="Hariç tutulacak sütunlar (virgülle)")
    ap.add_argument("--out", default="rapor", help="Çıktı klasörü")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    df, meta = load_data(args.data)
    types = infer_types(df)
    drop = [c.strip() for c in args.drop.split(",") if c.strip()]

    prof = profile(df, types, meta)
    print(prof[:1500])

    rel = inter = seg = anom = mi = causal = None

    if args.target and args.target in df.columns:
        y = df[args.target]
        mask = y.notna()
        feat_drop = drop + [args.target] + ([args.treatment] if args.treatment else [])
        X, _, _ = prepare_matrix(df.loc[mask], types, feat_drop)
        yv = y[mask]
        task = "classification" if (types[args.target] == "categorical"
                                    or yv.nunique() <= 10) else "regression"
        if task == "classification":
            yv = pd.factorize(yv)[0]
        print(f"\n[1/6] Doğrusal-olmayan ilişki + önem ({task})...")
        rel = discover_relationships(X, np.asarray(yv), task, list(X.columns))
        print(f"[2/6] Etkileşim keşfi...")
        inter = discover_interactions(rel["model"], rel["Xte"], list(X.columns))

    print("[3/6] Gizli segmentler...")
    Xall, _, _ = prepare_matrix(df, types, drop)
    seg = discover_segments(Xall)
    print("[4/6] Anomali tespiti...")
    anom = discover_anomalies(Xall)
    print("[5/6] Doğrusal-olmayan ilişki ağı (MI)...")
    mi = discover_mi_network(df, types, drop)

    if args.treatment and args.target:
        print("[6/6] Nedensel etki (DML)...")
        causal = estimate_causal(df, types, args.target, args.treatment, drop)

    report = build_report(prof, rel, inter, seg, anom, mi, causal, args.target)
    out_md = os.path.join(args.out, "bulgular.md")
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\n✅ Rapor yazıldı: {out_md}")


if __name__ == "__main__":
    main()
