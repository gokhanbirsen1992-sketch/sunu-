"""MegaStat Keşif Katmanı — düz korelasyonun ötesi (üniversite/ML düzeyi).

Bu modül, klasik istatistiklerin (Pearson vb.) **bulamadığı** örüntüleri arar:

1. GEREKSİZ/TANIMSAL korelasyon ayıklama — TotalBilirubin↔İndirekBilirubin,
   Insulin↔HomaIR, Kilo↔VKİ gibi "zaten belli" ilişkiler ayrı kutuya konur ki
   gerçek keşifleri boğmasın.
2. DOĞRUSAL-OLMAYAN ilişkiler — Karşılıklı Bilgi (Mutual Information) ile: Pearson'ın
   düşük çıktığı ama değişkenlerin aslında güçlü (eğrisel/eşikli) bağlı olduğu çiftler.
3. ÇOK DEĞİŞKENLİ ÖNGÖRÜ — Gradient Boosting (CatBoost/LightGBM ailesi) ile her hedefi
   diğer tüm değişkenlerden tahmin eder; çapraz doğrulamalı başarı + permütasyon önem
   sıralaması verir. "X'i asıl ne belirliyor?" sorusunun tek-değişkenli olmayan yanıtı.
4. GİZLİ ALT GRUPLAR — PCA + K-Means kümeleme ile veride kendiliğinden oluşan hasta/vaka
   kümelerini bulur ve her kümeyi ayırt eden değişkenleri açıklar.
5. SIRA DIŞI VAKALAR — Isolation Forest ile çok değişkenli aykırı (beklenmedik) kayıtlar.
6. SAHTE vs GERÇEK — Kısmi korelasyon: A↔B ilişkisi üçüncü bir değişken kontrol edilince
   kayboluyor mu (aracılı/sahte) yoksa güçleniyor mu (baskılanmış gizli ilişki)?

Tüm hesaplar sabit random_state ile deterministiktir. Yapay zekâ hiçbir sayı üretmez.
"""
from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from itertools import combinations
from typing import Any, Optional

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.ensemble import (
    HistGradientBoostingClassifier,
    HistGradientBoostingRegressor,
    IsolationForest,
)
from sklearn.feature_selection import mutual_info_regression
from sklearn.inspection import permutation_importance
from sklearn.metrics import roc_auc_score, silhouette_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict, cross_val_score
from sklearn.preprocessing import StandardScaler

RANDOM_STATE = 42
MAX_SATIR_ML = 5000          # daha büyük veride sabit tohumla örneklenir (bellek/hız)
REDUNDANT_ESIK = 0.95        # |r| bu üstüyse "beklenen/tanımsal" say
MIN_SATIR = 25               # keşif için gereken en az gözlem
MAX_GBM_HEDEF = 40           # en çok bu kadar değişken için model kurulur
CV_KAT = 5


def _ornekle(df: pd.DataFrame) -> pd.DataFrame:
    if len(df) > MAX_SATIR_ML:
        return df.sample(MAX_SATIR_ML, random_state=RANDOM_STATE)
    return df


@dataclass
class DiscoveryResult:
    calisti: bool
    neden: str = ""
    gereksiz_korelasyonlar: pd.DataFrame = field(default_factory=pd.DataFrame)
    dogrusal_olmayan: pd.DataFrame = field(default_factory=pd.DataFrame)
    gbm_onem: pd.DataFrame = field(default_factory=pd.DataFrame)
    kumeler: pd.DataFrame = field(default_factory=pd.DataFrame)
    kume_ozet: dict[str, Any] = field(default_factory=dict)
    anomaliler: pd.DataFrame = field(default_factory=pd.DataFrame)
    kismi_korelasyon: pd.DataFrame = field(default_factory=pd.DataFrame)
    risk_modelleri: pd.DataFrame = field(default_factory=pd.DataFrame)
    riskli_vakalar: pd.DataFrame = field(default_factory=pd.DataFrame)
    one_cikanlar: list[str] = field(default_factory=list)


# ── 1 & 2: Doğrusal-olmayan ilişkiler + gereksiz korelasyon ayıklama ──────────
def _mi_ciftler(df: pd.DataFrame, sayisallar: list[str]) -> pd.DataFrame:
    """Her sayısal çift için Pearson + Karşılıklı Bilgi (MI) ve 'doğrusalsızlık farkı'."""
    satirlar = []
    for a, b in combinations(sayisallar, 2):
        cift = df[[a, b]].dropna()
        if len(cift) < MIN_SATIR:
            continue
        x = cift[a].to_numpy(dtype=float)
        y = cift[b].to_numpy(dtype=float)
        if np.std(x) == 0 or np.std(y) == 0:
            continue
        r = float(stats.pearsonr(x, y)[0])
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            mi = float(
                mutual_info_regression(
                    x.reshape(-1, 1), y, random_state=RANDOM_STATE, n_neighbors=3
                )[0]
            )
        # MI'yi korelasyon-eşdeğerine çevir: r_mi = sqrt(1 - e^{-2 MI}) ∈ [0,1)
        r_mi = float(np.sqrt(max(0.0, 1 - np.exp(-2 * mi))))
        fark = r_mi - abs(r)  # büyük pozitif → doğrusalın kaçırdığı gizli ilişki
        satirlar.append({
            "değişken 1": a,
            "değişken 2": b,
            "n": len(cift),
            "Pearson |r|": abs(r),
            "Karşılıklı Bilgi (MI)": mi,
            "MI korelasyon-eşdeğeri": r_mi,
            "doğrusalsızlık farkı": fark,
        })
    return pd.DataFrame(satirlar)


def _iliskileri_ayikla(
    mi_tablo: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """(gereksiz/tanımsal korelasyonlar, gerçek doğrusal-olmayan keşifler)."""
    if mi_tablo.empty:
        return pd.DataFrame(), pd.DataFrame()
    gereksiz = mi_tablo[mi_tablo["Pearson |r|"] >= REDUNDANT_ESIK].copy()
    gereksiz = gereksiz.sort_values("Pearson |r|", ascending=False).reset_index(drop=True)
    if not gereksiz.empty:
        gereksiz["not"] = "beklenen/olası tanımsal ilişki (çok yüksek düz korelasyon)"

    # Gerçek keşif: MI güçlü AMA düz korelasyon zayıf/orta olan çiftler
    keskif = mi_tablo[
        (mi_tablo["MI korelasyon-eşdeğeri"] >= 0.30)
        & (mi_tablo["Pearson |r|"] < REDUNDANT_ESIK)
        & (mi_tablo["doğrusalsızlık farkı"] > 0.10)
    ].copy()
    keskif = keskif.sort_values("doğrusalsızlık farkı", ascending=False).reset_index(drop=True)
    if not keskif.empty:
        keskif["yorum"] = keskif.apply(
            lambda r: "düz korelasyon zayıf ("
            f"|r|={r['Pearson |r|']:.2f}) ama güçlü doğrusal-olmayan ilişki var "
            f"(MI-eşdeğeri={r['MI korelasyon-eşdeğeri']:.2f}) — Pearson bunu kaçırır",
            axis=1,
        )
    return gereksiz, keskif


# ── 3: Gradient Boosting çok değişkenli öngörü + önem ─────────────────────────
def _sayisal_matris(df: pd.DataFrame, sutunlar: list[str]) -> pd.DataFrame:
    """Kategorikleri sayısal kodlara çevirip medyanla doldurur (ML girdisi)."""
    X = pd.DataFrame(index=df.index)
    for s in sutunlar:
        seri = df[s]
        if pd.api.types.is_numeric_dtype(seri):
            X[s] = seri
        else:
            X[s] = seri.astype("category").cat.codes.replace(-1, np.nan)
    return X.fillna(X.median(numeric_only=True))


def _gbm_tarama(
    df: pd.DataFrame,
    sayisallar: list[str],
    kategorikler: list[str],
) -> pd.DataFrame:
    hedefler = (sayisallar + kategorikler)[:MAX_GBM_HEDEF]
    tum = sayisallar + kategorikler
    satirlar = []
    for hedef in hedefler:
        ozellikler = [s for s in tum if s != hedef]
        if len(ozellikler) < 2:
            continue
        alt = df[[hedef] + ozellikler].dropna(subset=[hedef])
        if len(alt) < MIN_SATIR:
            continue
        X = _sayisal_matris(alt, ozellikler)
        y_ham = alt[hedef]
        siniflandirma = hedef in kategorikler
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                if siniflandirma:
                    y = y_ham.astype("category").cat.codes
                    if y.nunique() < 2 or y.value_counts().min() < CV_KAT:
                        continue
                    model = HistGradientBoostingClassifier(random_state=RANDOM_STATE)
                    skorlar = cross_val_score(model, X, y, cv=CV_KAT, scoring="accuracy")
                    metrik_ad, metrik = "doğruluk (CV)", float(np.mean(skorlar))
                    # basit temel: en sık sınıfın oranı
                    temel = float(y.value_counts(normalize=True).max())
                    kazanc = metrik - temel
                else:
                    y = y_ham.astype(float)
                    if y.nunique() < 5:
                        continue
                    model = HistGradientBoostingRegressor(random_state=RANDOM_STATE)
                    skorlar = cross_val_score(model, X, y, cv=CV_KAT, scoring="r2")
                    metrik_ad, metrik = "R² (CV)", float(np.mean(skorlar))
                    temel, kazanc = 0.0, metrik
                model.fit(X, y)
                onem = permutation_importance(
                    model, X, y, n_repeats=5, random_state=RANDOM_STATE
                )
        except Exception:
            continue
        sirali = np.argsort(onem.importances_mean)[::-1]
        ilk = [
            f"{X.columns[i]} ({onem.importances_mean[i]:.3f})"
            for i in sirali[:5]
            if onem.importances_mean[i] > 0
        ]
        satirlar.append({
            "hedef değişken": hedef,
            "problem": "sınıflandırma" if siniflandirma else "regresyon",
            "başarı ölçütü": metrik_ad,
            "başarı": metrik,
            "temel (şans) düzeyi": temel,
            "şansın üstü kazanç": kazanc,
            "en güçlü belirleyiciler (permütasyon önemi)": "; ".join(ilk) if ilk else "belirgin yok",
            "öngörülebilir mi": "EVET ✓" if kazanc >= 0.15 else "zayıf",
        })
    tablo = pd.DataFrame(satirlar)
    if not tablo.empty:
        tablo = tablo.sort_values("şansın üstü kazanç", ascending=False).reset_index(drop=True)
    return tablo


# ── 4: Gizli alt gruplar (kümeleme) ───────────────────────────────────────────
def _kumeleme(df: pd.DataFrame, sayisallar: list[str]) -> tuple[pd.DataFrame, dict[str, Any]]:
    if len(sayisallar) < 3:
        return pd.DataFrame(), {"durum": "kümeleme için en az 3 sayısal değişken gerekir"}
    X = _sayisal_matris(df, sayisallar).dropna()
    if len(X) < max(MIN_SATIR, 20):
        return pd.DataFrame(), {"durum": "kümeleme için yeterli tam gözlem yok"}
    Xs = StandardScaler().fit_transform(X)
    n_bilesen = min(len(sayisallar), 10, Xs.shape[0] - 1)
    Xp = PCA(n_components=n_bilesen, random_state=RANDOM_STATE).fit_transform(Xs)

    en_iyi_k, en_iyi_skor, en_iyi_etiket = None, -1.0, None
    for k in range(2, min(7, len(X) // 10 + 1) or 3):
        if k < 2:
            continue
        etiket = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=10).fit_predict(Xp)
        if len(set(etiket)) < 2:
            continue
        skor = silhouette_score(Xp, etiket)
        if skor > en_iyi_skor:
            en_iyi_k, en_iyi_skor, en_iyi_etiket = k, skor, etiket
    if en_iyi_etiket is None:
        return pd.DataFrame(), {"durum": "anlamlı küme bulunamadı"}

    # Her kümeyi ayırt eden değişkenler: küme ortalamasının genel z-skoru
    genel_ort = X.mean()
    genel_sd = X.std(ddof=0).replace(0, np.nan)
    satirlar = []
    for c in sorted(set(en_iyi_etiket)):
        maske = en_iyi_etiket == c
        z = ((X[maske].mean() - genel_ort) / genel_sd).dropna()
        ayirt = z.reindex(z.abs().sort_values(ascending=False).index).head(5)
        aciklama = "; ".join(
            f"{ad}: {'yüksek' if v > 0 else 'düşük'} ({v:+.2f}sd)" for ad, v in ayirt.items()
        )
        satirlar.append({
            "küme": f"Küme {c + 1}",
            "n": int(maske.sum()),
            "oran %": round(100 * maske.sum() / len(X), 1),
            "ayırt edici özellikler (genel ort.'dan sapma)": aciklama,
        })
    ozet = {
        "küme sayısı": en_iyi_k,
        "silhouette skoru": round(float(en_iyi_skor), 3),
        "kalite": (
            "güçlü" if en_iyi_skor >= 0.5 else "orta" if en_iyi_skor >= 0.25 else "zayıf"
        ),
        "kullanılan gözlem": int(len(X)),
    }
    return pd.DataFrame(satirlar), ozet


# ── 5: Sıra dışı vakalar (çok değişkenli anomali) ─────────────────────────────
def _anomali(df: pd.DataFrame, sayisallar: list[str]) -> pd.DataFrame:
    if len(sayisallar) < 2:
        return pd.DataFrame()
    X = _sayisal_matris(df, sayisallar).dropna()
    if len(X) < MIN_SATIR:
        return pd.DataFrame()
    Xs = StandardScaler().fit_transform(X)
    iso = IsolationForest(random_state=RANDOM_STATE, contamination="auto")
    etiket = iso.fit_predict(Xs)
    skor = iso.score_samples(Xs)  # düşük = daha anormal
    anomali_idx = np.where(etiket == -1)[0]
    if len(anomali_idx) == 0:
        return pd.DataFrame()
    sirali = anomali_idx[np.argsort(skor[anomali_idx])]  # en anormal önce
    genel_ort = X.mean()
    genel_sd = X.std(ddof=0).replace(0, np.nan)
    satirlar = []
    for i in sirali[:25]:
        satir = X.iloc[i]
        z = ((satir - genel_ort) / genel_sd).dropna()
        uc = z.reindex(z.abs().sort_values(ascending=False).index).head(4)
        neden = "; ".join(f"{ad}={satir[ad]:.2f} ({v:+.1f}sd)" for ad, v in uc.items())
        satirlar.append({
            "satır (orijinal indeks)": int(X.index[i]),
            "anomali skoru": round(float(skor[i]), 4),
            "neden sıra dışı": neden,
        })
    return pd.DataFrame(satirlar)


# ── 6: Kısmi korelasyon (sahte vs gerçek) ─────────────────────────────────────
def _kismi_korelasyon(df: pd.DataFrame, sayisallar: list[str]) -> pd.DataFrame:
    if len(sayisallar) < 3:
        return pd.DataFrame()
    X = df[sayisallar].dropna()
    if len(X) < max(MIN_SATIR, len(sayisallar) + 5):
        return pd.DataFrame()
    korr = X.corr().to_numpy()
    try:
        inv = np.linalg.pinv(korr)
    except Exception:
        return pd.DataFrame()
    d = np.sqrt(np.abs(np.diag(inv)))
    with np.errstate(divide="ignore", invalid="ignore"):
        kismi = -inv / np.outer(d, d)
    np.fill_diagonal(kismi, 1.0)
    satirlar = []
    for i, j in combinations(range(len(sayisallar)), 2):
        r0 = float(korr[i, j])
        rp = float(kismi[i, j])
        if np.isnan(rp):
            continue
        dusus = abs(r0) - abs(rp)
        if abs(r0) >= 0.3 and dusus >= 0.2:
            durum = "SAHTE/ARACILI olabilir — başka değişkenler kontrol edilince ilişki zayıflıyor"
        elif abs(rp) - abs(r0) >= 0.2:
            durum = "BASKILANMIŞ — kontrol edilince ilişki güçleniyor (gizli gerçek ilişki)"
        else:
            continue
        satirlar.append({
            "değişken 1": sayisallar[i],
            "değişken 2": sayisallar[j],
            "ham korelasyon r": r0,
            "kısmi korelasyon r": rp,
            "değişim": rp - r0,
            "yorum": durum,
        })
    tablo = pd.DataFrame(satirlar)
    if not tablo.empty:
        tablo = tablo.reindex(
            tablo["değişim"].abs().sort_values(ascending=False).index
        ).reset_index(drop=True)
    return tablo


# ── 7: Risk skoru (ikili sonuçlar için çapraz-doğrulamalı olasılık modeli) ────
MIN_SINIF_N = 10


def _risk_skoru(
    df: pd.DataFrame, sayisallar: list[str], kategorikler: list[str]
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Her İKİLİ kategorik sonuç için: gradient boosting risk modeli.

    Çapraz doğrulamayla her vakaya 'dışarıda bırakılmış' risk olasılığı üretir;
    model gücü AUC ile ölçülür. Nadir sınıf 'riskli sonuç' kabul edilir.
    """
    model_satirlari, vaka_satirlari = [], []
    for hedef in kategorikler:
        alt = df.dropna(subset=[hedef])
        duzeyler = alt[hedef].astype(str).value_counts()
        if len(duzeyler) != 2 or duzeyler.min() < MIN_SINIF_N:
            continue
        pozitif = duzeyler.idxmin()  # nadir sınıf = ilgilenilen (riskli) sonuç
        ozellikler = [s for s in sayisallar + kategorikler if s != hedef]
        if len(ozellikler) < 2:
            continue
        X = _sayisal_matris(alt, ozellikler)
        y = (alt[hedef].astype(str) == pozitif).astype(int).to_numpy()
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                model = HistGradientBoostingClassifier(random_state=RANDOM_STATE)
                cv = StratifiedKFold(n_splits=CV_KAT, shuffle=True, random_state=RANDOM_STATE)
                proba = cross_val_predict(model, X, y, cv=cv, method="predict_proba")[:, 1]
                auc = float(roc_auc_score(y, proba))
                model.fit(X, y)
                onem = permutation_importance(
                    model, X, y, n_repeats=5, random_state=RANDOM_STATE
                )
        except Exception:
            continue
        sirali = np.argsort(onem.importances_mean)[::-1]
        belirleyiciler = "; ".join(
            f"{X.columns[i]} ({onem.importances_mean[i]:.3f})"
            for i in sirali[:5]
            if onem.importances_mean[i] > 0
        )
        model_satirlari.append({
            "sonuç değişkeni": hedef,
            "riskli sınıf": pozitif,
            "n": int(len(alt)),
            "riskli sınıf n": int(duzeyler.min()),
            "AUC (çapraz doğrulama)": auc,
            "model gücü": (
                "mükemmel" if auc >= 0.9 else "iyi" if auc >= 0.8
                else "orta" if auc >= 0.7 else "zayıf"
            ),
            "en güçlü risk belirleyicileri": belirleyiciler or "belirgin yok",
        })
        if auc >= 0.7:  # sadece işe yarar modellerin vaka listesi anlamlı
            en_riskli = np.argsort(proba)[::-1][:10]
            for i in en_riskli:
                vaka_satirlari.append({
                    "sonuç değişkeni": hedef,
                    "satır (orijinal indeks)": int(alt.index[i]),
                    "tahmini risk olasılığı": round(float(proba[i]), 3),
                    "gerçek durum": str(alt[hedef].astype(str).iloc[i]),
                })
    return pd.DataFrame(model_satirlari), pd.DataFrame(vaka_satirlari)


# ── Ana giriş ─────────────────────────────────────────────────────────────────
def kesif_analizi(
    df: pd.DataFrame, sayisallar: list[str], kategorikler: list[str]
) -> DiscoveryResult:
    if len(df) < MIN_SATIR:
        return DiscoveryResult(
            calisti=False,
            neden=f"Keşif katmanı için en az {MIN_SATIR} satır gerekir (veri: {len(df)}).",
        )
    if len(sayisallar) < 2:
        return DiscoveryResult(
            calisti=False, neden="Keşif katmanı için en az 2 sayısal değişken gerekir."
        )
    orn = _ornekle(df)

    mi_tablo = _mi_ciftler(orn, sayisallar)
    gereksiz, dogrusal_olmayan = _iliskileri_ayikla(mi_tablo)
    gbm = _gbm_tarama(orn, sayisallar, kategorikler)
    kumeler, kume_ozet = _kumeleme(orn, sayisallar)
    anomaliler = _anomali(orn, sayisallar)
    kismi = _kismi_korelasyon(orn, sayisallar)
    risk_modelleri, riskli_vakalar = _risk_skoru(orn, sayisallar, kategorikler)

    one_cikan: list[str] = []
    if not dogrusal_olmayan.empty:
        for _, r in dogrusal_olmayan.head(5).iterrows():
            one_cikan.append(
                f"🔗 Gizli doğrusal-olmayan ilişki: {r['değişken 1']} ↔ {r['değişken 2']} "
                f"(düz r={r['Pearson |r|']:.2f} zayıf, MI-eşdeğeri={r['MI korelasyon-eşdeğeri']:.2f})"
            )
    if not gbm.empty:
        for _, r in gbm[gbm["öngörülebilir mi"] == "EVET ✓"].head(5).iterrows():
            one_cikan.append(
                f"🎯 {r['hedef değişken']} çok değişkenli tahmin edilebiliyor "
                f"({r['başarı ölçütü']}={r['başarı']:.2f}); belirleyiciler: "
                f"{r['en güçlü belirleyiciler (permütasyon önemi)']}"
            )
    if not kumeler.empty:
        one_cikan.append(
            f"👥 Veride {kume_ozet.get('küme sayısı')} gizli alt grup bulundu "
            f"(silhouette={kume_ozet.get('silhouette skoru')}, {kume_ozet.get('kalite')})"
        )
    if not kismi.empty:
        for _, r in kismi.head(3).iterrows():
            one_cikan.append(f"⚖️ {r['değişken 1']} ↔ {r['değişken 2']}: {r['yorum']}")
    if not risk_modelleri.empty:
        for _, r in risk_modelleri[risk_modelleri["AUC (çapraz doğrulama)"] >= 0.7].iterrows():
            one_cikan.append(
                f"🩺 Risk modeli: '{r['sonuç değişkeni']}={r['riskli sınıf']}' "
                f"AUC={r['AUC (çapraz doğrulama)']:.2f} ({r['model gücü']}); "
                f"belirleyiciler: {r['en güçlü risk belirleyicileri']}"
            )
    if not anomaliler.empty:
        one_cikan.append(f"🚩 {len(anomaliler)} sıra dışı (çok değişkenli aykırı) vaka işaretlendi")

    return DiscoveryResult(
        calisti=True,
        gereksiz_korelasyonlar=gereksiz,
        dogrusal_olmayan=dogrusal_olmayan,
        gbm_onem=gbm,
        kumeler=kumeler,
        kume_ozet=kume_ozet,
        anomaliler=anomaliler,
        kismi_korelasyon=kismi,
        risk_modelleri=risk_modelleri,
        riskli_vakalar=riskli_vakalar,
        one_cikanlar=one_cikan,
    )
