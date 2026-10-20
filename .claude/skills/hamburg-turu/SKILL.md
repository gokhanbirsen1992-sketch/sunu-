---
name: hamburg-turu
description: Hamburg seyahatini sıfırdan planlayan ajan ordusu — uçuş, otel, transfer/ulaşım, gün gün gezi programı, vize/belge/pratik bilgi ve bütçe; sonunda denetçi ajan kaynak doğrulaması yapar. Kullanım — /hamburg-turu [gidiş YYYY-MM-DD] [dönüş YYYY-MM-DD] [kişi] [kalkış IATA]. Varsayılan 2026-12-07 → 2026-12-13, 1 kişi, AYT.
---
# /hamburg-turu — Orkestratör

## 1. Parametreler
Argümanları ayrıştır; eksikse `protokol.md` varsayılanlarını kullan. Değişen varsayılan varsa `protokol.md` tablosunu güncelle (ajanlar oradan okur).
Çıktı klasörü: `seyahat/hamburg-<ay>-<yıl>/` (varsayılan `seyahat/hamburg-aralik-2026/`).

## 2. Paralel işçi ajanlar (tek mesajda 5 `Agent` çağrısı, arka planda)
Her birine şu brief: "Önce `.claude/skills/hamburg-turu/protokol.md` ve kendi tanımını (`.claude/agents/<ad>.md`) oku; talimatları uygula; çıktıyı belirtilen dosyaya yaz; 10 satırlık özet döndür."

| # | Ajan | Dosya |
|---|---|---|
| 01 | hamburg-ucus-ajani | 01-ucus.md |
| 02 | hamburg-otel-ajani | 02-otel.md |
| 03 | hamburg-transfer-ajani | 03-transfer-ulasim.md |
| 04 | hamburg-gezi-ajani | 04-gezi-programi.md |
| 05 | hamburg-belge-butce-ajani | 05-belge-pratik.md |

Bu oturumda özel ajan tipleri yüklü değilse `subagent_type: general-purpose` ile aynı brief'i gönder.

## 3. Derleme → `PLAN.md`
Tüm raporlar geldikten sonra orkestratör:
1. Uçuş varış/kalkış saatlerini transfer ve gezi programıyla çaprazlar; çelişkiyi yazar.
2. Bütçeyi `05` şablonuna `01–04` sayılarıyla doldurur; toplamı **python ile** hesaplar (`[çıkarım]`), kuru `05`'teki tarihli kaynaktan alır.
3. `PLAN.md`: 1 sayfalık özet (tarihler, seçilen uçuş/otel, toplam bütçe, vize son tarihi) → gün gün program → rezervasyon yapılacaklar listesi (tarih sırası) → açık noktalar → dosya dizini.

## 4. Denetim
`hamburg-denetci-ajani`'yi (veya general-purpose ile aynı brief) çalıştır → `DENETIM.md`. Kırmızı bayrak varsa ilgili dosyayı düzelt, PLAN.md'yi güncelle, denetimi yeniden çalıştır (en fazla 2 tur).

## 5. Teslim
Kullanıcıya: PLAN.md yolu, güvenilirlik özeti (kesin/doğrulanmalı/çıkarım sayıları), karar bekleyen maddeler. Commit + push.
