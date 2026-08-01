"""Strateji aileleri — literatürdeki başlıca yaklaşımlar.

Her strateji fonksiyonu (open, high, low, close, volume, params) alır ve
(sinyal, stop) döndürür:
- sinyal[i] ∈ {0, 1}: i barı kapanışında istenen pozisyon (bakış açısı sızıntısı yok;
  yalnızca i ve öncesi veriyi kullanır). Motor, i+1 açılışında uygular.
- stop: bar içi iz süren stop seviyesi dizisi ya da None.
"""
from __future__ import annotations

import numpy as np

from . import indikatorler as ind


def supertrend_adx(o, h, l, c, v, p):
    """Supertrend (Seban) + ADX (Wilder) trend gücü filtresi."""
    _, yon = ind.supertrend(h, l, c, int(p["st_n"]), float(p["st_mult"]))
    sinyal = (yon == 1).astype(float)
    if p.get("adx_esik", 0) > 0:
        a, _, _ = ind.adx(h, l, c, int(p.get("adx_n", 14)))
        guclu = a > float(p["adx_esik"])
        # ADX zayıfken YENİ giriş yok; mevcut pozisyon Supertrend dönene dek korunur
        out = np.zeros_like(sinyal)
        for i in range(1, len(sinyal)):
            if sinyal[i] == 1 and (out[i - 1] == 1 or (not np.isnan(a[i]) and guclu[i])):
                out[i] = 1
        sinyal = out
    return sinyal, None


def ema_cross_macd(o, h, l, c, v, p):
    """EMA kesişimi (Brock-Lakonishok-LeBaron 1992) + MACD (Appel) onayı."""
    hizli = ind.ema(c, int(p["hizli"]))
    yavas = ind.ema(c, int(p["yavas"]))
    _, _, hist = ind.macd(c, int(p.get("macd_hizli", 12)), int(p.get("macd_yavas", 26)), int(p.get("macd_sinyal", 9)))
    sinyal = ((hizli > yavas) & (hist > 0)).astype(float)
    sinyal[np.isnan(hizli) | np.isnan(yavas) | np.isnan(hist)] = 0
    return sinyal, None


def donchian_turtle(o, h, l, c, v, p):
    """Donchian kırılımı (Turtle/Dennis): n-bar zirve kırılırsa gir, m-bar dip kırılırsa çık."""
    ust, _ = ind.donchian(h, l, int(p["giris_n"]))
    _, alt = ind.donchian(h, l, int(p["cikis_n"]))
    n = len(c)
    sinyal = np.zeros(n)
    for i in range(1, n):
        if np.isnan(ust[i - 1]) or np.isnan(alt[i - 1]):
            continue
        if sinyal[i - 1] == 0:
            sinyal[i] = 1.0 if c[i] > ust[i - 1] else 0.0
        else:
            sinyal[i] = 0.0 if c[i] < alt[i - 1] else 1.0
    stop = None
    if p.get("atr_stop_mult", 0) > 0:
        stop = _iz_suren_atr_stop(h, l, c, sinyal, int(p.get("atr_n", 22)), float(p["atr_stop_mult"]))
    return sinyal, stop


def kama_roc(o, h, l, c, v, p):
    """KAMA (Kaufman 1998) trendi + momentum (Jegadeesh-Titman 1993) onayı."""
    k = ind.kama(c, int(p["kama_n"]), int(p.get("kama_hizli", 2)), int(p.get("kama_yavas", 30)))
    mom = ind.roc(c, int(p["roc_n"]))
    sinyal = ((c > k) & (mom > float(p.get("roc_esik", 0.0)))).astype(float)
    sinyal[np.isnan(k) | np.isnan(mom)] = 0
    return sinyal, None


def rsi_meanrev(o, h, l, c, v, p):
    """Ortalamaya dönüş (kontrol grubu): RSI (Wilder) aşırı satımda al, aşırı alımda sat."""
    r = ind.rsi(c, int(p["rsi_n"]))
    n = len(c)
    sinyal = np.zeros(n)
    for i in range(1, n):
        if np.isnan(r[i]):
            continue
        if sinyal[i - 1] == 0:
            sinyal[i] = 1.0 if r[i] < float(p["alt"]) else 0.0
        else:
            sinyal[i] = 0.0 if r[i] > float(p["ust"]) else 1.0
    return sinyal, None


def komposit(o, h, l, c, v, p):
    """Çok-indikatörlü oylama sistemi (Pine indikatörünün birebir Python karşılığı).

    Oylar (her biri 0/1):
      1. Supertrend yönü yukarı
      2. EMA(hizli) > EMA(yavas)
      3. MACD histogram > 0
      4. RSI > rsi_esik (momentum rejimi, Wilder)
      5. Fiyat Donchian orta hattının üzerinde
      6. +DI > -DI (Wilder yön hakimiyeti)
    Giriş: puan >= giris_esik; Çıkış: puan <= cikis_esik veya Chandelier stop.
    """
    _, st_yon = ind.supertrend(h, l, c, int(p["st_n"]), float(p["st_mult"]))
    e_hizli = ind.ema(c, int(p["ema_hizli"]))
    e_yavas = ind.ema(c, int(p["ema_yavas"]))
    _, _, hist = ind.macd(c)
    r = ind.rsi(c, int(p.get("rsi_n", 14)))
    dc_ust, dc_alt = ind.donchian(h, l, int(p.get("dc_n", 20)))
    dc_orta = (dc_ust + dc_alt) / 2.0
    _, pdi, mdi = ind.adx(h, l, c, int(p.get("adx_n", 14)))

    oy = (
        (st_yon == 1).astype(float)
        + np.where(~np.isnan(e_hizli) & ~np.isnan(e_yavas) & (e_hizli > e_yavas), 1.0, 0.0)
        + np.where(~np.isnan(hist) & (hist > 0), 1.0, 0.0)
        + np.where(~np.isnan(r) & (r > float(p.get("rsi_esik", 50))), 1.0, 0.0)
        + np.where(~np.isnan(dc_orta) & (c > dc_orta), 1.0, 0.0)
        + np.where(~np.isnan(pdi) & ~np.isnan(mdi) & (pdi > mdi), 1.0, 0.0)
    )
    n = len(c)
    sinyal = np.zeros(n)
    for i in range(1, n):
        if sinyal[i - 1] == 0:
            sinyal[i] = 1.0 if oy[i] >= float(p["giris_esik"]) else 0.0
        else:
            sinyal[i] = 0.0 if oy[i] <= float(p["cikis_esik"]) else 1.0
    stop = None
    if p.get("chand_mult", 0) > 0:
        stop = _iz_suren_atr_stop(h, l, c, sinyal, int(p.get("chand_n", 22)), float(p["chand_mult"]))
    return sinyal, stop


def _iz_suren_atr_stop(h, l, c, sinyal, n, mult):
    """Chandelier Exit (LeBeau) mantığında iz süren stop: pozisyon içi HH - mult*ATR.

    Stop yalnızca yukarı güncellenir (ratchet). Pozisyon dışında NaN.
    """
    atr_ = ind.atr(h, l, c, n)
    stop = np.full(len(c), np.nan)
    aktif = False
    seviye = np.nan
    hh = np.nan
    for i in range(1, len(c)):
        if sinyal[i - 1] == 1 and not aktif:
            aktif = True
            hh = h[i]
            seviye = hh - mult * atr_[i] if not np.isnan(atr_[i]) else np.nan
        elif sinyal[i - 1] == 0:
            aktif = False
            seviye = np.nan
        if aktif:
            hh = max(hh, h[i])
            if not np.isnan(atr_[i]):
                yeni = hh - mult * atr_[i]
                seviye = yeni if np.isnan(seviye) else max(seviye, yeni)
            stop[i] = seviye
    return stop


AILELER = {
    "supertrend_adx": supertrend_adx,
    "ema_cross_macd": ema_cross_macd,
    "donchian_turtle": donchian_turtle,
    "kama_roc": kama_roc,
    "rsi_meanrev": rsi_meanrev,
    "komposit": komposit,
}
