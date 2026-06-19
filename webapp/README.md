# SPSS → Makale — iPhone PWA + FastAPI backend

SPSS `.sav` dosyasından **Türkçe akademik makale taslağı (Word)** üreten mobil web uygulaması.
iPhone'da Safari'de açılır, "Ana Ekrana Ekle" ile uygulama gibi durur. Tüm istatistik **deterministik**
ve **anahtarsız**; sayılar motordan birebir gelir (uydurma yok).

## Ne üretir (ücretsiz, LLM gerektirmez)
- Otomatik analiz planı (PII/kimlik değişkenleri otomatik dışlanır)
- İstatistik: tanımlayıcılar, grup karşılaştırmaları (t/Mann-Whitney/ANOVA/Kruskal-Wallis), korelasyon,
  regresyon — etki büyüklüğü + %95 GA
- **Gruplara göre Tablo 1** + kutu grafikleri (300 dpi)
- **Yöntem / Bulgular / Öz** (deterministik, `verify-numeric`'ten geçer) + ICMJE beyanları
- (Opsiyonel) **Gerçek PubMed kaynakları** — "konu" girip kutucuğu işaretleyin (ücretsiz NCBI API; sunucuda
  internet gerekir)

## Yerel çalıştırma
```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r webapp/requirements.txt
.venv/bin/python webapp/make_icons.py            # PWA ikonları
.venv/bin/uvicorn webapp.app:app --host 0.0.0.0 --port 8000
# tarayıcı: http://localhost:8000
```

## Buluta dağıtım (canlı URL → iPhone'da kullan)
Repo'da `Dockerfile` + `render.yaml` hazır. Üç kolay yol:

1. **Render** (tek tık): `https://render.com/deploy?repo=https://github.com/gokhanbirsen1992-sketch/sunu-`
   — ücretsiz hesapla bağlanın, dağıtım bitince size bir `https://…onrender.com` adresi verilir.
2. **Railway / Fly.io**: Docker'ı otomatik algılar; `Dockerfile`'dan derler, public URL verir.
3. **Kendi sunucunuz**: `docker build -t makale . && docker run -p 8000:8000 makale`.

> Bilimsel paketler ~0,5 GB RAM ister. Ücretsiz/512 MB planda bellek yetmezse ≥1 GB planı seçin
> (Render Standard / Railway / Fly).

Canlı URL'yi iPhone Safari'de açın → **Paylaş → Ana Ekrana Ekle**. Artık uygulama gibi çalışır.

## Gizlilik
Yüklenen `.sav` yalnızca üretim için kullanılır ve **işlem biter bitmez sunucudan silinir**; sonuç dosyası
indirme sonrası temizlenir. PII loglanmaz; literatür araması yalnızca girdiğiniz konu terimini gönderir.

## Mimari
`webapp/app.py` (FastAPI) → `sav2q1/pipeline.py` (başsız denetleyici) → `sav2q1/engine` (motor + planner +
narrate) → `sav2q1/docx` (Word). Aynı `pipeline` çekirdeği, istenirse `desktop/` (Tkinter + PyInstaller) ile
Windows `.exe` de verebilir.
