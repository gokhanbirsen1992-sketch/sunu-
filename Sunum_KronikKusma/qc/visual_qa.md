# Görsel kalite denetimi: slayt görüntüleri

- **Kaynak:** `output/slides_png/s-01.jpg … s-49.jpg` (1334×750 px, 100 dpi, yani 1 px = 0,01 in)
- **Kapsam:** Yalnız görsel kusurlar denetlendi, içerik doğruluğuna bakılmadı.
- **Yöntem:** 49 görüntünün her biri tek tek açıldı. Şüpheli bölgeler 2–8 kat büyütülerek ayrıca incelendi. Kenar payları, kutu hizaları ve kontrast oranları piksel ölçümüyle doğrulandı. Kontrast WCAG göreli parlaklık formülüyle hesaplandı; JPEG yumuşaması nedeniyle oranlar ±0,2 sapabilir.
- **Şiddet ölçütü:**
  - **Yüksek:** Anlamı bozan ya da okunamayan kusur.
  - **Orta:** Salonda fark edilecek bir düzen veya okunurluk sorunu.
  - **Düşük:** Cila düzeyinde bir düzeltme.

## Bulgular

| Slayt no | Kusur | Şiddet | Önerilen düzeltme |
|---|---|---|---|
| 19 | Dipnottaki "≠" işareti düzgün çizilmemiş. "(biyokimyasal anormallik ≠ tanı)" ifadesi, italik yazı tipinde yatay çizgileri olmayan küçük bir eğik çizgiyle "anormallik ⁄ tanı" olarak görünüyor. Bu yüzden "eşit değil" anlamı kayboluyor ve ifade "anormallik ya da tanı" gibi okunuyor. | yüksek | İşareti "≠" yerine yazıyla verin: "anormallik tanı değildir". İşaret kalacaksa onu destekleyen bir yazı tipinde ve düz (italik olmayan) stilde verin. Düzelttikten sonra yeniden render edip kontrol edin. |
| 40 | 1. maddenin kaynak üst simgesi "[83]" kendi satırına düşmüş, "(SR)" yukarıda kalmış. Madde gereksiz yere üç satır oluyor ve sonraki maddeyle arasına boşluk giriyor. | orta | Üst simgeyi önceki sözcüğe bölünmez bağla (U+2060 ya da NBSP) bağlayın. Alternatif olarak "(SR)" ifadesini kaldırın veya kısaltın ya da metin kutusunu ~0,2 in genişletin. |
| 06 | Grafikteki "neredeyse her gün, düşük yoğunluk" etiketinin ortasından y=8 kılavuz çizgisi geçiyor ve yazı üstü çizili gibi görünüyor. Alttaki panelde "ataklar arası iyilik" etiketi de 8 çizgisine oturuyor. | orta | Etiketlere beyaz yarı saydam bir arka plan kutusu ekleyin (matplotlib'de `bbox=dict(fc='white', ec='none')`) ya da etiketleri kılavuz çizgilerinin arasına (y≈10–11) taşıyın. |
| 06 | X ekseni başlığı "Gün" ile hemen sağındaki alt yazı ("Şematik çizim, hasta verisi değil · eşikler [3]") arasında ~0,07 in boşluk var, ikisi neredeyse değiyor. | düşük | Alt yazıyı eksen başlığının altına ayrı bir satır olarak koyun ya da sağa yaslı ve ~0,1 in aşağıda konumlandırın. |
| 09, 24, 33, 37 | Vurgu şeritlerinde ve kutularında metin dikeyde ortalanmamış, alt kenara yaslı duruyor: 09'da kırmızı "Her yaşta" şeridi, 24'te yeşil "Ardından %10 dekstroz" şeridi, 33'te kesik çizgili "Kronik, epizodik olmayan…" kutusu, 37'de gri "Tarihsel · 2008" şeridi. Sol iç boşluk ~0,08 in, kartlarda ise ~0,3 in. 24'te yan yana duran turuncu kutu ortalanmış olduğu için aynı satırda iki farklı hizalama görünüyor. | orta | Metin kutularında dikey hizalamayı "ortala" yapın. Sol ve sağ iç boşluğu kartlarla eşitleyin (~0,3 in). |
| 09, 24, 33 | Alttaki şeridin veya kutunun sağ kenarı (x≈12,73 in) üstteki üçlü kart ızgarasının sağ kenarından (x≈12,65 in) ~0,08 in dışarı taşıyor. Sol kenarlar hizalı, sağ kenarlar değil. | düşük | Şerit genişliğini kart ızgarasının dış kenarına eşitleyin. Ya da tüm şablonda içerik sağ kenarını tek bir değere (12,65 ya da 12,73 in) sabitleyin. |
| 22, 28 | Açık pembe zemin üzerindeki turuncu metnin kontrastı ≈3,0:1 ve projeksiyonda soluk görünüyor. 22'de bu, kartların asıl mesajını taşıyan eylem satırları ("→ Acil üst GİS grafisi…", "→ Beyin MR"). 28'de "Basamak 0 · Acil (aynı saat)" başlığı. | orta | Metni koyu kiremit rengine çekin (örn. #9E3B26, ≥4,5:1) ya da kart zeminini beyaz veya çok açık yapın. |
| 09, 24 | Renkli şeritlerdeki beyaz metnin kontrastı kırmızıda ≈3,9:1, yeşilde ≈3,8:1. Bu oran yalnız büyük veya kalın metin için yeterli. Kırmızı şerit üzerindeki küçük beyaz "[22]" üst simgesinde oran ≈3,3:1. | düşük | Şerit renklerini koyulaştırın (kırmızı ≈#B5432A, yeşil ≈#00756B; ikisi de ≥4,5:1). Üst simgeyi şeridin dışına, dipnot satırına alın. |
| 31 | Başlıktaki "→" işareti serif başlık yazı tipinde yedek bir glifle çiziliyor: küçük ve yukarıda kalıyor. Salonda "Rome IV – V" gibi kısa bir çizgi olarak okunuyor. | orta | Oku gövde yazı tipinde ayrı bir parça olarak verin ya da metni "Rome IV'ten V'ye" şeklinde yazın. |
| 22, 24, 28 | "Na↓ / glukoz↓" ifadesindeki "↓" okları yedek glifle çiziliyor. Harf ile ok arasındaki boşluk düzensiz: "Na ↓ /glukoz ↓ 'de". | düşük | "↓" için yazı tipini sabitleyin ya da yazıyla ifade edin: "düşük Na / glukoz". |
| 28 | Algoritma kutularındaki gövde metni ≈12–13 pt, üst simgeler ≈7 pt. Slayt çok yoğun ve orta–arka sıralardan okunmaz. | orta | Kutu metinlerini kısaltın ya da algoritmayı iki slayta bölün; gövdeyi ≥16 pt yapın. Kaynak üst simgelerini kutulardan çıkarıp alt kaynak satırında toplayın. |
| 28 | Satır sonu bölünmeleri ve sıkışık kutu: <br>• Basamak 0'da "Nörolojik bulgu →" satır sonunda kalıyor, "beyin MR" alt satıra iniyor. <br>• "Eforsuz regürjitasyon" kutusunda "HRIM-/empedans" tireden bölünmüş. <br>• Basamak 2'de "US" ikinci satırda tek başına kalıyor ve kutunun alt iç boşluğu ~0,15 in'e iniyor. | düşük | Tire için bölünmez tire (U+2011), ok ve sözcük arasında NBSP kullanın. Basamak 2 metnini kısaltın ("UPJ şüphesi → atakta US") ya da kutu yüksekliğini ~0,15 in artırın. |
| 28 | Basamak 3 kutusunda "Tanıyı testlerle destekle" satırı başlıktan ~0,1 in içeride başlıyor (baştaki boşluk karakteri). Diğer kutularda gövde metni başlıkla aynı hizada. | düşük | Baştaki boşluğu silin. |
| 28 | Kaynak üst simgelerinden önce boşluk var ("grafisi [55]", "MR [22–24,…]"). Destenin geri kalanında üst simge sözcüğe bitişik. | düşük | Boşluğu kaldırın. |
| 32 | Alt kutunun başlığında iç çalışma notu görünüyor: "Eşlik eden özellikler **(kutu başlığı doğrulanmadı)**:". Sahnede taslak artığı gibi okunuyor. | orta | Parantez içindeki notu konuşmacı notlarına taşıyın. Başlığı "Eşlik eden özellikler:" olarak bırakın. |
| 32 | Numaralı liste ≈16 pt, alt kutu metni ≈13 pt. Bu boyutlar destenin standart gövde boyutunun (≈20 pt) altında. Alt kutunun alt yarısı boş. | düşük | Listeyi ≥18–20 pt yapın. Kutu yüksekliğini metne göre küçültün ya da metni büyütün. |
| 09 | "Okul çağı" kartında sayı satır sonunda kalıp birimi alt satıra iniyor: "5,3–5,8 / yaş" ve "~3–6 / yaş". | orta | Sayı ile birim arasına NBSP (U+00A0) koyun. |
| 33 | FD kartında "EPS ≥1 / gün/hafta" ifadesinde sayı ile birim ayrı satırlarda. | orta | NBSP kullanın ya da kısaltın ("≥1 gün/hf"). |
| 17 | "mukoza normal görünse de ≥2 / seviyeden" ifadesinde sayı satır sonunda, birim alt satırda. | düşük | "≥2" ile "seviyeden" arasına NBSP koyun. |
| 08, 29 | Stat kartının alt yazısında sıra sayısı ile ardından gelen sözcük bölünmüş: "(3. / basamak, n=100)" ve "(2015, 3. / basamak)". | düşük | "3." ile "basamak" arasına NBSP koyun ya da alt yazıyı kısaltın. |
| 03, 13, 14, 26, 30 | İki satıra taşan başlıklarda ikinci satırda tek sözcük kalıyor: "yok", "değil", "belirler", "semptomda", "bulunabilir". Ayrıca gövde metni tek satırlı başlıklarla aynı y'de başladığı için başlık–gövde aralığı ~0,8 in'den ~0,4 in'e düşüyor ve başlık tutarsız görünüyor. | düşük | Başlığı tek satıra sığacak şekilde kısaltın ya da satırları dengeli kırın. İki satırlı başlıklarda gövdeyi ~0,3 in aşağı kaydırın (ya da başlığı alttan sabitleyin). |
| 01 | Kapak başlığında "Yaklaşım" tek başına ikinci satırda kalıyor. | düşük | Başlığı dengeli kırın: "Kronik Tekrarlayan Kusması Olan / Çocuğa Yaklaşım". |
| 05, 10, 20, 21, 36, 41 | "Kanıt notu" kutularında metin sol üst köşeye ~0,08 in yapışık ve kutunun alt yarısı boş. Kutunun köşeleri keskin, hemen üstündeki stat kartının köşeleri yuvarlak; stil tutarsız ve kutu yarım kalmış gibi görünüyor. | düşük | İç boşluğu 0,2–0,25 in yapın. Kutu yüksekliğini metne göre otomatik ayarlayın ya da metni dikeyde ortalayın. Köşe yarıçapını kartlarla eşitleyin. |
| 07, 10, 14, 20, 29, 41 | Sol sütun metni sağdaki karta 0,35–0,40 in kadar yaklaşıyor; diğer slaytlarda bu aralık 0,5–0,9 in. | düşük | Metin kutusunu ~0,15 in daraltın. Metin ile kart arasında ≥0,5 in sabit bir oluk bırakın. |
| 03, 04, 05, 07, 08, 10, 11, 13–21, 25–27, 29, 30, 34–41 | Madde işaretli metin ve stat kartı düzeninde içerik y≈3,7–5,0 in'de bitiyor. Dipnot veya kaynak satırına kadar ~1,5–2,5 in boş alan kalıyor: üst yarı dolu, alt yarı boş. 34'te boşluk hem madde işaretli metin ile kutular arasında hem de kutuların altında. | düşük | Gövde ve kartı dikeyde ortalayın ya da gövdeyi büyütün (≥22 pt). Alternatif olarak boşluğu bir şema veya görselle değerlendirin. |
| 02–42 (tüm içerik slaytları), 44–48 | Üstteki bölüm etiketi üst kenara ~0,27–0,29 in, alttaki "Kaynak no" satırı ve sayfa numarası alt kenara ~0,31–0,34 in uzaklıkta. Bu öğeler 0,5 in güvenli alanın içine giriyor ve projektör kırpmasında kaybolabilir. | düşük | Şablonda bölüm etiketini ≥0,45 in, alt bilgi satırını ≥0,45 in uzaklığa çekin. Ya da salon projektöründe kırpmayı test edin. |
| 02–42 | Alt bilgideki "Kaynak no: … · tam liste sondaki kaynak slaytlarında" satırı ≈7 pt gri; italik gri dipnotlar ≈9 pt. Bu boyutlar salonda okunmaz. | düşük | Alt bilgiyi ≥10 pt, dipnotları ≥11–12 pt yapın. |
| 06, 07, 12, 22, 31, 33, 42 | Bazı dipnotlar üretim veya doğrulama süreci notu gibi okunuyor, yani "TODO" benzeri artık izlenimi veriyor. Örnekler: "Pfau özetindeki oranlar ve sıklık SD'si bozuk → yalnız eşikler kullanıldı", "…PDF'ten doğrulanmadı", "…tam metinden doğrulanmadı", "…bu çalışmada pediatrik kaynak doğrulanmadı", "2025 tam metinleri görülmedi". | düşük | Bilinçli bir şeffaflık notuysa tek bir biçime çekin ("Not: …", "Sınırlılık: …"). Değilse konuşmacı notlarına taşıyın. Karar içerik sahibine ait. |
| 42 | Tablo hücrelerinde iç boşluk dar: "Bayrağa göre hedefe yönelik" sütun çizgisine ~0,12 in; iki satırlı hücrelerde ("Herkese kan + idrar + üst GİS / grafisi", "4 sınıf, koşullu; yaş ölçütü / (özette) yok") metin üst ve alt çizgiye ~0,05 in. | düşük | 1. sütunu daraltıp 2. ve 3. sütunu genişletin. Hücre iç boşluğunu ≥0,12 in yapın. |
| 43 | Diğer içerik slaytlarında olan sayfa numarası burada yok. Sağ yarı boş. | düşük | Kasıtlı değilse sayfa numarası ekleyin. Mesaj satırlarını büyütüp (≥24 pt) alanı dengeleyin. |
| 44–48 | Kaynak slaytlarında başlık üst kenardan ≈0,45 in'de, içerik slaytlarında ≈0,69 in'de; başlık hizası farklı. Sütunlar arası oluk ≈0,27 in ile dar. Metin ≈9 pt. | düşük | Başlık y konumunu içerik slaytlarıyla eşitleyin. Oluğu ≥0,4 in yapın. Sağ ve sol sütunları dengeleyin. |
| 48 | Son kaynak sayfasında 8 kaynak (81–88) yalnız sol sütunda; sağ yarı tamamen boş. | düşük | Kaynakları iki sütuna dağıtın (4+4) ya da 44–48 arasında yeniden dengeleyin. |
| 49 | Teşekkür slaytında içerik sol üstte; yüzeyin ~%85'i boş, yerleşim dengesiz. | düşük | Başlık ve alt satırı dikeyde ortalayın ya da kapak slaytıyla aynı yerleşimi kullanın. |
| 01 | *(Bilgi, kusur sayılmadı.)* Kapakta bilinçli yer tutucu var: "[Konuşmacı adı, unvan · Kurum] · [Kongre adı · Tarih]". | — | Sunumdan önce gerçek bilgilerle doldurun. |

## Kontrol edilip sorun bulunmayanlar

- **Metin taşması ve kesilme:** Hiçbir slaytta metin kutu ya da slayt kenarında kesilmiyor.
- **Kenar payları:** İçerik sol kenara ≥0,56 in, sağ kenara ≥0,59 in mesafede. Kenara yaklaşan öğeler yalnız yukarıda raporlanan bölüm etiketi ve alt bilgi satırı.
- **Çakışmalar:** Kaynak satırı veya dipnot içerikle çakışmıyor. 28'de alt kutular ile kaynak satırı arasındaki 0,32 in en dar aralık, ama çakışma yok.
- **Türkçe karakterler:** 49 slaytın hiçbirinde ı, ğ, ş, İ, ç, ö, ü bozulması yok; "GİS", "KİBAS", "ERİŞKİN", "İKİNCİL" doğru çiziliyor.
- **Yer tutucu ve artıklar:** Kapak dışında yer tutucu metin yok; "TODO", "XXX", "lorem" yok.
- **Başlık hizası:** Tek satırlı başlıklar 02–42 arasında aynı yükseklikte ve hizada (üst ≈0,69 in, sol 0,58 in).
- **Render artefaktı (sayılmadı):** 01, 43 ve 49'da sağ kenarda 1 px açık bir sütun görünüyor. Bu, 13,333 in × 100 dpi'nin tam sayı piksele yuvarlanmasından gelen bir render artefaktı; slaytın kendi kusuru değil.

## Toplam

| Şiddet | Bulgu (satır) sayısı |
|---|---|
| Yüksek | 1 |
| Orta | 9 |
| Düşük | 23 |
| **Toplam kusur** | **33** |
| Bilgi (yer tutucu, sayılmadı) | 1 |

- **Slayta özgü bulgusu olan slaytlar (36):** 01, 03, 05–10, 12–14, 17, 19–22, 24, 26, 28–33, 36, 37, 40–49.
- **Yalnız şablon düzeyinde bulgusu olan slaytlar (13):** 02, 04, 11, 15, 16, 18, 23, 25, 27, 34, 35, 38, 39. Bu slaytlardaki bulgular kenar payı, alt bilgi boyutu ve alt yarıdaki boşluk.
- **En yoğun kusur kümesi:** 28 (algoritma, 6 satır) ve 09/24/33 (vurgu şeritleri).
