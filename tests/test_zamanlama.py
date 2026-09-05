import numpy as np
import pandas as pd
import pytest

from zamanlama import (
    al_ve_tut,
    dip_tepe_kahini,
    gecikme_analizi,
    geri_test,
    ileriye_donuk,
    kesisim_kurali,
    mukemmel_ongoru,
    sma_kurali,
    veri_yukle,
)
from zamanlama.motor import gecikme_ozeti, zigzag_donusler


def _seri(degerler):
    idx = pd.date_range("2000-01-01", periods=len(degerler), freq="MS")
    return pd.Series(degerler, index=idx, dtype=float, name="fiyat")


def test_veri_yukle_temel():
    df = veri_yukle()
    assert df.index.is_monotonic_increasing
    assert (df["fiyat"] > 0).all()
    assert df.index[0].year == 1871
    assert df["temettu"].notna().sum() > 1000


def test_al_ve_tut_cagr_dogru():
    # 12 ayda 1 → 2: CAGR ≈ %100 (yıl = 11/12 ay aralığı olduğundan biraz üstü)
    fiyat = _seri(np.linspace(1, 2, 12))
    _, s = geri_test(fiyat, al_ve_tut(fiyat))
    assert s.son_deger == pytest.approx(2.0)
    assert s.islem_sayisi == 0
    assert s.max_dusus == 0.0


def test_pozisyon_bakis_ileri_yok():
    # pozisyon t kapanışında kurulur, t→t+1 getirisine uygulanır
    fiyat = _seri([1, 1, 2, 2, 4])
    poz = pd.Series([0, 1, 0, 1, 0], index=fiyat.index)
    ozk, s = geri_test(fiyat, poz)
    # ay1→ay2 (1→2) ve ay3→ay4 (2→4) getirileri alınır: 1*2*2 = 4
    assert ozk.iloc[-1] == pytest.approx(4.0)
    assert s.islem_sayisi == 4


def test_maliyet_ozkaynagi_dusurur():
    fiyat = _seri(np.cumprod(1 + 0.01 * np.sin(np.arange(60))))
    poz = sma_kurali(fiyat, 3)
    _, s0 = geri_test(fiyat, poz, 0.0)
    _, s1 = geri_test(fiyat, poz, 0.005)
    assert s1.son_deger < s0.son_deger
    assert s1.islem_sayisi == s0.islem_sayisi > 0


def test_sma_trendde_piyasada_kalir():
    fiyat = _seri(np.linspace(1, 3, 40))
    poz = sma_kurali(fiyat, 10)
    assert poz.iloc[:9].sum() == 0  # ısınma
    assert poz.iloc[9:].all()
    _, s_bh = geri_test(fiyat, al_ve_tut(fiyat))
    _, s_sma = geri_test(fiyat, poz)
    assert s_sma.son_deger < s_bh.son_deger  # ısınma boyunca dışarıda


def test_kesisim_parametre_kontrolu():
    fiyat = _seri(np.linspace(1, 2, 20))
    with pytest.raises(ValueError):
        kesisim_kurali(fiyat, 5, 5)
    with pytest.raises(ValueError):
        sma_kurali(fiyat, 0)


def test_kahin_aylik_al_ve_tutu_gecer():
    rng = np.random.default_rng(0)
    fiyat = _seri(np.cumprod(1 + rng.normal(0.005, 0.04, 240)))
    _, s_bh = geri_test(fiyat, al_ve_tut(fiyat))
    _, s_k = geri_test(fiyat, mukemmel_ongoru(fiyat))
    assert s_k.son_deger > s_bh.son_deger
    assert s_k.max_dusus == 0.0  # hiç düşen ay almaz


def test_zigzag_v_seklinde_dip_ve_tepe_bulur():
    fiyat = _seri([100, 90, 70, 60, 75, 90, 110, 120, 100, 90])
    d = zigzag_donusler(fiyat, 0.20)
    assert d[:3] == [
        (fiyat.index[0], "tepe"),  # 100 (başlangıçtaki gerçek tepe, 90 değil)
        (fiyat.index[3], "dip"),  # 60
        (fiyat.index[7], "tepe"),  # 120
    ]


def test_zigzag_yukselisle_baslayan_seri():
    # ilk hareket yükseliş: ilk dönüş 'dip' olmalı ve seri başında olmalı
    fiyat = _seri([50, 55, 62, 70, 60, 52, 65, 80])
    d = zigzag_donusler(fiyat, 0.20)
    assert d[0] == (fiyat.index[0], "dip")
    assert d[1] == (fiyat.index[3], "tepe")
    assert d[2] == (fiyat.index[5], "dip")
    poz = dip_tepe_kahini(fiyat, 0.20)
    ozk, _ = geri_test(fiyat, poz)
    # 50→70 ve 52→80 turları; son tur teyitsiz ama kâhin en yüksekte satar
    assert ozk.iloc[-1] == pytest.approx((70 / 50) * (80 / 52))


def test_kahin_zigzag_gercek_veride_makul():
    df = veri_yukle().loc["1950":]
    fiyat = df["fiyat"]
    poz = dip_tepe_kahini(fiyat, 0.20)
    _, s_k = geri_test(fiyat, poz)
    _, s_bh = geri_test(fiyat, al_ve_tut(fiyat))
    assert s_k.islem_sayisi >= 10  # 1950 sonrası birden çok %20'lik ayı piyasası var
    assert s_k.son_deger > s_bh.son_deger
    assert s_k.max_dusus > -0.20 - 1e-9


def test_kahin_zigzag_dipten_alir_tepeden_satar():
    fiyat = _seri([100, 90, 70, 60, 75, 90, 110, 120, 100, 90])
    poz = dip_tepe_kahini(fiyat, 0.20)
    ozk, s = geri_test(fiyat, poz)
    assert ozk.iloc[-1] == pytest.approx(120 / 60)
    tablo = gecikme_analizi(fiyat, poz)
    assert tablo["dipten_uzaklik"].iloc[0] == pytest.approx(0.0)
    assert tablo["tepeden_uzaklik"].iloc[0] == pytest.approx(0.0)


def test_gecikme_analizi_sma_dipten_uzak_alir():
    # V şekli: SMA kuralı dipten sonra girer, dolayısıyla dipten_uzaklik > 0
    v = np.concatenate([np.linspace(100, 50, 15), np.linspace(50, 130, 25)])
    fiyat = _seri(v)
    poz = sma_kurali(fiyat, 6)
    tablo = gecikme_analizi(fiyat, poz)
    assert len(tablo) >= 1
    assert tablo["dipten_uzaklik"].iloc[-1] > 0.05
    ozet = gecikme_ozeti(tablo)
    assert ozet["tur_sayisi"] >= 0


def test_ileriye_donuk_pencereler_ve_secim():
    rng = np.random.default_rng(1)
    fiyat = _seri(np.cumprod(1 + rng.normal(0.004, 0.04, 600)))
    tablo, poz = ileriye_donuk(fiyat, [3, 6, 12], egitim_ay=240, test_ay=120)
    assert len(tablo) == 3
    assert set(tablo["secilen_n"]).issubset({3, 6, 12})
    ilk = pd.Timestamp(tablo["test_bas"].iloc[0])
    assert poz.loc[:ilk].iloc[:-1].sum() == 0  # test öncesi pozisyon yok
    assert set(poz.unique()).issubset({0, 1})


def test_gercek_veri_uzerinde_calisir():
    df = veri_yukle().loc["1990":"2000"]
    fiyat = df["fiyat"]
    _, s = geri_test(fiyat, sma_kurali(fiyat, 10), 0.001)
    assert np.isfinite(s.cagr)
    assert 0 < s.piyasada_oran <= 1
