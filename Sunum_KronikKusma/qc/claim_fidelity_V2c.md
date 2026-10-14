# V2c iddia sadakati — A5, A6

Denetçi: V2c (adversaryal iddia-sadakat) · Tarih: 2026-10-14 · Sözleşme: `qc/_DENETCI_SOZLESME.md`

**Yöntem.**
- Satırlardaki 45 PMID'nin hepsi bu oturumda `mcp__PubMed__get_article_metadata` ile getirildi (10'arlı 5 parti + 1). Getirilenler: A5 ve A6 tablolarındaki tüm PMID'ler, not ve çelişki bölümlerindeki PMID'ler (Benninga 2016, Sigal 2025, Falsaperla 2023, Hikita 2026, Treepongkaruna 2014, Thavamani 2024, Partovi 2023, Martinez 2021).
- Tam metinler `mcp__PubMed__get_full_text_article` ile her PMC için bir kez alındı: PMC13202739 (Rosen 2026), PMC12954363 (Hernandez 2025), PMC6899751 (Venkatesan 2019), PMC6153591 (Li 2018), PMC13638314 (Nurko 2026), PMC13638347 (Sperber 2026), PMC12384603 (Altuntaş 2025). Topiramat karşılaştırması için ek olarak PMC6296701 (Bagherian 2019) alındı.
- Rosen ve Venkatesan alıntıları betikle denetlendi: boşluk, tire ve tırnak farkları normalize edildi, ardından alt dizi araması yapıldı. Özet ve öteki tam metin alıntıları satır satır okunarak karşılaştırıldı.
- DOI'ler betikle metadata'ya karşı denetlendi: 101 satırın hepsinde PMID↔DOI eşleşiyor.
- Geri çekilme: hiçbir kaydın `article_types` alanında "Retracted Publication" ya da "Expression of Concern" yok. Scite kullanılmadı.

**Karar ölçütü.**
- SUPPORTED: Türkçe iddia alıntı ya da kaynak metinle aynı anlamı taşıyor.
- PARTIAL: Anlamı değiştiren bir niteleyici düşmüş, tanım eksik ya da iddianın bir öğesi atıf yapılan alıntıda yok. Sorun sütununda (minör) ya da (önemli) olarak işaretlendi.
- OVERSTATED: İddia kaynaktan daha güçlü bir zorunluluk ya da daha geniş bir kapsam ileri sürüyor.

## Özet: n=101, SUPPORTED=76, PARTIAL=24, OVERSTATED=1, UNSUPPORTED=0, QUOTE_NOT_FOUND=0

- A5 (46 satır): SUPPORTED=35, PARTIAL=11.
- A6 (55 satır): SUPPORTED=41, PARTIAL=13, OVERSTATED=1.
- Bütün verbatim alıntılar kaynakta harfiyen bulundu (A5-03, A5-04 ve A6-49'un ilk alıntısı PubMed özetinde).
- Bibliyografik tutarlılık: 101/101 satırda PMID, DOI, ilk yazar, dergi ve yıl metadata ile uyumlu. Yalnız epub/baskı yılı kuralı dosyalar arasında tutarsız; bkz. Sistematik #9.

| ID | Karar | Alıntı bulundu mu | Sorun (kısa) | Önerilen düzeltme (TR, yalnız kaynak metnine dayalı) |
|---|---|---|---|---|
| A5-01 | SUPPORTED | Evet (özet) | — | — |
| A5-02 | SUPPORTED | Evet (özet) | — | — |
| A5-03 | SUPPORTED | Evet (özet; tam metinde özet yok) | — | — |
| A5-04 | PARTIAL | Evet (özet) | (minör) Kaynak "testing plays a greater role in **many of** these diagnostic criteria" diyor. İddia bunu tüm kriterlere genelliyor. | "Empedans ve yüksek çözünürlüklü manometrideki ilerlemeler nedeniyle testler, Rome V'teki bu tanı kriterlerinin **birçoğunda** önceki Rome sürümlerine göre daha büyük rol oynuyor." |
| A5-05 | SUPPORTED | Evet (özet) | Anket araştırma aracıdır; Not sütunu bunu doğru belirtiyor. | — |
| A5-06 | SUPPORTED | Evet (özet) | Rome IV; yalnız karşılaştırma için. | — |
| A5-07 | SUPPORTED | Evet (PMC) | CVS kutusunda ifade "by **other medical conditions**" (çoğul). Not sütunundaki "aynı ifade" kısmen doğru. | — |
| A5-08 | SUPPORTED | Evet (PMC, Nurko: Discussion) | İkincil ifade. Rosen'de açık bir "kaldırıldı" cümlesi yok. | — |
| A5-09 | SUPPORTED | Evet (özet) | — | — |
| A5-10 | SUPPORTED | Evet (özet) | — | — |
| A5-11 | SUPPORTED | Evet (PMC; 3/3) | — | — |
| A5-12 | PARTIAL | Evet (PMC) | (minör) Tanımdaki "**repetitive**" sözcüğü düşmüş. | "CVS: semptomsuz dönemlerle ayrılan, stereotipik, **tekrarlayıcı** bulantı, kusma ve/veya öğürme ataklarıyla karakterize bir bozukluk." |
| A5-13 | PARTIAL | Evet (PMC; kutu metni birebir) | (önemli) 1) Dışlama maddesindeki "**fully**" çevrilmemiş ("başka durumla açıklanamaz"). 2) "listlessness" → "letarji": Türkçe tıpta letarji bilinç düzeyini çağrıştırır; anlam kayıyor. 3) "**incessant** retching" ve maddeler arasındaki "**and/or**" düşmüş. 4) "Less acute or intermittent" → "hafif" olmuş. 5) İkinci listenin başlığı kaynak çıktısında yok. | "Rome V CVS, kutudaki ilk liste: (1) akut başlangıçlı, saatte birden çok tekrarlayan kusma içeren stereotipik ataklar; (2) son 12 ayda 2 saat–7 gün süren ≥4 ayrı atak; (3) ataklar arası en az 1 hafta; (4) ataklar arasında bazal sağlık durumuna dönüş; (5) uygun değerlendirmeden sonra semptomlar başka tıbbi durumlarla **tam olarak** açıklanamaz. İkinci liste (başlığı tam metin çıktısında yok, PDF'ten teyit edilmeden 'destekleyici' denmemeli): migren baş ağrısı öyküsü ya da aile öyküsü; ataklara halsizlik/durgunluk (*listlessness*), terleme, fotofobi, dinmeyen bulantı, karın ağrısı **ve/veya** mide boşaldıktan sonra da **aralıksız** süren öğürmenin eşlik etmesi; ataklar arasında karın ağrısı ve bulantı gibi **daha az akut ya da aralıklı** semptomlar bulunabilir." |
| A5-14 | SUPPORTED | Evet (PMC; 2/2) | — | — |
| A5-15 | SUPPORTED | Evet (PMC; 2/2) | Rosen'in "%2'ye kadar" verisi ile Nurko'nun %1,1 verisi birlikte verilirse kaynakları ayrı belirtilmeli. | — |
| A5-16 | SUPPORTED | Evet (PMC; 3/3) | Not sütunundaki NASPGHAN tanı kılavuzu cümlesi özette birebir var. Ancak özette bu önerinin **gücü (strong/conditional) yazmıyor**; slayta güç etiketi konmamalı. | — |
| A5-17 | PARTIAL | Evet (özet; 3/3) | (minör) "Rome IV kriterleri CVS'yi kaçırıyordu" genel bir yargı. Veri tek merkezli bir kohorttan (46 CVS, 54 CVS dışı analiz). | "Tek merkezli prospektif bir kohortta (108 kayıtlı; 46 CVS ve 54 CVS dışı hasta analiz edildi) CVS hastalarının yarıdan azı Rome IV ve NASPGHAN kriterlerini karşıladı. ROC analizinde en yüksek duyarlılık 12 ayda 4–10 atak ve >2 saat süre eşiğindeydi." |
| A5-18 | PARTIAL | Evet (PMC; Table 2 değerleri ve Results cümlesi) | (minör) "KHS **tanısı alan** çocuk yok" ifadesi yanlış yönlendiriyor. Kaynak "no child **met criteria**" diyor; veri ebeveyn bildirimli ankete dayanıyor, klinik tanıya değil. | "… KHS **ölçütlerini karşılayan** çocuk olmadı (yazarlara göre muhtemelen eksik bildirim). Veriler ebeveyn bildirimli çevrimiçi ankettir; Rome V anketi hekim tanısına karşı henüz valide edilmemiştir." |
| A5-19 | SUPPORTED | Evet (PMC) | — | — |
| A5-20 | SUPPORTED | Evet (PMC; kutu birebir) | "Supportive remarks:" başlığı kaynakta korunmuş. CHS kutusunda süre dipnotu yok. | — |
| A5-21 | SUPPORTED | Evet (PMC; 2/2) | Kaynak "limited data" diyor; bu not korunmalı. | — |
| A5-22 | SUPPORTED | Evet (PMC) | — | — |
| A5-23 | SUPPORTED | Evet (özet) | — | — |
| A5-24 | SUPPORTED | Evet (PMC) | — | — |
| A5-25 | SUPPORTED | Evet (PMC; 2/2) | Üç madde de birebir; "**Not associated with vomiting**" kaynakta harfiyen var. Kutunun giriş sözcüğü kayıp ("Must include**?**of"); maddelerin tümünün zorunlu olduğu varsayımı PDF ile doğrulanmalı (bkz. Rome V bölümü). | — |
| A5-26 | SUPPORTED | Evet (özet) | Rosen tam metninde ayrı bir "functional vomiting" kutusu yok (bu oturumda teyit edildi). | — |
| A5-27 | SUPPORTED | Evet (PMC; 2/2) | — | — |
| A5-28 | PARTIAL | Evet (PMC) | (minör) Mide boşalma çalışmasının istisnaları düşmüş: "unless vomiting is severe, the diagnosis is unclear, or the nausea is intractable". | "… Mide boşalma çalışması; kusma ağır, tanı belirsiz ya da bulantı inatçı **olmadıkça** rutin gerekmez. …" |
| A5-29 | PARTIAL | Evet (PMC; 2/2) | (önemli, kriter dili) Dışlama maddesinde "**fully**" çevrilmemiş. Geri kalan kriter çevirisi doğru. | "… uygun değerlendirmeden sonra semptomlar başka bir tıbbi durumla **tam olarak** açıklanamaz; yeme bozukluğu dışlanmalıdır." |
| A5-30 | SUPPORTED | Evet (PMC; 2/2) | Kaynak "Rome IV" değil "previous pediatric criteria" diyor. | — |
| A5-31 | SUPPORTED | Evet (PMC; 3/3) | 3/16 küçük seri. HRIM, başlığı kayıp ikinci listede. | — |
| A5-32 | SUPPORTED | Evet (PMC; 2/2) | — | — |
| A5-33 | PARTIAL | Evet (PMC; 3/3) | (önemli, kriter dili) 1) "**fully**" çevrilmemiş. 2) EPS tek ifadeye indirgenmiş: "PDS kriterleri karşılanmıyor" ve "fonksiyonel karın ağrısı/İBS ile açıklanamaz" maddeleri yok. 3) EPS kutusunun giriş sözcüğü kayıp. | "FD: rahatsız edici postprandiyal dolgunluk, erken doyma ya da epigastrik ağrı/yanmadan en az biri; uygun değerlendirmeden sonra başka bir tıbbi durumla **tam olarak** açıklanamaz; tanıdan önce en az 2 ay. PDS: haftada en az 3 gün; 'postprandiyal' = yemekten sonraki 2 saat içinde tetiklenen; postprandiyal bulantı destekleyici. EPS: işlevi ya da yaşam kalitesini etkileyen, haftada en az 1 gün, epigastriuma sınırlı ağrı/yanma; ağrı başka karın/göğüs bölgesinde yok; PDS kriterleri karşılanmıyor; fonksiyonel karın ağrısı ya da İBS dahil başka durumla tam olarak açıklanamaz. (EPS giriş sözcüğü PDF ile doğrulanmalı.)" |
| A5-34 | SUPPORTED | Evet (PMC) | Kaynakta gerekçe üç bileşenli: erişkin standardı, tipik öğün düzeni ve ön pediatrik veri. | — |
| A5-35 | SUPPORTED | Evet (PMC; 2/2) | — | — |
| A5-36 | SUPPORTED | Evet (PMC; 3/3) | — | — |
| A5-37 | SUPPORTED | Evet (PMC; 2/2) | — | — |
| A5-38 | SUPPORTED | Evet (PMC; Table 3 ve Discussion) | — | — |
| A5-39 | SUPPORTED | Evet (özet) | — | — |
| A5-40 | SUPPORTED | Evet (PMC; Table 3 ve Discussion) | ERİŞKİN. Kaynak bir epidemiyoloji makalesi, erişkin kriter belgesi değil; ikincil bir dayanak. | — |
| A5-41 | SUPPORTED | Evet (özet) | — | — |
| A5-42 | PARTIAL | Evet (PMC; 2/2) | (minör) Profilaksi koşulundaki "**that impair functioning**" düşmüş. Rome V'in tedavi cümleleri GRADE'lenmiş öneri değil. | "… Profilaktik ilaçlar, **işlevselliği bozan** sık ya da uzun ataklarda düşünülür." |
| A5-43 | SUPPORTED | Evet (PMC) | — | — |
| A5-44 | SUPPORTED | Evet (PMC; 2/2) | — | — |
| A5-45 | PARTIAL | Evet (PMC; 4/4) | (önemli) "Baklofen ek tedavidir" ifadesi kaynağın "**may be** an adjunctive therapy, **though data in children are limited**" ifadesini kesinleştiriyor. | "… Baklofen ek tedavi **olabilir**; ancak çocuk verisi sınırlıdır (yakın tarihli retrospektif bir pediatrik çalışmada çocukların yaklaşık %50'sinde güvenli ve etkili). …" |
| A5-46 | PARTIAL | Evet (PMC; 2/2) | (önemli) Kaynak "was **more effective** in functional nausea but not in FD" diyor; bu karşılaştırmalı bir ifade. İddia bunu "FD'de **etkili değil**" diye mutlaklaştırıyor. Birincil RCT özetine göre hipnoterapi ve standart tıbbi tedavi FD'de de etkili. | "57 çocukluk retrospektif seride (fonksiyonel bulantı ya da PDS) mirtazapinle yanıt %82. 100 çocukluk bir çalışmada hipnoterapi 3. ve 6. ayda daha iyi sonuç eğilimi gösterdi; fonksiyonel bulantıda standart tedaviden daha etkiliydi, FD'de üstünlük göstermedi." |
| A6-01 | PARTIAL | Evet (özet) | (minör) Karrento özeti "prior expert consensus recommendations" diyor; "**2008**" bu alıntıda yok. Yıl Hernandez tam metninde geçiyor ("replaces the prior 2008 NASPGHAN expert consensus statements"). | "NASPGHAN 2025 yönetim kılavuzu (GRADE, 16 öneri), önceki uzman konsensüs önerilerinin yerini almak üzere hazırlandı." Yıl isteniyorsa Hernandez 2025 alıntısı eklenmeli. |
| A6-02 | SUPPORTED | Evet (PMC) | — | — |
| A6-03 | SUPPORTED | Evet (PMC Hernandez; 3/3) | İKİNCİL. Hernandez 16 öneriyi hastane hekimi için 10'a indirmiş ("condensed"). "Recommendation 6/7" numaraları NASPGHAN'ın kendi numaraları değil; slaytta kullanılmamalı. | — |
| A6-04 | SUPPORTED | Evet (PMC Li 2018) | Fleisher'den aktarma. Kaynak cümlenin devamında bir sözcük kayıp ("70% of patients[?]the use of medications"); alıntı bu kısımdan önce kesilmiş. | — |
| A6-05 | SUPPORTED | Evet (özet) | Yazarlar "should not be interpreted as evidence that pharmacological treatments are unnecessary" diyor; Not sütunu bunu doğru veriyor. | — |
| A6-06 | SUPPORTED | Evet (özet) | Güçlü öneri özette birebir var. Kesinlik düzeyi ("moderate certainty") yalnız Hernandez'de. Karrento, pediatrik migren literatüründen dolaylı kanıt kullandığını belirtiyor. | — |
| A6-07 | SUPPORTED | Evet (PMC) | Rome V cümleleri derecelendirilmemiş konsensüs ifadesi. | — |
| A6-08 | SUPPORTED | Evet (özet; 2/2) | — | — |
| A6-09 | SUPPORTED | Evet (özet) | MeSH'te "Young Adult" da var; tamamen pediatrik değil. | — |
| A6-10 | PARTIAL | Evet (PMC) | (minör) "The efficacy **appears to** diminish" ifadesi "etkisi azalır" diye kesinleştirilmiş. ERİŞKİN kılavuz. | "ERİŞKİN (ANMS 2019, koşullu, orta kalite): triptanların prodromda ya da kusma başladıktan sonraki 30–45 dk içinde verilmesi önerilir. Etkinlik ilk 60 dakikadan sonra azalıyor **görünmektedir**. Oral emilim belirsiz olduğundan nazal ve enjektabl yol önerilir." |
| A6-11 | PARTIAL | Evet (PMC) | (önemli, doz) 1) Kaynakta 2. ve 3. gün dozu "**as needed**"; iddiada bu yok. 2) Doz, ERİŞKİN bir kılavuzun refrakter çocuklardaki tek bir seriyi aktarmasından geliyor. ANMS seriyi "open-label trial" olarak tanımlıyor, Cristofori özeti "retrospectively reviewed" diyor. ANMS'nin kendi "125, 80, 80 mg on three consecutive days" önerisi erişkin içindir. 3) Birincil pediatrik makalenin özetinde doz yok. | "Pediatrik veri, ERİŞKİN ANMS 2019 kılavuzunun aktarımıyla (refrakter çocuklarda tek seri; kanıt çok düşük): >20 kg çocuklara prodromda 125 mg, ardından sonraki 2 gün **gerektiğinde** 80 mg/gün verilmiş. Prodromda, kusmadan en az 30 dk önce alınan oral aprepitant tutulabilmiş." |
| A6-12 | SUPPORTED | Evet (özet) | — | — |
| A6-13 | SUPPORTED | Evet (özet) | Tarihsel (2008). | — |
| A6-14 | SUPPORTED | Evet (PMC Hernandez; 2/2) | İKİNCİL. İddianın ">24 saat gecikme en güçlü öngördürücü" kısmı Hernandez metninde var ("Delayed emergency department (ED) presentation (>24 h after symptom onset) is the greatest independent predictor for hospital admission."), ama tablodaki alıntıda yok. Alıntıya eklenmeli. | — |
| A6-15 | PARTIAL | Evet (PMC Li 2018; 2/2) | (minör) "can **occasionally** curtail episodes" ifadesindeki "occasionally" düşmüş. Tek merkez uzman deneyimi. | "… atakların çoğu (%72) uykuyla sona erdiğinden, indüklenen uyku semptomları hafifletir ve **bazen** atakları kısaltabilir (uzman deneyimi). Sedasyon için lorazepam ya da klorpromazin + difenhidramin kullanılır." |
| A6-16 | SUPPORTED | Evet (özet) | Tarihsel. "≤5 / >5" ile "<5 / ≥5" farkı (Li 2018) doğru saptanmış. | — |
| A6-17 | PARTIAL | Evet (özet) | (minör) "(siproheptadin)" Karrento özetinde yok; Hernandez Rec 9'da geçiyor ("e.g., cyproheptadine"). Kesinlik düzeyleri de yalnız Hernandez'de. | "… beta-blokerler, NK-1 ve 5-HT2A reseptör antagonistleri (Hernandez 2025 özetindeki örnek: siproheptadin) ve TSA'lar koşullu öneri…" Hernandez alıntısı kaynak olarak eklenmeli. |
| A6-18 | SUPPORTED | Evet (PMC Hernandez) | İKİNCİL. | — |
| A6-19 | SUPPORTED | Evet (özet; 3/3) | Tek kör, plasebosuz, Rome III, 6 ay. Özette doz yok. | — |
| A6-20 | SUPPORTED | Evet (özet; 2/2) | Doz ve oranlar özette birebir; pediatrik (3–15 yaş). Notlar: 1) "Atak kesildi" tam metinde "en azından son ay atak olmaması" (3 aylık izlem). 2) Tam metnin yöntem bölümünde topiramat dozu "1-2 mg/kg ... twice a day" yazıyor; özetle tutarsız. 3) Amitriptilin 1 mg/kg/gün, bu çalışmada titrasyon tanımlanmadan kullanılan sabit doz; bir kılavuz dozu değil. | — |
| A6-21 | SUPPORTED | Evet (özet) | — | — |
| A6-22 | PARTIAL | Evet (özet; 2/2) | (önemli) "Yanıt" tanımlanmamış: ≥%50 azalma demek, ve yalnız ≥12 ay tedaviyi tamamlayanlar alınmış. Topiramatta atak tamamen kesilmesi %81. Çelişki bölümünde Bagherian'ın "atak kesildi %39"u ile Sezer'in "%94"ü karşılaştırılıyor; sonlanımlar farklı. | "Türkiye, retrospektif (≥12 ay tedaviyi tamamlayan 38 hasta): atakların tamamen kesilmesi topiramatla %81, propranololle %59. ≥%50 azalmayı da içeren yanıt oranı topiramatla %94, propranololle %81." |
| A6-23 | PARTIAL | Evet (özet; 2/2) | (minör) "≥%50 iyileşme" aslında "dört parametreden **en az birinde** %50 azalma". Gevşek bir ölçüt. | "… dört parametreden (sıklık, süre, kusma sayısı, bulantı şiddeti) en az birinde %50 azalma: amitriptilinle %72, Co-Q ile %68. …" |
| A6-24 | PARTIAL | Evet (özet) | (önemli) Kaynak "6 patients **who responded**" diyor: seri yalnız yanıt verenlerden oluşuyor. İddia bunu bir kohort gibi sunuyor. | "L-karnitine yanıt veren 6 hastalık seri (yalnız yanıt verenler raporlanmış): ataklar arası ortalama süre 1,7 aydan 1,1 yıla uzadı." |
| A6-25 | SUPPORTED | Evet (özet; 2/2) | Retrospektif seri, n=14. | — |
| A6-26 | PARTIAL | Evet (özet) | (önemli) Randomize olmayan bir grupta "tamamında başarı" denmiş. Başarı tanımı gevşek. Tam metne göre SSRI, yaşam tarzına uyumu yüksek hastalarda ek fayda göstermedi ("did not show additional benefit over the attack group with high lifestyle adherence"). | "Retrospektif, randomize olmayan kohort: psikiyatrist kararıyla SSRI başlanan orta–ağır anksiyeteli 34 hastanın tümü 12. haftada başarı ölçütünü karşıladı. Başarı: atakların tamamen durması ya da yatış, uzamış atak ve okul/iş devamsızlığının olmaması. Yaşam tarzına uyumu yüksek hastalarda SSRI, yalnız atak tedavisine göre ek fayda göstermedi." |
| A6-27 | SUPPORTED | Evet (özet; 2/2) | Kontrolsüz. | — |
| A6-28 | SUPPORTED | Evet (PMC Li 2018) | Uzman derlemesi; kılavuz eşiği değil. | — |
| A6-29 | SUPPORTED | Evet (PMC; 3/3) | — | — |
| A6-30 | SUPPORTED | Evet (PMC; 4/4) | — | — |
| A6-31 | SUPPORTED | Evet (özet; 2/2) | — | — |
| A6-32 | SUPPORTED | Evet (özet; 2/2) | — | — |
| A6-33 | SUPPORTED | Evet (özet) | ERİŞKİN (19–79 yaş). | — |
| A6-34 | SUPPORTED | Evet (özet; 2/2) | ERİŞKİN. Popülasyon "rumination **and/or SGB**" şüphesi olan hastalar. | — |
| A6-35 | SUPPORTED | Evet (PMC; 3/3) | — | — |
| A6-36 | SUPPORTED | Evet (özet; 2/2) | — | — |
| A6-37 | SUPPORTED | Evet (özet; 2/2) | Popülasyon refrakter üst GİS semptomlu çocuklar (fundoplikasyon sonrası öğürme dahil); salt FD değil. | — |
| A6-38 | SUPPORTED | Evet (özet; 2/2) | — | — |
| A6-39 | SUPPORTED | Evet (PMC) | — | — |
| A6-40 | SUPPORTED | Evet (özet; 2/2) | Kanıt türü sütunundaki "açık etiketli, çok merkezli" özette geçmiyor. | — |
| A6-41 | SUPPORTED | Evet (özet; 3/3) | — | — |
| A6-42 | SUPPORTED | Evet (özet; 3/3) | Kontrolsüz önce–sonra çalışması, n=16. Sonuç cümlesi yazarların genellemesi. | — |
| A6-43 | PARTIAL | Evet (PMC) | (minör) "kademeli azaltma **önerilir**" ifadesi kaynağın "gradual reduction and lower-THC products **may improve success**" ifadesini öneriye çeviriyor; "düşük THC'li ürünler" de düşmüş. (A5-43 doğru çevirmiş.) | "… Ani bırakma yoksunluk ve nükse yol açabileceğinden kademeli azaltma ve düşük THC'li ürünler başarıyı artırabilir." |
| A6-44 | SUPPORTED | Evet (özet; 3/3) | ERİŞKİN; dozlar erişkin içindir. | — |
| A6-45 | SUPPORTED | Evet (özet; 3/3) | ERİŞKİN. Not sütunundaki Hernandez kapsaisin cümlesi tam metinde birebir var. | — |
| A6-46 | SUPPORTED | Evet (özet) | Retrospektif, tek merkez. Not sütunundaki "yatış kriteri değil" uyarısı doğru. | — |
| A6-47 | SUPPORTED | Evet (özet; 2/2) | — | — |
| A6-48 | PARTIAL | Evet (PMC Hernandez; 3/3) | (önemli) 1) "Subspecialist consultation" ve "monthly episodes…" cümleleri **Hernandez ve Gardner'ın kendi görüşü** ("We recommend…"); NASPGHAN önerisi değil. 2) "such as monthly episodes" bir **örnek**; iddia bunu ölçüte çevirmiş. | "NASPGHAN 2025 (Hernandez özeti): antikonvülzanlar (ör. topiramat, valproat) yalnız refrakter hastalıkta kullanılmalı (koşullu öneri, çok düşük kesinlik). Hernandez ve Gardner'ın kendi önerisi: profilaktik ilaç öncesi subspesiyalist konsültasyonu; antikonvülzanlar yalnız ağır refrakter semptomlarda düşünülmeli (örneğin acil başvuru ve yatış gerektiren aylık ataklar)." |
| A6-49 | SUPPORTED | Evet (özet ve PMC; 3/3) | ERİŞKİN. Protokol "sample template". | — |
| A6-50 | SUPPORTED | Evet (PMC Li 2018; 2/2) | Uzman görüşü. | — |
| A6-51 | OVERSTATED | Evet (PMC) | 1) Kaynak betimleyici: "Diagnosis is clinical but supported by tests to rule out mimics, especially if…". İddia bunu "tetkik **yapılmalı**" diye zorunluluğa çeviriyor. 2) "(tanıyı yeniden sorgulama eşiği)" ifadesi kaynakta yok; yorum. 3) Cümle yalnız **CVS** bölümünde geçiyor; izlem slaytında genelleştirilmemeli. | "Rome V (CVS bölümü): tanı kliniktir; ancak özellikle kırmızı bayraklar (ör. safralı kusma, nörolojik semptomlar, hepatomegali) varsa ya da standart tedaviye 2 ay içinde yanıt alınamazsa taklitçileri dışlamak için testlerle desteklenir." |
| A6-52 | PARTIAL | Evet (özet) | (minör) Kaynakta kırmızı bayraklar ilk tanıdaki hedefe yönelik tetkik stratejisi olarak geçiyor. "İzlemde tanının yeniden düşünülme nedeni" yorumu kaynakta yok. | "NASPGHAN 2008: 'shotgun' test yerine 4 kırmızı bayrağa göre değişen hedefe yönelik tetkik önerilir; bunlardan biri kusma ataklarının ilerleyici kötüleşmesi ya da paterninin değişmesidir." |
| A6-53 | SUPPORTED | Evet (PMC Li 2018; 2/2) | Uzman görüşü. | — |
| A6-54 | PARTIAL | Evet (özet; 3/3) | (minör) Kaynaktaki "**may need to be** adjusted" ifadesi "uyarlanmalı" olmuş. Tek merkezli üçüncü basamak serisi; %40'ın yalnız %20'si kapsamlı otonom testle doğrulanmış. | "Tek merkezli retrospektif seride (n=100) CVS'li çocukların %40'ında otonom disfonksiyon semptomları gelişti (%20'si kapsamlı otonom testle doğrulandı). Kronik semptom başlangıç yaşı medyan 14. Semptomlar zamanla değişirse tedavinin buna göre uyarlanması **gerekebilir**." |
| A6-55 | SUPPORTED | Evet (özet; 2/2) | Retrospektif. Kohort yalnız ilacı kesilen hastalardan oluşuyor. | — |

### Hassas noktalar: kısa yanıtlar

1. **Karrento 2025 kılavuzları (tam metin yok).**
   - Yönetim kılavuzu (40223700): "A strong recommendation was formulated for the use of anti-migraine agents…" ve koşullu önerilerin tamamı özette birebir var.
   - Özette **kesinlik düzeyi (certainty) hiçbir öneri için yok**; kesinlikler yalnız ikincil kaynak Hernandez'de.
   - Tanı kılavuzu (40836301): "The panel recommends screening serum and urine laboratory testing and an upper gastrointestinal radiographic series…" özette birebir var, ama **öneri gücü yazmıyor**. NASPGHAN 2025 tanı kriterlerinin metni de özette yok.
2. **Hernandez 2025.**
   - Kendi ifadesiyle "16 recommendations condensed into 10". Öneri numaraları ve metinleri kılavuzun birebir dili olarak kullanılamaz.
   - A6-48'deki iki cümle yazarların kendi görüşü.
   - İkincil olarak kullanıldığı satırlar: A6-03, A6-14, A6-18, A6-48. Not sütununda kullanıldığı satırlar: A6-01, A6-06, A6-17, A6-45.
3. **Topiramat ve amitriptilin verileri.**
   - Badihian RCT: tek kör, plasebosuz, Rome III, 6 ay. Tam remisyon amitriptilinle %65,6, siproheptadinle %50 (P=0,206). Yaşa bağlı etki yok.
   - Bagherian RCT: blok randomizasyon; körleme tanımlanmamış; 3 ay.
     - "Vomit-free" (son ay atak yok): amitriptilin %68 (23/34), topiramat %39 (14/36).
     - ≥%50 iyileşme: %79,4 ve %44,4.
   - Sezer (retrospektif, ≥12 ay tamamlayanlar), topiramat: atak tamamen kesilmesi %81, ≥%50 yanıt %94.
   - **Doğru eşleştirme:** tam kesilme için %39 ile %81; ≥%50 yanıt için %44,4 ile %94.
   - "%39 ile %94" karşılaştırması farklı sonlanımları yan yana koyuyor. Bagherian tam metni de karşılaştırılamazlığı kabul ediyor.
4. **Amitriptilin 1 mg/kg/gün.** Bagherian özetinde birebir var; pediatrik (3–15 yaş). Ancak bu tek bir İran RCT'sinin sabit çalışma dozu.
   - Hernandez (ikincil): "TCA standard dosing is 1.0–1.5 mg/kg/day", QTc uyarısıyla birlikte.
   - Li 2018 (uzman görüşü): 0,2–0,3 mg/kg/gün ile başlayıp yavaş titrasyon ve EKG.
   - Slaytta "kılavuz dozu" olarak değil, "RCT'de kullanılan doz" olarak etiketlenmeli.
5. **Aprepitant >20 kg 125/80/80 mg.** Alıntı ANMS 2019 (ERİŞKİN kılavuz) içinde birebir var ve pediatrik seriyi aktarıyor. 2. ve 3. gün dozları "as needed". Ayrıntı için A6-11 satırına bakın.
6. **Abdulkader 2020.** Dört öngördürücü ve %62 yatış oranı özette birebir var. Retrospektif, tek merkez, 152 acil başvurusu. Bunlar yatış kriteri değil.
7. **"2 ay" ifadesi (Rome V).** Tam cümle: "Diagnosis is clinical but supported by tests to rule out mimics, especially if red flags (e.g., bilious vomiting, neurologic symptoms, hepatomegaly) are present or if no response to standard treatment occurs within 2 months."
   - "Tanıyı sorgula" ifadesi kaynakta yok.
   - Cümle yalnız CVS bölümünde geçiyor (A6-51).
8. **Kronik bulantı sendromu, "Not associated with vomiting".** Madde 2 olarak harfiyen var. Gerekçe cümlesi: "Vomiting is excluded from the definition, as children typically present with nausea alone."

## Rome V kriter metni karşılaştırması

Karşılaştırılan: `fulltext/romeV_kriterler_verbatim.md` içindeki HAM ve OKUMA KOPYASI blokları ile bu oturumda alınan PMC13202739 tam metni. Karşılaştırma betikle yapıldı. Her HAM bloğu, kaynakta paragraf arası boş satırlar dışında **ardışık ve birebir** bulundu. Her OKUMA KOPYASI, satır sonları silindiğinde HAM ile birebir aynı.

| Blok | Sonuç | Not |
|---|---|---|
| G3b CVS tanım | Birebir aynı | — |
| G3b CVS kutu | Birebir aynı (yalnız boş satır farkı) | İki numaralı liste (1–5 ve 1–4); ikinci listenin başlığı kaynak çıktısında **yok**. Süre dipnotu yok. |
| G3b.i CHS kutu | Birebir aynı | "Supportive remarks:" korunmuş. "Δ(THC)" kaynakta da böyle; üst simge kaybı olabilir. |
| G3c CNS tanım ve kutu | Birebir aynı | "vomit.CNS" boşluksuz yazım kaynakta da var. "Must includeof" kaynakta da böyle. |
| G3a RS tanım ve kutu | Birebir aynı | İkinci listenin başlığı yok. "After appropriate evaluation…" cümlesi numarasız. |
| G3d FD başlıklar/tanım | Kelimeler aynı; **küçük yapısal eksik** | HAM bloğunda kaynaktaki "Definition" ara başlık satırı atlanmış. Kriter metnini etkilemiyor. "C3d.i/C3d.ii" yazım hatası kaynakta da var. |
| G3d FD, PDS, EPS kutuları | Birebir aynı | EPS'de "Must includeof" var. "that's symptoms" ve "medicalcondition" kaynakta da böyle. |
| G2 FPFD kutu, G2b ARF | Birebir aynı | Alt başlıklar kaynak çıktısında yok. "thewith" ve "dysfunctionand" kaynakta da böyle. |

**Ajanın üç uyarısının değerlendirmesi.**

1. **"Kutu başlıkları kaybolmuş": DOĞRU.** Araç çıktısında kutu içi alt başlıklar yok; FPFD kutusunun altı listesi, RS ve CVS'nin ikinci listeleri başlıksız. Sözcük ve boşluk kaybına başka örnekler de var: "Criteriafor", "thewith", "dysfunctionand", "medicalcondition". RH kutusunda yaş sütun başlıkları ("Patients <8 years old / >8 years old") korunmuş; kayıp tutarlı değil.
2. **"Must includeof" boşluğu: DOĞRU, ve ajanın bildirdiğinden yaygın.** Tam metinde 5 kez geçiyor: RH <8 yaş, RH >8 yaş, RNEPD >8 yaş, CNS ve EPS. Ajan RNEPD >8'i saymamış.
   - Aynı belgedeki paralel kutular "Must include **all** of the following" diyor: RNEPD <8 yaş ve RS ("Must include all of the following symptoms").
   - CNS ve EPS kutularında dışlama maddesi listenin bir parçası. Bu da tüm maddelerin zorunlu olduğu bir yapıya işaret ediyor.
   - Yine de eksik sözcük araç çıktısından **kesin belirlenemez → dergi PDF'iyle kontrol gerekir.** Tahmin yazılmadı.
3. **CVS ikinci listesinin destekleyici olup olmadığı: ÇÖZÜLEMEDİ → dergi PDF'iyle kontrol gerekir.**
   - Lehine işaret: aynı belgede aerofaji kutusunun başlıksız ikinci listesindeki öğeler (flatus, geğirme) gerekçe metninde "no longer a major criterion" ve "excessive belching … is a supportive criterion" diye tanımlanıyor. Yani belgede başlıksız ikinci liste en az bir kez destekleyici/minör kriter anlamında kullanılmış. CVS klinik değerlendirme metni de bu öğeleri "associated symptoms" olarak anıyor.
   - Aleyhine işaret: CVS ikinci listesi dışlama maddesini (4. madde) birebir tekrarlıyor. Bu, destekleyici bir liste için olağandışı.
   - Sonuç: Slaytta başlık yazılmamalı ya da "ek özellikler (Rome V kutusu, ikinci liste)" gibi nötr bir ifade kullanılmalı. "Destekleyici kriterler" yalnız PDF teyidinden sonra yazılmalı.

**Türkçe kriter çevirileri** (A5-13, A5-20, A5-25, A5-29, A5-33):
- CHS (A5-20) ve CNS (A5-25) çevirileri sadık.
- CVS, RS ve FD çevirilerinde (A5-13, A5-29, A5-33) dışlama maddesindeki "**fully**" sözcüğü çevrilmemiş. Bu, A5-07'nin vurguladığı Rome V dil değişikliğinin tam tersini yaratıyor.
- CVS'de ek olarak "listlessness → letarji", "incessant" düşmesi ve "and/or" kaybı var.
- EPS maddeleri FD satırında eksik.

## Sistematik sorunlar (dosya geneli)

1. **Kriter dilinde "tam olarak" kaybı (A5-13, A5-29, A5-33).**
   - Rome V dışlama cümlesi "cannot be **fully** explained by". A5-07 bunu Rome IV'ten farkı diye öne çıkarıyor, ama kriter çevirileri bu sözcüğü düşürüyor.
   - Slaytlarda tüm dışlama maddeleri "başka bir tıbbi durumla tam olarak açıklanamaz" diye yazılmalı.
2. **Kaçınma ifadelerinin silinmesi.** Kaynaktaki "may / appears to / occasionally / may need to / may improve success" ifadeleri Türkçede kesin yargıya dönüşüyor: A5-45, A6-10, A6-15, A6-43, A6-51, A6-54. Aynı türden niteleyici düşmesi: A5-42 ("that impair functioning") ve A5-28 (mide boşalma istisnaları). Tedavi slaytlarında bu, öneri gücünü abartır.
3. **İkincil kaynağın birincil kılavuz yerine geçmesi (Hernandez 2025).**
   - NASPGHAN 2025 önerilerinin kesinlik düzeyleri yalnız bu ikincil, sıkıştırılmış özetten geliyor.
   - Slaytta "NASPGHAN 2025 (Hernandez 2025 özetiyle)" diye atıf yapılmalı. "Öneri 1…10" numaraları kullanılmamalı. Hernandez yazarlarının kendi "We recommend…" cümleleri NASPGHAN'a mal edilmemeli (A6-48).
   - JPGN tam metniyle karşılaştırma ihtiyacı sürüyor; A6'nın kendi [DOĞRULANAMADI] #1 maddesi de bunu söylüyor.
4. **Farklı sonlanımların yan yana konması (çelişki bölümleri).**
   - A6 Çelişki #3 Bagherian'ın "vomit-free %39" verisini Sezer'in "responder %94" verisiyle karşılaştırıyor. Doğru eşleştirmeler: %39 ile %81 (atak tamamen kesilmesi), %44,4 ile %94 (≥%50 yanıt).
   - Benzer tanım belirsizlikleri: A6-23 (Boles: dört parametreden biri), A6-12 (tam ya da kısmi yanıt), A6-26 (gevşek başarı tanımı).
   - Slaytta her oranın yanında sonlanım tanımı ve izlem süresi verilmeli.
5. **Doz etiketleri.** A6'nın "yalnız RCT/kılavuz kaynaklı doz" kuralı biçimsel olarak sağlanıyor, ama:
   - Amitriptilin 1 mg/kg/gün tek bir İran RCT'sinin sabit dozu (plasebosuz, 3 ay, titrasyon tanımsız).
   - Aprepitant 125/80/80 mg ERİŞKİN bir kılavuzun refrakter çocuklardaki tek bir retrospektif/açık etiketli seriyi aktarması; 2. ve 3. gün dozu "gerektiğinde".
   - Bagherian tam metninde topiramat dozu yöntemde "1-2 mg/kg ... twice a day", özette "1-2 mg/kg/d"; tutarsız.
   - Dozlar "önerilen doz" değil, "çalışmada kullanılan doz" diye etiketlenmeli. Hernandez'deki QTc uyarısı (ikincil) da amitriptilinle birlikte verilmeli.
6. **Rome V tedavi cümleleri derecelendirilmemiş konsensüs.** "Kılavuz / uzman konsensüsü" etiketi slaytta öneri gücü (GRADE) gibi görünmemeli. Rosen metninde strong/conditional derecelendirmesi yok.
7. **Kapsam genelleştirmesi.** Yalnız CVS bölümünde geçen "2 ay" cümlesi (A6-51) genel izlem kuralı gibi sunuluyor. NASPGHAN 2008'in tanı amaçlı kırmızı bayrakları da (A6-52) izlem ölçütü gibi kullanılıyor.
8. **Çelişki bölümünde seçici alıntı (A6 #3).** Hikita 2026'dan yalnız "recommend not using the antiseizure medications" cümlesi alınmış. Özetin hemen sonraki cümlesi atlanmış: "However, antiseizure medications are recommended only for patients who are unresponsive to the aforementioned preventive medications and who have frequent vomiting and severe symptoms." Bu cümle Karrento'nun "only in refractory CVS" ifadesiyle örtüşüyor; ileri sürülen "çelişki" büyük ölçüde yapay.
   - Çelişki #5'teki Partovi alıntısında GA "0.2 (0.08-0.005)" kaynakta da böyle; üst sınır alt sınırdan küçük, kaynak dizgi hatası. Slayta konmamalı.
9. **Bibliyografya.**
   - Aynı makale iki dosyada farklı anahtarlarla yer alıyor: Rosen2026a (A5) ile Rosen2026 (A6), Karrento2025b (A5) ile Karrento2025 (A6). Birleştirmede kopya kayıt oluşur.
   - Epub ve baskı yılı kuralı karışık: Badihian 2017 (cilt 113, 2018), Pauwels 2017, Ruberto 2020, Browne 2021, Abdulkader 2020, Hikita 2010, Hernandez 2025 (cilt 21) epub yılıyla; diğerleri baskı yılıyla yazılmış. Slayt atıflarında tek kural seçilmeli.
   - PMID ve DOI eşleşmelerinin tümü doğru.
10. **Popülasyon ve kanıt etiketleri.**
    - ERİŞKİN etiketi A6-10, A6-33, A6-34, A6-44, A6-45 ve A6-49'da doğru konmuş. A6-11 karma bir durum: pediatrik veri, erişkin kılavuz.
    - A6-09'da MeSH'te "Young Adult" var.
    - A5-18'deki prevalanslar ebeveyn anketine dayanıyor ve Rome V anketi henüz valide değil; "tanı" sözcüğü kullanılmamalı.
11. **Kutu yapısı belirsizlikleri slayta taşınmamalı.**
    - CVS ikinci listesinin başlığı.
    - "Must include…of" boşluğu: CNS, EPS, RH ve RNEPD kutuları.
    - RS ikinci listesinin statüsü.
    - FPFD alt başlıkları.

    Dördü de **dergi PDF'iyle kontrol gerektiriyor.** Bu denetimde tahminle doldurulmadı.
