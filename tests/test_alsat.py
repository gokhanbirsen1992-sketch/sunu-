"""alsat modülü testleri — tohumlu sentetik veriyle, ağsız ve deterministik."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from alsat import dongu, gostergeler, olcutler, rapor, sinama, veri


def sentetik_seri(n=2200, mu=0.001, sigma=0.03, seed=42, start="2015-01-01") -> pd.Series:
    rng = np.random.default_rng(seed)
    getiriler = rng.normal(mu, sigma, n)
    fiyat = 100.0 * np.exp(np.cumsum(getiriler))
    return pd.Series(fiyat, index=pd.date_range(start, periods=n, freq="D"),
                     name="kapanis")


@pytest.fixture
def kapanis() -> pd.Series:
    return sentetik_seri()


@pytest.fixture
def seriler() -> dict[str, pd.Series]:
    return {"AAA": sentetik_seri(seed=1), "BBB": sentetik_seri(seed=2, mu=0.0005)}


# ── göstergeler ────────────────────────────────────────────────────────────────

def test_gostergeler_pozisyon_araliginda(kapanis):
    for aile, tanim in gostergeler.AILELER.items():
        poz = gostergeler.pozisyon_uret(kapanis, aile, tanim["izgara"][0])
        assert poz.index.equals(kapanis.index), aile
        assert poz.min() >= 0.0 and poz.max() <= 1.0, aile
        assert poz.notna().all(), aile


def test_gostergeler_nedensel(kapanis):
    """Gösterge, serinin geleceği değişince geçmiş değerlerini değiştirmemeli."""
    kesik = kapanis.iloc[:1500]
    for aile, tanim in gostergeler.AILELER.items():
        tam = gostergeler.pozisyon_uret(kapanis, aile, tanim["izgara"][0]).iloc[:1400]
        parcali = gostergeler.pozisyon_uret(kesik, aile, tanim["izgara"][0]).iloc[:1400]
        pd.testing.assert_series_equal(tam, parcali, check_names=False), aile


def test_vol_hedef_tavani(kapanis):
    poz = pd.Series(1.0, index=kapanis.index)
    olcekli = gostergeler.vol_hedef(poz, kapanis, hedef_vol=0.10)
    assert olcekli.max() <= 1.0 + 1e-12
    assert olcekli.mean() < 1.0  # yüksek vol'lü seride ölçek küçülmeli


# ── sınama motoru ──────────────────────────────────────────────────────────────

def test_backtest_ileri_bakis_korumasi(kapanis):
    """Pozisyon bir gün gecikmeli uygulanmalı: 'yarını bilen' pozisyon serisi,
    gecikme sayesinde aynı gün getirisini yakalayamamalı."""
    getiri = kapanis.pct_change().fillna(0.0)
    hileli = (getiri > 0).astype(float)  # t günü getirisini t günü 'bilen' pozisyon
    sonuc = sinama.backtest(kapanis, hileli, maliyet_bps=0.0)
    gecikmesiz_ort = (hileli * getiri).mean()
    assert sonuc.net_getiriler.mean() < gecikmesiz_ort * 0.5  # sihir kaybolmalı


def test_backtest_maliyet_monoton(kapanis):
    poz = gostergeler.sma_kesisim(kapanis, 5, 20)
    netler = [sinama.backtest(kapanis, poz, maliyet_bps=m).net_getiriler.sum()
              for m in (0.0, 20.0, 80.0)]
    assert netler[0] > netler[1] > netler[2]


def test_walk_forward_dilim_butunlugu(kapanis):
    dilimler = sinama.walk_forward_dilimleri(kapanis.index, egitim_yil=3, test_yil=1)
    assert dilimler
    onceki_son = None
    for egitim, test in dilimler:
        assert egitim.start == kapanis.index[0]         # genişleyen pencere
        assert egitim.stop < test.start                  # eğitim, testten önce biter
        if onceki_son is not None:
            assert test.start > onceki_son               # test blokları örtüşmez
        onceki_son = test.stop
        test_gunleri = kapanis.loc[test]
        assert len(test_gunleri) > 0


def test_satin_al_tut_maliyetsiz(kapanis):
    bh = sinama.satin_al_tut(kapanis)
    beklenen = kapanis.iloc[-1] / kapanis.iloc[0]
    assert bh.ozsermaye.iloc[-1] == pytest.approx(beklenen, rel=1e-9)


# ── ölçütler ───────────────────────────────────────────────────────────────────

def test_sharpe_ve_dusus_isaretleri():
    idx = pd.date_range("2020-01-01", periods=400, freq="D")
    artan = pd.Series(0.001, index=idx)
    assert olcutler.sharpe(artan) > 5
    oz = (1 + pd.Series([0.1, -0.5, 0.2], index=idx[:3])).cumprod()
    assert olcutler.maks_dusus(oz) == pytest.approx(-0.5)


def test_dsr_deneme_sayisiyla_azalir(kapanis):
    net = sinama.backtest(kapanis, gostergeler.fiyat_sma(kapanis, 50)).net_getiriler
    assert olcutler.deflated_sharpe(net, 1) > olcutler.deflated_sharpe(net, 200)


def test_bootstrap_p_ayrimi():
    idx = pd.date_range("2020-01-01", periods=800, freq="D")
    rng = np.random.default_rng(42)
    gurultu = pd.Series(rng.normal(0, 0.01, 800), index=idx)
    kazancli = pd.Series(rng.normal(0.002, 0.01, 800), index=idx)
    assert olcutler.bootstrap_p(kazancli) < 0.05
    assert olcutler.bootstrap_p(gurultu) > 0.05


# ── döngü + hakem + rapor ─────────────────────────────────────────────────────

def test_dongu_deterministik(seriler):
    s1 = dongu.calistir(seriler, maks_tur=2, gunluk=lambda *_: None)
    s2 = dongu.calistir(seriler, maks_tur=2, gunluk=lambda *_: None)
    assert s1.final_spek == s2.final_spek
    assert [t.olcutler["sharpe"] for t in s1.turlar] == \
           [t.olcutler["sharpe"] for t in s2.turlar]


def test_dongu_kaydi_ve_rapor(seriler):
    sonuc = dongu.calistir(seriler, maks_tur=2, gunluk=lambda *_: None)
    assert 1 <= len(sonuc.turlar) <= 2
    for t in sonuc.turlar:
        assert set(t.kabul_durumu) == {"K1_oos_sharpe", "K2_dsr", "K3_maliyet_2x",
                                       "K4_dusus", "K5_engel_yok"}
        assert t.aday_tablosu is not None and len(t.aday_tablosu) == t.aday_sayisi
    xlsx = rapor.excel_raporu(sonuc)
    assert xlsx[:2] == b"PK" and len(xlsx) > 5000  # geçerli bir zip/xlsx
    ozet = rapor.metin_ozeti(sonuc)
    assert "Reviewer 2" in ozet and "FİNAL" in ozet


def test_dongu_gurultude_kabul_etmez():
    """Saf rastgele yürüyüşte (sürüklenmesiz) döngü kural KABUL etmemeli."""
    seriler = {"XXX": sentetik_seri(seed=7, mu=0.0),
               "YYY": sentetik_seri(seed=8, mu=0.0)}
    sonuc = dongu.calistir(seriler, maks_tur=2, gunluk=lambda *_: None)
    assert not sonuc.kabul_edildi


# ── veri katmanı (ağsız) ──────────────────────────────────────────────────────

def test_csv_yukle_esnek_kolonlar(tmp_path):
    yol = tmp_path / "veri.csv"
    idx = pd.date_range("2015-01-01", periods=300, freq="D")
    pd.DataFrame({"Date": idx, "Close": np.linspace(100, 200, 300)}).to_csv(yol, index=False)
    seri = veri.csv_yukle(yol)
    assert seri.name == "kapanis" and len(seri) == 300


def test_csv_yukle_eksik_kolon_hatasi(tmp_path):
    yol = tmp_path / "bozuk.csv"
    pd.DataFrame({"a": [1, 2], "b": [3, 4]}).to_csv(yol, index=False)
    with pytest.raises(ValueError):
        veri.csv_yukle(yol)


def test_seri_yap_temizligi():
    tarih = ["2020-01-02", "2020-01-01", "2020-01-02", "bozuk"] + [
        str(d.date()) for d in pd.date_range("2020-01-03", periods=250)]
    deger = [1.0, 2.0, 3.0, 4.0] + list(np.linspace(5, 10, 250))
    seri = veri._seri_yap(tarih, deger)
    assert seri.index.is_monotonic_increasing
    assert not seri.index.duplicated().any()
    assert seri.loc["2020-01-02"] == 3.0  # kopyada sonuncusu kalır


def test_seri_yap_yetersiz_veri():
    with pytest.raises(ValueError):
        veri._seri_yap(["2020-01-01"], [1.0])


# ── final indikatör ───────────────────────────────────────────────────────────

def test_final_indikator(kapanis):
    from alsat import final_indikator as fi

    poz = fi.al_sat_sinyali(kapanis)
    assert set(poz.unique()) <= {0.0, 1.0}
    # nedensellik: gelecek veriyi kesmek geçmiş sinyali değiştirmemeli
    parcali = fi.al_sat_sinyali(kapanis.iloc[:1500]).iloc[:1400]
    pd.testing.assert_series_equal(poz.iloc[:1400], parcali, check_names=False)
    assert fi.son_karar(kapanis) in {"AL (yarın geçerli)", "SAT (yarın geçerli)",
                                     "BEKLE — pozisyonda kal", "BEKLE — nakitte kal"}
