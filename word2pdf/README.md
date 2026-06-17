# word2pdf — Word'den PDF'e Dönüştürücü

Word belgelerini (`.docx`, `.doc`) PDF'e çeviren basit ve sağlam bir araç.
Hem terminalden hem de Python kodu içinden kullanılabilir; tek dosya ya da
bütün bir klasörü toplu olarak dönüştürebilir.

## Nasıl çalışır? (İki motor)

| Motor | Açıklama | Gereksinim |
|---|---|---|
| **`libreoffice`** | LibreOffice'i arka planda (headless) çalıştırır. **En yüksek doğruluk**: tablo, resim, sütun, başlık, font — her şey korunur. `.doc` ve `.docx` destekler. | Sistemde LibreOffice kurulu olmalı |
| **`python`** | Saf-Python yedeği (`python-docx` + `reportlab`). Metin, başlık, kalın/italik ve tabloları aktarır. Resimler ve karmaşık düzen atlanır. Yalnızca `.docx`. | `pip install` ile iki paket |

Varsayılan **`auto`** motoru önce LibreOffice'i dener; bulunamazsa **veya
LibreOffice çalışmazsa** otomatik olarak Python motoruna düşer. Yani her iki
yol da kuruluysa hiç uğraşmadan en iyi sonucu alırsın.

> Türkçe karakterler (ç, ğ, ı, İ, ö, ş, ü) her iki motorda da tam desteklenir.
> Python motoru bunun için sistemdeki DejaVu fontunu kullanır (yoksa Helvetica'ya düşer).

## Kurulum

**1. LibreOffice (önerilir, en iyi sonuç için):**

```bash
# Debian/Ubuntu
sudo apt install libreoffice-writer
# macOS (Homebrew)
brew install --cask libreoffice
# Windows: https://www.libreoffice.org/download/
```

**2. Python bağımlılıkları (saf-Python yedek motoru için):**

```bash
pip install -r word2pdf/requirements.txt
```

> Sadece LibreOffice'i kullanacaksan yalnızca `click` yeterlidir.
> Sadece Python motorunu kullanacaksan LibreOffice'e hiç gerek yok.

Python 3.10+ gereklidir.

## Kullanım (terminal)

```bash
# Tek dosya — çıktı: rapor.pdf (aynı klasör)
python -m word2pdf rapor.docx

# Çıktı yolunu belirt
python -m word2pdf rapor.docx -o ciktilar/rapor.pdf

# Bütün bir klasörü dönüştür (alt klasörler dahil)
python -m word2pdf belgeler/ -o pdfler/ --recursive

# Motoru zorla seç
python -m word2pdf rapor.docx --engine python
python -m word2pdf rapor.docx --engine libreoffice

# Var olan PDF'lerin üzerine yaz
python -m word2pdf rapor.docx --overwrite
```

| Seçenek | Kısa | Açıklama |
|---|---|---|
| `--output` | `-o` | Çıktı PDF yolu (tek dosya) veya çıktı klasörü (toplu) |
| `--engine` | `-e` | `auto` (varsayılan) \| `libreoffice` \| `python` |
| `--recursive` | `-r` | Klasörde alt klasörleri de tara |
| `--overwrite` | `-f` | Var olan PDF'lerin üzerine yaz |

## Kullanım (Python kodu içinden)

```python
from word2pdf import convert_file

# En basit hâli — rapor.pdf üretir, üretilen yolu döndürür
pdf_yolu = convert_file("rapor.docx")

# Hedef ve motor belirterek
convert_file("rapor.docx", "ciktilar/rapor.pdf", engine="libreoffice", overwrite=True)
```

Bir klasördeki tüm Word dosyalarını gezmek için:

```python
from pathlib import Path
from word2pdf import convert_file, iter_word_files

for docx in iter_word_files(Path("belgeler"), recursive=True):
    convert_file(docx, Path("pdfler"), overwrite=True)
```

Hata durumunda `word2pdf.ConversionError` fırlatılır.

## Sınırlamalar (yalnızca `python` motoru)

- Resimler, metin kutuları, üstbilgi/altbilgi ve sütun düzeni aktarılmaz.
- Yalnızca `.docx` okunur (`.doc` için LibreOffice gerekir).
- Tam görsel doğruluk gerektiğinde `libreoffice` motorunu kullan.

## Test

```bash
pip install -r word2pdf/requirements.txt pytest
python -m pytest tests/test_word2pdf.py -v
```

LibreOffice kurulu değilse, ona özel entegrasyon testi otomatik olarak atlanır.
