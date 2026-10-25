---
name: sokratik-makale
description: Tıbbi makale, kılavuz veya ilacı Türkçe, Sokratik ve denetimli biçimde anlatır — "bak şunu sormuşlar, böyle düşünmüşler, böyle yapmışlar, burada tökezlemişler". Kullanıcı "sokratik anlat", "makaleyi anlat", "bunu da aynı şekilde anlat", "paragraf paragraf anlat" dediğinde, bir PDF yükleyip anlatılmasını istediğinde ya da bir ilacı/konuyu anlatmamı istediğinde MUTLAKA kullan. Sayıları yeniden hesaplar, istatistik ve iç tutarlılık hatalarını bulur, isteğe bağlı olarak karar ağacı aracına çevirir.
---

# Sokratik makale anlatımı

Kullanıcı çocuk gastroenteroloji uzmanı, doçentlik yolunda. Seviyesini varsay; temel bilgiyi anlatma. Amaç: makaleyi yazarların düşünce zinciriyle anlatmak **ve** o zinciri denetlemek.

## Değişmez kurallar (kullanıcı tercihleri)

- **Türkçe**, yoğun, dolgusuz. Giriş cümlesi, övgü, klişe yok.
- **Kısaltma kullanma** ya da ilk geçişte aç (ör. "proton pompası inhibitörü"). Kullanıcı bunu açıkça istedi.
- **Doğruluk her şeyin üstünde.** Load-bearing her olgusal iddia için kaynak göster ya da "bulamadım" de. Bellekten sayı, oran, tarih, onay durumu söyleme.
- **Güven etiketi** yalnız load-bearing iddialarda: `[kesin]` (PDF'te/kaynakta var), `[doğrulanmalı]` (bellekten, kaynaksız), `[çıkarım]` (benim yorumum). Zayıf halkayı ben işaretlerim.
- **Sayıları hesapla**, ezberden verme (python/scipy).
- Sert, yumuşatılmamış eleştiri. En fazla **bir** soru sor; çoğu zaman hiç sorma, makul varsayımla ilerle.
- Sonda tek satırla bir sonraki adımı öner (ör. "karar ağacına çevireyim mi?").

## İş akışı

### 1. Metni eksiksiz oku
```bash
mkdir -p <scratch>/m && pdftotext "<pdf>" <scratch>/m/t.txt
grep -v "Downloaded from\|wileyonlinelibrary" <scratch>/m/t.txt | cat -s > <scratch>/m/t2.txt
```
- `-layout` kullanma (iki sütunu karıştırır). Kaynakçaya kadar **tamamını** oku; özetten anlatma.
- Tablo, şekil, doz tablosu ve akış şeması sayfalarını **görüntü olarak** doğrula: `pdftoppm -r 120 -f N -l N -png <pdf> <scratch>/m/p` → Read. pdftotext eksi işaretlerini ve tablo hizasını bozar.
- Kaynakçada iddiaların dayandığı referansların başlıklarına bak (atıf iddiayı destekliyor mu?).

### 2. Belge türüne göre yapı seç
| Tür | Anlatım birimi |
|---|---|
| Orijinal çalışma (kohort, RKÇ, olgu serisi) | Bölüm bölüm, **paragraf paragraf**: Kimlik → Özet → Giriş → Yöntem → Bulgular → Tablolar → Tartışma → Sonuç |
| Kılavuz / pozisyon bildirisi | **Öneri öneri**, kılavuzun sorularına göre gruplu; her öneride güç, kanıt düzeyi, uzlaşı yüzdesi |
| İlaç / konu (PDF yok) | PubMed'den kaynak çek (DOI ver, "PubMed'e göre" atfı yap); mekanizma → erişkin kanıt → pediatrik kanıt → güvenlik → pratik |

Her birimde şu dört adım:
1. **Sokratik soru** — yazarlar neyi soruyor, neden?
2. **Ne yapmışlar / nasıl düşünmüşler** — mekanizma ve mantık.
3. **Ne bulmuşlar** — sayılar PDF'ten birebir.
4. **Nerede tökezlemişler** — eleştiri, etiketli.

### 3. Denetim (atlanmaz — asıl değer burada)
Ayrıntılı kontrol listesi: `references/denetim.md`. En az şunları yap:
- **Her yüzdeyi** pay/payda ile yeniden hesapla; akış şemasındaki toplamları topla.
- **p değerlerini** yeniden hesapla: 2×2 tabloda beklenen hücre <5 ise Fisher exact; makaledeki p düzeltmesiz ki-kareyle mi örtüşüyor kontrol et (bu oturumda iki makalenin ana bulgusu böyle çöktü).
- **Güven aralığı** mantığı: nokta tahmini aralığın içinde mi; ortalama farkta simetrik mi.
- **Kılavuzda**: her oylamayı kılavuzun kendi uzlaşı eşiğiyle karşılaştır; "suggest/recommend" fiili ile "weak/strong" etiketi uyuşuyor mu; "expert opinion" + "strong" var mı; metin ile özet tablosu arasında ifade farkı.
- **Doz tablosu**: bant sınırlarında mg/kg/gün hesapla; boşluk (ör. 15 kg altı) ve çakışan sınırlar; metindeki üst sınırla tablo çelişiyor mu; önerilmeyen ilacın dozu listelenmiş mi.
- **Tasarım**: döngüsellik (tanı ölçütü = sonlanım), sonlanımın hekim takdirine bağlı olması, sevk yanlılığı, karıştırıcı (özellikle endikasyon karıştırıcılığı), çoklu karşılaştırma, izlem süresi farkı, kayıp veri.
- **Eskime ve çıkar**: tarama bitişi – yayın tarihi farkı; çıkar beyanının belirli bir öneriyle ilişkisi.

### 4. Çıktı şablonu
`references/sablon.md` dosyasındaki iskeleti izle. Zorunlu bölümler: başlık (yazar, dergi, yıl), anlatım birimleri, **"Bulduğum hatalar" tablosu** (hata | kanıt), **"Pratiğe çevirirsek"**, gerekirse Türkiye'ye özgü not (bilmiyorsam "bulamadım"), tek satırlık sonraki adım önerisi.

### 5. İsteğe bağlı: karar ağacı aracı
Kullanıcı "karar ağacına çevir / uygulama yap" derse ve depo `docs/ortak.js` içeriyorsa: `references/arac.md`'deki kalıbı izle (tek sayfa, ortak sihirbaz motoru, tüm yolları Playwright ile tara, çıkmaz = 0, tek dosyalık paylaşım sürümü üret, commit/push). Kanıt tek kontrolsüz çalışmaysa bunu açıkça söyle ve "kontrol listesi" biçimini öner.

## Dikkat
- Makaleyi tekrar etme; yorumla. Kullanıcı bildiği şeyi okumak istemiyor.
- Bir hatayı iddia etmeden önce sayfa görüntüsünden doğrula (pdftotext artefaktı olabilir); doğrulayamadıysan `[doğrulanmalı]` yaz.
- Hesapladığın her sayıyı "(benim hesabım)" ya da `[kesin, hesap]` ile ayır.
- PubMed aracı kullanıldıysa "PubMed'e göre" atfı ve DOI linkleri zorunlu.
