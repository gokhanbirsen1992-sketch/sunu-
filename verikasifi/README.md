# 🔎 Veri Kâşifi

PaperForge (bu deponun kök dizinindeki uygulama) ile **hiçbir kod paylaşmayan**, tamamen
bağımsız, tek başına çalışan bir web uygulaması. Makale yazmaz, literatür taramaz, yapay zekâ
kullanmaz — yalnızca veri dosyanızı alır ve size şunları içeren bir Word raporu üretir:

- Klasik istatistik testleri (t-testi, ANOVA, korelasyon, ki-kare)
- **Gizli grup keşfi** — K-Means kümeleme, sizin fark edemeyeceğiniz alt-grupları bulur
- **Sıra dışı vaka tespiti** — Isolation Forest ile çok-değişkenli anomali taraması
- **Gizli ilişkiler** — Mutual Information ile klasik korelasyonun kaçırdığı bağıntılar
- **Risk skoru** — ikili bir sonuç değişkeni belirtirseniz Lojistik Regresyon + Random Forest

Tüm hesaplamalar deterministiktir (SciPy/scikit-learn, sabit `random_state`).

## Telefondan kullanım (iPhone dahil)

1. Aşağıdaki "Çalıştırma" adımlarıyla uygulamayı bir sunucuda (yerel ağ, Render, Hugging Face
   Spaces vb.) çalıştırın.
2. Adresi Safari'de açın (`http://<sunucu-adresi>:7860` veya deploy adresiniz).
3. **Paylaş → Ana Ekrana Ekle** ile telefonunuza tam ekran bir uygulama gibi ekleyin.
4. Veri dosyanızı yükleyin, isterseniz sonuç değişkenini yazın, **Analiz Et**'e dokunun.
5. Sonuçlar ekranda özetlenir; **📥 Raporu İndir** ile Word dosyasını indirirsiniz.

## Yerelde çalıştırma

```bash
cd verikasifi
pip install -r requirements.txt
uvicorn main:app --reload
```

Tarayıcıda `http://127.0.0.1:8000` açın.

## Test

```bash
cd verikasifi
pytest -q
```

## Canlıya alma (Render.com, ücretsiz)

1. [render.com](https://render.com) hesabı açın (GitHub ile).
2. **New + → Blueprint** → bu depoyu seçin.
3. Sorulan **Root Directory** alanına `verikasifi` yazın (bu klasördeki `render.yaml`
   kullanılacaktır — kök dizindeki PaperForge'un `render.yaml`'ından bağımsızdır).
4. Birkaç dakika içinde `https://veri-kasifi-xxxx.onrender.com` adresiniz hazır olur.
5. Bu adresi iPhone'da Safari ile açıp yukarıdaki "Ana Ekrana Ekle" adımını uygulayın.

## Mimari

```
verikasifi/
├── main.py         # FastAPI: dosya yükleme, analiz, indirme uçları
├── analysis.py      # istatistik + keşif motoru (kümeleme, anomali, MI, risk skoru)
├── report.py        # python-docx ile Word rapor üretici
├── static/          # mobil uyumlu tek sayfa arayüz (PWA)
└── tests/
```

## Lisans

MIT
