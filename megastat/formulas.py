"""MegaStat gizli formül katmanı — ilişkinin varlığını değil, DENKLEMİNİ bulur.

İki tarama:

1. EĞRİ (FORMÜL) TARAMASI — her sayısal çift için 7 aday model uydurulur:
   doğrusal, karesel, kübik, logaritmik, üstel, güç (power) ve ters (1/x).
   En iyi model düzeltilmiş R²'ye göre seçilir ve AÇIK DENKLEM olarak yazılır
   (örn. "skor = 12.4 + 8.1·ln(yas)"). Doğrusal modele göre belirgin kazanç
   varsa "gizli formül" olarak işaretlenir — Pearson'ın düşük gösterdiği ama
   aslında kurallı olan ilişkinin kuralı budur.

2. ETKİLEŞİM (MODERASYON) TARAMASI — "X'in Y üzerindeki etkisi Z'ye bağlı mı?"
   Her sayısal bağımlı için tüm yordayıcı çiftlerinde Y ~ X + Z + X·Z modeli
   kurulur; etkileşim teriminin katsayısı, p'si ve ΔR² katkısı raporlanır.
   İki düzeyli kategorikler 0/1 kodlanarak moderatör adayı olur.

engine.py ile aynı ilkeler: sınırsız, deterministik, güvenli, FDR düzeltmeli.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations
from typing import Any, Optional

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

from megastat.engine import ALFA, _guvenli, _p_duzeltmeleri

MIN_EGRI_N = 20            # eğri uydurma için en az gözlem
MIN_ETKILESIM_N = 30       # moderasyon modeli için en az gözlem
MIN_KAZANC = 0.05          # "gizli formül" için doğrusala göre düz. R² kazancı eşiği
MIN_R2 = 0.20              # "gizli formül" için en iyi modelin düz. R² tabanı
MAX_ETKILESIM_MODEL = 3000  # kombinasyon patlamasına karşı üst sınır


@dataclass
class FormulaResult:
    egriler: pd.DataFrame = field(default_factory=pd.DataFrame)
    etkilesimler: pd.DataFrame = field(default_factory=pd.DataFrame)


# ── Eğri (formül) taraması ────────────────────────────────────────────────────
def _duz_r2(y: np.ndarray, yhat: np.ndarray, n: int, p: int) -> tuple[float, float]:
    """(R², düzeltilmiş R²) — p: yordayıcı terim sayısı (sabit hariç)."""
    ss_res = float(np.sum((y - yhat) ** 2))
    ss_top = float(np.sum((y - np.mean(y)) ** 2))
    if ss_top <= 0 or n - p - 1 <= 0:
        return np.nan, np.nan
    r2 = 1 - ss_res / ss_top
    return r2, 1 - (1 - r2) * (n - 1) / (n - p - 1)


def _terim(katsayi: float, govde: str) -> str:
    isaret = "+" if katsayi >= 0 else "−"
    return f" {isaret} {abs(katsayi):.4g}·{govde}"


def _modelleri_uydur(x: np.ndarray, y: np.ndarray, x_ad: str, y_ad: str) -> list[dict[str, Any]]:
    """Tüm aday modelleri dener; her biri için (ad, R², düz. R², denklem, terim sayısı)."""
    n = len(x)
    modeller: list[dict[str, Any]] = []

    def ekle(ad: str, yhat: np.ndarray, p: int, denklem: str) -> None:
        r2, ar2 = _duz_r2(y, yhat, n, p)
        if np.isfinite(ar2):
            modeller.append({"model": ad, "R2": r2, "aR2": ar2, "denklem": denklem, "p_terim": p})

    lin = _guvenli(lambda: stats.linregress(x, y))
    if lin:
        a, b = float(lin.intercept), float(lin.slope)
        ekle("doğrusal", a + b * x, 1, f"{y_ad} = {a:.4g}{_terim(b, x_ad)}")

    for derece, ad, ust in ((2, "karesel", "²"), (3, "kübik", "³")):
        kat = _guvenli(lambda d=derece: {"k": np.polyfit(x, y, d)})
        if kat and n > derece + 2:
            k = kat["k"]
            denklem = f"{y_ad} = {k[-1]:.4g}"
            for j in range(1, derece + 1):
                govde = x_ad if j == 1 else f"{x_ad}{'²' if j == 2 else '³'}"
                denklem += _terim(float(k[derece - j]), govde)
            ekle(ad, np.polyval(k, x), derece, denklem)

    if np.min(x) > 0:
        log_fit = _guvenli(lambda: stats.linregress(np.log(x), y))
        if log_fit:
            a, b = float(log_fit.intercept), float(log_fit.slope)
            ekle("logaritmik", a + b * np.log(x), 1, f"{y_ad} = {a:.4g}{_terim(b, f'ln({x_ad})')}")

    if np.min(y) > 0:
        ust_fit = _guvenli(lambda: stats.linregress(x, np.log(y)))
        if ust_fit:
            a, b = float(np.exp(ust_fit.intercept)), float(ust_fit.slope)
            ekle("üstel", a * np.exp(b * x), 1, f"{y_ad} = {a:.4g}·e^({b:.4g}·{x_ad})")

    if np.min(x) > 0 and np.min(y) > 0:
        guc_fit = _guvenli(lambda: stats.linregress(np.log(x), np.log(y)))
        if guc_fit:
            a, b = float(np.exp(guc_fit.intercept)), float(guc_fit.slope)
            ekle("güç", a * x ** b, 1, f"{y_ad} = {a:.4g}·{x_ad}^{b:.4g}")

    if np.all(x != 0):
        ters_fit = _guvenli(lambda: stats.linregress(1.0 / x, y))
        if ters_fit:
            a, b = float(ters_fit.intercept), float(ters_fit.slope)
            ekle("ters (1/x)", a + b / x, 1, f"{y_ad} = {a:.4g}{_terim(b, f'(1/{x_ad})')}")

    return modeller


def _yon_tara(x: np.ndarray, y: np.ndarray, x_ad: str, y_ad: str) -> Optional[dict[str, Any]]:
    """Tek yön (y ← x) için en iyi modeli ve doğrusala göre kazancı bulur."""
    modeller = _modelleri_uydur(x, y, x_ad, y_ad)
    dogrusal = next((m for m in modeller if m["model"] == "doğrusal"), None)
    if dogrusal is None or not modeller:
        return None
    en_iyi = max(modeller, key=lambda m: m["aR2"])
    n = len(x)
    k = en_iyi["p_terim"]
    r2 = en_iyi["R2"]
    if 0 <= r2 < 1 and n - k - 1 > 0:
        f_ist = (r2 / k) / ((1 - r2) / (n - k - 1))
        model_p = float(stats.f.sf(f_ist, k, n - k - 1))
    else:
        model_p = np.nan
    return {
        "bağımlı": y_ad,
        "yordayıcı": x_ad,
        "n": n,
        "doğrusal düz. R²": dogrusal["aR2"],
        "en iyi model": en_iyi["model"],
        "en iyi düz. R²": en_iyi["aR2"],
        "denklem": en_iyi["denklem"],
        "doğrusal ötesi kazanç": en_iyi["aR2"] - dogrusal["aR2"],
        "model p": model_p,
        "tüm modeller (düz. R²)": "; ".join(
            f"{m['model']}: {m['aR2']:.3f}" for m in sorted(modeller, key=lambda m: -m["aR2"])
        ),
    }


def egri_taramasi(
    df: pd.DataFrame, sayisallar: list[str], atlanan: list[dict[str, str]]
) -> pd.DataFrame:
    satirlar = []
    for a, b in combinations(sayisallar, 2):
        cift = df[[a, b]].dropna()
        n = len(cift)
        if n < MIN_EGRI_N:
            atlanan.append({"test": f"eğri taraması: {a} × {b}",
                            "neden": f"ortak gözlem n={n} < {MIN_EGRI_N}"})
            continue
        x = cift[a].to_numpy(dtype=float)
        y = cift[b].to_numpy(dtype=float)
        if np.std(x) == 0 or np.std(y) == 0:
            atlanan.append({"test": f"eğri taraması: {a} × {b}", "neden": "değişkenlerden biri sabit"})
            continue
        yonler = [s for s in (_yon_tara(x, y, a, b), _yon_tara(y, x, b, a)) if s]
        if not yonler:
            continue
        satir = max(yonler, key=lambda s: s["en iyi düz. R²"])
        kazanc, ar2 = satir["doğrusal ötesi kazanç"], satir["en iyi düz. R²"]
        satir["gizli formül mü"] = (
            "EVET ✓ — doğrusal bakış bunu kaçırır"
            if kazanc >= MIN_KAZANC and ar2 >= MIN_R2 else "hayır (doğrusal yeterli)"
        )
        satirlar.append(satir)
    tablo = pd.DataFrame(satirlar)
    if not tablo.empty:
        tablo = _p_duzeltmeleri(tablo, "model p")
        tablo = tablo.sort_values("doğrusal ötesi kazanç", ascending=False).reset_index(drop=True)
    return tablo


# ── Etkileşim (moderasyon) taraması ──────────────────────────────────────────
def _aday_serileri(
    df: pd.DataFrame, sayisallar: list[str], kategorikler: list[str]
) -> dict[str, pd.Series]:
    """Yordayıcı adayları: sayısallar + 0/1 kodlanmış iki düzeyli kategorikler."""
    seriler: dict[str, pd.Series] = {s: df[s].astype(float) for s in sayisallar}
    for kat in kategorikler:
        duzeyler = sorted(df[kat].dropna().astype(str).unique())
        if len(duzeyler) == 2:
            olay = duzeyler[1]
            kodlu = (df[kat].astype(str) == olay).where(df[kat].notna()).astype(float)
            seriler[f"{kat} ({olay}=1)"] = kodlu
    return seriler


def etkilesim_taramasi(
    df: pd.DataFrame,
    sayisallar: list[str],
    kategorikler: list[str],
    atlanan: list[dict[str, str]],
) -> pd.DataFrame:
    adaylar = _aday_serileri(df, sayisallar, kategorikler)
    satirlar = []
    model_sayisi = 0
    sinir_asildi = False
    for bagimli in sayisallar:
        yordayicilar = [a for a in adaylar if a != bagimli]
        for x_ad, z_ad in combinations(yordayicilar, 2):
            if model_sayisi >= MAX_ETKILESIM_MODEL:
                sinir_asildi = True
                break
            veri = pd.concat(
                [df[bagimli].astype(float).rename("_y"), adaylar[x_ad].rename("_x"),
                 adaylar[z_ad].rename("_z")], axis=1,
            ).dropna()
            n = len(veri)
            if n < MIN_ETKILESIM_N:
                continue  # tek tek raporlamak listeyi boğar; toplam zaten sınırlı
            y = veri["_y"].to_numpy()
            xs, zs = veri["_x"].to_numpy(), veri["_z"].to_numpy()
            if np.std(y) == 0 or np.std(xs) == 0 or np.std(zs) == 0:
                continue
            # Ortalamadan arındırma: etkileşim terimiyle çoklu bağlantıyı azaltır
            xs = (xs - xs.mean()) / xs.std(ddof=1)
            zs = (zs - zs.mean()) / zs.std(ddof=1)
            ys = (y - y.mean()) / y.std(ddof=1)

            def _model():
                tam = sm.OLS(ys, sm.add_constant(np.column_stack([xs, zs, xs * zs]))).fit()
                yalin = sm.OLS(ys, sm.add_constant(np.column_stack([xs, zs]))).fit()
                return {"tam": tam, "yalin": yalin}

            sonuc = _guvenli(_model)
            model_sayisi += 1
            if sonuc is None:
                continue
            tam, yalin = sonuc["tam"], sonuc["yalin"]
            b_int = float(tam.params[3])
            p_int = float(tam.pvalues[3])
            satirlar.append({
                "bağımlı": bagimli,
                "X (yordayıcı)": x_ad,
                "Z (moderatör)": z_ad,
                "n": n,
                "etkileşim B (std)": b_int,
                "p": p_int,
                "ΔR² (etkileşim katkısı)": float(tam.rsquared - yalin.rsquared),
                "model R²": float(tam.rsquared),
                "yorum": (
                    f"{z_ad} arttıkça {x_ad}'nin {bagimli} üzerindeki etkisi "
                    + ("güçleniyor" if b_int > 0 else "zayıflıyor/tersine dönüyor")
                ),
            })
        if sinir_asildi:
            break
    if sinir_asildi:
        atlanan.append({
            "test": "etkileşim taraması",
            "neden": f"kombinasyon sayısı {MAX_ETKILESIM_MODEL} model sınırını aştı; kalanlar atlandı",
        })
    tablo = pd.DataFrame(satirlar)
    if not tablo.empty:
        tablo = _p_duzeltmeleri(tablo, "p")
        tablo = tablo.sort_values("p").reset_index(drop=True)
    return tablo


# ── Ana giriş noktası ─────────────────────────────────────────────────────────
def formul_analizi(
    df: pd.DataFrame,
    sayisallar: list[str],
    kategorikler: list[str],
    atlanan: list[dict[str, str]],
) -> FormulaResult:
    return FormulaResult(
        egriler=egri_taramasi(df, sayisallar, atlanan),
        etkilesimler=etkilesim_taramasi(df, sayisallar, kategorikler, atlanan),
    )
