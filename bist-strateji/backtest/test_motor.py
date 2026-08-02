"""Motor ve indikatör doğruluk testleri (elle hesaplanmış küçük örneklerle)."""
from __future__ import annotations

import numpy as np
import pytest

from . import indikatorler as ind
from .motor import backtest
from .veri import haftalik, sentetik_bist


def test_sma_ema_temel():
    x = np.array([1, 2, 3, 4, 5], dtype=float)
    s = ind.sma(x, 3)
    assert np.isnan(s[1])
    assert s[2] == pytest.approx(2.0)
    assert s[4] == pytest.approx(4.0)
    e = ind.ema(x, 3)
    assert e[2] == pytest.approx(2.0)          # SMA tohumu
    assert e[3] == pytest.approx(0.5 * 4 + 0.5 * 2.0)
    assert e[4] == pytest.approx(0.5 * 5 + 0.5 * 3.0)


def test_rsi_wilder_bilinen_deger():
    # Tümü yükselen seri → RSI 100; tümü düşen → RSI 0
    up = np.arange(1, 30, dtype=float)
    assert ind.rsi(up, 14)[-1] == pytest.approx(100.0)
    dn = np.arange(30, 1, -1, dtype=float)
    assert ind.rsi(dn, 14)[-1] == pytest.approx(0.0)


def test_atr_sabit_aralik():
    n = 30
    high = np.full(n, 12.0)
    low = np.full(n, 10.0)
    close = np.full(n, 11.0)
    a = ind.atr(high, low, close, 14)
    assert a[-1] == pytest.approx(2.0)  # her bar TR=2 → ATR=2


def test_supertrend_yon_degisimi():
    # Kesintisiz güçlü yükseliş → yön +1; ardından sert düşüş → -1
    n = 120
    c = np.concatenate([np.linspace(100, 200, 60), np.linspace(200, 120, 60)])
    h = c * 1.01
    l = c * 0.99
    _, yon = ind.supertrend(h, l, c, 10, 3.0)
    assert yon[55] == 1
    assert yon[-1] == -1


def test_donchian():
    h = np.array([1, 2, 3, 2, 1], dtype=float)
    l = h - 0.5
    ust, alt = ind.donchian(h, l, 3)
    assert ust[2] == pytest.approx(3.0)
    assert alt[4] == pytest.approx(0.5)


def test_backtest_sonraki_acilis_ve_komisyon():
    # 4 bar: sinyal 1. barın kapanışında → 2. barın açılışında (100) alım,
    # sinyal 2. barda 0 → 3. barın açılışında (110) satış. Komisyon %1.
    o = np.array([90.0, 100.0, 110.0, 111.0])
    h = o + 1
    l = o - 1
    c = np.array([95.0, 105.0, 110.5, 111.0])
    sinyal = np.array([1.0, 0.0, 0.0, 0.0])
    r = backtest(o, h, l, c, sinyal, komisyon_yuzde=1.0)
    # Alım: 1 TL * 0.99 / 100 = 0.0099 lot; Satış: 0.0099 * 110 * 0.99 = 1.078...
    beklenen = 0.99 / 100 * 110 * 0.99
    assert r.equity[-1] == pytest.approx(beklenen)
    assert r.islem_sayisi == 1
    assert r.islemler[0]["giris_px"] == 100.0
    assert r.islemler[0]["cikis_px"] == 110.0
    assert r.kazanma_orani == 100.0


def test_backtest_hodl_ile_ayni_surekli_long():
    rng = np.random.default_rng(1)
    n = 200
    c = 100 * np.exp(np.cumsum(rng.normal(0.001, 0.01, n)))
    o = np.roll(c, 1); o[0] = 100.0
    h = np.maximum(o, c) * 1.001
    l = np.minimum(o, c) * 0.999
    sinyal = np.ones(n)
    r = backtest(o, h, l, c, sinyal, komisyon_yuzde=0.0)
    # İlk barda alım yapılamaz (sinyal önceki bar gerekir) → 2. bar açılışından itibaren long
    beklenen = c[-1] / o[1]
    assert r.equity[-1] == pytest.approx(beklenen, rel=1e-9)


def test_stop_bar_ici_calisir():
    # Pine parite: bar 1 kapanışında konan stop (97) bar 2 boyunca geçerlidir;
    # bar 2'de low=94 stopu kırar → çıkış 97'den.
    o = np.array([100.0, 100.0, 100.0, 100.0])
    h = np.array([101.0, 101.0, 101.0, 101.0])
    l = np.array([99.0, 99.0, 94.0, 99.0])
    c = np.array([100.0, 100.5, 95.0, 99.0])
    sinyal = np.array([1.0, 1.0, 1.0, 1.0])
    stop = np.array([np.nan, 97.0, 97.0, np.nan])
    r = backtest(o, h, l, c, sinyal, komisyon_yuzde=0.0, stop_seviyesi=stop)
    assert r.islemler[0].get("stop") is True
    assert r.islemler[0]["cikis_px"] == 97.0
    assert r.islemler[0]["cikis_i"] == 2


def test_sentetik_veri_tutarli():
    df = sentetik_bist(n_gun=500, seed=42)
    assert len(df) == 500
    assert (df["high"] >= df[["open", "close"]].max(axis=1) - 1e-9).all()
    assert (df["low"] <= df[["open", "close"]].min(axis=1) + 1e-9).all()
    hf = haftalik(df)
    assert 90 <= len(hf) <= 110
    # Haftalık bar, haftanın günlük barlarını kapsamalı
    assert hf["high"].iloc[0] >= hf[["open", "close"]].iloc[0].max() - 1e-9


def test_ayni_seed_ayni_veri():
    a = sentetik_bist(n_gun=100, seed=7)
    b = sentetik_bist(n_gun=100, seed=7)
    assert np.allclose(a["close"], b["close"])


def test_kazanan_strateji_regresyon():
    """Doğrulanmış kazanan parametrelerin davranışını sabitler (seed 100).

    Bu test kırılırsa strateji/motor/veri değişikliği doğrulanmış sonuçları
    geçersiz kılmıştır — SONUCLAR.md yeniden üretilmelidir.
    """
    from .optimize import kos, veri_seti

    p = {"sma_gun": 131, "mom_gun": 284, "band_yuzde": 3.0, "be_giris": 0}
    vs = veri_seti(100)
    r = kos("rejim_filtre", p, vs["gunluk"], 252.0)
    assert r.islem_sayisi == 2
    assert r.net_kar_yuzde == pytest.approx(3635.271, abs=0.5)
    assert r.hodl_yuzde == pytest.approx(3305.978, abs=0.5)
    assert r.maks_dusus == pytest.approx(23.15, abs=0.05)
    rh = kos("rejim_filtre", p, vs["haftalik"], 52.0)
    assert rh.islem_sayisi == 2
    assert rh.net_kar_yuzde == pytest.approx(3235.898, abs=0.5)


def test_zirve_stop_regresyon():
    """Zirve İz Stop doğrulanmış parametrelerinin davranışını sabitler (seed 100)."""
    from .optimize import kos, veri_seti

    p = {"esik": 10, "sma_gun": 100, "mom_gun": 284, "be": 1}
    vs = veri_seti(100)
    r = kos("tepe_iz_stop", p, vs["gunluk"], 252.0)
    assert r.islem_sayisi == 21
    assert r.net_kar_yuzde == pytest.approx(3080.394, abs=0.5)
    rh = kos("tepe_iz_stop", p, vs["haftalik"], 52.0)
    assert rh.islem_sayisi == 11
    assert rh.net_kar_yuzde == pytest.approx(3688.536, abs=0.5)
