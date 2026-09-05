# "Dipten al, tepeden sat" — literatür taraması ve sayısal sınama

Tarih: 2026-09-05. Veri ve kod: `zamanlama/` (çalıştır: `python -m zamanlama --bas 1950 --toplam-getiri --maliyet 0.002`).

Güven etiketleri yalnızca yük taşıyan olgusal iddialarda: **[kesin]** kaynaktan birebir; **[doğrulanmalı]** kaynağın özeti/atıf yoluyla; **[çıkarım]** benim hesabım/yorumum.

---

## 0. Sonuç (önce kötü haber)

1. **Hissenin gerçek dibini alıp gerçek tepesini satan, önceden bilinebilir bir yöntem literatürde yok.** 100+ yıllık veride binlerce teknik kural sınandı; veri-madenciliği düzeltmesi ve işlem maliyeti sonrası kalıcı bir "dip/tepe yakalama" kabiliyeti bulunamadı [kesin: Sullivan-Timmermann-White 1999; Bajgrowicz-Scaillet 2012; Rink 2023]. Güneydoğu Asya endeksleri için yazılmış cümle aynen şu: *"traders cannot expect to buy at a relative low price and sell at a relative high price by just using technical trading rules"* [kesin: Tharavanij ve ark. 2015].
2. **Şikâyetiniz bir hata değil, kuralın tanımı.** Trend-takip sinyalleri (hareketli ortalama, kesişim, RSI eşiği) *tanım gereği* gecikir: dönüş gerçekleşmeden sinyal üretemezler. Kendi ölçümümde 1950–2026 S&P 500 aylık veride 10 aylık HO kuralı **alımı dipten ortalama %8,2 yukarıda, satışı tepeden ortalama %6,0 aşağıda** yapıyor ve **satışların %74'ünde hisse daha pahalıya geri alınıyor** [çıkarım, hesaplandı].
3. **Buna rağmen trend kuralları tamamen değersiz değil**; getiriyi değil *düşüş derinliğini* iyileştiriyor. Aynı veride al-ve-tut CAGR %11,6 / maks. düşüş −%49; HO(10) CAGR %11,0 / maks. düşüş −%19 [çıkarım, hesaplandı]. Literatürle uyumlu: kazanç yön tahmininden değil, ödeme asimetrisinden (az sayıda büyük çöküşten kaçmak) gelir [kesin: Tharavanij 2015; Faber 2007 (özet erişilemedi, sonuç ikincil kaynaklardan) [doğrulanmalı]].
4. **Ödülün gerçek büyüklüğü sanıldığından küçük.** ≥%20'lik her dibi ve tepeyi *kusursuz* bilen bir kâhin 1950–2026'da yıllık %15,4 yapıyor; al-ve-tut %11,6. Yani mükemmel dip/tepe zamanlaması bile yılda ~3,7 puan. Aylık düzeyde her yukarı ayı bilen kâhin ise %23,4 — asıl para öngörülemeyen aylık gürültüde, dip/tepe "şeklinde" değil [çıkarım, hesaplandı].
5. **Haberin fiyatlanmış olması** yarı-güçlü etkinliğin ta kendisi; kazanç açıklaması sonrası sürüklenme (PEAD) bile büyük hisselerde 2006'dan beri yok [kesin: Martineau 2022].
6. **"Sonuç alana kadar döngü" isteğinin dürüst cevabı:** döngü, hedefi değiştirmeden sonuç veremez. Hedefi "dipten al-tepeden sat"tan "riske göre düzeltilmiş getiriyi ve maksimum düşüşü iyileştir"e çevirirseniz literatürde kanıtı olan 3 yol var (§5).

---

## 1. Teşhis: sinyaliniz neden hep geç?

**Mekanik neden [çıkarım].** n-aylık HO kuralı, fiyat ortalamanın altına inince satar. Fiyat tepeden döndükten sonra ortalamanın altına inmesi için tepeden en az birkaç yüzde düşmesi gerekir; dip için tersi. Yani kural *dönüşü teyit ettikten sonra* işlem yapar. Gecikmeyi kısaltmak (kısa HO) yanlış sinyal (whipsaw) sayısını artırır; uzatmak her dönüşte daha fazla kâr bırakır. Bu bir ayar hatası değil, filtre teorisindeki gecikme-gürültü ödünleşimidir.

**Ölçüm (S&P 500, aylık, toplam getiri, 1950-01 → 2026-08, tek yön maliyet %0,2):**

| Kural | Tur | Alım dipten ne kadar yukarıda (ort.) | Satış tepeden ne kadar aşağıda (ort.) | Kazanan tur | Satıp daha pahalıya geri alma |
|---|---:|---:|---:|---:|---:|
| HO(10) | 42 | %8,2 | %6,0 | %69 | %74 |
| HO(12) | 36 | %9,6 | %7,1 | %69 | %75 |
| Kesişim HO(2)>HO(10) | 37 | %10,1 | %7,2 | %78 | %78 |
| Kesişim HO(3)>HO(12) | 28 | %12,8 | %8,4 | %89 | %82 |

Okuma: kural her turda dipten ~%8–13 yukarıda alıp tepeden ~%6–9 aşağıda satıyor; çıkışların dörtte üçünde hisse çıkış fiyatının üstünden geri alınıyor. "Alım tepede, satış dipte" hissi tam olarak bu tabloya karşılık gelir. Kural yine de portföyü koruyor, çünkü kalan %25'lik çıkışlar 1973–74, 2000–02, 2007–09 gibi büyük ayıları içeriyor.

**Haber neden fiyatlanmış [kesin/doğrulanmalı].** Kamuya açık bilgi açıklandığı anda fiyata girer (yarı-güçlü etkin piyasa; Fama 1970 klasiği, burada ayrıca sorgulanmadı [doğrulanmalı]). Piyasanın habere *eksik* tepki verdiği tek belgelenmiş büyük anomali PEAD idi; Martineau (2022) modern piyasalarda kazanç sürprizinin açıklama gününde tamamen fiyatlandığını, büyük hisselerde PEAD'in 2006'dan beri var olmadığını, mikro-kap'larda ise yakın zamanda kaybolduğunu gösteriyor [kesin, özet].

---

## 2. Literatür: ne çalışmıyor

### 2.1 Teknik kurallar ve veri-madenciliği
- **Brock-Lakonishok-LeBaron (1992)**, Dow Jones 1897–1986, 26 kural: alım sinyallerini izleyen getiriler satış sinyallerini izleyenlerden tutarlı biçimde yüksek; sonuçlar rassal yürüyüş/AR(1)/GARCH-M/EGARCH ile bağdaşmıyor [kesin, özet]. Bu, teknik analiz lehine en çok atıf alan makaledir.
- **Sullivan-Timmermann-White (1999)**: aynı evreni 7.846 kurala genişletip White'ın Reality Check'iyle veri-madenciliğini düzeltti. En iyi kuralın örneklem-içi üstünlüğü düzeltme sonrası da ayakta kalıyor; **ama 1987–1996 örneklem-dışı dönemde tekrarlanmıyor** [kesin, tam metin]: *"the superior performance of the best technical trading rule is not repeated in the out-of-sample experiment covering the 10-year period 1987–1996."*
- **Bajgrowicz-Scaillet (2012)**, DJIA 1897–2008, FDR yöntemi: *"an investor would never have been able to select ex ante the future best-performing rules… even the in-sample performance is completely offset by the introduction of transaction costs"* [kesin, özet].
- **Rink (2023)**, 23 gelişmiş + 18 gelişen piyasa, 6.406 kural, 66 yıl: örneklem-içi üstün kurallar var, gelişen piyasalarda daha çok; **öngörülebilirlik zamanla drastik düşüyor, son yıllarda piyasalar öngörülemez hale geliyor; ılımlı işlem maliyetine çok duyarlı; en iyi performanslı kurallar sonraki dönemde al-ve-tut'tan anlamlı biçimde kötü** [kesin, özet].
- **Ready (2002)**: BLL kurallarının maliyet sonrası görünür başarısı veri-madenciliğinin sahte sonucu [kesin, özet].
- **Park-Irwin (2007) derlemesi**: 95 "modern" çalışmanın 56'sı olumlu, 20'si olumsuz, 19'u karışık; ama çoğu veri-madenciliği, kuralın sonradan seçimi, risk ve maliyet tahmini sorunlu [kesin, özet].
- **Lo-Mamaysky-Wang (2000)**: omuz-baş-omuz, çift dip gibi şekiller kernel regresyonla otomatik tanındığında "bazı göstergeler artımsal bilgi sağlıyor ve pratik değeri olabilir" [kesin, özet]. Dikkat: bu "koşullu dağılım farklı" demek, "kârlı ticaret kuralı" demek değil; makale kârlılık iddia etmiyor.

### 2.2 Zamanlama için gereken isabet
- **Sharpe (1975)**: hisse/nakit arasında yıllık geçiş yapan bir zamanlayıcının al-ve-tut'u geçmesi için yılın yönünü **10'da en az 7** doğru bilmesi gerekir [doğrulanmalı; Sharpe'ın metnine erişilemedi, Buzzacchi-Ghezzi 2021 aynen bu ifadeyle doğruluyor: *"at least 7 times out of 10"*; başka atıflar %70–83 aralığı veriyor].
- **Buzzacchi-Ghezzi (2021)** güncellemesi: 1973–2018'de eşik ~%61–72'ye iner ama sonuç ayakta [kesin, tam metin].
- **Estrada (2008)**, 15 piyasa, 160.000+ günlük getiri: en iyi 10 günü kaçırmak portföyü pasife göre ortalama **%50,8** küçültür; en kötü 10 günü atlamak **%150,4** büyütür; 10 gün gözlemlerin %0,1'inden az — *"the odds against successful market timing are staggering"* [kesin, özet]. Kendi aylık replikasyonum (1950–2026): en iyi 10 ay kaçırılınca −%63, en kötü 10 ay atlanınca +%304 [çıkarım, hesaplandı].
- Perakende yatırımcı gerçeği: **Barber-Odean (2000)**, 66.465 hane: en çok işlem yapanlar yıllık %11,4, piyasa %17,9 [kesin, özet]. **Chague ve ark. (2019)**, Brezilya vadeli piyasası, 2013–15'te başlayan tüm gün-içi işlemciler: 300 günden uzun süre devam edenlerin **%97'si** para kaybetti, yalnızca %1,1'i asgari ücretten fazla kazandı [kesin, özet]. **Kuo-Lin (2013)**, Tayvan: 3.470 gün-içi işlemci ortalama net zarar; deneyimliler daha agresif ama daha iyi değil [kesin, özet].

### 2.3 Türkiye'ye özgü kanıt (zayıf ve çelişkili)
- **Metghalchi ve ark. (2021)**, FTSE Türkiye all-cap/small-cap, 2003–2019: küçük şirket endeksinde bazı kurallar (50/200 "altın kesişim" dahil) maliyet ve risk sonrası al-ve-tut'u geçiyor; büyük endekste sonuçlar karışık [kesin, özet]. Tek çalışma, tek örneklem, veri-madenciliği düzeltmesi belirtilmemiş → Rink (2023)'ün "gelişen piyasada örneklem-içi görünür, kalıcı değil" örüntüsüne uyuyor [çıkarım].
- **Özçalıcı ve ark. (2022)**, BIST 357 hisse, genetik algoritma + yapay sinir ağı: seçilmiş hisselerde al-ve-tut üstü getiri; yazarlar yalnızca GA sonuçlarıyla BIST'in zayıf-form etkin göründüğünü de söylüyor [kesin, özet]. Örneklem-dışı zayıf performansı YSA ile "düzeltme" yaklaşımı çoklu-test riski taşır; bağımsız replikasyon bulamadım [çıkarım].
- BIST fiyat verisine bu oturumda erişemedim (Borsa MCP yetkilendirilmemiş; Yahoo/Stooq proxy'den engelli). Geri-test S&P 500 üzerinde; **BIST'e aktarılabilirliği doğrulanmadı.**

---

## 3. Literatür: kısmen çalışan ve *neden* çalıştığı bilinen şeyler

Bunların hiçbiri dip/tepe yakalamaz; hepsi ya zamansal risk yönetimi ya da kesitsel anomali.

1. **Trend-takip / zaman-serisi momentumu.** Moskowitz-Ooi-Pedersen (2012) 58 vadeli işlem enstrümanında geçmiş 12 ay getirisinin gelecek getiriyi öngördüğünü raporlar [doğrulanmalı; makale başlığı/varlığı kesin, özet metni erişilemedi]. Eleştiriler: Goyal-Jegadeesh (2018) fazlalığın büyük kısmını net uzun pozisyonun risk primine bağlar; Huang ve ark. (2020) öngörü kanıtının orijinalden çok zayıf olduğunu savunur [kesin, Pitkäjärvi 2020'deki atıf metinleri]. Faber (2007) 10 aylık HO kuralını beş varlık sınıfında uygular; sonuç "benzer getiri, çok daha düşük düşüş" olarak aktarılır [doğrulanmalı, metne erişilemedi]. **Benim replikasyonum bunu doğruluyor** (§4).
2. **Oynaklık-yönetimli portföy.** Moreira-Muir (2017, JF): oynaklık yüksekken riski azaltmak piyasa/değer/momentum/kârlılık faktörlerinde alfa üretir ve Sharpe'ı yükseltir; mekanizma "oynaklık değişince beklenen getiri orantılı değişmiyor" [kesin, özet]. Bu bir dip/tepe kuralı değil; pozisyon büyüklüğü kuralı.
3. **Kesitsel momentum.** Jegadeesh-Titman (1993): son 3–12 ayın kazananlarını alıp kaybedenlerini satmak 3–12 ay ufukta anormal getiri [doğrulanmalı; makale kesin, özet erişilemedi]. Han-Yang-Zhou (2013): HO zamanlaması *oynaklığa göre sıralanmış portföylere* uygulanınca yüksek-oynaklık portföylerinde momentumdan büyük anormal getiri; tek hissede değil [kesin, özet]. Ahmad ve ark. (2018) UK ve Arif ve ark. (2018/2020) Pakistan replikasyonları: **tek hisse getirileri çok gürültülü, HO tek hissede anlamsız; portföyde çalışıyor** [kesin, özet].
4. **Teknik göstergelerle risk primi öngörüsü.** Neely-Rapach-Tu-Zhou (2014) 14 teknik göstergenin aylık hisse risk primini tarihsel ortalamadan iyi öngördüğünü bulmuştu; Maciel-da Silva (2024) daha yeni veride öngörü gücünün bozulduğunu, yalnızca düşük finansal belirsizlik dönemlerinde çalıştığını raporluyor [kesin, tam metin alıntıları].

Ortak nokta: hepsi *piyasa/portföy* düzeyinde, *aylık* frekansta, *küçük* ama istatistiksel olarak savunulabilir avantaj. Tek hisse + günlük sinyal + "dip/tepe" kombinasyonu için kanıt yok.

---

## 4. Kendi geri-testim (S&P 500, Shiller aylık verisi)

Kurallar: pozisyon ay kapanışında belirlenir, sonraki ayın getirisine uygulanır (bakış-ileri yok); açığa satış yok; nakit getirisi 0 (muhafazakâr, zamanlamanın aleyhine); temettü yıllık/12 yeniden yatırım. Kod ve testler: `zamanlama/motor.py`, `tests/test_zamanlama.py`.

### 4.1 1950-01 → 2026-08, tek yön maliyet %0,2

| Strateji | CAGR | Yıllık oynaklık | Sharpe (rf=0) | Maks. düşüş | İşlem | Piyasada |
|---|---:|---:|---:|---:|---:|---:|
| Al-ve-tut | %11,62 | %12,0 | 0,98 | −%49,0 | 0 | %100 |
| HO(10) | %10,97 | %9,0 | 1,20 | −%19,2 | 85 | %75 |
| HO(12) | %10,56 | %9,2 | 1,14 | −%19,2 | 73 | %77 |
| Kesişim 2/10 | %9,97 | %9,2 | 1,09 | −%26,8 | 75 | %75 |
| Kesişim 3/12 | %9,78 | %9,3 | 1,06 | −%25,3 | 57 | %75 |
| **KÂHİN** ≥%20 dip/tepe (zigzag) | %15,35 | %10,1 | 1,47 | −%19,3 | 13 | %89 |
| **KÂHİN** her ayın yönü | %23,40 | %7,4 | 2,89 | −%0,6 | 363 | %66 |

- Trend kuralları al-ve-tut'tan **daha az** getiriyor; farkı maks. düşüşte yapıyor. Faber ve Tharavanij ile tutarlı.
- Kâhin satırları gelecek bilgisi kullanır; ulaşılabilir değildir. "Dipten al tepeden sat"ın **tavanı** yılda ~3,7 puan; HO(10) bu tavanın ~4,4 puan altında (gecikme + whipsaw maliyeti).

### 4.2 1900 → 2026, maliyet %0,5 + nakitte 10y faiz/12 (zamanlamanın lehine varsayımlar)

Al-ve-tut %10,05 / −%81,8; HO(10) %11,47 / −%47,5. Yani lehte varsayımlarla bile fark ~1,4 puan ve bunun kaynağı 1929–32 ile 1970'lerdeki nakit faizi. Nakit vekili 10 yıllık tahvil faizi olduğu için nakit getirisi abartılıdır; bu satır duyarlılık analizidir, tahmin değil [çıkarım].

### 4.3 Parametre kalıcılığı (yürüyen pencere: 30 yıl eğitim, 10 yıl test, HO uzunluğu 2–24 aydan seçildi)

| Dönem | Al-ve-tut | Sabit HO(10) | Eğitimde seçilen HO |
|---|---:|---:|---:|
| 1930–2019 (9 pencere) | %9,72 | %10,36 | %10,35 |
| 1980–2019 (4 pencere) | %11,63 | %11,32 | %10,20 |
| 2010–2024 (10y eğitim/5y test, 3 pencere) | %13,82 | %11,24 | %11,06 |

Eğitimde en iyi olan parametre test penceresinde al-ve-tut'u 1930–2019'da pencerelerin %44'ünde, 1980–2019'da %25'inde, 2010–2024'te **%0**'ında geçti. Seçilen n değerleri pencereden pencereye 2 ile 14 arasında zıplıyor. Bu, Bajgrowicz-Scaillet ve Rink'in "ex ante en iyi kural seçilemez" bulgusunun küçük ölçekli replikasyonu [çıkarım].

### 4.4 En iyi/en kötü aylar (1950–2026, 919 ay)

| | Portföy çarpanı | Fark |
|---|---:|---:|
| Tam dönem | 4.530× | — |
| En iyi 10 ay kaçırılırsa | 1.696× | −%63 |
| En kötü 10 ay atlanırsa | 18.297× | +%304 |

Estrada (2008) günlük bulgusunun aylık karşılığı. Kâhin-aylık satırının %23 CAGR'ı buradan gelir: getiri birkaç uç aya yığılmıştır ve o ayların öncesinde sinyal yoktur.

### 4.5 Sınırlılıklar [çıkarım]
- Shiller verisi ayın *ortalama* fiyatı; düzleştirme HO kurallarını **lehte** yanıltır (2020 Mart çöküşü aylık ortalamada −%19 kalıp zigzag eşiğine bile girmedi). Günlük kapanışla whipsaw daha çok, sonuçlar trend kuralı için daha kötü olur.
- Tek endeks, tek ülke, aylık frekans. Tek hisse ve günlük/saatlik sinyal için literatür daha da olumsuz (§3 madde 3).
- Nakit getirisi 0 varsayımı zamanlamanın aleyhine; 10y faiz vekili lehine. Gerçek T-bill ikisinin arasında.
- BIST test edilmedi (veri erişimi yok).

---

## 5. Yapılabilir olan (literatür kanıtı olan, hedef değiştirilmiş hali)

Hedef "dipten al tepeden sat" değil, "aynı beklenen getiride daha sığ düşüş" veya "aynı düşüşte biraz daha yüksek getiri" olursa:

1. **Tek hisseyle uğraşmayı bırakıp endeks/portföyde aylık trend kuralı** (HO(10) ya da 12 ay getirisi>0): Getiri al-ve-tut'un biraz altında, maks. düşüş yarıdan az (§4.1). Sinyallerin ~%70'inin whipsaw olacağını **peşinen kabul** etmek gerekir; kazanç %30'luk azınlıktan gelir. Whipsaw'ı azaltmak için sinyali aylık kapanışta ve tek seferde değerlendirmek; günlük bakmamak.
2. **Oynaklık hedefleme**: pozisyon büyüklüğü ∝ 1/σ (geçen ayın gerçekleşen oynaklığı). Moreira-Muir'in mekanizması; dip/tepe bilmeyi gerektirmez. BIST için parametreler test edilmedi.
3. **Kesitsel momentum** (son 12 ay, son ayı atlayarak, kazanan desilini al) — tek hissede değil, sepet halinde; Türkiye'de kanıt kalitesi düşük [doğrulanmalı].
4. **İşlem sıklığını düşürmek** en güçlü ve en kesin kanıtlı müdahale: Barber-Odean, Chague, Kuo-Lin (§2.2). Al-sat ile HODL'ı geçemeyişinizin en olası açıklaması bir sinyal kusuru değil, sinyal sayısıdır [çıkarım].

Ne yapılamaz: haberden önce pozisyon almak (içeriden bilgi = suç), tek hissede günlük dip/tepe yakalamak, parametreyi geçmişe göre optimize edip geleceğe uygulamak (§4.3).

---

## 6. Mantık denetimi: sorudaki örtük varsayımlar

- *"Sinyal en tepede alım veriyor" → "daha iyi sinyal bulmalıyım."* Yanlış çıkarım: gecikme, gecikmesiz göstergenin olmamasından gelir; gösterge değişince gecikme değil, gürültü değişir (§1).
- *"Haber çıktığında fiyatlanmış" → "haberi önce bilmeliyim."* Yasal yol yok; yasal alternatif habere değil *rejime* (trend/oynaklık) tepki vermektir.
- *"HODL'ı geçemiyorum" → "strateji kötü."* Beklenen sonuç bu; literatürde bireysel yatırımcıların büyük çoğunluğu al-ve-tut'un altında kalır. Geçmek istisnadır ve istisnalar örneklem-dışı kalıcı değildir.
- *"Sonuç alana kadar döngü."* Döngü, veri-madenciliğinin tanımıdır: yeterince parametre denenirse geçmişte çalışan bir kural *mutlaka* bulunur (Jensen-Bennington 1970'in "rastgele sayı tablosu" argümanı, STW 1999 içinde aktarılıyor [kesin]). §4.3 bunun bedelini gösteriyor.

---

## Kaynaklar

Yalnızca bu oturumda kayıt olarak erişilenler (Scite/Consensus). Tam metne erişilemeyenler "özet" olarak işaretlidir.

- Ahmad, M. ve ark. (2018). Performance of moving average investment timing strategy in UK stock market. *J. Economic and Social Studies*. doi:10.14706/jecoss17722 (özet)
- Arif, M. ve ark. (2020). Profitability of the moving averages technical trading rules… Pakistan Stock Exchange. *J. Business Strategies*, 12(2). doi:10.29270/jbs.12.2(2018).095 (özet)
- Bajgrowicz, P. & Scaillet, O. (2012). Technical trading revisited: False discoveries, persistence tests, and transaction costs. *J. Financial Economics*, 106(3), 473–491. doi:10.1016/j.jfineco.2012.06.001
- Barber, B. M. & Odean, T. (2000). Trading is hazardous to your wealth. *J. Finance*, 55(2), 773–806. doi:10.2139/ssrn.219228 (SSRN kaydı)
- Brock, W., Lakonishok, J. & LeBaron, B. (1992). Simple technical trading rules and the stochastic properties of stock returns. *J. Finance*, 47(5), 1731–1764. doi:10.1111/j.1540-6261.1992.tb04681.x (özet)
- Buzzacchi, L. & Ghezzi, L. (2021). The odds of profitable market timing. *J. Risk and Financial Management*, 14(6), 250. doi:10.3390/jrfm14060250
- Chague, F., De-Losso, R. & Giovannetti, B. (2019). Day trading for a living? SSRN. doi:10.2139/ssrn.3423101 (özet)
- Estrada, J. (2008). Black swans and market timing: How not to generate alpha. *J. Investing*, 17(3), 20–34. doi:10.3905/joi.2008.710917; SSRN doi:10.2139/ssrn.1032962 (özet)
- Faber, M. T. (2007). A quantitative approach to tactical asset allocation. *J. Wealth Management*, 9(4), 69–79. doi:10.3905/jwm.2007.674809 (metne erişilemedi)
- Han, Y., Yang, K. & Zhou, G. (2013). A new anomaly: The cross-sectional profitability of technical analysis. *JFQA*, 48(5), 1433–1461. doi:10.1017/s0022109013000586 (özet)
- Jegadeesh, N. & Titman, S. (1993). Returns to buying winners and selling losers. *J. Finance*, 48(1), 65–91. doi:10.2307/2328882 (metne erişilemedi)
- Kuo, W. & Lin, T.-C. (2013). Overconfident individual day traders: Evidence from the Taiwan futures market. *J. Banking & Finance*, 37(9), 3548–3561. doi:10.1016/j.jbankfin.2013.04.036 (özet)
- Lo, A. W., Mamaysky, H. & Wang, J. (2000). Foundations of technical analysis. *J. Finance*, 55(4), 1705–1765. doi:10.1111/0022-1082.00265 (özet)
- Maciel, L. & da Silva, R. F. (2024). Market efficiency and equity risk premium predictability. *Int. J. Finance & Economics*, 30(3), 3064–3091. doi:10.1002/ijfe.3058
- Martineau, C. (2022). Rest in peace post-earnings announcement drift. *Critical Finance Review*, 11(3–4), 613–646. doi:10.1561/104.00000122 (özet)
- Metghalchi, M. ve ark. (2021). Trading rules and excess returns: evidence from Turkey. *Int. J. Islamic and Middle Eastern Finance and Management*. doi:10.1108/imefm-01-2020-0043 (özet)
- Moreira, A. & Muir, T. (2017). Volatility-managed portfolios. *J. Finance*, 72(4), 1611–1644. doi:10.1111/jofi.12513
- Moskowitz, T. J., Ooi, Y. H. & Pedersen, L. H. (2012). Time series momentum. *J. Financial Economics*, 104(2), 228–250. doi:10.1016/j.jfineco.2011.11.003 (metne erişilemedi)
- Neely, C. J., Rapach, D. E., Tu, J. & Zhou, G. (2014). Forecasting the equity risk premium: The role of technical indicators. *Management Science*, 60(7). SSRN doi:10.2139/ssrn.1787554 (Maciel & da Silva 2024 üzerinden)
- Özçalıcı, M. ve ark. (2022). Optimizing filter rule parameters with genetic algorithm… Borsa Istanbul. *Expert Systems with Applications*. doi:10.1016/j.eswa.2022.118120 (özet)
- Park, C.-H. & Irwin, S. H. (2007). What do we know about the profitability of technical analysis? *J. Economic Surveys*, 21(4), 786–826. doi:10.1111/j.1467-6419.2007.00519.x (özet)
- Pitkäjärvi, A., Suominen, M. & Vaittinen, L. (2020). Cross-asset signals and time series momentum. *J. Financial Economics*, 136(1), 63–85. doi:10.1016/j.jfineco.2019.02.011 (Goyal-Jegadeesh 2018 ve Huang ve ark. 2020 eleştirileri buradaki atıf metinlerinden)
- Ready, M. J. (2002). Profits from technical trading rules. *Financial Management*, 31(3). doi:10.2139/ssrn.64168 (özet)
- Rink, K. (2023). The predictive ability of technical trading rules: an empirical analysis of developed and emerging equity markets. *Financial Markets and Portfolio Management*. doi:10.1007/s11408-023-00433-2 (özet)
- Sharpe, W. F. (1975). Likely gains from market timing. *Financial Analysts Journal*, 31(2), 60–69. doi:10.2469/faj.v31.n2.60 (metne erişilemedi; ikincil kaynaklardan)
- Sullivan, R., Timmermann, A. & White, H. (1999). Data-snooping, technical trading rule performance, and the bootstrap. *J. Finance*, 54(5), 1647–1691. doi:10.1111/0022-1082.00163
- Tharavanij, P., Siraprapasiri, V. & Rajchamaha, K. (2015). Performance of technical trading rules: evidence from Southeast Asian stock markets. *SpringerPlus*, 4, 552. doi:10.1186/s40064-015-1334-7 (özet)

Veri: Shiller, R. — aylık S&P 500 fiyat/temettü/faiz tablosu, `datasets/s-and-p-500` GitHub deposu (1871-01 → 2026-08; temettü 2023-06'ya kadar).
