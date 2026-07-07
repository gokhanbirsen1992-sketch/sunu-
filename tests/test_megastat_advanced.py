"""MegaStat gelişmiş katman (advanced.py) testleri."""
import io

import numpy as np
import pandas as pd
import pytest

from megastat.advanced import (
    _cronbach_alfa,
    gelismis_analiz,
    madde_gruplari,
)
from megastat.engine import ALFA, analyze_dataframe
from megastat.report import excel_raporu, metin_ozeti


@pytest.fixture()
def klinik_veri() -> pd.DataFrame:
    """Ölçek maddeleri + ön/son test + ikili sonuç + iki değerlendirici içeren veri."""
    rng = np.random.default_rng(7)
    n = 200
    ortak = rng.normal(0, 1, n)                       # ölçek maddelerinin ortak faktörü
    maddeler = {
        f"madde{i}": np.clip(np.round(3 + 1.2 * ortak + rng.normal(0, 0.8, n)), 1, 5)
        for i in range(1, 6)
    }
    on_test = rng.normal(50, 10, n)
    son_test = on_test + 5 + rng.normal(0, 4, n)       # gerçek ön/son farkı
    belirtec = rng.normal(10, 2, n)
    logit = -8 + 0.8 * belirtec + rng.normal(0, 1, n)  # belirteç olayı gerçekten yordar
    hastalik = np.where(1 / (1 + np.exp(-logit)) > rng.uniform(0, 1, n), "var", "yok")
    hakem1 = rng.choice(["olumlu", "olumsuz"], n)
    hakem2 = np.where(rng.uniform(0, 1, n) < 0.8, hakem1,  # %80 uyumlu ikinci hakem
                      rng.choice(["olumlu", "olumsuz"], n))
    return pd.DataFrame({
        **maddeler,
        "on_test": on_test,
        "son_test": son_test,
        "belirtec": belirtec,
        "hastalik": hastalik,
        "hakem1": hakem1,
        "hakem2": hakem2,
    })


def test_madde_gruplari():
    gruplar = madde_gruplari(["madde1", "madde2", "madde3", "yas", "STAI_1", "STAI_2"])
    assert gruplar == {"madde": ["madde1", "madde2", "madde3"]}  # STAI 2 maddeyle grup olamaz


def test_cronbach_paralel_maddelerde_formulle_uyusur():
    """k paralel madde, korelasyon r → alfa = k·r / (1+(k-1)·r) (Spearman-Brown)."""
    rng = np.random.default_rng(3)
    n, k, r = 100_000, 4, 0.5
    ortak = rng.normal(0, np.sqrt(r), n)
    X = np.column_stack([ortak + rng.normal(0, np.sqrt(1 - r), n) for _ in range(k)])
    beklenen = k * r / (1 + (k - 1) * r)
    assert _cronbach_alfa(X) == pytest.approx(beklenen, abs=0.02)


def test_gelismis_analiz_tam(klinik_veri):
    atlanan: list[dict[str, str]] = []
    say = ["madde1", "madde2", "madde3", "madde4", "madde5", "on_test", "son_test", "belirtec"]
    kat = ["hastalik", "hakem1", "hakem2"]
    g = gelismis_analiz(klinik_veri, say, kat, atlanan)

    # Eşleştirilmiş: gerçek ön/son farkı FDR sonrası anlamlı olmalı
    e = g.eslestirilmis
    on_son = e[(e["ölçüm 1"] == "on_test") & (e["ölçüm 2"] == "son_test")].iloc[0]
    assert on_son["FDR p"] < ALFA
    assert abs(on_son["ortalama fark"] + 5) < 1.5  # fark ≈ -5 (son test daha yüksek)

    # Güvenilirlik: 5 korelasyonlu madde → alfa yüksek olmalı
    guv = g.guvenilirlik
    madde_grubu = guv[guv["madde grubu"] == "madde"].iloc[0]
    assert madde_grubu["Cronbach alfa"] > 0.7
    assert madde_grubu["McDonald omega"] > 0.7
    assert madde_grubu["alfa %95 GA alt"] < madde_grubu["Cronbach alfa"] < madde_grubu["alfa %95 GA üst"]
    assert (g.madde_analizi["madde grubu"] == "madde").sum() == 5

    # Faktör: madde grubu tek faktörlü, KMO makul olmalı
    fak = g.faktor_uygunluk[g.faktor_uygunluk["madde grubu"] == "madde"].iloc[0]
    assert fak["KMO"] > 0.6
    assert fak["Bartlett p"] < ALFA
    assert fak["faktör sayısı (Kaiser: özdeğer>1)"] == 1
    assert (g.faktor_yukler["madde grubu"] == "madde").sum() == 5

    # Friedman: madde grubu için hesaplanmış olmalı
    assert not g.friedman.empty
    assert "Kendall W (uyum)" in g.friedman.columns

    # Lojistik: belirteç anlamlı, OR > 1, AUC iyi
    lo = g.lojistik
    bel = lo[(lo["sonuç değişkeni"] == "hastalik") & (lo["yordayıcı"] == "belirtec")].iloc[0]
    assert bel["odds oranı (OR)"] > 1.5
    assert bel["p"] < ALFA
    assert bel["model AUC"] > 0.7

    # ROC: belirteç hastalığı ayırt etmeli
    roc = g.roc
    r = roc[(roc["sonuç değişkeni"] == "hastalik") & (roc["belirteç"] == "belirtec")].iloc[0]
    assert r["AUC"] > 0.7
    assert 0 <= r["kesimde duyarlılık"] <= 1
    assert 0 <= r["kesimde özgüllük"] <= 1
    assert r["AUC %95 GA alt"] < r["AUC"] < r["AUC %95 GA üst"]

    # Uyum: hakem1 × hakem2 kappa pozitif ve McNemar hesaplanmış
    u = g.uyum
    hakem = u[(u["değişken 1"] == "hakem1") & (u["değişken 2"] == "hakem2")].iloc[0]
    assert hakem["Cohen kappa"] > 0.3
    assert np.isfinite(hakem["McNemar p"])

    # Çoklu regresyon: son_test'i on_test yordamalı
    cr = g.coklu_regresyon
    sonuc = cr[(cr["bağımlı değişken"] == "son_test") & (cr["yordayıcı"] == "on_test")].iloc[0]
    assert sonuc["p"] < ALFA
    assert sonuc["model R²"] > 0.5
    assert "VIF" in cr.columns


def test_uctan_uca_analiz_ve_excel(klinik_veri):
    sonuc = analyze_dataframe(klinik_veri, kesif_yap=False)
    assert sonuc.gelismis is not None
    o = sonuc.ozet
    assert o["eşleştirilmiş test"] > 0
    assert o["güvenilirlik analizi (ölçek)"] > 0
    assert o["ROC analizi"] > 0

    # Likert (1-5) kodlu maddeler "kategorik" sınıflansa da ölçek maddesi sayılmalı
    assert "madde" in set(sonuc.gelismis.guvenilirlik["madde grubu"])
    assert "madde" in set(sonuc.gelismis.faktor_uygunluk["madde grubu"])

    rapor = excel_raporu(sonuc)
    tablolar = pd.read_excel(io.BytesIO(rapor), sheet_name=None)
    for sayfa in (
        "Eşleştirilmiş Testler", "Güvenilirlik (Alfa-Omega)", "Madde Analizi",
        "Faktör Analizi (KMO)", "Faktör Yükleri", "Çoklu Regresyon",
        "Lojistik Regresyon", "ROC Analizi", "Uyum (Kappa-McNemar)",
        "Tekrarlı Ölçüm (Friedman)",
    ):
        assert sayfa in tablolar, f"Excel'de '{sayfa}' sayfası yok"

    ozet = metin_ozeti(sonuc)
    assert "Gelişmiş katman" in ozet

    # Yeni normallik sütunları betimsellerde olmalı
    for sutun in ("Lilliefors (KS) p", "Anderson-Darling p", "Jarque-Bera p"):
        assert sutun in sonuc.betimsel_sayisal.columns


def test_kucuk_veri_gelismis_katman_cokmez():
    df = pd.DataFrame({"a": [1.0, 2.0, 3.0], "b": ["x", "y", "x"]})
    sonuc = analyze_dataframe(df, kesif_yap=False)  # hata vermemeli
    assert sonuc.ozet["satır sayısı"] == 3
