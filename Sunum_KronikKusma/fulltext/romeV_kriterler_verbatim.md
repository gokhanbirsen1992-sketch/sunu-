# Rome V pediatrik kriterler — VERBATIM (A5)

Bu dosya **yalnız** PubMed Central tam metninden (`mcp__PubMed__get_full_text_article`, PMC13202739, erişim 2026-10-14) alınmış kriter metinlerini içerir. Kriter metinlerinde tek kelime değiştirilmemiştir.

**Birincil kaynak (tüm bloklar, aksi belirtilmedikçe):** Rosen R, Borrelli O, Faure C, et al. Rome V Pediatric Upper Gastrointestinal Disorders of Gut-Brain Interaction. Gastroenterology 2026;170(6):1347-1366. PMID 41713704 · DOI 10.1053/j.gastro.2026.01.039 · PMC13202739

## Okuma kuralları ve araç çıktısı uyarıları (slayta geçirmeden önce MUTLAKA okuyun)

1. Her blok iki biçimde verilir: **HAM** = araç çıktısı aynen (kod bloğu); **OKUMA KOPYASI** = yalnız madde numaralarının önüne satır sonu eklenmiş hali. Bir Python betiği, OKUMA KOPYASI'ndan satır sonları silindiğinde HAM metnin birebir elde edildiğini doğruladı (kelime/karakter değişikliği yok).
2. PMC→araç dönüşümünde **kutu/tablo başlıkları ve kalın/italik bazı sözcükler kaybolmuştur.** Saptanan kayıplar:
   - `Must includeof the following` (CNS, EPS kutuları): `include` ile `of` arasında bir sözcük düşmüş görünüyor. Eksik sözcük **tahmin edilip eklenmedi**; dergi PDF'i ile kontrol edilmeli.
   - CVS kutusu: iki ayrı numaralı liste var (1–5 ve 1–4); **ikinci listenin başlığı araç çıktısında yok.** İkinci listenin "destekleyici kriterler" olduğu varsayımı kaynakta yazılı olarak doğrulanamadı → slaytta başlık yazılacaksa PDF'ten teyit edilmeli. (Karşılaştırma: aynı bölümdeki CHS kutusunda başlık korunmuş: `Supportive remarks:`.)
   - Ruminasyon kutusu: zorunlu kriterlerden sonra gelen ikinci numaralı listenin (stres, HRIM) başlığı yok; `After appropriate evaluation…` cümlesinin madde numarası da görünmüyor.
   - FPFD (G2) kutusu: altı ayrı liste/paragraf var, **hiçbirinin başlığı (ör. hangi listenin "en az biri", hangisinin dışlama, hangisinin alt tip tanımı olduğu) çıktıda yok.** Bu kutu slayta yalnız PDF ile karşılaştırıldıktan sonra konmalı.
   - `Diagnostic Criteriafor` başlıklarında dipnot işareti (`*`) boşluğu kaybolmuş; FD alt tip başlıklarında kaynakta `C3d.i` / `C3d.ii` yazıyor (muhtemelen dizgi hatası, `G3d` olmalı) — aynen bırakıldı.
3. Dipnotlar (`*Criteria fulfilled for at least …`) kutunun hemen altında ayrı satırdadır; süre eşikleri buradadır.
4. Rome IV kriter metni bu dosyada **yoktur** (Rome IV pediatrik makaleleri PMC'de değil; verbatim alınamadı → [DOĞRULANAMADI]).

---
## 1. Siklik kusma sendromu (CVS) — G3b

### G3b — CVS: tanım

*Kaynak:* Rosen 2026, PMC tam metin — bölüm: `G3b.Cyclic Vomiting Syndrome (CVS) / Definition` (araç çıktısı satırları [293]).

**HAM:**

```text
CVS is a disorder characterized by stereotypical episodes of repetitive nausea, vomiting, and/or retching dispersed with symptom-free periods.
```

**OKUMA KOPYASI (yalnız satır sonu eklendi):**

```text
CVS is a disorder characterized by stereotypical episodes of repetitive nausea, vomiting, and/or retching dispersed with symptom-free periods.
```

### G3b — CVS: kriter kutusu

*Kaynak:* Rosen 2026, PMC tam metin — bölüm: `G3b.Diagnostic Criteria for Cyclic Vomiting Syndrome` (araç çıktısı satırları [295, 297]).

> UYARI: İkinci numaralı listenin (1–4) başlığı araç çıktısında kayıp; ikinci listenin 4. maddesi birinci listenin 5. maddesi ile aynı cümledir. Kutu düzeni PDF'ten teyit edilmeli.

**HAM:**

```text
G3b.Diagnostic Criteria for Cyclic Vomiting Syndrome
1. Stereotypical episodes of acute onset, repetitive vomiting multiple times per hour2. ≥4 discrete episodes in the prior 12 months, lasting 2 hours to 7 days3. Episodes at least 1 week apart4. Return to baseline health between episodes5. After appropriate evaluation, the symptoms cannot be fully explained by other medical conditions1. History or family history of migraine headaches2. Episodes associated with listlessness, diaphoresis, photophobia, unrelenting nausea, abdominal pain, and/or incessant retching after emptying stomach3. Less acute or intermittent symptoms such as abdominal pain and nausea can be present between episodes4. After appropriate evaluation, the symptoms cannot be fully explained by other medical conditions
```

**OKUMA KOPYASI (yalnız satır sonu eklendi):**

```text
G3b.Diagnostic Criteria for Cyclic Vomiting Syndrome
1. Stereotypical episodes of acute onset, repetitive vomiting multiple times per hour
2. ≥4 discrete episodes in the prior 12 months, lasting 2 hours to 7 days
3. Episodes at least 1 week apart
4. Return to baseline health between episodes
5. After appropriate evaluation, the symptoms cannot be fully explained by other medical conditions
1. History or family history of migraine headaches
2. Episodes associated with listlessness, diaphoresis, photophobia, unrelenting nausea, abdominal pain, and/or incessant retching after emptying stomach
3. Less acute or intermittent symptoms such as abdominal pain and nausea can be present between episodes
4. After appropriate evaluation, the symptoms cannot be fully explained by other medical conditions
```

---
## 2. Kannabinoid hiperemezis sendromu (CHS) — G3b.i (CVS alt grubu)

### G3b.i — CHS: kriter kutusu

*Kaynak:* Rosen 2026, PMC tam metin — bölüm: `G3b.i. Diagnostic Criteria for Cannabinoid Hyperemesis Syndrome` (araç çıktısı satırları [299, 301]).

**HAM:**

```text
G3b.i. Diagnostic Criteria for Cannabinoid Hyperemesis Syndrome
1. Stereotypical episodes of vomiting resembling cyclic vomiting syndrome (CVS) in terms of onset, duration and frequency2. Presentation after prolonged (e.g. 1–2 years), excessive (e.g. near daily) cannabis use3. Resolution of vomiting episodes by sustained (at least 6 months) cessation of cannabis useSupportive remarks:1. May be associated with pathologic bathing behavior (prolonged hot baths or showers)2. Diagnosis strengthened by positive urine Δ(THC) test
```

**OKUMA KOPYASI (yalnız satır sonu eklendi):**

```text
G3b.i. Diagnostic Criteria for Cannabinoid Hyperemesis Syndrome
1. Stereotypical episodes of vomiting resembling cyclic vomiting syndrome (CVS) in terms of onset, duration and frequency
2. Presentation after prolonged (e.g. 1–2 years), excessive (e.g. near daily) cannabis use
3. Resolution of vomiting episodes by sustained (at least 6 months) cessation of cannabis use
Supportive remarks:
1. May be associated with pathologic bathing behavior (prolonged hot baths or showers)
2. Diagnosis strengthened by positive urine Δ(THC) test
```

---
## 3. Kronik bulantı sendromu (Chronic nausea syndrome, CNS) — G3c

Rome V pediatrik metindeki resmî ad: **"Chronic Nausea Syndrome"** (kutu başlığı) / "chronic nausea syndrome (CNS)". Pediatrik Rome V'te ad "kronik bulantı **ve kusma** sendromu" DEĞİLDİR; kusma tanımdan çıkarılmıştır (gerekçe metni: "Vomiting is excluded from the definition, as children typically present with nausea alone.").

### G3c — Kronik bulantı sendromu: tanım

*Kaynak:* Rosen 2026, PMC tam metin — bölüm: `G3c.Chronic nausea syndrome (CNS) / Definition` (araç çıktısı satırları [349]).

**HAM:**

```text
Nausea, a common symptom, is an unpleasant feeling, usually in the epigastrium or throat, associated with a sense of needing to vomit.CNS is now recognized as a disabling condition often linked to multiple comorbidities.
```

**OKUMA KOPYASI (yalnız satır sonu eklendi):**

```text
Nausea, a common symptom, is an unpleasant feeling, usually in the epigastrium or throat, associated with a sense of needing to vomit.CNS is now recognized as a disabling condition often linked to multiple comorbidities.
```

### G3c — Kronik bulantı sendromu: kriter kutusu

*Kaynak:* Rosen 2026, PMC tam metin — bölüm: `G3c.Chronic Nausea Syndrome` (araç çıktısı satırları [355, 357, 359, 361]).

> UYARI: `Must includeof` — bir sözcük kayıp (bkz. okuma kuralları 2).

**HAM:**

```text
G3c.Chronic Nausea Syndrome
Must includeof the following:1. Bothersome nausea as the predominant symptom, occurring at least twice per week2. Not associated with vomiting3. After appropriate evaluation, the nausea cannot be fully explained by another medical condition
*
Criteria fulfilled for at least 2 months before diagnosis
```

**OKUMA KOPYASI (yalnız satır sonu eklendi):**

```text
G3c.Chronic Nausea Syndrome
Must includeof the following:
1. Bothersome nausea as the predominant symptom, occurring at least twice per week
2. Not associated with vomiting
3. After appropriate evaluation, the nausea cannot be fully explained by another medical condition
*
Criteria fulfilled for at least 2 months before diagnosis
```

---
## 4. Ruminasyon sendromu (RS) — G3a

### G3a — Ruminasyon sendromu: tanım

*Kaynak:* Rosen 2026, PMC tam metin — bölüm: `G3a.Rumination Syndrome (RS) / Definition` (araç çıktısı satırları [245]).

**HAM:**

```text
RS is an acquired behavioral disorder characterized by repetitive and volitional, although subconscious, episodes of regurgitation of gastric contents.
```

**OKUMA KOPYASI (yalnız satır sonu eklendi):**

```text
RS is an acquired behavioral disorder characterized by repetitive and volitional, although subconscious, episodes of regurgitation of gastric contents.
```

### G3a — Ruminasyon sendromu: kriter kutusu

*Kaynak:* Rosen 2026, PMC tam metin — bölüm: `G3a.Diagnostic Criteriafor Rumination Syndrome` (araç çıktısı satırları [247, 249, 251, 253]).

> UYARI: İkinci numaralı listenin (stres / HRIM) başlığı kayıp.

**HAM:**

```text
G3a.Diagnostic Criteriafor Rumination Syndrome
Must include all of the following symptoms for minimum 2 months, starting after 3 months of age:1. Repeated, seemingly effortless regurgitation of gastric contents that is:a. Re-swallowed and/or re-chewed and/or expelled during or immediately after a meal or ingestion of fluidsb. Does not occur during sleep2. Does not respond to standard management for gastroesophageal reflux disease or infant regurgitation.After appropriate evaluation, the symptoms cannot be fully explained by another medical condition. An eating disorder must be ruled out.1. The repeated regurgitation of gastric contents might occur during or after physical or psychological stress2. High resolution esophageal impedance manometry (HRIM) may help confirm the diagnosis in cases of unusual symptomatology or family skepticism. HRIM allows for prompt identification of the rumination episodes, with the sensitivity maximized by an extended recording after a test meal
*
Criteria fulfilled for at least 2 months prior to diagnosis with onset of symptoms after 3 months of age:
```

**OKUMA KOPYASI (yalnız satır sonu eklendi):**

```text
G3a.Diagnostic Criteriafor Rumination Syndrome
Must include all of the following symptoms for minimum 2 months, starting after 3 months of age:
1. Repeated, seemingly effortless regurgitation of gastric contents that is:
a. Re-swallowed and/or re-chewed and/or expelled during or immediately after a meal or ingestion of fluids
b. Does not occur during sleep
2. Does not respond to standard management for gastroesophageal reflux disease or infant regurgitation.
After appropriate evaluation, the symptoms cannot be fully explained by another medical condition. An eating disorder must be ruled out.
1. The repeated regurgitation of gastric contents might occur during or after physical or psychological stress
2. High resolution esophageal impedance manometry (HRIM) may help confirm the diagnosis in cases of unusual symptomatology or family skepticism. HRIM allows for prompt identification of the rumination episodes, with the sensitivity maximized by an extended recording after a test meal
*
Criteria fulfilled for at least 2 months prior to diagnosis with onset of symptoms after 3 months of age:
```

---
## 5. Fonksiyonel dispepsi (FD) — G3d ve alt tipleri

### G3d — FD: başlıklar ve tanım

*Kaynak:* Rosen 2026, PMC tam metin — bölüm: `G3d.Functional Dyspepsia (FD) / Definition` (araç çıktısı satırları [385, 387, 389, 393]).

**HAM:**

```text
G3d.Functional Dyspepsia (FD)
C3d.i Postprandial Distress Syndrome (PDS)
C3d.ii Epigastric Pain Syndrome (EPS)
FD describes upper GI discomfort that may include a variable combination of features, including epigastric pain, postprandial upper abdominal fullness, early satiety, bloating, nausea, belching, and vomiting. Two main subtypes have been identified: PDS and EPS.
```

**OKUMA KOPYASI (yalnız satır sonu eklendi):**

```text
G3d.Functional Dyspepsia (FD)
C3d.i Postprandial Distress Syndrome (PDS)
C3d.ii Epigastric Pain Syndrome (EPS)
FD describes upper GI discomfort that may include a variable combination of features, including epigastric pain, postprandial upper abdominal fullness, early satiety, bloating, nausea, belching, and vomiting. Two main subtypes have been identified: PDS and EPS.
```

### G3d — FD: kriter kutusu

*Kaynak:* Rosen 2026, PMC tam metin — bölüm: `G3d.Diagnostic Criteria* for Functional Dyspepsia` (araç çıktısı satırları [395, 397]).

**HAM:**

```text
G3d.Diagnostic Criteria* for Functional Dyspepsia
Must include 1 or more of the following bothersome symptoms1. Postprandial fullness2. Early satiation3. Epigastric pain or burningAfter appropriate evaluation, the symptoms cannot be fully explained by another medical condition.*Criteria fulfilled for at least 2 months prior to diagnosisTwo subtypes:G3d.i. Postprandial distress syndromeG3d.ii. Epigastric pain syndrome
```

**OKUMA KOPYASI (yalnız satır sonu eklendi):**

```text
G3d.Diagnostic Criteria* for Functional Dyspepsia
Must include 1 or more of the following bothersome symptoms
1. Postprandial fullness
2. Early satiation
3. Epigastric pain or burning
After appropriate evaluation, the symptoms cannot be fully explained by another medical condition.
*Criteria fulfilled for at least 2 months prior to diagnosis
Two subtypes:
G3d.i. Postprandial distress syndrome
G3d.ii. Epigastric pain syndrome
```

### G3d.i — PDS: kriter kutusu

*Kaynak:* Rosen 2026, PMC tam metin — bölüm: `G3d.i.Diagnostic criteria for Post Prandial Distress Syndrome` (araç çıktısı satırları [399, 401]).

> Not: `**` işareti dipnot işaretidir ("Postprandial" tanımı, 2 saat).

**HAM:**

```text
G3d.i.Diagnostic criteria for Post Prandial Distress Syndrome
Must include one or more of the following bothersome symptoms at least 3 days per week1. Bothersome postprandial **fullness that occurs with completion of a developmentally and culturally appropriate meal2. Early satiation that prevents finishing a developmentally and culturally appropriate mealSupportive features include upper abdominal bloating, postprandial nausea, discomfort or excessive belching.** Postprandial means that’s symptoms are triggered within 2 hours after meal intake
```

**OKUMA KOPYASI (yalnız satır sonu eklendi):**

```text
G3d.i.Diagnostic criteria for Post Prandial Distress Syndrome
Must include one or more of the following bothersome symptoms at least 3 days per week
1. Bothersome postprandial **fullness that occurs with completion of a developmentally and culturally appropriate meal
2. Early satiation that prevents finishing a developmentally and culturally appropriate meal
Supportive features include upper abdominal bloating, postprandial nausea, discomfort or excessive belching.
** Postprandial means that’s symptoms are triggered within 2 hours after meal intake
```

### G3d.ii — EPS: kriter kutusu

*Kaynak:* Rosen 2026, PMC tam metin — bölüm: `G3d.ii. Diagnostic criteria for Epigastric Pain Syndrome` (araç çıktısı satırları [403, 405]).

> UYARI: `Must includeof` — bir sözcük kayıp.

**HAM:**

```text
G3d.ii. Diagnostic criteria for Epigastric Pain Syndrome
Must includeof the following bothersome symptoms (interferes with function or quality of life) at least one day per week1. Pain or burning localized to the epigastrium.2. The pain is not present in any other abdominal or chest region3. Symptoms can be induced or worsened post-prandially or can occur independently of meals but PDS criteria are not fulfilled4. After appropriate evaluation, the symptoms cannot be fully explained by another medicalcondition including functional abdominal pain or IBS
```

**OKUMA KOPYASI (yalnız satır sonu eklendi):**

```text
G3d.ii. Diagnostic criteria for Epigastric Pain Syndrome
Must includeof the following bothersome symptoms (interferes with function or quality of life) at least one day per week
1. Pain or burning localized to the epigastrium.
2. The pain is not present in any other abdominal or chest region
3. Symptoms can be induced or worsened post-prandially or can occur independently of meals but PDS criteria are not fulfilled
4. After appropriate evaluation, the symptoms cannot be fully explained by another medicalcondition including functional abdominal pain or IBS
```

---
## 6. Fonksiyonel pediatrik beslenme bozuklukları (FPFD) — G2 (kusma ile ilişkili kısım)

Kusma ile bağlantı: Anticipatory Restrictive Feeding (ARF) "bulantı … veya kusma" gibi aversif deneyim korkusu ile tanımlanır (aşağıdaki anlatı). FPFD kriter kutusu araç çıktısında başlıksız listeler halindedir.

### G2 — FPFD: kriter kutusu (alt başlıklar araç çıktısında kayıp)

*Kaynak:* Rosen 2026, PMC tam metin — bölüm: `G.2.Diagnostic Criteria* for Functional Feeding Disorders` (araç çıktısı satırları [171, 173, 175, 177, 179, 181, 183]).

> UYARI: Listelerin hangi kriter grubuna (A/B/C, alt tip tanımı) ait olduğu araç çıktısından çıkarılamıyor. Slayta konmadan PDF ile karşılaştırılmalı. Süre eşiği dipnotu: `*Criteria fulfilled for at least 1 month prior to diagnosis`.

**HAM:**

```text
G.2.Diagnostic Criteria* for Functional Feeding Disorders
1. Evidence of nutritional compromise (micronutrient deficiency, macronutrient deficiency)2. Use of supplemental enteral or parenteral nutrition3. Active or passive avoidance behavior(s)4. Use of a restricted/selective diet or a diet that is not developmentally appropriate to treat symptoms5. Lack of developmentally expected self-feeding6. Excessive use of routine feeding strategies (e.g., chewing, liquid wash down, pacing) to complete a meal
*Criteria fulfilled for at least 1 month prior to diagnosis
1. No evidence of pharyngeal or esophageal mucosal or structural abnormalities2. Absence of major esophageal motor disorders3. No evidence of bolus transit abnormalities
1. Significant weight loss (or failure to achieve expected weight gain or faltering growth in children)2. Significant nutritional deficiency3. Dependence on enteral feeding or oral nutritional supplements4. Marked interference with other psychosocial functioning
The patient will not voluntarily eat or drink calorically appropriate foods after periods of age-appropriate fasting AND the patient requires prompting and/or scheduling of meals in order to insure adequate intake.The patient has excessive hunger manifested by inability to stop eating even after finishing a meal and excessive eating between meals even after completing a full meal.
1. Developed in the context of a medical condition but the feeding dysfunctionand cannot be attributed to the underlying medical condition2. Manifests as a regression or lack of progression of feeding patterns or skills that previously achieved and cannot be attributed to the medical condition
```

**OKUMA KOPYASI (yalnız satır sonu eklendi):**

```text
G.2.Diagnostic Criteria* for Functional Feeding Disorders
1. Evidence of nutritional compromise (micronutrient deficiency, macronutrient deficiency)
2. Use of supplemental enteral or parenteral nutrition
3. Active or passive avoidance behavior(s)
4. Use of a restricted/selective diet or a diet that is not developmentally appropriate to treat symptoms
5. Lack of developmentally expected self-feeding
6. Excessive use of routine feeding strategies (e.g., chewing, liquid wash down, pacing) to complete a meal
*Criteria fulfilled for at least 1 month prior to diagnosis
1. No evidence of pharyngeal or esophageal mucosal or structural abnormalities
2. Absence of major esophageal motor disorders
3. No evidence of bolus transit abnormalities
1. Significant weight loss (or failure to achieve expected weight gain or faltering growth in children)
2. Significant nutritional deficiency
3. Dependence on enteral feeding or oral nutritional supplements
4. Marked interference with other psychosocial functioning
The patient will not voluntarily eat or drink calorically appropriate foods after periods of age-appropriate fasting AND the patient requires prompting and/or scheduling of meals in order to insure adequate intake.The patient has excessive hunger manifested by inability to stop eating even after finishing a meal and excessive eating between meals even after completing a full meal.
1. Developed in the context of a medical condition but the feeding dysfunctionand cannot be attributed to the underlying medical condition
2. Manifests as a regression or lack of progression of feeding patterns or skills that previously achieved and cannot be attributed to the medical condition
```

### G2b — ARF: anlatı tanımı (kriter kutusu değil)

*Kaynak:* Rosen 2026, PMC tam metin — bölüm: `i G2b.Anticipatory Restrictive Feeding (ARF)` (araç çıktısı satırları [197, 199]).

> Bu bir kriter kutusu değil, bölüm anlatı metnidir (ARF için ayrı kriter kutusu araç çıktısında yok).

**HAM:**

```text
i G2b.Anticipatory Restrictive Feeding (ARF)
ARF is characterized by the fear of an aversive experience with eating (e.g., nausea, pain, bloating, gagging, choking or vomiting). Clinically, these patients may present with significant diet restrictions resulting in elimination of entire food groups, specific food textures, or food temperatures. Children may express experiences of anxiety, disgust, or fear when consuming new, symptom-triggering or nonpreferred foods. ARF differs from a medically triggered functional feeding disorder in that the latter is associated with thewith the development of a medical illness. ARF does not have a loss of skills or milestones but is associated with fear of eating. ARF is common in children with concurrent DGBI and the majority (>80%) of these patients have underlying gastrointestinal symptoms.
```

**OKUMA KOPYASI (yalnız satır sonu eklendi):**

```text
i G2b.Anticipatory Restrictive Feeding (ARF)
ARF is characterized by the fear of an aversive experience with eating (e.g., nausea, pain, bloating, gagging, choking or vomiting). Clinically, these patients may present with significant diet restrictions resulting in elimination of entire food groups, specific food textures, or food temperatures. Children may express experiences of anxiety, disgust, or fear when consuming new, symptom-triggering or nonpreferred foods. ARF differs from a medically triggered functional feeding disorder in that the latter is associated with thewith the development of a medical illness. ARF does not have a loss of skills or milestones but is associated with fear of eating. ARF is common in children with concurrent DGBI and the majority (>80%) of these patients have underlying gastrointestinal symptoms.
```

---
## 7. Süt çocuğu regürjitasyonu (infant regurgitation)

Rosen 2026 pediatrik üst GİS tam metninde ayrı bir "infant regurgitation" kriter kutusu **yoktur**. Terim yalnız ruminasyon kriterinde geçer: `Does not respond to standard management for gastroesophageal reflux disease or infant regurgitation.` [Rosen 2026, PMC fulltext: G3a kriter kutusu].

Rome V'te kaldırıldığına dair doğrudan ifade (ikincil, Rome Foundation pediatrik global çalışması):

> "This increase largely reflects better methodology and the inclusion of additional Rome V entities, despite the elimination of infant regurgitation." — Nurko S, Taft T, Palsson OS, et al. Gut 2026;75(10):1898-1909. PMID 42613193 · DOI 10.1136/gutjnl-2026-339667 · PMC13638314 [PMC fulltext: Discussion]

---
## 8. Abdominal migren (Rome V pediatrik) — [DOĞRULANAMADI]

Kriter metni Di Lorenzo C ve ark. Gastroenterology 2026;170(6):1367-1387 (PMID 41713707, DOI 10.1053/j.gastro.2026.01.036) içindedir; makalenin PMC kaydı yok (`convert_article_ids` ve `find_related_articles` pubmed_pmc boş döndü), özette AM kriteri geçmiyor, Scite tam metin aracı (ücretli plan gerekli) ve Wiley Scholar Gateway (ücretsiz kota bitti) kullanılamadı. **Bu nedenle AM kriter metni yazılmamıştır.** Rome IV AM kriteri yerine konmamalıdır.

Doğrulanabilen sınırlı bilgi:

- Nurko 2026 Gut Rome V pediatrik global çalışmasında AM, `Abdominal pain disorders (ages 5 and older)` başlığı altında listelenmiş; prevalans `1.5%(1.2%–1.8%)n=94` [PMC fulltext: Table 3]; tartışmada: "abdominal migraine 1.5% as previously reported" [PMC fulltext: Discussion].
- Rosen 2026: "Nausea is also a fundamental symptom in episodic DGBI such as abdominal migraines and CVS" [PMC fulltext: G3c Epidemiology].
- ERİŞKİN: Rome V'te AM erişkinlerde yeni DGBI: "The prevalence rates for two new DGBI were 5.1% for abdominal migraine and 1.4% for inability to belch syndrome." — Sperber AD ve ark. Gut 2026;75(10):1887-1897. PMID 42613194 · DOI 10.1136/gutjnl-2026-339666 [abstract].

---
## 9. Rome IV karşılaştırma metinleri — [DOĞRULANAMADI]

Hyams JS ve ark. Gastroenterology 2016 (PMID 27144632, DOI 10.1053/j.gastro.2016.02.015) ve Benninga MA ve ark. Gastroenterology 2016 (PMID 27144631, DOI 10.1053/j.gastro.2016.02.016) PMC'de yok; Rome IV CVS / fonksiyonel bulantı-kusma / ruminasyon / infant regürjitasyon kriterlerinin verbatim metni bu oturumda alınamadı. Rome IV→V farkları yalnız (a) Rosen 2026 "rationale/justification" paragrafları ve (b) Hyams 2016 özeti üzerinden verilmiştir (bkz. `research/A5_romeV.md`).

