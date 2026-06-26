# SPSS-Keşif — SPSS'in Ötesinde İstatistiksel Keşif Skill'i

Bir SPSS (`.sav`), CSV veya Excel veri dosyasını verirsin; bu skill, klasik
SPSS testlerinin **göremediği** gizli örüntüleri modern ML/istatistikle bulur
ve her bulguyu **yayın titizliğiyle** eler.

## Nasıl kullanılır?

Claude Code içinde veri dosyanı paylaş ve şöyle bir şey söyle:

> "Bu .sav dosyasında SPSS'in yapamadığı analizleri yap, gizli ilişkileri bul"

Claude `spss-kesif` skill'ini çağırır, sana değişken listesini gösterir, hedef
(ve varsa tedavi) değişkenini sorar, sonra motoru çalıştırıp bulguları
yorumlar.

Elle de çalıştırabilirsin:

```bash
# Hedef tahmini + tüm keşif modülleri
python analyze.py veri.sav --target SONUC_DEGISKENI --out rapor/

# + nedensel etki analizi (EconML)
python analyze.py veri.sav --target SONUC --treatment TEDAVI --out rapor/

# Hedef yoksa (sadece yapı/ilişki/anomali keşfi)
python analyze.py veri.sav --out rapor/

# Bazı sütunları hariç tut (ID, tarih...)
python analyze.py veri.sav --target SONUC --drop "id,tarih" --out rapor/
```

Çıktı: `rapor/bulgular.md` — yorumlanmış, uyarılı bulgu raporu.

## Hangi modüller, neyi bulur?

| Modül | Bulduğu şey | SPSS neden kaçırır |
|---|---|---|
| **1. Doğrusal-olmayan ilişki** | Eşik/U-şekli/doygunluk etkileri; lineer-ötesi kazanç | SPSS regresyonu doğrusal varsayar |
| **2. Etkileşim keşfi** | Hangi değişken çiftleri birlikte etki eder (SHAP) | SPSS'te etkileşimi elle yazman gerekir |
| **3. Gizli segmentler** | Önceden tanımlanmamış doğal alt-gruplar (kümeleme) | SPSS'te grupları sen tanımlarsın |
| **4. Çok boyutlu anomali** | Tek değişkende normal, çok-değişkenli uzayda sıra dışı vakalar | SPSS aykırıya tek değişkende bakar |
| **5. Gizli MI ağı** | Yüksek karşılıklı bilgi ama düşük korelasyon = gizli doğrusal-olmayan ilişki | SPSS korelasyonu sadece doğrusaldır |
| **6. Nedensel etki (DML)** | Confounder kontrollü gerçek etki + güven aralığı | SPSS doğrusal GLM ile sınırlı |

## ⚠️ Yayın titizliği — neden bu skill p-hacking makinesi DEĞİL

"Gizli ilişki" bulmak kolaydır; çoğu gürültüdür. Skill her bulguyu eler:

- **Holdout doğrulama:** Örüntüler eğitim setinde aranır, ayrı test setinde teyit
  edilir. Önem permütasyon testiyle **holdout'ta** ölçülür.
- **FDR (Benjamini-Hochberg):** Yüzlerce ilişki test edilince oluşan yanlış
  keşifler düzeltilir.
- **Etki büyüklüğü:** p değil, pratik büyüklük (R² kazancı, SHAP katkısı) raporlanır.
- **Gürültü reddi:** Test verisinde etkisiz değişkenler "anlamsız" işaretlenir
  (doğrulandı: sentetik gürültü değişkeni p=0.83 ile reddedildi).
- **Nedensellik uyarısı:** Her nedensel çıktıya varsayım notu eklenir.

> Skill'in çıktısı **yayına ADAY hipotezlerdir.** Gerçek yayın için bağımsız/yeni
> veriyle (ideal: ön-kayıtlı) doğrulama şarttır.

## Kurulum

```bash
pip install pyreadstat pandas numpy scipy scikit-learn xgboost   # çekirdek
pip install shap umap-learn econml                                # opsiyonel modüller
```

Opsiyonel paketler yoksa ilgili modül zarifçe atlanır (rapor bunu belirtir).

## Doğrulanmış örnek

`analyze.py`, içine gizli (a) U-şekli kuadratik etki ve (b) çarpım etkileşimi
gömülü sentetik veride test edildi:

- Doğrusal model R²=0.17 → boosting R²=0.94 (**doğrusal-olmayanlığı yakaladı**).
- Gizli kuadratik değişken: **Pearson −0.01 (SPSS "ilişki yok" der) ama MI 0.51**
  → ⭐ işaretlendi.
- Gömülü etkileşim çifti: tüm çiftler arasında **1. sırada** otomatik bulundu.
- Saf gürültü değişkeni: doğru biçimde **anlamsız** (FDR p=0.83) reddedildi.

## Sınırlılıklar / dürüst notlar

- Keşif **hipotez üretir**, kanıt üretmez — doğrulama kullanıcının sorumluluğu.
- Nedensel modül "ölçülmeyen confounder yok" varsayımına dayanır.
- Çok küçük veride (<~100-200 satır) sonuçlar kararsızdır.
- Bu bir araçtır; alan bilgisi ve eleştirel yorum yerine geçmez.
