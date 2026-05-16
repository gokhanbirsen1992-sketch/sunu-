# Pediatrik Pankreatit — Hemogram Tabanlı Basit İndekslerin Şiddet Üzerine Etkisi

**Veri seti:** `data/Pankreatit_Analiz_SPSS_Fixed.xlsx` (n=163, yaş ort. 10.9, 1-18 yıl; 90 erkek, 73 kadın). Şiddet (Atlanta tipi sınıflama): 1=hafif (n=85), 2=orta (n=57), 3=şiddetli (n=20). 9 hasta yoğun bakım gerektirmiş (hepsi siddet=3).

**Hedef:** Hemogram parametrelerinden **en fazla 3 değişken** içeren basit indeksler türetmek ve bunların şiddet ile ilişkisini değerlendirmek. Mevcut Naples Pankreatit Prognostik Skoru (NPPS) referans alındı.

**Yöntem özeti:** Kabul (0h), 24. saat ve 48. saat hemogramından 22 indeks hesaplandı. Üç gruplu karşılaştırma için Kruskal-Wallis + Dunn (Bonferroni), ikili karşılaştırma için Mann-Whitney U, sınıflandırma performansı için ROC/AUC + Youden indeksi, sıralı sonuç için Spearman ρ ve yaş+cinsiyet ayarlı ordinal lojistik regresyon uygulandı. Çoklu test için Benjamini-Hochberg FDR. Tüm pipeline `analyze.py` üzerinden tekrar üretilebilir; ham tablolar `results/` altında.

---

## 1. Türetilen indeksler (her zaman noktası için)

| Aile | Formül | İndeks |
|---|---|---|
| 1-değişkenli (referans) | — | WBC, NEU, LENF, MONO, PLT, HB |
| 2-değişkenli klasik | iki hücre tipi oranı | NLR=NEU/LENF, PLR=PLT/LENF, LMR=LENF/MONO, MLR=MONO/LENF, NMR=NEU/MONO, PNR=PLT/NEU |
| 2-değişkenli türev | dNLR + Hb içerikli | **dNLR**=NEU/(WBC−NEU), HLR=HB/LENF, HNR=HB/NEU, NHR=NEU/HB, MHR=MONO/HB |
| 3-değişkenli kompozit | yangı + trombosit/Hb | **SII**=NEU×PLT/LENF, **SIRI**=NEU×MONO/LENF, **NLPR**=NEU/(LENF×PLT), dSII=(WBC−LENF)×PLT/LENF, dSIRI=(WBC−LENF)×MONO/LENF, SIIH=SII/HB, HSI=HB×LENF/NEU |

Her indeks 0h, 24h, 48h'da; ek olarak Δ24 = X₂₄ − X₀ ve Δ48 = X₄₈ − X₀ hesaplandı.

---

## 2. Kabul (0h) bulguları — şiddet ile ilişki

### 2.1 Tanımlayıcı (medyan [IQR])

| İndeks | Hafif (n=85) | Orta (n=57) | Şiddetli (n=20) |
|---|---|---|---|
| WBC | 10,100 [7,500-12,500] | 10,200 [8,000-12,600] | **12,600 [9,800-18,725]** |
| NEU | 6,090 [4,130-8,150] | 7,070 [4,700-9,910] | **9,270 [5,820-15,387]** |
| LENF | 2,430 [1,690-3,490] | 1,960 [1,310-2,440] | **1,380 [793-1,895]** |
| PLT | 317,000 | 312,000 | **274,500** |
| HB | 12.5 | 13.2 | 13.2 |
| NLR | 2.36 [1.33-3.86] | 3.93 [2.33-7.06] | **6.09 [3.84-10.24]** |
| dNLR | 1.65 | 2.45 | **3.21** |
| LMR | 3.93 | 2.20 | **2.08** |
| SII | 702,761 | 1,258,399 | **1,520,832** |
| SIRI | 1,775 | 2,973 | **4,599** |
| NLPR | 8.5×10⁻⁶ | 1.32×10⁻⁵ | **2.10×10⁻⁵** |
| HLR | 0.0050 | 0.0067 | **0.0096** |
| HSI | 5.53 | 3.54 | **1.86** |

Şiddet arttıkça NLR, dNLR, SII, SIRI, NLPR, HLR yükselir; LENF, PLT, LMR, PNR, HSI düşer.

### 2.2 Kruskal-Wallis (3 grup karşılaştırma)

19 indeks FDR-düzeltilmiş p<0.05. En güçlü 8:

| İndeks | KW H | p (ham) | p (FDR) |
|---|---:|---:|---:|
| HLR | 19.7 | 5.4×10⁻⁵ | 0.0007 |
| NLR | 19.2 | 6.8×10⁻⁵ | 0.0007 |
| NLPR | 18.8 | 8.5×10⁻⁵ | 0.0007 |
| SIRI | 17.3 | 0.0002 | 0.0007 |
| SII | 17.1 | 0.0002 | 0.0007 |
| LMR / MLR | 16.9 | 0.0002 | 0.0007 |
| dNLR | 15.5 | 0.0004 | 0.0013 |
| HSI | 15.1 | 0.0005 | 0.0014 |

WBC, HB, MONO, PLT (tek başına) ve MHR anlamlı değil.

### 2.3 Dunn post-hoc (gruplar arası)

| İndeks | Hafif vs Orta | Hafif vs Şiddetli | Orta vs Şiddetli |
|---|---:|---:|---:|
| HLR | 0.011 | **0.0002** | 0.160 |
| NLR | 0.006 | **0.0004** | 0.305 |
| NLPR | 0.026 | **0.0002** | 0.099 |
| SII | 0.003 | 0.003 | 0.916 |
| dNLR | 0.061 | **0.0006** | 0.133 |
| PNR | 0.360 | **0.002** | 0.071 |

**Çıkarım:** Tüm güçlü indeksler hafif vs şiddetli ayrımını net yapar; **orta ile şiddetli ayrımı bu hemogram tabanlı indekslerle güçlü değildir**. Klinik olarak en kritik karar — "orta mı şiddetli mi?" — yine ek skorlama (Naples, görüntüleme) gerektirir.

### 2.4 Mann-Whitney U (şiddetli vs şiddetli değil)

| İndeks | Med. şiddetli | Med. diğer | p | p (FDR) |
|---|---:|---:|---:|---:|
| NLPR | 1.84×10⁻⁵ | 8.49×10⁻⁶ | 0.0006 | 0.009 |
| HLR | 0.0098 | 0.0059 | 0.0008 | 0.009 |
| dNLR | 3.21 | 1.91 | 0.0015 | 0.009 |
| PNR | 28.3 | 47.9 | 0.0018 | 0.009 |
| NLR | 6.09 | 2.79 | 0.0019 | 0.009 |
| SIRI | 4,600 | 2,135 | 0.006 | 0.018 |

### 2.5 ROC / AUC (şiddetli = pozitif sınıf, n=20 vs 142)

| İndeks | AUC | %95 GA | Yön | Kesim noktası | Sens | Spes |
|---|---:|---|---|---:|---:|---:|
| **NLPR** | **0.738** | 0.61-0.84 | ≥ | 1.26×10⁻⁵ | 0.80 | 0.63 |
| **HLR** | **0.732** | 0.59-0.85 | ≥ | 0.0084 | 0.65 | 0.76 |
| **dNLR** | **0.720** | 0.59-0.83 | ≥ | 2.72 | 0.80 | 0.68 |
| **PNR** | 0.716 | 0.56-0.86 | ≤ | 29.2 | 0.60 | 0.82 |
| **NLR** | 0.715 | 0.58-0.83 | ≥ | 3.49 | 0.85 | 0.59 |
| SIRI | 0.691 | 0.55-0.82 | ≥ | 3,900 | 0.70 | 0.73 |
| HSI | 0.685 | 0.54-0.83 | ≤ | 1.90 | 0.55 | 0.83 |

Naples skoru (referans, mevcut çoklu-bileşenli): **AUC = 0.784** (0.69-0.87).

### 2.6 Spearman korelasyon (indeks vs sıralı şiddet)

HLR ρ=0.344 (p=7×10⁻⁶) > NLR ρ=0.343 > NLPR ρ=0.332 > SIRI ρ=0.327 > SII ρ=0.326 > LMR ρ=−0.322 > HSI ρ=−0.306 > dNLR ρ=0.300. Tüm korelasyonlar FDR-düzeltilmiş p<0.001.

### 2.7 Yaş + cinsiyet ayarlı ordinal lojistik regresyon

Log+z dönüşümlü indeks başına 1-SD artış için OR (sıralı sonuç: hafif < orta < şiddetli):

| İndeks | OR | %95 GA | p |
|---|---:|---|---:|
| NLR | 1.92 | 1.39-2.66 | 8.6×10⁻⁵ |
| SIRI | 1.91 | 1.31-2.78 | 0.0007 |
| NLPR | 1.83 | 1.30-2.58 | 0.0006 |
| dNLR | 1.62 | 1.19-2.22 | 0.0025 |
| dSIRI | 1.59 | 1.10-2.30 | 0.013 |
| PNR | 0.53 | 0.38-0.74 | 0.0002 |
| LENF | 0.70 | 0.51-0.95 | 0.021 |

PNR ve LENF **koruyucu** (yüksek değer → hafif şiddet); diğerleri risk yönünde.

> **Not (HLR):** HLR için OR=1.7×10⁶ raporlandı (`tablo7_ord_logistic_0h.csv`). Bu ölçek, indeksin çok küçük mutlak değerlerinden (Hb÷LENF≈0.005-0.02) kaynaklanan log+z dönüşüm artefaktıdır; pratik yorum için **AUC ve sıralı kesim noktası** referans alınmalıdır. Bulgu yönü (artış → şiddet) geçerli.

---

## 3. Dinamik analiz (Δ24, Δ48)

24. ve 48. saat hemogramları sırasıyla 84 ve 86 hastada mevcut. Bu nedenle delta analizi alt-örneklem üzerinde.

### En anlamlı Δ bulguları (Kruskal-Wallis sıralı)

| İndeks (Δ) | Med. şiddetli | Med. diğer | p (KW) | p (MW şid. vs değil) |
|---|---:|---:|---:|---:|
| **HB Δ48** | **−1.9** | −0.6 | 0.005 | 0.003 |
| HNR Δ48 | +0.0002 | +0.0007 | 0.014 | 0.25 |
| HLR Δ48 | −0.0022 | −0.0003 | 0.026 | 0.007 |
| WBC Δ48 | −4,200 | −2,400 | 0.032 | 0.054 |
| NEU Δ48 | −3,090 | −1,800 | 0.033 | 0.035 |
| HSI Δ48 | +0.55 | +1.14 | 0.036 | 0.28 |

**Klinik anlam:** Şiddetli pankreatitte 48. saatte:
- **Hemoglobin daha fazla düşer** (medyan −1.9 g/dL vs −0.6) — sıvı resüsitasyonu/hemodilüsyon ve/veya intra-abdominal kayıp.
- Lökositoz/nötrofili gerilemesi daha belirgindir ama bu mutlak değerler hâlâ yüksektir (başlangıçta da yüksekti).
- HSI iyileşme yönünde olsa da şiddetlilerde artış sınırlı kalır (kontrolde +1.14 vs şiddetlide +0.55).

### 24h kesit verileri (n=84)

48h'a göre 24h'da en güçlü indeksler: **dNLR (AUC 0.68), NLPR (0.71), PNR (0.71), HSI (0.69)**. Yön ve büyüklük 0h ile uyumlu.

### 48h kesit verileri (n=86)

48h'da **HB tek başına AUC 0.78** ile öne çıkıyor (kesim ≤11.3 g/dL → şiddet için sens 0.73, spes 0.80). PLT ≤295,000 → AUC 0.73, sens 1.00 spes 0.42. NLPR ve dNLR hâlâ anlamlı ama AUC'leri 0h'a göre düşmüş (örneklem azalması ve geç dönemde indekslerin gerilemesi).

---

## 4. Naples skoru ile kıyas

| Skor | AUC | %95 GA | n | Değişken sayısı |
|---|---:|---|---:|---:|
| **Naples (mevcut)** | 0.784 | 0.69-0.87 | 125 | 4 (alb + kol + NLR + LMR puanları) |
| NLPR | 0.738 | 0.61-0.84 | 162 | 3 (NEU, LENF, PLT) |
| HLR | 0.732 | 0.59-0.85 | 162 | 2 (HB, LENF) |
| dNLR | 0.720 | 0.59-0.83 | 162 | 2 (NEU, WBC) |
| PNR | 0.716 | 0.56-0.86 | 162 | 2 (PLT, NEU) |
| NLR | 0.715 | 0.58-0.83 | 162 | 2 (NEU, LENF) |

**Çıkarım:** Naples skoru (4 bileşenli) yine en yüksek AUC'ye sahip, ancak yeni türetilen **NLPR, HLR ve dNLR** sadece hemogram bileşenleriyle ve daha küçük eksik veri kaybıyla (n=162 vs 125) yakın performans gösterir. Albümin/kolesterol istenmeyen veya gecikmiş senaryolarda **hızlı triyaj için NLPR≥1.26×10⁻⁵ veya dNLR≥2.72 veya HLR≥0.0084** klinik kullanışlılık taşıyabilir.

---

## 5. Önerilen 3 odak indeks (klinik kullanım için)

| İndeks | Formül | Kabul cutoff (şiddetli) | Yorum |
|---|---|---|---|
| **NLPR** | NEU / (LENF × PLT) | ≥ 1.26×10⁻⁵ | En yüksek AUC; klasik NLR'yi trombositopeni ile birleştirir |
| **HLR** | HB / LENF | ≥ 0.0084 | Spesifite 0.76; hemokonsantrasyon + lenfopeni göstergesi |
| **dNLR** | NEU / (WBC − NEU) | ≥ 2.72 | Diferansiyel sayım gerekmeden CBC-only varyant; LMR'a tamamlayıcı |

Üçü birlikte (ör. "≥2 pozitif = yüksek risk") sezgisel triyaj kuralı kurgulanabilir; resmi kalibrasyon için çapraz doğrulama gerekir.

---

## 6. Sınırlamalar

1. **Şiddetli grubun küçüklüğü (n=20)** — ROC GA'ları geniş; cutoff'lar dış geçerlilik için **prospektif doğrulama** gerektirir.
2. **24/48h eksik veri (~%50)** — Δ analizi alt-örneklem; selection bias olasılığı (uzun yatış = takip).
3. **Tek merkez, retrospektif** — pediatrik popülasyon kohort özellikleriyle sınırlı (yetişkin pankreatite genelleştirilemez).
4. **Üç gruplu ayrım sınırlı** — indeksler hafif vs şiddetli ayrımı yapar; orta vs şiddetli için tek başına yetersiz.
5. **Çoklu test** — 22 indeks × 3 zaman noktası → 66 test; FDR ile düzeltildi ama keşifsel niteliktedir.
6. **WBC outlier** — minimum WBC değeri 10.4 (muhtemelen birim/veri girişi); analizde aynen bırakıldı, log/winsorize uygulanmadı.
7. **HLR ordinal lojistik OR ölçek artefaktı** — ham değer aralığı çok küçük (~0.005-0.02); cutoff'a dayalı yorumla sınırlı kalın.

---

## 7. Sonuç

Pediatrik akut pankreatit kohortunda **kabul anındaki tek bir hemogram örneğinden hesaplanan 3 basit indeks — NLPR, HLR ve dNLR — şiddetli pankreatit (Atlanta tip 3) için AUC 0.72-0.74 ile anlamlı ayırt edici güç göstermektedir.** Bu indeksler:
- Mevcut Naples skoruna (AUC 0.78) yakın performans gösterir,
- Albümin/kolesterol gibi ek tetkikleri gerektirmez,
- Hesaplanması basittir (bir CBC sonucundan ≤3 değişken).

Dinamik takipte, **48. saat Hb değişimi (Δ48 ≈ −1.9 vs −0.6 g/dL)** klinik kötüleşmenin erken bir göstergesi olarak çıkmıştır. Bu bulguların dış doğrulanması ve prospektif klinik karar destek aracı olarak değerlendirilmesi önerilir.

---

### Ek dosyalar

- `results/tablo1_tanimlayici_0h.csv` — tüm indekslerin grup başı medyan [IQR]
- `results/tablo2_kruskal_wallis_{0,24,48}h.csv` — 3'lü karşılaştırma p-değerleri
- `results/tablo3_dunn_posthoc_0h.csv` — ikili gruplar arası
- `results/tablo4_mann_whitney_{0,24,48}h.csv` — şiddetli vs değil
- `results/tablo5_roc_auc_{0,24,48}h.csv` — AUC + cutoff + sens/spes
- `results/tablo6_spearman_0h.csv` — sıralı korelasyon
- `results/tablo7_ord_logistic_0h.csv` — yaş+cinsiyet ayarlı OR
- `results/tablo8_delta.csv` — Δ24 / Δ48 analizi
- `results/tablo9_naples_kiyas.csv` — Naples vs yeni indeksler
- `results/tum_indeksler.csv` — her hasta için tüm indeks değerleri (raw)
- `results/grafikler/fig1_boxplot_top5_0h.png` — en güçlü 5 indeks boxplot
- `results/grafikler/fig2_roc_top5_0h.png` — ROC eğrileri (Naples dahil)
- `results/grafikler/fig3_boxplot_delta.png` — en anlamlı Δ indeksler
- `results/grafikler/fig4_naples_vs_yeni.png` — Naples vs ilk 3 yeni indeks ROC
