"""MegaStat gelişmiş klasik istatistik katmanı.

engine.py'nin kapsamadığı, makale/tezlerde sık istenen analizler:

* Eşleştirilmiş testler — her sayısal çift için eşleştirilmiş t + Wilcoxon işaretli sıra
  (aynı satırdaki iki ölçüm; ön-test/son-test tasarımları için)
* Tekrarlı ölçüm — madde gruplarında (örn. madde1..madde5) Friedman + Kendall W
* Uyum — aynı düzeylere sahip kategorik çiftler için Cohen kappa (+ ağırlıklı) ve
  2×2'de McNemar
* Güvenilirlik — madde grupları için Cronbach alfa (+%95 GA), McDonald omega,
  iki-yarı (Spearman-Brown), madde-toplam korelasyonları, silinirse-alfa
* Faktör analizi (AFA) — KMO, Bartlett küresellik, özdeğerler, Kaiser ölçütü,
  varimax döndürülmüş yükler
* Çoklu doğrusal regresyon — her sayısal bağımlı için diğer sayısallarla OLS:
  B, SH, standardize beta, %95 GA, VIF, R², F
* Lojistik regresyon — her ikili kategorik sonuç için sayısal yordayıcılarla
  odds oranları (+%95 GA), McFadden R², AUC
* ROC analizi — her ikili sonuç × sayısal belirteç için AUC (+%95 GA),
  Youden kesim noktası, duyarlılık/özgüllük

engine.py ile aynı ilkeler: sınırsız, deterministik, güvenli (yetersiz örneklem
atlanır ve nedeni raporlanır), dürüst (FDR düzeltmeleri).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from itertools import combinations
from typing import Any, Optional

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from sklearn.metrics import cohen_kappa_score, roc_auc_score, roc_curve
from statsmodels.stats.contingency_tables import mcnemar
from statsmodels.stats.outliers_influence import variance_inflation_factor

from megastat.engine import ALFA, _guvenli, _normallik, _p_duzeltmeleri

MIN_ESLESTIRME_N = 5      # eşleştirilmiş test için en az ortak gözlem
MIN_MADDE = 3             # güvenilirlik / Friedman için en az madde sayısı
MIN_FAKTOR_MADDE = 4      # faktör analizi için en az madde sayısı
MIN_UYUM_N = 10           # kappa / McNemar için en az ortak gözlem
MIN_SINIF_N = 5           # lojistik / ROC'ta her sonuç sınıfında en az gözlem


@dataclass
class AdvancedResult:
    eslestirilmis: pd.DataFrame = field(default_factory=pd.DataFrame)
    friedman: pd.DataFrame = field(default_factory=pd.DataFrame)
    uyum: pd.DataFrame = field(default_factory=pd.DataFrame)
    guvenilirlik: pd.DataFrame = field(default_factory=pd.DataFrame)
    madde_analizi: pd.DataFrame = field(default_factory=pd.DataFrame)
    faktor_uygunluk: pd.DataFrame = field(default_factory=pd.DataFrame)
    faktor_yukler: pd.DataFrame = field(default_factory=pd.DataFrame)
    coklu_regresyon: pd.DataFrame = field(default_factory=pd.DataFrame)
    lojistik: pd.DataFrame = field(default_factory=pd.DataFrame)
    roc: pd.DataFrame = field(default_factory=pd.DataFrame)


# ── Madde grupları (madde1..madde5 gibi ortak önekli sütunlar) ────────────────
def madde_gruplari(sayisallar: list[str]) -> dict[str, list[str]]:
    """Sonu rakamla biten sütunları ortak öneke göre gruplar (ölçek maddeleri)."""
    gruplar: dict[str, list[str]] = {}
    for ad in sayisallar:
        onek = re.sub(r"[\s_\-.]*\d+$", "", str(ad)).strip()
        if onek and onek != str(ad):
            gruplar.setdefault(onek, []).append(ad)
    return {o: k for o, k in gruplar.items() if len(k) >= MIN_MADDE}


# ── Eşleştirilmiş testler ─────────────────────────────────────────────────────
def eslestirilmis_testler(
    df: pd.DataFrame, sayisallar: list[str], atlanan: list[dict[str, str]]
) -> pd.DataFrame:
    satirlar = []
    for a, b in combinations(sayisallar, 2):
        cift = df[[a, b]].dropna()
        n = len(cift)
        if n < MIN_ESLESTIRME_N:
            atlanan.append({"test": f"eşleştirilmiş: {a} × {b}",
                            "neden": f"ortak gözlem n={n} < {MIN_ESLESTIRME_N}"})
            continue
        x = cift[a].to_numpy(dtype=float)
        y = cift[b].to_numpy(dtype=float)
        fark = x - y
        sd_fark = float(np.std(fark, ddof=1))
        if sd_fark == 0:
            atlanan.append({"test": f"eşleştirilmiş: {a} × {b}",
                            "neden": "tüm farklar aynı (test anlamsız)"})
            continue
        t = _guvenli(lambda: dict(zip(("t", "p"), map(float, stats.ttest_rel(x, y)))))
        w = _guvenli(lambda: dict(zip(("W", "p"), map(float, stats.wilcoxon(x, y)))))
        _, norm_p, _ = _normallik(fark)
        farklar_normal = norm_p is not None and norm_p >= ALFA
        d_z = float(np.mean(fark) / sd_fark)
        if farklar_normal and t:
            onerilen, p_onerilen = "eşleştirilmiş t (farklar normal)", t["p"]
        elif w:
            onerilen, p_onerilen = "Wilcoxon işaretli sıra (farklar normal değil)", w["p"]
        else:
            onerilen, p_onerilen = "hesaplanamadı", np.nan
        satirlar.append({
            "ölçüm 1": a,
            "ölçüm 2": b,
            "n (çift)": n,
            "ortalama fark": float(np.mean(fark)),
            "fark std sapma": sd_fark,
            "medyan fark": float(np.median(fark)),
            "farklar normal mi": "evet" if farklar_normal else "hayır",
            "eşleştirilmiş t": t["t"] if t else np.nan,
            "eşleştirilmiş t p": t["p"] if t else np.nan,
            "Wilcoxon W": w["W"] if w else np.nan,
            "Wilcoxon p": w["p"] if w else np.nan,
            "Cohen d_z": d_z,
            "önerilen test": onerilen,
            "önerilen test p": p_onerilen,
        })
    tablo = pd.DataFrame(satirlar)
    if not tablo.empty:
        tablo = _p_duzeltmeleri(tablo, "önerilen test p")
        tablo = tablo.sort_values("önerilen test p").reset_index(drop=True)
    return tablo


# ── Friedman (madde gruplarında tekrarlı ölçüm) ───────────────────────────────
def friedman_testleri(
    df: pd.DataFrame, gruplar: dict[str, list[str]], atlanan: list[dict[str, str]]
) -> pd.DataFrame:
    satirlar = []
    for onek, maddeler in gruplar.items():
        veri = df[maddeler].dropna()
        n, k = len(veri), len(maddeler)
        if n < MIN_UYUM_N:
            atlanan.append({"test": f"Friedman: {onek}", "neden": f"tam gözlem n={n} < {MIN_UYUM_N}"})
            continue
        fr = _guvenli(lambda: dict(zip(
            ("ki2", "p"),
            map(float, stats.friedmanchisquare(*(veri[m].to_numpy(dtype=float) for m in maddeler))),
        )))
        if fr is None:
            atlanan.append({"test": f"Friedman: {onek}", "neden": "hesaplama hatası"})
            continue
        kendall_w = fr["ki2"] / (n * (k - 1)) if n * (k - 1) > 0 else np.nan
        satirlar.append({
            "madde grubu": onek,
            "madde sayısı": k,
            "n (tam gözlem)": n,
            "Friedman ki-kare": fr["ki2"],
            "p": fr["p"],
            "Kendall W (uyum)": float(kendall_w),
            "madde ortalamaları": "; ".join(
                f"{m}: {veri[m].mean():.3f}" for m in maddeler
            ),
        })
    tablo = pd.DataFrame(satirlar)
    if not tablo.empty:
        tablo = _p_duzeltmeleri(tablo, "p")
        tablo = tablo.sort_values("p").reset_index(drop=True)
    return tablo


# ── Uyum: Cohen kappa + McNemar ───────────────────────────────────────────────
def uyum_testleri(
    df: pd.DataFrame, kategorikler: list[str], atlanan: list[dict[str, str]]
) -> pd.DataFrame:
    satirlar = []
    for a, b in combinations(kategorikler, 2):
        cift = df[[a, b]].dropna().astype(str)
        duzey_a, duzey_b = set(cift[a].unique()), set(cift[b].unique())
        if duzey_a != duzey_b:
            continue  # düzey kümeleri farklıysa uyum sorusu anlamsız — sessizce geç
        n = len(cift)
        if n < MIN_UYUM_N:
            atlanan.append({"test": f"uyum (kappa): {a} × {b}",
                            "neden": f"ortak gözlem n={n} < {MIN_UYUM_N}"})
            continue
        etiketler = sorted(duzey_a)
        kappa = _guvenli(lambda: {"k": float(
            cohen_kappa_score(cift[a], cift[b], labels=etiketler))})
        sayisal_duzey = all(re.fullmatch(r"-?\d+(\.\d+)?", e) for e in etiketler)
        agirlikli = _guvenli(lambda: {"k": float(
            cohen_kappa_score(cift[a], cift[b], labels=etiketler, weights="linear"))}) \
            if sayisal_duzey and len(etiketler) > 2 else None
        satir: dict[str, Any] = {
            "değişken 1": a,
            "değişken 2": b,
            "n": n,
            "düzeyler": ", ".join(etiketler),
            "tam uyum %": round(100 * float((cift[a] == cift[b]).mean()), 2),
            "Cohen kappa": kappa["k"] if kappa else np.nan,
            "kappa yorumu": _kappa_yorumu(kappa["k"]) if kappa else "",
            "ağırlıklı kappa (doğrusal)": agirlikli["k"] if agirlikli else np.nan,
        }
        if len(etiketler) == 2:
            def _mcnemar():
                tablo = pd.crosstab(cift[a], cift[b]).reindex(
                    index=etiketler, columns=etiketler, fill_value=0)
                uyumsuz = int(tablo.iloc[0, 1] + tablo.iloc[1, 0])
                sonuc = mcnemar(tablo.to_numpy(), exact=uyumsuz < 25)
                return {"ist": float(sonuc.statistic), "p": float(sonuc.pvalue)}
            mn = _guvenli(_mcnemar)
            satir["McNemar istatistiği"] = mn["ist"] if mn else np.nan
            satir["McNemar p"] = mn["p"] if mn else np.nan
        else:
            satir["McNemar istatistiği"] = np.nan
            satir["McNemar p"] = np.nan
        satirlar.append(satir)
    tablo = pd.DataFrame(satirlar)
    if not tablo.empty and tablo["McNemar p"].notna().any():
        tablo = _p_duzeltmeleri(tablo, "McNemar p")
    if not tablo.empty:
        tablo = tablo.sort_values("Cohen kappa", ascending=False).reset_index(drop=True)
    return tablo


def _kappa_yorumu(k: float) -> str:
    if k < 0.2:
        return "zayıf"
    if k < 0.4:
        return "vasat"
    if k < 0.6:
        return "orta"
    if k < 0.8:
        return "iyi"
    return "çok iyi"


# ── Güvenilirlik: Cronbach alfa, omega, madde analizi ────────────────────────
def _cronbach_alfa(X: np.ndarray) -> float:
    k = X.shape[1]
    toplam_var = float(np.var(X.sum(axis=1), ddof=1))
    if toplam_var == 0 or k < 2:
        return np.nan
    return float(k / (k - 1) * (1 - np.var(X, axis=0, ddof=1).sum() / toplam_var))


def _alfa_guven_araligi(alfa: float, n: int, k: int) -> tuple[float, float]:
    """Feldt (1965) F-dağılımı yöntemiyle %95 GA."""
    if not np.isfinite(alfa) or n < 3 or k < 2:
        return np.nan, np.nan
    df1, df2 = n - 1, (n - 1) * (k - 1)
    alt = 1 - (1 - alfa) * stats.f.ppf(0.975, df1, df2)
    ust = 1 - (1 - alfa) * stats.f.ppf(0.025, df1, df2)
    return float(alt), float(ust)


def _mcdonald_omega(X: np.ndarray) -> float:
    """Tek faktörlü modelin ilk temel bileşen yükleriyle omega yaklaşımı."""
    try:
        R = np.corrcoef(X.T)
        ozdeger, ozvektor = np.linalg.eigh(R)
        yukler = ozvektor[:, -1] * np.sqrt(max(ozdeger[-1], 0))
        if np.sum(yukler) < 0:  # işaret belirsizliği: çoğunluk pozitif olsun
            yukler = -yukler
        pay = float(np.sum(yukler)) ** 2
        payda = pay + float(np.sum(1 - np.clip(yukler, -1, 1) ** 2))
        return float(pay / payda) if payda > 0 else np.nan
    except Exception:
        return np.nan


def guvenilirlik_analizi(
    df: pd.DataFrame,
    sayisallar: list[str],
    gruplar: dict[str, list[str]],
    atlanan: list[dict[str, str]],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """(güvenilirlik özeti, madde analizi) tabloları."""
    hedefler = dict(gruplar)
    if len(sayisallar) >= MIN_MADDE:
        hedefler["(tüm sayısal değişkenler — keşif amaçlı)"] = list(sayisallar)
    ozet_satirlar, madde_satirlar = [], []
    for onek, maddeler in hedefler.items():
        veri = df[maddeler].dropna()
        n, k = len(veri), len(maddeler)
        if n < MIN_UYUM_N:
            atlanan.append({"test": f"güvenilirlik: {onek}",
                            "neden": f"tam gözlem n={n} < {MIN_UYUM_N}"})
            continue
        X = veri.to_numpy(dtype=float)
        alfa = _cronbach_alfa(X)
        ga_alt, ga_ust = _alfa_guven_araligi(alfa, n, k)
        omega = _mcdonald_omega(X)
        # İki-yarı: tek/çift sıralı maddeler + Spearman-Brown
        yarim1, yarim2 = X[:, 0::2].sum(axis=1), X[:, 1::2].sum(axis=1)
        iki_yari = _guvenli(lambda: {"r": float(stats.pearsonr(yarim1, yarim2)[0])})
        sb = (2 * iki_yari["r"] / (1 + iki_yari["r"])) if iki_yari and iki_yari["r"] > -1 else np.nan
        ozet_satirlar.append({
            "madde grubu": onek,
            "madde sayısı": k,
            "n (tam gözlem)": n,
            "Cronbach alfa": alfa,
            "alfa %95 GA alt": ga_alt,
            "alfa %95 GA üst": ga_ust,
            "alfa yorumu": _alfa_yorumu(alfa),
            "McDonald omega": omega,
            "iki-yarı r": iki_yari["r"] if iki_yari else np.nan,
            "Spearman-Brown": float(sb) if sb == sb else np.nan,
        })
        toplam = X.sum(axis=1)
        for i, madde in enumerate(maddeler):
            digerleri_toplam = toplam - X[:, i]
            mt = _guvenli(lambda: {"r": float(stats.pearsonr(X[:, i], digerleri_toplam)[0])})
            silinirse = _cronbach_alfa(np.delete(X, i, axis=1)) if k > 2 else np.nan
            madde_satirlar.append({
                "madde grubu": onek,
                "madde": madde,
                "ortalama": float(np.mean(X[:, i])),
                "std sapma": float(np.std(X[:, i], ddof=1)),
                "düzeltilmiş madde-toplam r": mt["r"] if mt else np.nan,
                "silinirse alfa": silinirse,
                "silinirse alfa artar mı": (
                    "EVET — maddeyi gözden geçirin"
                    if np.isfinite(silinirse) and np.isfinite(alfa) and silinirse > alfa else "hayır"
                ),
            })
    return pd.DataFrame(ozet_satirlar), pd.DataFrame(madde_satirlar)


def _alfa_yorumu(alfa: float) -> str:
    if not np.isfinite(alfa):
        return ""
    if alfa < 0.5:
        return "kabul edilemez"
    if alfa < 0.6:
        return "zayıf"
    if alfa < 0.7:
        return "sorgulanabilir"
    if alfa < 0.8:
        return "kabul edilebilir"
    if alfa < 0.9:
        return "iyi"
    return "mükemmel"


# ── Faktör analizi (AFA) ──────────────────────────────────────────────────────
def _kmo(R: np.ndarray) -> float:
    """Kaiser-Meyer-Olkin örneklem uygunluğu ölçüsü (anti-imaj kısmi korelasyonlarla)."""
    ters = np.linalg.pinv(R)
    d = np.sqrt(np.abs(np.diag(ters)))
    kismi = -ters / np.outer(d, d)
    np.fill_diagonal(kismi, 0)
    R0 = R.copy()
    np.fill_diagonal(R0, 0)
    pay = float(np.sum(R0 ** 2))
    payda = pay + float(np.sum(kismi ** 2))
    return pay / payda if payda > 0 else np.nan


def _bartlett(R: np.ndarray, n: int) -> tuple[float, int, float]:
    p = R.shape[0]
    isaret, log_det = np.linalg.slogdet(R)
    if isaret <= 0:
        return np.nan, p * (p - 1) // 2, np.nan
    ki2 = -(n - 1 - (2 * p + 5) / 6) * log_det
    sd = p * (p - 1) // 2
    return float(ki2), sd, float(stats.chi2.sf(ki2, sd))


def _varimax(Y: np.ndarray, en_fazla_iter: int = 100, tol: float = 1e-8) -> np.ndarray:
    p, k = Y.shape
    R = np.eye(k)
    d_eski = 0.0
    for _ in range(en_fazla_iter):
        L = Y @ R
        u, s, vt = np.linalg.svd(
            Y.T @ (L ** 3 - (1.0 / p) * L @ np.diag(np.sum(L ** 2, axis=0)))
        )
        R = u @ vt
        d_yeni = float(np.sum(s))
        if d_yeni <= d_eski * (1 + tol):
            break
        d_eski = d_yeni
    return Y @ R


def faktor_analizi(
    df: pd.DataFrame,
    sayisallar: list[str],
    gruplar: dict[str, list[str]],
    atlanan: list[dict[str, str]],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """(uygunluk/özet, döndürülmüş yükler) tabloları."""
    hedefler = {o: m for o, m in gruplar.items() if len(m) >= MIN_FAKTOR_MADDE}
    if not hedefler and len(sayisallar) >= MIN_FAKTOR_MADDE:
        hedefler = {"(tüm sayısal değişkenler)": list(sayisallar)}
    uygunluk_satirlar, yuk_satirlar = [], []
    for onek, maddeler in hedefler.items():
        veri = df[maddeler].dropna()
        n, k = len(veri), len(maddeler)
        if n < max(20, 3 * k):
            atlanan.append({"test": f"faktör analizi: {onek}",
                            "neden": f"tam gözlem n={n} < gereken {max(20, 3 * k)} (3×madde)"})
            continue
        X = veri.to_numpy(dtype=float)
        sd = np.std(X, axis=0, ddof=1)
        if np.any(sd == 0):
            atlanan.append({"test": f"faktör analizi: {onek}", "neden": "sabit madde var"})
            continue
        R = np.corrcoef(X.T)
        kmo = _kmo(R)
        bart_ki2, bart_sd, bart_p = _bartlett(R, n)
        ozdeger, ozvektor = np.linalg.eigh(R)
        sira = np.argsort(ozdeger)[::-1]
        ozdeger, ozvektor = ozdeger[sira], ozvektor[:, sira]
        n_faktor = max(1, int(np.sum(ozdeger > 1)))
        n_faktor = min(n_faktor, k - 1)
        yukler = ozvektor[:, :n_faktor] * np.sqrt(np.clip(ozdeger[:n_faktor], 0, None))
        if n_faktor >= 2:
            yukler = _varimax(yukler)
        # işaret: her faktörde yüklerin çoğunluğu pozitif olsun
        for f in range(n_faktor):
            if np.sum(yukler[:, f]) < 0:
                yukler[:, f] = -yukler[:, f]
        aciklanan = 100 * np.sum(yukler ** 2, axis=0) / k
        uygunluk_satirlar.append({
            "madde grubu": onek,
            "madde sayısı": k,
            "n (tam gözlem)": n,
            "KMO": float(kmo),
            "KMO yorumu": _kmo_yorumu(kmo),
            "Bartlett ki-kare": bart_ki2,
            "Bartlett sd": bart_sd,
            "Bartlett p": bart_p,
            "faktör sayısı (Kaiser: özdeğer>1)": n_faktor,
            "özdeğerler": "; ".join(f"{o:.3f}" for o in ozdeger[: min(k, 8)]),
            "toplam açıklanan varyans %": float(np.sum(aciklanan)),
        })
        for i, madde in enumerate(maddeler):
            satir: dict[str, Any] = {"madde grubu": onek, "madde": madde}
            for f in range(n_faktor):
                satir[f"Faktör {f + 1}"] = float(yukler[i, f])
            baskin = int(np.argmax(np.abs(yukler[i, :n_faktor])))
            satir["baskın faktör"] = f"Faktör {baskin + 1}"
            satir["ortak varyans (h²)"] = float(np.sum(yukler[i, :n_faktor] ** 2))
            yuk_satirlar.append(satir)
    return pd.DataFrame(uygunluk_satirlar), pd.DataFrame(yuk_satirlar)


def _kmo_yorumu(kmo: float) -> str:
    if not np.isfinite(kmo):
        return ""
    if kmo < 0.5:
        return "kabul edilemez — AFA önerilmez"
    if kmo < 0.6:
        return "zayıf"
    if kmo < 0.7:
        return "vasat"
    if kmo < 0.8:
        return "orta"
    if kmo < 0.9:
        return "iyi"
    return "mükemmel"


# ── Çoklu doğrusal regresyon ─────────────────────────────────────────────────
def coklu_regresyon(
    df: pd.DataFrame, sayisallar: list[str], atlanan: list[dict[str, str]]
) -> pd.DataFrame:
    satirlar = []
    for bagimli in sayisallar:
        yordayicilar = [s for s in sayisallar if s != bagimli]
        p = len(yordayicilar)
        if p < 2:
            continue  # tek yordayıcı zaten Korelasyonlar sayfasındaki basit regresyonda
        veri = df[[bagimli] + yordayicilar].dropna()
        n = len(veri)
        gereken = 5 * p + 10
        if n < gereken:
            atlanan.append({"test": f"çoklu regresyon: {bagimli}",
                            "neden": f"tam gözlem n={n} < gereken {gereken} (5×yordayıcı+10)"})
            continue
        X = veri[yordayicilar]
        sabit_sutunlar = [s for s in yordayicilar if X[s].std(ddof=1) == 0]
        if sabit_sutunlar:
            yordayicilar = [s for s in yordayicilar if s not in sabit_sutunlar]
            X = veri[yordayicilar]
            if len(yordayicilar) < 2:
                continue
        y = veri[bagimli].to_numpy(dtype=float)

        def _ols():
            tasarim = sm.add_constant(X.to_numpy(dtype=float))
            model = sm.OLS(y, tasarim).fit()
            ga = model.conf_int()
            return {"model": model, "ga": ga, "tasarim": tasarim}

        sonuc = _guvenli(_ols)
        if sonuc is None:
            atlanan.append({"test": f"çoklu regresyon: {bagimli}", "neden": "hesaplama hatası"})
            continue
        model, ga, tasarim = sonuc["model"], sonuc["ga"], sonuc["tasarim"]
        sd_y = float(np.std(y, ddof=1))
        for i, ad in enumerate(yordayicilar, start=1):  # 0 = sabit
            vif = _guvenli(lambda: {"v": float(variance_inflation_factor(tasarim, i))})
            sd_x = float(X[ad].std(ddof=1))
            satirlar.append({
                "bağımlı değişken": bagimli,
                "yordayıcı": ad,
                "B": float(model.params[i]),
                "SH": float(model.bse[i]),
                "standardize beta": float(model.params[i] * sd_x / sd_y) if sd_y > 0 else np.nan,
                "t": float(model.tvalues[i]),
                "p": float(model.pvalues[i]),
                "%95 GA alt": float(ga[i][0]),
                "%95 GA üst": float(ga[i][1]),
                "VIF": vif["v"] if vif else np.nan,
                "VIF>5 (çoklu bağlantı)": (
                    "DİKKAT" if vif and vif["v"] > 5 else "hayır" if vif else ""
                ),
                "model R²": float(model.rsquared),
                "model düzeltilmiş R²": float(model.rsquared_adj),
                "model F": float(model.fvalue),
                "model F p": float(model.f_pvalue),
                "model sabiti (B₀)": float(model.params[0]),
                "n": n,
            })
    tablo = pd.DataFrame(satirlar)
    if not tablo.empty:
        tablo = _p_duzeltmeleri(tablo, "p")
        tablo = tablo.sort_values(["bağımlı değişken", "p"]).reset_index(drop=True)
    return tablo


# ── Lojistik regresyon + ROC ─────────────────────────────────────────────────
def _ikili_sonuclar(df: pd.DataFrame, kategorikler: list[str]) -> list[tuple[str, str, pd.Series]]:
    """(değişken, olay düzeyi, 0/1 seri) listesi — tam iki düzeyli kategorikler."""
    sonuclar = []
    for kat in kategorikler:
        s = df[kat].dropna().astype(str)
        duzeyler = s.value_counts()
        if len(duzeyler) != 2 or duzeyler.min() < MIN_SINIF_N:
            continue
        olay = str(duzeyler.index[-1])  # az görülen düzey = olay
        sonuclar.append((kat, olay, (df[kat].astype(str) == olay).where(df[kat].notna())))
    return sonuclar


def lojistik_regresyon(
    df: pd.DataFrame,
    sayisallar: list[str],
    kategorikler: list[str],
    atlanan: list[dict[str, str]],
) -> pd.DataFrame:
    satirlar = []
    for kat, olay, y01 in _ikili_sonuclar(df, kategorikler):
        yordayicilar = list(sayisallar)
        p = len(yordayicilar)
        if p == 0:
            continue
        veri = pd.concat([y01.rename("_olay"), df[yordayicilar]], axis=1).dropna()
        n = len(veri)
        y = veri["_olay"].astype(float).to_numpy()
        olay_n = int(y.sum())
        gereken_n, gereken_olay = 10 * (p + 1), max(MIN_SINIF_N, 5 * p)
        if n < gereken_n or min(olay_n, n - olay_n) < gereken_olay:
            atlanan.append({
                "test": f"lojistik regresyon: {kat}",
                "neden": f"n={n}, olay={olay_n} — gereken n≥{gereken_n} ve her sınıfta ≥{gereken_olay}",
            })
            continue

        def _logit():
            X = sm.add_constant(veri[yordayicilar].to_numpy(dtype=float))
            model = sm.Logit(y, X).fit(disp=0, maxiter=200)
            if not np.all(np.isfinite(model.bse)) or np.any(model.bse > 1e3):
                raise ValueError("ayrışma / kararsız katsayılar")
            return {"model": model, "auc": float(roc_auc_score(y, model.predict(X)))}

        sonuc = _guvenli(_logit)
        if sonuc is None:
            atlanan.append({"test": f"lojistik regresyon: {kat}",
                            "neden": "yakınsama/ayrışma sorunu (tam ayrışan yordayıcı olabilir)"})
            continue
        model, auc = sonuc["model"], sonuc["auc"]
        ga = model.conf_int()
        for i, ad in enumerate(yordayicilar, start=1):
            satirlar.append({
                "sonuç değişkeni": kat,
                "olay (1) düzeyi": olay,
                "yordayıcı": ad,
                "B": float(model.params[i]),
                "SH": float(model.bse[i]),
                "odds oranı (OR)": float(np.exp(model.params[i])),
                "OR %95 GA alt": float(np.exp(ga[i][0])),
                "OR %95 GA üst": float(np.exp(ga[i][1])),
                "p": float(model.pvalues[i]),
                "model McFadden R²": float(model.prsquared),
                "model AUC": auc,
                "n": n,
                "olay n": olay_n,
            })
    tablo = pd.DataFrame(satirlar)
    if not tablo.empty:
        tablo = _p_duzeltmeleri(tablo, "p")
        tablo = tablo.sort_values(["sonuç değişkeni", "p"]).reset_index(drop=True)
    return tablo


def roc_analizi(
    df: pd.DataFrame,
    sayisallar: list[str],
    kategorikler: list[str],
    atlanan: list[dict[str, str]],
) -> pd.DataFrame:
    satirlar = []
    for kat, olay, y01 in _ikili_sonuclar(df, kategorikler):
        for say in sayisallar:
            veri = pd.concat([y01.rename("_olay"), df[say]], axis=1).dropna()
            y = veri["_olay"].astype(int).to_numpy()
            x = veri[say].to_numpy(dtype=float)
            n1, n0 = int(y.sum()), int(len(y) - y.sum())
            if min(n1, n0) < MIN_SINIF_N:
                atlanan.append({"test": f"ROC: {kat} ~ {say}",
                                "neden": f"sınıf boyutları yetersiz (olay={n1}, olay-değil={n0})"})
                continue
            if np.std(x) == 0:
                atlanan.append({"test": f"ROC: {kat} ~ {say}", "neden": "belirteç sabit"})
                continue
            ham_auc = _guvenli(lambda: {"a": float(roc_auc_score(y, x))})
            if ham_auc is None:
                continue
            yon = "yüksek değer olayı yordar" if ham_auc["a"] >= 0.5 else "düşük değer olayı yordar"
            skor = x if ham_auc["a"] >= 0.5 else -x
            auc = max(ham_auc["a"], 1 - ham_auc["a"])
            # Hanley-McNeil güven aralığı
            q1 = auc / (2 - auc)
            q2 = 2 * auc ** 2 / (1 + auc)
            se = np.sqrt(
                (auc * (1 - auc) + (n1 - 1) * (q1 - auc ** 2) + (n0 - 1) * (q2 - auc ** 2))
                / (n1 * n0)
            )
            fpr, tpr, esikler = roc_curve(y, skor)
            j = int(np.argmax(tpr - fpr))
            kesim = esikler[j] if ham_auc["a"] >= 0.5 else -esikler[j]
            mw = _guvenli(lambda: {"p": float(stats.mannwhitneyu(x[y == 1], x[y == 0]).pvalue)})
            satirlar.append({
                "sonuç değişkeni": kat,
                "olay (1) düzeyi": olay,
                "belirteç": say,
                "n (olay/değil)": f"{n1}/{n0}",
                "AUC": float(auc),
                "AUC %95 GA alt": float(max(0.0, auc - 1.96 * se)),
                "AUC %95 GA üst": float(min(1.0, auc + 1.96 * se)),
                "AUC yorumu": _auc_yorumu(auc),
                "yön": yon,
                "Youden kesim noktası": float(kesim),
                "kesimde duyarlılık": float(tpr[j]),
                "kesimde özgüllük": float(1 - fpr[j]),
                "p (Mann-Whitney)": mw["p"] if mw else np.nan,
            })
    tablo = pd.DataFrame(satirlar)
    if not tablo.empty:
        tablo = _p_duzeltmeleri(tablo, "p (Mann-Whitney)")
        tablo = tablo.sort_values("AUC", ascending=False).reset_index(drop=True)
    return tablo


def _auc_yorumu(auc: float) -> str:
    if auc < 0.6:
        return "ayırt edici değil"
    if auc < 0.7:
        return "zayıf"
    if auc < 0.8:
        return "kabul edilebilir"
    if auc < 0.9:
        return "iyi"
    return "mükemmel"


# ── Ana giriş noktası ─────────────────────────────────────────────────────────
def gelismis_analiz(
    df: pd.DataFrame,
    sayisallar: list[str],
    kategorikler: list[str],
    atlanan: list[dict[str, str]],
) -> AdvancedResult:
    # Likert maddeleri (1-5 gibi) az benzersiz değer yüzünden "kategorik" sınıflanır;
    # güvenilirlik / faktör / Friedman için sayı kodlu kategorikler de madde sayılır.
    likert = [k for k in kategorikler if pd.api.types.is_numeric_dtype(df[k])]
    madde_havuzu = list(sayisallar) + likert
    gruplar = madde_gruplari(madde_havuzu)
    guvenilirlik, madde = guvenilirlik_analizi(df, sayisallar, gruplar, atlanan)
    faktor_uygunluk, faktor_yukler = faktor_analizi(df, sayisallar, gruplar, atlanan)
    return AdvancedResult(
        eslestirilmis=eslestirilmis_testler(df, sayisallar, atlanan),
        friedman=friedman_testleri(df, gruplar, atlanan),
        uyum=uyum_testleri(df, kategorikler, atlanan),
        guvenilirlik=guvenilirlik,
        madde_analizi=madde,
        faktor_uygunluk=faktor_uygunluk,
        faktor_yukler=faktor_yukler,
        coklu_regresyon=coklu_regresyon(df, sayisallar, atlanan),
        lojistik=lojistik_regresyon(df, sayisallar, kategorikler, atlanan),
        roc=roc_analizi(df, sayisallar, kategorikler, atlanan),
    )
