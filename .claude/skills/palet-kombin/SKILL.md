---
name: palet-kombin
description: Kullanıcının kişisel renk paletine göre giysi/aksesuar seçimi, ürün×renk matrisi ve kombin üretimi. "Kombin yap", "bu ürün palete uyar mı", "ne alayım hangi renk", "X rengi olur mu", "5 kombin yap", "listeyi güncelle" dendiğinde kullan. Paleti yeniden icat etme; ref/profil.md ve ref/palet.json'daki kararlar sabittir, yalnızca kullanıcı açıkça değiştirirse güncelle.
---

# Palet-Kombin

Amaç: kullanıcı ürünü kendisi seçer; bu skill yalnızca **hangi üründe hangi renk olur / olabilir / olmaz** sorusuna mekanik, tutarlı cevap verir ve istenirse kombin üretir.

## 0. Önce oku
- `ref/profil.md` — vücut, ten, bağlam (hastane, Antalya), stil kararları, öğrenilmiş tercihler.
- `ref/palet.json` — renkler (hex), roller, ürün×renk matrisi (I/O/X), sayım kuralları, `magaza_modu`, `renk_esleme` (vizon, mink, terracotta gibi mağaza adları).
- `ref/dolap.json` — seçilmiş dolap (parça, renk, alternatifler, zincirleme şartlar, satın alma turu), Prag kapsülü.

Bu üç dosya karar kaynağıdır. Bellekten renk veya beden uydurma; beden `profil.md`'de "çözülmedi" ise kullanıcıya sor.

Matrisi veya dolabı her değiştirdiğinde `python3 scripts/denetim.py` çalıştır; "Temiz: 0 ihlal" görmeden kullanıcıya dönme.

## 1. Cevap türleri

**a) "X ürün Y renk olur mu?"** → matristeki hücreyi oku: I = ideal, O = olabilir, X = yasak. Tek cümle + gerekçe (yüz-ten kontrastı / alt gövde koyuluğu / rol çakışması). Hücre yoksa 4. bölümdeki türetme kuralıyla karar ver ve "[çıkarım]" etiketle.

**b) "Ne alayım / liste"** → `ref/palet.json` içindeki `adetler` ile ürün satırlarını birleştir; her ürün için adet + yeşil/sarı renkler + kırmızı renkler. Kullanıcı renk seçimini kendi yapar; karar verilmiş tek renk dayatma (kullanıcı bunu açıkça reddetti).

**c) "Kombin yap"** → 5. bölümdeki kombin kuralları. Varsayılan 5 kombin, yukarıdan aşağı: iç katman / orta-dış katman / pantolon / ayakkabı. Hastane kombinlerinde blazer yok (blazer yalnızca 10 dk geçiş katmanı); iç katman tek başına ayakta durmalı.

**d) "Görsel yap"** → `scripts/matris.py` (matris), `scripts/kombin.py` (5 kombin kartı), `scripts/liste.py` (seçilmiş dolap listesi). Çıktı PNG, scratchpad'e yaz, SendUserFile ile gönder.

**e) "Mağazadayım / bu ürünü alayım mı"** → `magaza_modu`: yalnızca 3 şart eleme kriteri (renk I/O, omuz-bel-uyluk oturuyor, parlak/süet/siyah/logolu değil). Pens, astar, gramaj, yaka tipi "varsa iyi"dir; bunlar yüzünden ürünü eleme. Mağaza renk adını `renk_esleme` ile palete çevir.

**f) "Dolabı kontrol et"** → `scripts/denetim.py` çıktısını raporla; kullanılmayan parça, vurgu sayımı, deri tonu tekliği.

**g) Seyahat** → `dolap.json > seyahat_prag_kasim` örnek; soğuk şehirde hafif flanel/pamuk twill önerme, pensli yüksek bel şartı arama.

## 2. Sabit kurallar (fizik, zevk değil)
1. Yüze değen parça (gömlek, polo, tişört): ten rengine yakın renk yasak → camel, taupe, taba. (Tütün tenden koyu, serbest.)
2. Alt gövde (pantolon, denim) ve kaban: yalnızca koyu taban renkleri.
3. Vurgu aile (pas, kiremit, bordo, şarap, hardal, okra): küçük veya kısa süreli yüzeyde; pantolon/kaban/hırka/blazer'da yasak veya "olabilir" en fazla.
4. Deri hep kahve (bordo ayakkabı/kemer yok), metal hep pirinç. Mavi yalnızca koyu indigo denim. Siyah, saf beyaz, açık gri, pastel, parlak kumaş, süet yok.
5. Bitişik iki katman aynı renk olmaz; bir kombinde en fazla bir vurgu parça.

## 3. Sayım kuralı (tek)
Hastanede giyilen **gömlek + polo + kazak** toplamında vurgu aileden en fazla **3 parça**; gömlekte en az **2 ekru**. Tişört, çorap, atkı, denim sayıma girmez.

## 4. Matriste olmayan renk/ürün için türetme
- Yeni renk → en yakın palet rengine eşle (ör. "terracotta" → kiremit, "haki" → zeytin ailesi). Eşleşmiyorsa (mavi, gri, siyah, pastel) → X.
- Yeni ürün → en yakın katman tipine eşle: yüze değen (gömlek kuralı), orta (kazak kuralı), dış (blazer/kaban kuralı), alt (pantolon kuralı), deri (ayakkabı kuralı).
- Sonucu "[çıkarım]" etiketle ve kullanıcı onaylarsa `ref/palet.json`'a ekle.

## 5. Kombin kuralları
- Katman sırası: iç (gömlek/polo/tişört) → orta (kazak/hırka; kazak yalnızca gömlek üstüne, polo üstüne kazak olur, gömlek üstüne polo olmaz) → dış (blazer/kaban) → pantolon → ayakkabı.
- Hastane: iç katman tek başına düzgün (tişört hariç); blazer yok; loafer. Yağmur günü loafer ve sneaker yerine bot.
- Yeşil üstüne yeşil yok (koyu yeşil / koyu zeytin / zeytin / haki aynı aile sayılır, pantolon dahil); kahve üstüne kahve (çikolata / koyu kahve) aynı şekilde.
- Loafer, bot, kemer, çanta aynı kahve tonu.
- Hafta sonu: tişört, denim, sneaker serbest.
- Kaban + aynı renk pantolon → iç katman açık (ekru).
- Camel ↔ hardal, camel ↔ tütün bitişik gelirse "sınırda", tercih etme.
- Çıktıda her kombin için tek satır gerekçe; kural ihlali varsa söyle.

## 6. Dil ve biçim
Türkçe, yoğun, dolgusuz. Jargon kullanma ("vurgu" dersen hangi renkler olduğunu aynı cümlede yaz). Tablo tercih; kullanıcı "karar verilmiş liste" değil "seçenekli liste" ister. Kullanıcı bir kuralı reddederse `ref/profil.md`'ye "öğrenilmiş tercih" olarak ekle, tekrar dayatma.
