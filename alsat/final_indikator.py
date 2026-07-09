"""FİNAL İNDİKATÖR — Donchian kanal kırılımı (giriş 20 gün, çıkış 10 gün).

Reviewer 2 döngüsünün (bkz. alsat/RAPOR.md) 2. turda KABUL ettiği kural. Bu dosya
tek başına kopyalanıp kullanılabilir; bağımlılığı yalnızca pandas/numpy'dir.

Kural (kapanış tabanlı, günlük mumlar, long/flat):
  AL  → bugünkü kapanış, önceki 20 günün en yüksek kapanışını aşarsa
  SAT → bugünkü kapanış, önceki 10 günün en düşük kapanışının altına inerse
  aksi hâlde mevcut pozisyon korunur.

Literatür: Brock-Lakonishok-LeBaron (1992) "trading range break"; Donchian kanalı;
kripto kanıtı için Detzel ve ark. (2021), Hudson & Urquhart (2021).

Walk-forward doğrulaması (BTC+ETH+BNB+XRP+ADA eşit ağırlıklı, 2013–2026 OOS,
20 bps maliyet): net Sharpe 1.76, yıllık ≈%138, maks düşüş -%65 (satın-al-tut:
1.36 / %126 / -%87). Sembol bazında OOS Sharpe 0.97–1.53; isabet oranı ~%47–54
(kırılım sistemlerinde normaldir: çok küçük zarar, az büyük kazanç). Kuralın gücü
portföy düzeyindedir — tek sembolde aylarca süren zarar serisi beklenen davranıştır.

UYARILAR — bunlar pazarlama notu değil, sonucun parçasıdır:
* Sinyal t günü KAPANIŞINDA üretilir ve en erken t+1'de uygulanabilir; aynı gün
  uygulama backtest'te Sharpe'ı yapay olarak şişirir (H1 denetimi).
* Geçmiş performans gelecek getirinin garantisi değildir; kural trend dönemlerinde
  çalışır, yatay piyasada testere (whipsaw) zararı üretir. Yatırım tavsiyesi değildir.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

GIRIS_PENCERE = 20
CIKIS_PENCERE = 10


def al_sat_sinyali(kapanis: pd.Series,
                   giris: int = GIRIS_PENCERE,
                   cikis: int = CIKIS_PENCERE) -> pd.Series:
    """Günlük kapanış serisinden hedef pozisyon üretir: 1 = uzun, 0 = nakit.

    Dönen seri t günü kapanışında bilinen karardır; işlem t+1'de yapılmalıdır.
    """
    kapanis = kapanis.astype(float)
    ust = kapanis.shift(1).rolling(giris).max()
    alt = kapanis.shift(1).rolling(cikis).min()
    ham = pd.Series(np.nan, index=kapanis.index)
    ham[kapanis > ust] = 1.0
    ham[kapanis < alt] = 0.0
    return ham.ffill().fillna(0.0)


def evrensel_al_sat_sinyali(kapanis: pd.Series, kisa: int = 50,
                            uzun: int = 200) -> pd.Series:
    """EVRENSEL MOD — altın kesişim (SMA 50/200): 1 = uzun, 0 = nakit.

    Kripto + 486 S&P 500 hissesi üzerinde yapılan sınıflar-arası turnuvada
    (bkz. RAPOR.md Koşu 3) "her sembolde çalışma" ölçütünü (en kötü sınıfın
    medyan Sharpe'ı) en iyi sağlayan kural. Kaynak: Faber (2007) uzun-pencere
    trend kuralları; Brock ve ark. (1992) MA kesişimi. Hisselerde %78, kriptoda
    %100 sembolde pozitif net Sharpe üretti; buna karşılık boğa piyasasında
    satın-al-tut'u nadiren geçer — gücü, derin düşüşleri sınırlamasındadır.
    Kripto SADECE kullanılacaksa Donchian 20/10 (yukarıdaki kural) tercih edilir.
    """
    kapanis = kapanis.astype(float)
    k = kapanis.rolling(kisa).mean()
    u = kapanis.rolling(uzun).mean()
    return (k > u).astype(float)


def son_karar(kapanis: pd.Series) -> str:
    """İnsan-okur özet: serinin son günü için AL / SAT / BEKLE(pozisyonda) / BEKLE(nakitte)."""
    poz = al_sat_sinyali(kapanis)
    bugun, dun = poz.iloc[-1], (poz.iloc[-2] if len(poz) > 1 else 0.0)
    if bugun > dun:
        return "AL (yarın geçerli)"
    if bugun < dun:
        return "SAT (yarın geçerli)"
    return "BEKLE — pozisyonda kal" if bugun > 0 else "BEKLE — nakitte kal"
