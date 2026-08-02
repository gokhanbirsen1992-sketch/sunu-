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


def _gun2bar(p: dict, n_gun: float) -> int:
    """'İşlem günü' cinsinden periyodu bar sayısına çevirir (günlük→aynı, haftalık→/5)."""
    bpy = float(p.get("_bpy", 252.0))
    return max(2, int(round(n_gun * bpy / 252.0)))


def faber_sma(o, h, l, c, v, p):
    """Faber (2007) trend filtresi + Zakamulin histerezis bandı.

    Giriş: kapanış > SMA(n)*(1+band); Çıkış: kapanış < SMA(n)*(1-band).
    Bant, testere (whipsaw) işlemlerini azaltır. n işlem günü cinsindendir.
    """
    n = _gun2bar(p, p["sma_gun"])
    band = float(p.get("band_yuzde", 0.0)) / 100.0
    s = ind.sma(c, n)
    sinyal = np.zeros(len(c))
    sinyal[0] = 1.0
    for i in range(1, len(c)):
        if np.isnan(s[i]):
            sinyal[i] = 1.0  # ısınma döneminde piyasada kal (HODL ile aynı başla)
            continue
        if sinyal[i - 1] == 0:
            sinyal[i] = 1.0 if c[i] > s[i] * (1 + band) else 0.0
        else:
            sinyal[i] = 0.0 if c[i] < s[i] * (1 - band) else 1.0
    return sinyal, None


def mutlak_momentum(o, h, l, c, v, p):
    """Mutlak momentum (Antonacci 2014): n günlük getiri histerezisli.

    Giriş: ROC(n) > giris_esik; Çıkış: ROC(n) < cikis_esik (negatif eşik =
    yavaş çıkış). Zaman-serisi momentumu: Moskowitz-Ooi-Pedersen (2012).
    """
    n = _gun2bar(p, p["mom_gun"])
    r = ind.roc(c, n)
    ge = float(p.get("giris_esik", 0.0))
    ce = float(p.get("cikis_esik", 0.0))
    sinyal = np.zeros(len(c))
    sinyal[0] = 1.0
    for i in range(1, len(c)):
        if np.isnan(r[i]):
            sinyal[i] = 1.0  # ısınma döneminde piyasada kal
            continue
        if sinyal[i - 1] == 0:
            sinyal[i] = 1.0 if r[i] > ge else 0.0
        else:
            sinyal[i] = 0.0 if r[i] < ce else 1.0
    return sinyal, None


def rejim_filtre(o, h, l, c, v, p):
    """Varsayılan pozisyon LONG; sadece ÇİFTE ayı teyidinde çıkar.

    Çıkış: kapanış < SMA(nL)*(1-band) VE ROC(nM) < 0 (iki yavaş sinyal aynı anda).
    Geri giriş: kapanış > SMA(nL) VEYA ROC(nM) > 0 (hızlı dönüş — boğayı kaçırma),
    ayrıca be_giris=1 ise kapanış çıkış fiyatını aşarsa da geri gir (breakeven
    kuralı, Kaminski & Lo 2014: yanlış alarmın maliyetini 2 komisyona sabitler).
    Amaç: piyasada kalma süresini maksimize edip yalnızca gerçek ayıları atlamak.
    (Faber 2007 + Antonacci 2014 bileşimi, asimetrik histerezis.)
    """
    nL = _gun2bar(p, p["sma_gun"])
    nM = _gun2bar(p, p["mom_gun"])
    band = float(p.get("band_yuzde", 0.0)) / 100.0
    be = int(p.get("be_giris", 0)) == 1
    s = ind.sma(c, nL)
    r = ind.roc(c, nM)
    sinyal = np.zeros(len(c))
    sinyal[0] = 1.0
    cikis_px = np.nan
    for i in range(1, len(c)):
        if np.isnan(s[i]) or np.isnan(r[i]):
            sinyal[i] = 1.0  # ısınma döneminde piyasada kal (HODL ile aynı başla)
            continue
        if sinyal[i - 1] == 1:
            if c[i] < s[i] * (1 - band) and r[i] < 0:
                sinyal[i] = 0.0
                cikis_px = c[i]
            else:
                sinyal[i] = 1.0
        else:
            geri = c[i] > s[i] or r[i] > 0
            if be and not np.isnan(cikis_px):
                geri = geri or c[i] > cikis_px
            sinyal[i] = 1.0 if geri else 0.0
    return sinyal, None


def supertrend_yavas(o, h, l, c, v, p):
    """Çok yavaş Supertrend: geniş çarpanla yalnızca büyük ayılarda çıkış."""
    n = _gun2bar(p, p["st_gun"])
    _, yon = ind.supertrend(h, l, c, n, float(p["st_mult"]))
    sinyal = (yon == 1).astype(float)
    # Isınma döneminde piyasada kal (HODL ile aynı başlangıç)
    ilk = np.argmax(yon != 0) if (yon != 0).any() else len(c)
    sinyal[:ilk] = 1.0
    return sinyal, None


def tepe_dip_bant(o, h, l, c, v, p):
    """Tepe-Dip Bandı: güce sat, zayıflığa al (trend çapalı ortalamaya dönüş).

    Sapma d = kapanış/SMA(sma_gun) - 1.
    - Varsayılan LONG.
    - TEPE SATIŞI: d > ust_esik (aşırı uzama — güce satış).
    - DİP ALIMI: d < geri_esik (ortalamaya dönüş) → geri gir.
    - Kaçırma sigortası: satış sonrası fiyat çıkış fiyatının (1+kacirma)%
      üstüne koşarsa geri gir (ralli devam ediyorsa dışarıda kalma maliyeti sınırlanır).
    - KRİZ ÇIKIŞI (isteğe bağlı): kapanış < SMA*(1-kriz_band) VE ROC(mom_gun)<0
      → çık; geri giriş rejim kuralı (kapanış > SMA VEYA ROC > 0).
    Literatür: Bollinger bant dönüşü, aşırılık satışı (mean reversion), Faber
    kriz filtresi bileşimi.
    """
    nS = _gun2bar(p, p["sma_gun"])
    nM = _gun2bar(p, p.get("mom_gun", 284))
    ust = float(p["ust_esik"]) / 100.0
    geri = float(p.get("geri_esik", 0.0)) / 100.0
    kacirma = float(p.get("kacirma", 0.0)) / 100.0
    kriz_band = float(p.get("kriz_band", 0.0)) / 100.0
    s = ind.sma(c, nS)
    r = ind.roc(c, nM)
    n = len(c)
    sinyal = np.zeros(n)
    sinyal[0] = 1.0
    DURUM_LONG, DURUM_TEPE, DURUM_KRIZ = 1, 2, 3
    durum = DURUM_LONG
    cikis_px = np.nan
    tepe_kurulu = True  # kaçırma sigortasıyla girişte, sapma eşiğin altına inene
    for i in range(1, n):  # kadar tepe satışı devre dışı (aynı barda tekrar satmasın)
        if np.isnan(s[i]) or np.isnan(r[i]):
            sinyal[i] = 1.0  # ısınmada piyasada kal
            continue
        d = c[i] / s[i] - 1.0
        if durum == DURUM_LONG:
            if not tepe_kurulu and d < ust:
                tepe_kurulu = True
            if kriz_band > 0 and c[i] < s[i] * (1 - kriz_band) and r[i] < 0:
                durum = DURUM_KRIZ
            elif tepe_kurulu and d > ust:
                durum = DURUM_TEPE
                cikis_px = c[i]
        elif durum == DURUM_TEPE:
            if d < geri:
                durum = DURUM_LONG          # dip alımı: ortalamaya döndü
                tepe_kurulu = True
            elif kacirma > 0 and c[i] > cikis_px * (1 + kacirma):
                durum = DURUM_LONG          # kaçırma sigortası — tepe satışı yeniden
                tepe_kurulu = False         # kurulana kadar askıda
            elif kriz_band > 0 and c[i] < s[i] * (1 - kriz_band) and r[i] < 0:
                durum = DURUM_KRIZ          # beklerken kriz teyidi geldi
        else:  # DURUM_KRIZ
            if c[i] > s[i] or r[i] > 0:
                durum = DURUM_LONG
                tepe_kurulu = True
        sinyal[i] = 1.0 if durum == DURUM_LONG else 0.0
    return sinyal, None


def tepe_iz_stop(o, h, l, c, v, p):
    """Zirve İz Stop: pozisyon zirvesinden esik% düşünce sat — tepeye yakın satış.

    Satış her zaman son zirvenin en fazla esik% altında gerçekleşir (dipte değil).
    Geri giriş: kapanış > SMA(sma_gun) VEYA ROC(mom_gun) > 0 (rejim kuralı);
    be=1 ise ayrıca kapanış çıkış fiyatını aşarsa (breakeven, yanlış alarmın
    maliyetini 2 komisyona sabitler). Doğrulama: endeks profili, 3 aşama GEÇTİ.
    """
    nS = _gun2bar(p, p.get("sma_gun", 100))
    nM = _gun2bar(p, p.get("mom_gun", 284))
    esik = float(p["esik"]) / 100.0
    be = int(p.get("be", 1)) == 1
    s = ind.sma(c, nS)
    r = ind.roc(c, nM)
    n = len(c)
    sinyal = np.zeros(n)
    sinyal[0] = 1.0
    zirve = c[0]
    cikis_px = np.nan
    for i in range(1, n):
        if np.isnan(s[i]) or np.isnan(r[i]):
            sinyal[i] = 1.0
            zirve = max(zirve, c[i])
            continue
        if sinyal[i - 1] == 1:
            zirve = max(zirve, c[i])
            if c[i] < zirve * (1 - esik):
                sinyal[i] = 0.0
                cikis_px = c[i]
            else:
                sinyal[i] = 1.0
        else:
            geri = c[i] > s[i] or r[i] > 0
            if be and not np.isnan(cikis_px):
                geri = geri or c[i] > cikis_px
            if geri:
                sinyal[i] = 1.0
                zirve = c[i]
            else:
                sinyal[i] = 0.0
    return sinyal, None


AILELER = {
    "supertrend_adx": supertrend_adx,
    "ema_cross_macd": ema_cross_macd,
    "donchian_turtle": donchian_turtle,
    "kama_roc": kama_roc,
    "rsi_meanrev": rsi_meanrev,
    "komposit": komposit,
    "faber_sma": faber_sma,
    "mutlak_momentum": mutlak_momentum,
    "rejim_filtre": rejim_filtre,
    "supertrend_yavas": supertrend_yavas,
    "tepe_dip_bant": tepe_dip_bant,
    "tepe_iz_stop": tepe_iz_stop,
}
