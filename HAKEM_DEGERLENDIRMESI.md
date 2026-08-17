# Hakem Değerlendirmesi (Hakem 2)

**Makale:** Metabolik Disfonksiyon ile İlişkili Steatotik Karaciğer Hastalığı Olan Çocuklarda I-FABP, Sitrülin ve Zonulin Serum Düzeylerinin Değerlendirilmesi

**Öneri: Büyük revizyon (Major Revision).** Çalışmanın sorusu geçerli ve MR-PDFF ile kantitatif steatoz ölçümü takdire değer; ancak metodolojik geçerlilik (özellikle ELISA temelli ölçümler), güç analizi hesapları ve istatistiksel raporlamada, aşağıda tek tek gösterdiğim, sonuçların güvenilirliğini doğrudan etkileyen ciddi sorunlar ve iç tutarsızlıklar mevcuttur. Bunlar giderilmeden ana mesajın ("sitrülin pediatrik MASLD'de umut verici belirteç") desteklendiğine ikna olmadım.

---

## Majör Eleştiriler

### 1. Birincil belirteç olan sitrülinin ELISA ile ölçümü çalışmanın en zayıf halkasıdır
Sitrülin bir amino asittir; küçük moleküllerin ölçümünde altın standart iyon değişim kromatografisi veya LC-MS/MS'dir. Ticari sandviç ELISA kitlerinin (özellikle araştırma amaçlı, valide edilmemiş kitlerin) amino asit ölçümündeki analitik geçerliliği tartışmalıdır ve üretici dışı bağımsız validasyon verisi sunulmamıştır. Nitekim:
- Sağlıklı kontrol grubunuzun medyan sitrülin düzeyi **61,15 µmol/L** olup, hem pediatrik referans aralıklarının (~20–40 µmol/L) hem de güç analizinize temel aldığınız Bugajska ve ark. çalışmasındaki kontrol değerinin (38,8 ± 6,1 µmol/L) çok üzerindedir. Bu farkın nedeni açıklanmalıdır; en olası açıklama yöntem (ELISA vs. kromatografi) farkıdır ve bu durumda mutlak değerleriniz ve ROC kesim noktanız (≤31,1 nmol/mL) başka merkezlere taşınamaz.
- Kit tanımında iç çelişki vardır: sitrülin kitinin ölçüm aralığı 0,5–100 nmol/mL olarak bildirilmişken standart eğrinin en üst noktası **128 nmol/mL**'dir. Ölçüm aralığının üzerinde standart olamaz; hangisi doğrudur?
- Zonulin (aralık 0,3–90; standartlar 3–48) ve I-FABP (aralık 0,5–150; standartlar 5–80) için de bildirilen ölçüm aralıkları standart eğrinin dışına taşmaktadır; eğri dışı değerler ekstrapole mi edildi?

**İstenen:** En azından rastgele seçilmiş bir alt örneklemde LC-MS/MS ile yöntem karşılaştırması (Bland-Altman) yapılmalı ya da bu yapılamıyorsa, mutlak değerlerin ve kesim noktasının genellenemeyeceği sınırlılıklarda açıkça kabul edilmelidir.

### 2. Zonulin bulgusu "literatüre katkı" olarak sunulamaz
Yaygın ticari zonulin ELISA kitlerinin gerçekte zonulini (pre-haptoglobin-2) değil, haptoglobin ve kompleman C3 gibi başka proteinleri tanıdığı gösterilmiştir (Scheffler et al., Front Endocrinol 2018; Ajamian et al., PLoS One 2019). Kullanılan kitin hedef antijeni doğrulanmadığı sürece, gruplar arası fark bulunmaması "yeni bir bulgu" değil, büyük olasılıkla ölçüm geçersizliğinin sonucudur. Tartışmadaki "çalışmamızda elde edilen veriler literatüre yeni bulgular katması açısından değerlidir" cümlesi bu haliyle savunulamaz; ya kaldırılmalı ya da kit validasyon verisiyle desteklenmelidir.

### 3. I-FABP değerleriniz dayandığınız literatürle ~100 kat uyumsuz
Çalışmanızda I-FABP medyanları ~22–25 **ng/mL** iken, güç analizinize temel aldığınız pediatrik çalışmada [9] aynı belirteç 272–321 **pg/mL** düzeyindedir — yaklaşık iki kademe (≈100 kat) fark. Aynı analit için bu büyüklükte bir uyumsuzluk, ölçümlerden en az birinin analitik geçerliliğini sorgulatır ve makalede hiç tartışılmamıştır. Ayrıca [9] numaralı çalışmadan yalnızca **medyanlar** aktarılmışken bunlardan Cohen's d (≈0,12) hesaplanmış görünmektedir; standart sapma olmadan d hesaplanamaz. Bu etki büyüklüğünün nasıl türetildiği açıklanmalıdır.

### 4. Güç analizi bölümü baştan sona yeniden yazılmalıdır
1. Çalışmanın asıl klinik sorusu MASLD'li obez ile MASLD'siz obez ayrımı iken, sitrülin için temel alınan etki büyüklüğü **kontrol vs. fazla kilolu/obez** karşılaştırmasından alınmıştır; birincil karşılaştırmanız için güç hesabı fiilen yapılmamıştır.
2. d=1,88 ve %95 güç (iki yönlü α=0,05) için grup başına gereken örneklem ~**8**'dir, bildirilen 6 değil. Hesap doğrulanmalı, G*Power çıktısı eklenmelidir.
3. d=0,12 ve %80 güç için grup başına gereken örneklem ~**1.090**'dır, bildirilen "yaklaşık 500" değil. Bu hesap da yanlıştır.
4. Referans alınan Bugajska ve ark. örneklemi 5–9 yaş prepubertal çocuklardır; 10–18 yaş, ağırlıklı pubertal popülasyona genellenmesi (yazarların kendilerinin de sınırlılıklarda kabul ettiği üzere) sorunludur.
5. "EPV kuralı gözetilerek 50 katılımcı" gerekçesi kendi içinde çelişkilidir: 6 bağımsız değişkenli lojistik regresyonda 50 olay ile EPV ≈ 8,3'tür ve klasik ≥10 kuralının **altındadır**. Model ya değişken sayısı azaltılarak yeniden kurulmalı ya da aşırı uyum (overfitting) riski açıkça belirtilip penalize edilmiş (ör. Firth) regresyon düşünülmelidir.

### 5. MASLD tanımındaki kardiyometabolik kriter bu örneklemde totolojiktir
Kardiyometabolik kriterlerin ilki "VKİ ≥85. persentil"dir. Çalışmaya yalnızca **obez** çocuklar alındığına göre, steatozu olan her katılımcı bu kriteri otomatik olarak karşılar; "≥1 kriter" koşulu hiçbir hastayı dışlamamıştır. Grupların fiili tanımı "steatozlu obez vs. steatozsuz obez"dir; bu, metinde açıkça belirtilmeli ve kaç hastanın VKİ dışında ek kriter taşıdığı raporlanmalıdır. Ayrıca obezite tanımının kendisi (hangi persentil/z-skoru eşiği, hangi referans) makalede hiçbir yerde verilmemiştir — temel bir eksikliktir.

### 6. İstatistiksel raporlamada iç tutarsızlıklar (düzeltilmesi zorunlu)
1. **Korelasyon örneklemi çelişkisi:** Yöntemde Spearman analizi "(n=150)" olarak yazılmış, Tablo 2 başlığında ise "(n=100)" denmektedir. Tablodaki p-değerleri n=100 ile uyumludur (ör. r=−0,094 → p=0,353); dolayısıyla yöntem metni yanlıştır. Hangi popülasyonda yapıldığı netleştirilmelidir — n=150'de yapılmışsa grup yapısı korelasyonları yapay olarak şişirir.
2. **Çifte Bonferroni şüphesi:** I-FABP için MASLD vs. MASLD'siz obez karşılaştırmasında Mann-Whitney p=0,123 bildirilmiş; oysa aynı karşılaştırmanın ROC analizi (AUC anlamlılık testi Mann-Whitney ile matematiksel olarak eşdeğerdir) p=0,048 vermektedir. 0,041 × 3 = 0,123 olması, Tablo 1'deki ikili p-değerlerinin Bonferroni ile **çarpılmış** olduğunu düşündürmektedir; ancak tablo dipnotu anlamlılık eşiğini 0,017 (**bölünmüş** alfa) olarak uygulamaktadır. Bu, çifte düzeltme demektir ve bazı gerçek farkları maskelemiş olabilir. Ya ham p + eşik 0,017 ya da düzeltilmiş p + eşik 0,05 raporlanmalı; hangisinin yapıldığı açıkça yazılmalıdır.
3. **Anlamsız omnibus sonrası post-hoc:** Zonulin (genel p=0,094) ve total kolesterol (genel p=0,058) için Kruskal-Wallis anlamlı değilken ikili karşılaştırma p-değerleri (0,041; 0,026) sunulmuştur. Kendi yönteminize göre bu post-hoc testler hiç yapılmamalıydı; tablodan çıkarılmalıdır.
4. Metinde I-FABP için "istatistiksel olarak anlamlı bir ayırt edicilik" (AUC 0,612; p=0,048; GA alt sınırı 0,501) ifadesi, aynı karşılaştırmada grup farkının anlamsız bulunmasıyla (p=0,123) birlikte sunulamaz; bu çelişki çözülmeden iki iddiadan biri geri çekilmelidir.

### 7. ROC kesim değeri iç doğrulamasızdır; "tanı" iddiası aşırıdır
Kesim noktası (≤31,1) aynı örneklemde türetilmiş ve performansı yine aynı örneklemde raporlanmıştır; optimizm düzeltmesi (bootstrap/çapraz doğrulama) yapılmamıştır. Amaç cümlesindeki "pediatrik MASLD'nin **tanısı ve ayırıcı tanısındaki** yerini belirlemek" ifadesi, kesitsel, tek merkezli, dış doğrulaması olmayan bir ilişki çalışması için fazla iddialıdır; "ilişkisini incelemek" düzeyine çekilmelidir. Duyarlılığın %69 olduğu bir testin tanısal değeri zaten yazarlarca da sınırlı bulunmuştur — bu doğru; o hâlde başlıktan sonuca kadar dil buna göre yumuşatılmalıdır.

### 8. Kontrol grubu ve etik/uygulama soruları
- "Sağlıklı" kontroller hastaneye **başvuran** çocuklardır; başvuru nedenleri bildirilmemiştir. Gerçek anlamda sağlıklı toplum örneklemi değildir; seçim yanlılığı tartışılmalıdır.
- Sağlıklı çocuklara yalnızca araştırma amacıyla abdominal MR uygulanmıştır. Kontrast kullanılmasa da, bu uygulamanın etik kurul onayında açıkça yer alıp almadığı ve onam sürecinde nasıl anlatıldığı belirtilmelidir.
- Etik kurul tarihi 28.08.2025 iken karar numarası "24/19"dur; numara 2024'ü ima etmektedir. Tutarsızlık düzeltilmeli/açıklanmalıdır.
- Akış şemasında 219 − 69 = 150 tam olarak denk gelmektedir; ancak "her grup 50'ye ulaşınca kota durduruldu" deniyor. Kota durdurma varsa, kotadan sonra başvuran uygun hastaların da şemada "dışlanan" olarak görünmesi gerekirdi. Sayıların bu kadar "temiz" olması açıklanmalıdır.

### 9. Yöntem eksikleri
- Puberte (Tanner) evrelemesi yapılmamıştır; buna rağmen tartışmada puberte etkisi uzun uzadıya (ve yalnızca yaş korelasyonu üzerinden dolaylı biçimde) savuşturulmaktadır. Yaş, puberte evresinin zayıf bir vekilidir; bu sınırlılık daha dürüst ifade edilmelidir.
- İnsülin ölçüm yöntemi ve HOMA-IR formülü, kan basıncı ölçüm protokolü (kaç ölçüm, hangi cihaz, hangi referans) verilmemiştir.
- İki radyolog değerlendirme yapmış ancak gözlemciler arası uyum (ICC) raporlanmamıştır; analizlerde hangi okuyucunun (veya ortalamanın) değerlerinin kullanıldığı belirsizdir.
- Örneklerin toplu mu (tek seferde) analiz edildiği, kaç dondurma-çözme döngüsü geçirdiği ve saklama süresi belirtilmemiştir (I-FABP'nin kısa yarı ömrü tartışılırken preanalitik değişkenlik es geçilemez).
- n=50'lik gruplar için normallik testi olarak Kolmogorov-Smirnov yerine Shapiro-Wilk tercih edilmeliydi (en azından Lilliefors düzeltmesi belirtilmelidir).

### 10. Yapısal/editoryal sorunlar
- **Özet ve anahtar kelimeler yoktur.**
- Sınırlılıklar iki ayrı paragrafta mükerrer yazılmıştır (tartışmanın sondan üçüncü ve ikinci paragrafları büyük ölçüde aynı içeriği tekrarlar); sonuç cümlesi de neredeyse kelimesi kelimesine iki kez geçmektedir. Birleştirilmelidir.
- Bölüm numaralandırması tutarsızdır (Giriş numarasız, "2. Gereç ve Yöntem", "3. İstatistiksel Analiz" ayrı ana bölüm).
- Çıkar çatışması, finansman, yazar katkı beyanı ve veri paylaşım beyanı eksiktir.

---

## Minör Eleştiriler

1. "gösterirmiştir" → "göstermiştir" (Tartışma, ilk paragraf).
2. Ondalık ayraç tutarsız: metnin geneli virgül kullanırken ROC bölümü ve Şekil 2 alt yazısı nokta kullanmaktadır (0.742 vs 0,742). Tek biçime getirilmelidir.
3. "[14][23]" → "[14], [23]".
4. Tablo 1'de 21 değişken için değişkenler-arası çoklu test düzeltmesi yapılmamıştır; en azından bu durum dipnotta kabul edilmelidir.
5. Tablo 2'de işaret gösterimi tutarsız (bazı satırlarda "+/−" işareti var, bazılarında "-"); ayrıca HOMA-IR–sitrülin ilişkisi (p=0,015) Bonferroni sonrası anlamsızken HOMA-IR ve sitrülinin regresyonda birlikte anlamlı çıkması tartışmada kısaca yorumlanabilirdi.
6. Kaynak [27] (Pacifico) tek yazarlı görünmektedir; orijinal makale çok yazarlıdır, "vd." eksik olabilir. Tüm kaynakların dergi biçimine uygunluğu kontrol edilmelidir.
7. Şekil 1'deki ok/kutu düzeni metin akışında bozulmuştur (dizgi sorunu); vektörel şekil olarak yeniden hazırlanmalıdır.
8. "Birincil analizler için %95 güç" ile ikincil belirteçte %80 güç seçimi keyfîdir; gerekçe verilmelidir.

## Sonuç

Araştırma sorusu değerli, görüntüleme metodolojisi güçlüdür; ancak (i) üç belirtecin üçünün de analitik geçerliliği gösterilmemiş ELISA kitleriyle ölçülmüş olması, (ii) güç analizi hesaplarının doğrulanamaması ve (iii) istatistiksel raporlamadaki iç çelişkiler nedeniyle mevcut haliyle yayına uygun değildir. Yukarıdaki maddelerin tamamına madde madde yanıt verilmesi koşuluyla, büyük revizyon sonrası yeniden değerlendirmeye hazırım.
