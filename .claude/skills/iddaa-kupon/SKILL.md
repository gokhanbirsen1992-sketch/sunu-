---
name: iddaa-kupon
description: Günlük spor bültenine bakıp The Odds API'den oranları çekerek value-bet (EV) bazlı 3 farklı risk profilinde (güvenli / dengeli / riskli) iddaa kuponu önerir. Kullanıcı "kupon yap", "iddaa kuponu", "bugünün maçları" dediğinde tetiklenir.
---

# İddaa Kupon Önericisi

> ⚠️ **Uyarı:** Bu skill yatırım/kumar tavsiyesi değildir, eğitim ve eğlence amaçlıdır. Kayıp riski tamamen kullanıcıya aittir. 18+ ve yasal bahis kullanın.

## Ne yapar?

1. **The Odds API**'den günlük spor bültenini ve oranları çeker
2. Her maç için **implied probability** ve **value (EV)** hesaplar
3. Üç profilde kupon önerir: **Güvenli**, **Dengeli**, **Riskli**
4. Her seçimin gerekçesini (oran, implied %, value %) açıklar

## Ön gereksinimler

`.env` dosyasında **ODDS_API_KEY** olmalı. Anahtar https://the-odds-api.com adresinden ücretsiz alınır (aylık 500 istek). Yoksa kullanıcıya ekletmeden çalışmayı deneme.

```bash
# .env
ODDS_API_KEY=xxxxxxxxxxxxx
```

## Kullanım akışı

Kullanıcı "kupon yap" / "bugünün iddaa bülteni" / "maç önerisi" dediğinde aşağıdaki adımları sırayla uygula.

### Adım 1: Spor / lig seçimi

Kullanıcıya hangi sporları/ligleri istediğini sor (varsayılan: Avrupa futbol ligleri). Yaygın `sport_key` değerleri:

| Lig | sport_key |
|---|---|
| Türkiye Süper Lig | `soccer_turkey_super_league` |
| Premier League | `soccer_epl` |
| La Liga | `soccer_spain_la_liga` |
| Serie A | `soccer_italy_serie_a` |
| Bundesliga | `soccer_germany_bundesliga` |
| Champions League | `soccer_uefa_champs_league` |
| NBA | `basketball_nba` |
| Euroleague | `basketball_euroleague` |

Tüm spor listesi için: `GET https://api.the-odds-api.com/v4/sports?apiKey=$ODDS_API_KEY`

### Adım 2: Oranları çek

Her seçilen lig için Bash + curl ile:

```bash
curl -s "https://api.the-odds-api.com/v4/sports/${SPORT_KEY}/odds/?apiKey=${ODDS_API_KEY}&regions=eu&markets=h2h,totals&oddsFormat=decimal&dateFormat=iso"
```

Önemli parametreler:
- `regions=eu` → Avrupa bahis siteleri (Pinnacle, Bet365, Unibet vs.) en sağlıklı oranlar
- `markets=h2h,totals` → Maç sonucu + Üst/Alt 2.5
- `oddsFormat=decimal` → ondalık format

Yanıt çok büyükse `jq` ile gerekli alanları süz: `home_team, away_team, commence_time, bookmakers[].markets[].outcomes[]`.

### Adım 3: Value bet hesapla

Her maçın her bahis sitesi oranı için:

```
implied_prob = 1 / decimal_odd
fair_prob    = 1 / median(tüm sitelerdeki ilgili oranlar)   # bookmaker konsensüsü
edge_pct     = (fair_prob - implied_prob) / implied_prob * 100
```

**Value bet:** En yüksek oran veren bookmaker'ın sunduğu oranın implied probability'si, konsensüs fair probability'den **düşükse** value vardır (yani oran fiyatlandırmadan yüksek).

Daha sağlam yaklaşım: **Pinnacle** oranını "fair" referans say (en düşük marjlı bookmaker). Diğer sitelerdeki oranı Pinnacle'a göre kıyasla.

### Adım 4: Kupon profillerine göre seç

| Profil | Maç sayısı | Tek oran aralığı | Toplam oran hedef | Min edge % |
|---|---|---|---|---|
| **Güvenli** 🛡️ | 2-3 | 1.40 - 2.00 | 2.5 - 5 | ≥ 3% |
| **Dengeli** ⚖️ | 3-5 | 1.60 - 2.80 | 6 - 15 | ≥ 5% |
| **Riskli** 🎲 | 5-8 | 1.80 - 4.50 | 20 - 100+ | ≥ 7% |

Ek kurallar:
- Aynı maçtan birden fazla seçim **alma** (h2h ve totals çelişebilir)
- Aynı liglerden çok yığılma yapma — çeşitlendir
- `commence_time` bugün veya yarın 24 saat içinde olsun
- Seçimleri edge % yüksek olandan düşüğe sırala

### Adım 5: Çıktı formatı

Kullanıcıya **markdown tablo** halinde göster:

```markdown
## 🛡️ Güvenli Kupon (Toplam Oran: X.XX)

| Maç | Saat | Seçim | Oran | Site | Implied % | Edge |
|---|---|---|---|---|---|---|
| Galatasaray - Fenerbahçe | 20:00 | MS 1 | 1.85 | Pinnacle | 54% | +6.2% |
| ... |

**Gerekçe:** ...

---

## ⚖️ Dengeli Kupon (Toplam Oran: X.XX)
...

## 🎲 Riskli Kupon (Toplam Oran: X.XX)
...
```

Her kuponun sonuna **kısa gerekçe** (1-2 cümle): neden bu seçimler value, hangi bookmaker konsensüsünden ne kadar saptılar.

## Önemli notlar

- **Her cevabın sonuna uyarı ekle:** "Yatırım/kumar tavsiyesi değildir. Kayıp riski size aittir. 18+."
- API hata verirse (rate limit, 401) kullanıcıya net mesaj ver, fallback olarak manuel oran girişini öner
- Kullanıcı bütçe/risk yüzdesi belirtirse Kelly criterion ile bahis miktarı öner: `f = (b·p - q) / b` (b=oran-1, p=fair_prob, q=1-p). Kelly'nin **yarım/çeyrek**ini kullan (full Kelly çok agresif)
- Hiçbir zaman "kesin kazanır" / "garantili" deme. Value bahis bile uzun vadeli istatistikseldir

## Hızlı test

Skill çalışıyor mu kontrol için:

```bash
curl -s "https://api.the-odds-api.com/v4/sports/?apiKey=$ODDS_API_KEY" | jq '.[0:5]'
```

5 spor listelenirse API ve key OK.
