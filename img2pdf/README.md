# img2pdf — Fotoğrafları PDF'e Çevir

Verdiğin resimleri (JPG, PNG, BMP, GIF, TIFF, WebP) **tek bir PDF** dosyasında
birleştiren basit bir araç. Her resim PDF'te ayrı bir sayfa olur.

## Kurulum

```bash
pip install Pillow
```

## Kullanım

### Tek tek resimleri sırayla birleştir

```bash
python -m img2pdf.cli foto1.jpg foto2.png foto3.jpg -o sonuc.pdf
```

### Bir klasördeki tüm resimleri birleştir

```bash
python -m img2pdf.cli ./fotograflarim -o album.pdf
```

### Seçenekler

| Seçenek | Açıklama | Varsayılan |
|---|---|---|
| `-o`, `--cikti` | Oluşacak PDF dosyasının adı | `cikti.pdf` |
| `-q`, `--kalite` | JPEG sıkıştırma kalitesi (1-100) | `90` |

## Python içinden kullanım

```python
from img2pdf import pdfe_cevir

pdfe_cevir(["foto1.jpg", "foto2.png"], "sonuc.pdf")
```

## Notlar

- **Sıralama:** Klasör verdiğinde resimler dosya adına göre alfabetik sıralanır.
  `foto1, foto2, foto10` gibi bir sıra istiyorsan dosyalarını `foto01`, `foto02`,
  `foto10` şeklinde sıfır dolgulu adlandır ya da resimleri komuta tek tek
  istediğin sırada ver.
- **Şeffaflık:** Şeffaf PNG'ler beyaz zemine basılır.
