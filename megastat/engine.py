"""MegaStat çekirdeği: kapsamlı, sınırsız istatistik hesaplama motoru.

Tasarım ilkeleri:
* SINIRSIZ — mümkün olan her değişken çifti için mümkün olan her test hesaplanır.
* DETERMİNİSTİK — aynı veri her zaman aynı sonucu verir; yapay zekâ yoktur.
* GÜVENLİ — örneklem yetersizse test atlanır ve nedeni raporlanır, program çökmez.
* DÜRÜST — çok sayıda test yapıldığı için tüm p-değerlerine Bonferroni, Holm ve
  Benjamini-Hochberg (FDR) düzeltmeleri uygulanır; ham p tek başına bırakılmaz.
"""
from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from itertools import combinations
from typing import Any, Callable, Optional

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.oneway import anova_oneway

# ── Değişken tipi algılama eşikleri ───────────────────────────────────────────
MAX_KATEGORI_SEVIYESI = 25   # bundan çok seviyesi olan metin sütunu = serbest metin/kimlik, atla
MIN_SAYISAL_BENZERSIZ = 7    # sayısal dtype ama az benzersiz değer → kategorik say (Likert vb.)
MIN_GRUP_N = 3               # bir grupta bundan az gözlem varsa o grup karşılaştırmaya girmez
SHAPIRO_MAX_N = 5000         # Shapiro-Wilk bu boyuta kadar; üstünde D'Agostino kullanılır

ALFA = 0.05


# ── Veri sınıfları ────────────────────────────────────────────────────────────
@dataclass
class Degisken:
    ad: str
    tip: str            # "sayisal" | "kategorik"
    n: int
    eksik: int
    benzersiz: int


@dataclass
class AnalysisResult:
    degiskenler: list[Degisken]
    atlanan_sutunlar: list[dict[str, str]]
    betimsel_sayisal: pd.DataFrame
    betimsel_kategorik: pd.DataFrame
    korelasyonlar: pd.DataFrame
    grup_karsilastirmalari: pd.DataFrame
    posthoc: pd.DataFrame
    kategorik_iliskiler: pd.DataFrame
    atlanan_testler: list[dict[str, str]]
    ozet: dict[str, Any] = field(default_factory=dict)


# ── Yardımcılar ───────────────────────────────────────────────────────────────
def _guvenli(fonk: Callable[[], dict[str, Any]]) -> Optional[dict[str, Any]]:
    """Tek bir istatistiğin hatası tüm analizi durdurmasın."""
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return fonk()
    except Exception:
        return None


def degiskenleri_algila(df: pd.DataFrame) -> tuple[list[Degisken], list[dict[str, str]]]:
    """Her sütunu sayısal / kategorik olarak sınıflar; kullanılamayanları nedeniyle listeler."""
    degiskenler: list[Degisken] = []
    atlanan: list[dict[str, str]] = []
    for ad in df.columns:
        s = df[ad]
        # Metin görünümlü sayı sütunlarını sayıya çevirmeyi dene ("3,5" → 3.5 dahil)
        if s.dtype == object:
            cevrilmis = pd.to_numeric(
                s.astype(str).str.replace(",", ".", regex=False), errors="coerce"
            )
            if cevrilmis.notna().sum() >= 0.9 * s.notna().sum() and s.notna().sum() > 0:
                s = cevrilmis
                df[ad] = s
        n = int(s.notna().sum())
        benzersiz = int(s.dropna().nunique())
        if n == 0:
            atlanan.append({"sutun": ad, "neden": "tüm değerler eksik"})
            continue
        if benzersiz <= 1:
            atlanan.append({"sutun": ad, "neden": "sabit sütun (tek değer)"})
            continue
        if pd.api.types.is_numeric_dtype(s):
            if benzersiz >= MIN_SAYISAL_BENZERSIZ:
                tip = "sayisal"
            else:
                tip = "kategorik"  # 1-2-3-4-5 gibi Likert / kod sütunları
        else:
            if benzersiz > MAX_KATEGORI_SEVIYESI:
                atlanan.append(
                    {"sutun": ad, "neden": f"{benzersiz} farklı metin değeri (serbest metin/kimlik)"}
                )
                continue
            tip = "kategorik"
        if benzersiz == n and tip == "sayisal" and _tam_sayi_dizisi_gibi(s):
            atlanan.append({"sutun": ad, "neden": "her satırda farklı tam sayı (kimlik/sıra no)"})
            continue
        degiskenler.append(
            Degisken(ad=ad, tip=tip, n=n, eksik=int(s.isna().sum()), benzersiz=benzersiz)
        )
    return degiskenler, atlanan


def _tam_sayi_dizisi_gibi(s: pd.Series) -> bool:
    v = s.dropna()
    if not (v % 1 == 0).all():
        return False
    sirali = np.sort(v.to_numpy())
    farklar = np.diff(sirali)
    return bool(len(farklar) > 0 and np.median(farklar) == 1)


# ── Betimsel istatistikler ────────────────────────────────────────────────────
def _normallik(v: np.ndarray) -> tuple[Optional[float], Optional[float], str]:
    """(istatistik, p, test adı) döndürür; örneklem yetersizse (None, None, açıklama)."""
    n = len(v)
    if n < 3:
        return None, None, "n<3, normallik testi yapılamadı"
    if np.ptp(v) == 0:
        return None, None, "tüm değerler aynı, normallik testi anlamsız"
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            if n <= SHAPIRO_MAX_N:
                w, p = stats.shapiro(v)
                return float(w), float(p), "Shapiro-Wilk"
            k2, p = stats.normaltest(v)
            return float(k2), float(p), "D'Agostino K²"
    except Exception:
        return None, None, "normallik testi hesaplanamadı"


def betimsel_sayisal(df: pd.DataFrame, sayisallar: list[str]) -> pd.DataFrame:
    satirlar = []
    for ad in sayisallar:
        v = df[ad].dropna().to_numpy(dtype=float)
        n = len(v)
        if n == 0:
            continue
        ort = float(np.mean(v))
        sd = float(np.std(v, ddof=1)) if n > 1 else 0.0
        se = sd / np.sqrt(n) if n > 0 else np.nan
        if n > 1 and sd > 0:
            t_kritik = stats.t.ppf(0.975, n - 1)
            ci_alt, ci_ust = ort - t_kritik * se, ort + t_kritik * se
        else:
            ci_alt = ci_ust = ort
        q1, med, q3 = (float(x) for x in np.percentile(v, [25, 50, 75]))
        iqr = q3 - q1
        aykiri = int(np.sum((v < q1 - 3 * iqr) | (v > q3 + 3 * iqr))) if iqr > 0 else 0
        norm_ist, norm_p, norm_test = _normallik(v)
        satirlar.append({
            "değişken": ad,
            "n": n,
            "eksik": int(df[ad].isna().sum()),
            "ortalama": ort,
            "std sapma": sd,
            "std hata": float(se),
            "%95 GA alt": float(ci_alt),
            "%95 GA üst": float(ci_ust),
            "medyan": med,
            "Q1": q1,
            "Q3": q3,
            "IQR": iqr,
            "min": float(np.min(v)),
            "maks": float(np.max(v)),
            "aralık": float(np.max(v) - np.min(v)),
            "çarpıklık": float(stats.skew(v)) if n > 2 else np.nan,
            "basıklık": float(stats.kurtosis(v)) if n > 3 else np.nan,
            "varyasyon katsayısı %": (100 * sd / abs(ort)) if ort != 0 else np.nan,
            "aykırı değer (3×IQR)": aykiri,
            "normallik testi": norm_test,
            "normallik istatistiği": norm_ist,
            "normallik p": norm_p,
            "normal dağılıyor mu": (
                "evet" if (norm_p is not None and norm_p >= ALFA)
                else "hayır" if norm_p is not None else "bilinmiyor"
            ),
        })
    return pd.DataFrame(satirlar)


def betimsel_kategorik(df: pd.DataFrame, kategorikler: list[str]) -> pd.DataFrame:
    satirlar = []
    for ad in kategorikler:
        s = df[ad].dropna()
        n = len(s)
        if n == 0:
            continue
        frekans = s.value_counts()
        # Düzeylerin eşit dağılıp dağılmadığı: ki-kare uyum iyiliği
        gof = _guvenli(lambda: {"p": float(stats.chisquare(frekans.to_numpy()).pvalue)})
        for i, (duzey, adet) in enumerate(frekans.items()):
            satirlar.append({
                "değişken": ad if i == 0 else "",
                "düzey": str(duzey),
                "n": int(adet),
                "%": round(100 * adet / n, 2),
                "toplam n": n if i == 0 else None,
                "düzey sayısı": int(frekans.size) if i == 0 else None,
                "eşit dağılım p (ki-kare uyum)": gof["p"] if (gof and i == 0) else None,
            })
    return pd.DataFrame(satirlar)


# ── Sayısal × Sayısal: korelasyonlar ─────────────────────────────────────────
def _pearson_ci(r: float, n: int) -> tuple[float, float]:
    if n < 4 or abs(r) >= 1:
        return np.nan, np.nan
    z = np.arctanh(r)
    se = 1 / np.sqrt(n - 3)
    return float(np.tanh(z - 1.96 * se)), float(np.tanh(z + 1.96 * se))


def korelasyon_taramasi(
    df: pd.DataFrame, sayisallar: list[str], atlanan: list[dict[str, str]]
) -> pd.DataFrame:
    satirlar = []
    for a, b in combinations(sayisallar, 2):
        cift = df[[a, b]].dropna()
        n = len(cift)
        if n < 4:
            atlanan.append({"test": f"korelasyon: {a} × {b}", "neden": f"ortak gözlem n={n} < 4"})
            continue
        x, y = cift[a].to_numpy(dtype=float), cift[b].to_numpy(dtype=float)
        if np.std(x) == 0 or np.std(y) == 0:
            atlanan.append({"test": f"korelasyon: {a} × {b}", "neden": "değişkenlerden biri sabit"})
            continue
        pr = _guvenli(lambda: dict(zip(("r", "p"), map(float, stats.pearsonr(x, y)))))
        sp = _guvenli(lambda: dict(zip(("r", "p"), map(float, stats.spearmanr(x, y)))))
        kd = _guvenli(lambda: dict(zip(("r", "p"), map(float, stats.kendalltau(x, y)))))
        reg = _guvenli(lambda: _dogrusal_regresyon(x, y))
        ci_alt, ci_ust = _pearson_ci(pr["r"], n) if pr else (np.nan, np.nan)
        satirlar.append({
            "değişken 1": a,
            "değişken 2": b,
            "n": n,
            "Pearson r": pr["r"] if pr else np.nan,
            "Pearson p": pr["p"] if pr else np.nan,
            "Pearson %95 GA alt": ci_alt,
            "Pearson %95 GA üst": ci_ust,
            "Spearman rho": sp["r"] if sp else np.nan,
            "Spearman p": sp["p"] if sp else np.nan,
            "Kendall tau": kd["r"] if kd else np.nan,
            "Kendall p": kd["p"] if kd else np.nan,
            "regresyon eğimi": reg["egim"] if reg else np.nan,
            "regresyon sabiti": reg["sabit"] if reg else np.nan,
            "R²": reg["r2"] if reg else np.nan,
            "ilişki gücü": _iliski_gucu(pr["r"]) if pr else "",
        })
    tablo = pd.DataFrame(satirlar)
    if not tablo.empty:
        tablo = _p_duzeltmeleri(tablo, "Pearson p")
        tablo = tablo.sort_values("Pearson p").reset_index(drop=True)
    return tablo


def _dogrusal_regresyon(x: np.ndarray, y: np.ndarray) -> dict[str, float]:
    sonuc = stats.linregress(x, y)
    return {"egim": float(sonuc.slope), "sabit": float(sonuc.intercept), "r2": float(sonuc.rvalue ** 2)}


def _iliski_gucu(r: float) -> str:
    r = abs(r)
    if r < 0.1:
        return "ihmal edilebilir"
    if r < 0.3:
        return "zayıf"
    if r < 0.5:
        return "orta"
    if r < 0.7:
        return "güçlü"
    return "çok güçlü"


# ── Kategorik × Sayısal: grup karşılaştırmaları ──────────────────────────────
def _cohen_d(g1: np.ndarray, g2: np.ndarray) -> float:
    n1, n2 = len(g1), len(g2)
    s_havuz = np.sqrt(
        ((n1 - 1) * np.var(g1, ddof=1) + (n2 - 1) * np.var(g2, ddof=1)) / (n1 + n2 - 2)
    )
    if s_havuz == 0:
        return 0.0
    return float((np.mean(g1) - np.mean(g2)) / s_havuz)


def _hedges_g(d: float, n1: int, n2: int) -> float:
    duzeltme = 1 - 3 / (4 * (n1 + n2) - 9)
    return float(d * duzeltme)


def _etki_yorumu_d(d: float) -> str:
    d = abs(d)
    if d < 0.2:
        return "ihmal edilebilir"
    if d < 0.5:
        return "küçük"
    if d < 0.8:
        return "orta"
    return "büyük"


def grup_karsilastirmalari(
    df: pd.DataFrame,
    kategorikler: list[str],
    sayisallar: list[str],
    atlanan: list[dict[str, str]],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Her kategorik × sayısal çift için tam test bataryası. (ana tablo, post-hoc tablo) döner."""
    satirlar = []
    posthoc_satirlar = []
    for kat in kategorikler:
        for say in sayisallar:
            cift = df[[kat, say]].dropna()
            gruplar_ham = {
                str(d): g[say].to_numpy(dtype=float) for d, g in cift.groupby(kat, observed=True)
            }
            gruplar = {d: v for d, v in gruplar_ham.items() if len(v) >= MIN_GRUP_N}
            kucukler = [d for d, v in gruplar_ham.items() if len(v) < MIN_GRUP_N]
            k = len(gruplar)
            if k < 2:
                atlanan.append({
                    "test": f"grup karşılaştırma: {say} ~ {kat}",
                    "neden": f"n≥{MIN_GRUP_N} olan grup sayısı {k} (<2)",
                })
                continue
            adlar = list(gruplar)
            dizi = [gruplar[d] for d in adlar]
            n_toplam = sum(len(v) for v in dizi)

            # Varsayım kontrolleri
            levene = _guvenli(lambda: {"p": float(stats.levene(*dizi).pvalue)})
            grup_norm_p = []
            for v in dizi:
                _, p, _ = _normallik(v)
                grup_norm_p.append(p)
            hepsi_normal = all(p is not None and p >= ALFA for p in grup_norm_p)
            varyans_esit = levene is not None and levene["p"] >= ALFA

            satir: dict[str, Any] = {
                "sayısal değişken": say,
                "gruplayıcı": kat,
                "grup sayısı": k,
                "toplam n": n_toplam,
                "gruplar (n)": "; ".join(f"{d} (n={len(gruplar[d])})" for d in adlar),
                "grup ortalamaları": "; ".join(
                    f"{d}: {np.mean(gruplar[d]):.3f}±{np.std(gruplar[d], ddof=1):.3f}" for d in adlar
                ),
                "grup medyanları": "; ".join(f"{d}: {np.median(gruplar[d]):.3f}" for d in adlar),
                "Levene p (varyans eşitliği)": levene["p"] if levene else np.nan,
                "tüm gruplar normal mi": "evet" if hepsi_normal else "hayır",
                "atlanan küçük gruplar": "; ".join(kucukler) if kucukler else "",
            }

            if k == 2:
                g1, g2 = dizi
                t_st = _guvenli(lambda: dict(zip(("t", "p"), map(float, stats.ttest_ind(g1, g2)))))
                t_w = _guvenli(
                    lambda: dict(zip(("t", "p"), map(float, stats.ttest_ind(g1, g2, equal_var=False))))
                )
                mw = _guvenli(
                    lambda: dict(zip(("u", "p"), map(float, stats.mannwhitneyu(g1, g2))))
                )
                d = _cohen_d(g1, g2)
                rb = (1 - 2 * mw["u"] / (len(g1) * len(g2))) if mw else np.nan
                satir.update({
                    "Student t": t_st["t"] if t_st else np.nan,
                    "Student t p": t_st["p"] if t_st else np.nan,
                    "Welch t": t_w["t"] if t_w else np.nan,
                    "Welch t p": t_w["p"] if t_w else np.nan,
                    "Mann-Whitney U": mw["u"] if mw else np.nan,
                    "Mann-Whitney p": mw["p"] if mw else np.nan,
                    "Cohen d": d,
                    "Hedges g": _hedges_g(d, len(g1), len(g2)),
                    "sıra çiftserisi r": float(rb),
                    "etki yorumu": _etki_yorumu_d(d),
                })
                onerilen, p_onerilen = _iki_grup_onerisi(
                    hepsi_normal, varyans_esit, t_st, t_w, mw
                )
            else:
                anova = _guvenli(lambda: dict(zip(("F", "p"), map(float, stats.f_oneway(*dizi)))))
                def _welch():
                    sonuc = anova_oneway(dizi, use_var="unequal", welch_correction=True)
                    return {"F": float(sonuc.statistic), "p": float(sonuc.pvalue)}

                welch = _guvenli(_welch)
                kw = _guvenli(lambda: dict(zip(("H", "p"), map(float, stats.kruskal(*dizi)))))
                eta2 = _eta_kare(dizi)
                eps2 = ((kw["H"] - k + 1) / (n_toplam - k)) if kw and n_toplam > k else np.nan
                satir.update({
                    "ANOVA F": anova["F"] if anova else np.nan,
                    "ANOVA p": anova["p"] if anova else np.nan,
                    "Welch ANOVA F": welch["F"] if welch else np.nan,
                    "Welch ANOVA p": welch["p"] if welch else np.nan,
                    "Kruskal-Wallis H": kw["H"] if kw else np.nan,
                    "Kruskal-Wallis p": kw["p"] if kw else np.nan,
                    "eta²": eta2,
                    "epsilon²": float(eps2) if eps2 == eps2 else np.nan,
                    "etki yorumu": _etki_yorumu_eta(eta2),
                })
                onerilen, p_onerilen = _cok_grup_onerisi(hepsi_normal, varyans_esit, anova, welch, kw)
                # Post-hoc: genel test anlamlıysa ikili karşılaştırmalar
                if p_onerilen is not None and p_onerilen < ALFA:
                    posthoc_satirlar.extend(
                        _posthoc(say, kat, adlar, dizi, parametrik=hepsi_normal and varyans_esit)
                    )
            satir["önerilen test"] = onerilen
            satir["önerilen test p"] = p_onerilen if p_onerilen is not None else np.nan
            satirlar.append(satir)

    tablo = pd.DataFrame(satirlar)
    if not tablo.empty:
        tablo = _p_duzeltmeleri(tablo, "önerilen test p")
        tablo = tablo.sort_values("önerilen test p").reset_index(drop=True)
    posthoc = pd.DataFrame(posthoc_satirlar)
    if not posthoc.empty:
        posthoc = _p_duzeltmeleri(posthoc, "p")
        posthoc = posthoc.sort_values("p").reset_index(drop=True)
    return tablo, posthoc


def _iki_grup_onerisi(normal, var_esit, t_st, t_w, mw):
    if normal and var_esit and t_st:
        return "Student t (varsayımlar sağlandı)", t_st["p"]
    if normal and t_w:
        return "Welch t (varyanslar eşit değil)", t_w["p"]
    if mw:
        return "Mann-Whitney U (normal dağılım yok)", mw["p"]
    return "hesaplanamadı", None


def _cok_grup_onerisi(normal, var_esit, anova, welch, kw):
    if normal and var_esit and anova:
        return "ANOVA (varsayımlar sağlandı)", anova["p"]
    if normal and welch:
        return "Welch ANOVA (varyanslar eşit değil)", welch["p"]
    if kw:
        return "Kruskal-Wallis (normal dağılım yok)", kw["p"]
    return "hesaplanamadı", None


def _eta_kare(dizi: list[np.ndarray]) -> float:
    hepsi = np.concatenate(dizi)
    genel_ort = np.mean(hepsi)
    ss_ara = sum(len(v) * (np.mean(v) - genel_ort) ** 2 for v in dizi)
    ss_toplam = float(np.sum((hepsi - genel_ort) ** 2))
    return float(ss_ara / ss_toplam) if ss_toplam > 0 else 0.0


def _etki_yorumu_eta(eta2: float) -> str:
    if eta2 < 0.01:
        return "ihmal edilebilir"
    if eta2 < 0.06:
        return "küçük"
    if eta2 < 0.14:
        return "orta"
    return "büyük"


def _posthoc(say, kat, adlar, dizi, parametrik: bool) -> list[dict[str, Any]]:
    satirlar = []
    if parametrik:
        sonuc = _guvenli(lambda: {"r": stats.tukey_hsd(*dizi)})
        if sonuc:
            r = sonuc["r"]
            for i, j in combinations(range(len(adlar)), 2):
                satirlar.append({
                    "sayısal değişken": say,
                    "gruplayıcı": kat,
                    "karşılaştırma": f"{adlar[i]} vs {adlar[j]}",
                    "yöntem": "Tukey HSD",
                    "fark (ort.)": float(np.mean(dizi[i]) - np.mean(dizi[j])),
                    "p": float(r.pvalue[i, j]),
                })
        return satirlar
    for i, j in combinations(range(len(adlar)), 2):
        mw = _guvenli(lambda: {"p": float(stats.mannwhitneyu(dizi[i], dizi[j]).pvalue)})
        if mw:
            satirlar.append({
                "sayısal değişken": say,
                "gruplayıcı": kat,
                "karşılaştırma": f"{adlar[i]} vs {adlar[j]}",
                "yöntem": "Mann-Whitney (ikili)",
                "fark (medyan)": float(np.median(dizi[i]) - np.median(dizi[j])),
                "p": mw["p"],
            })
    return satirlar


# ── Kategorik × Kategorik ─────────────────────────────────────────────────────
def kategorik_iliskiler(
    df: pd.DataFrame, kategorikler: list[str], atlanan: list[dict[str, str]]
) -> pd.DataFrame:
    satirlar = []
    for a, b in combinations(kategorikler, 2):
        cift = df[[a, b]].dropna()
        if len(cift) < 5:
            atlanan.append({"test": f"ki-kare: {a} × {b}", "neden": f"ortak gözlem n={len(cift)} < 5"})
            continue
        tablo = pd.crosstab(cift[a], cift[b])
        if tablo.shape[0] < 2 or tablo.shape[1] < 2:
            atlanan.append({"test": f"ki-kare: {a} × {b}", "neden": "tabloda 2×2'den az düzey"})
            continue
        ki = _guvenli(lambda: _ki_kare(tablo))
        if ki is None:
            atlanan.append({"test": f"ki-kare: {a} × {b}", "neden": "hesaplama hatası"})
            continue
        satir = {
            "değişken 1": a,
            "değişken 2": b,
            "n": int(tablo.to_numpy().sum()),
            "tablo boyutu": f"{tablo.shape[0]}×{tablo.shape[1]}",
            **ki,
        }
        if tablo.shape == (2, 2):
            fisher = _guvenli(
                lambda: dict(zip(("odds oranı", "Fisher p"),
                                 map(float, stats.fisher_exact(tablo.to_numpy()))))
            )
            if fisher:
                satir.update(fisher)
        satirlar.append(satir)
    sonuc = pd.DataFrame(satirlar)
    if not sonuc.empty:
        sonuc = _p_duzeltmeleri(sonuc, "ki-kare p")
        sonuc = sonuc.sort_values("ki-kare p").reset_index(drop=True)
    return sonuc


def _ki_kare(tablo: pd.DataFrame) -> dict[str, Any]:
    arr = tablo.to_numpy()
    chi2, p, dof, beklenen = stats.chi2_contingency(arr)
    n = arr.sum()
    k = min(arr.shape) - 1
    cramers_v = float(np.sqrt(chi2 / (n * k))) if n * k > 0 else np.nan
    dusuk_beklenen = int(np.sum(beklenen < 5))
    return {
        "ki-kare": float(chi2),
        "ki-kare p": float(p),
        "serbestlik derecesi": int(dof),
        "Cramér V": cramers_v,
        "beklenen<5 hücre sayısı": dusuk_beklenen,
        "ki-kare güvenilir mi": "evet" if dusuk_beklenen == 0 else
            "dikkat: bazı hücrelerde beklenen<5" + (" — Fisher p'ye bakın" if arr.shape == (2, 2) else ""),
    }


# ── Çoklu test düzeltmeleri ───────────────────────────────────────────────────
def _p_duzeltmeleri(tablo: pd.DataFrame, p_sutunu: str) -> pd.DataFrame:
    p = tablo[p_sutunu].to_numpy(dtype=float)
    gecerli = ~np.isnan(p)
    for yontem, ad in (("bonferroni", "Bonferroni p"), ("holm", "Holm p"), ("fdr_bh", "FDR p")):
        duzeltilmis = np.full_like(p, np.nan)
        if gecerli.sum() > 0:
            duzeltilmis[gecerli] = multipletests(p[gecerli], method=yontem)[1]
        tablo[ad] = duzeltilmis
    tablo["FDR sonrası anlamlı"] = np.where(
        np.isnan(tablo["FDR p"]), "", np.where(tablo["FDR p"] < ALFA, "EVET ✓", "hayır")
    )
    return tablo


# ── Ana giriş noktası ─────────────────────────────────────────────────────────
def analyze_dataframe(df: pd.DataFrame) -> AnalysisResult:
    """Tüm istatistik bataryasını çalıştırır ve sonuç paketini döndürür."""
    df = df.copy()
    degiskenler, atlanan_sutunlar = degiskenleri_algila(df)
    sayisallar = [d.ad for d in degiskenler if d.tip == "sayisal"]
    kategorikler = [d.ad for d in degiskenler if d.tip == "kategorik"]
    atlanan_testler: list[dict[str, str]] = []

    bet_say = betimsel_sayisal(df, sayisallar)
    bet_kat = betimsel_kategorik(df, kategorikler)
    korelasyon = korelasyon_taramasi(df, sayisallar, atlanan_testler)
    gruplar, posthoc = grup_karsilastirmalari(df, kategorikler, sayisallar, atlanan_testler)
    kat_iliski = kategorik_iliskiler(df, kategorikler, atlanan_testler)

    istatistik_sayisi = int(
        bet_say.size + bet_kat.size + korelasyon.size + gruplar.size + posthoc.size + kat_iliski.size
    )
    anlamli = 0
    for t in (korelasyon, gruplar, kat_iliski, posthoc):
        if not t.empty and "FDR sonrası anlamlı" in t:
            anlamli += int((t["FDR sonrası anlamlı"] == "EVET ✓").sum())

    ozet = {
        "satır sayısı": int(len(df)),
        "sütun sayısı": int(df.shape[1]),
        "kullanılan değişken": len(degiskenler),
        "sayısal değişken": len(sayisallar),
        "kategorik değişken": len(kategorikler),
        "atlanan sütun": len(atlanan_sutunlar),
        "korelasyon çifti": int(len(korelasyon)),
        "grup karşılaştırması": int(len(gruplar)),
        "post-hoc karşılaştırma": int(len(posthoc)),
        "kategorik ilişki testi": int(len(kat_iliski)),
        "hesaplanan istatistik (hücre) sayısı": istatistik_sayisi,
        "FDR sonrası anlamlı bulgu": anlamli,
        "atlanan test": len(atlanan_testler),
    }
    return AnalysisResult(
        degiskenler=degiskenler,
        atlanan_sutunlar=atlanan_sutunlar,
        betimsel_sayisal=bet_say,
        betimsel_kategorik=bet_kat,
        korelasyonlar=korelasyon,
        grup_karsilastirmalari=gruplar,
        posthoc=posthoc,
        kategorik_iliskiler=kat_iliski,
        atlanan_testler=atlanan_testler,
        ozet=ozet,
    )
