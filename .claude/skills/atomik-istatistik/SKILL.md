---
name: atomik-istatistik
description: >-
  İstatistiksel ve hesaplamalı yöntemlerin 9 sütunlu (Sütun 0–8) kapsamlı
  taksonomisini ("Atomic Registry of the Statistical Universe v2") üretir veya
  günceller. Kullanıcı "atomik istatistik", "atomic statistics", "istatistik
  evreni", "Atomic Registry" ya da istatistik/ML yöntem haritası/sınıflandırması
  istediğinde kullan.
---

# Atomik İstatistik Registry Skill

## Amaç
İstatistik + makine öğrenmesi + nedensellik + zaman serisi yöntemlerinin
**9 sütunlu kapsamlı taksonomisini** sunmak, gözden geçirmek veya güncellemek.

## Kaynak (referans dosya)
Tam ve güncel sınıflandırma şurada tutulur:
- `docs/atomic-statistics-registry.md` (bu repoda)

Bu dosya mevcutsa **önce onu oku** ve kaynak doğruluğu için onu temel al.
Yoksa aşağıdaki iskeleti kullanarak yeniden üret.

## 9 Sütunlu Mimari (özet iskelet)
| # | Sütun | Rol |
|---|-------|-----|
| 0 | Metodolojik Temeller (Bootstrap, CV, optimizasyon, AIC/BIC, çoklu karşılaştırma) | Zemin |
| 1 | Frequentist Inference (parametrik/non-parametrik/GoF/survival/mixed) | Yargıç |
| 2 | Predictive / Algorithmic ML (lineer, ağaç, ensemble, deep, unsupervised) | Kâhin |
| 3 | Causal Inference (SCM, quasi-exp, g-methods, discovery) | Mühendis |
| 4 | Bayesian Probability (sampling/VI, model tipleri, nonparametric) | Filozof |
| 5 | Information Theory (entropi, karmaşıklık, Fisher info, PID) | Sinyalci |
| 6 | Cybernetics / Dynamic (RL, bandits, kontrol, oyun teorisi) | Karar Verici |
| 7 | Time Series & Stochastic (ARIMA, GARCH, VAR, Granger, wavelet) | Tarihçi |
| 8 | Structural / Geometric (graph, ağ modelleri, TDA, chaos, spatial) | Geometrist |

## Davranış kuralları
1. **Üretme isteği** ("atomik istatistik göster/yap") → referans dosyadan tam tabloyu sun.
2. **Güncelleme isteği** ("ekle/düzelt/çıkar") → `docs/atomic-statistics-registry.md`'yi
   güncelle ve belge sonundaki "Değişiklik Özeti" mantığıyla sürüm notu ekle.
3. **PDF isteği** → Markdown'ı stillenmiş HTML'e çevir, Chromium headless ile PDF üret:
   `chrome --headless --no-sandbox --print-to-pdf=out.pdf file://.../in.html`,
   sonra dosyayı kullanıcıya gönder.
4. **Çerçeve**: "eksiksiz/complete" iddiası yerine "kapsamlı ve genişletilebilir referans".
