# 📄 PaperForge — SPSS'ten Makaleye Otomatik Pipeline

SPSS (.sav) verinizi yükleyin; **ajan orduları** sırasıyla veriyi temizlesin, doğru istatistiksel
testlere karar verip çalıştırsın, anlamlı bulgular için literatür tarasın, Giriş/Yöntem/Bulgular/
Tartışma bölümlerini yazsın, dil düzenlemesi yapsın, **Reviewer 2** gibi eleştirip revize etsin ve
size **APA formatında Word (.docx)** makale taslağı versin — tamamı **ücretsiz** altyapıyla.

## Özellikler

| Aşama | Ne yapar | Ajanlar |
|---|---|---|
| 1. Veri Temizleme | Kopya satır, sabit sütun, aşırı eksik satır, 3×IQR aykırı değer temizliği + rapor | Veri Yükleyici, Tip Müfettişi, Temizlik Ajanı, Bütünlük Denetçisi |
| 2. İstatistik | Normallik (Shapiro-Wilk) + Levene kontrolüyle **otomatik test seçimi** (t/Welch/Mann-Whitney, ANOVA/Kruskal + post-hoc, Pearson/Spearman, ki-kare/Fisher, regresyon), Holm/FDR p-düzeltmesi, etki büyüklükleri | Karar Motoru, Hesap Ordusu, Sağlamlık Denetçisi |
| 2b. Keşifsel Analiz | Gizli grup keşfi (PCA + K-Means), çok-değişkenli aykırı vaka tespiti (Isolation Forest), klasik korelasyonun kaçırdığı ilişkiler için bilgi teorisi (Mutual Information), ikili sonuç değişkeni işaretlenirse Lojistik Regresyon + Random Forest ile çapraz doğrulamalı **risk skoru** — hipotez üretici, doğrulayıcı sonuçlardan ayrı raporlanır | Örüntü Kaşifi, Sağlamlık Denetçisi |
| 3. Literatür | Anlamlı bulgular için **OpenAlex + Crossref + PubMed** taraması (anahtarsız, ücretsiz), DOI dedup + skorlama | Sorgu Yazarı, Tarama Ordusu, Kaynak Denetçisi |
| 4. Yazım | Yöntem/Bulgular gerçek analizlerden; Giriş/Tartışma literatüre dayalı — **paralel işçi ajanlar + seçici editör** | N× Bölüm Yazarı, Seçici Editör, Atıf/Yapı/Tutarlılık Denetçileri |
| 5. Dil Düzenleme | Akıcılık ve dilbilgisi; atıf işaretleri ve sayılar **korunarak** | Dil Editörü, Atıf Koruması |
| 6. Reviewer 2 | Düşmanca hakem eleştirisi → gerekirse **ek literatür** → revizyon → yanıt denetimi (2 tur) | Reviewer 2, Ek Literatür Tarayıcı, Revizyon Yazarı, Yanıt Denetçisi |
| 7. Çıktı | Uçtan uca son doğrulama, atıfların APA'ya dönüşümü, **Word (.docx)** üretimi | Atıf Montajcısı, Uçtan Uca Denetçi, Word Üretici |

Her aşamada **işçi ajanlar** üretir, **doğrulayıcı ajanlar** denetler; doğrulama geçilmezse geri
bildirimle yeniden denenir. İstatistikler asla yapay zekâya hesaplatılmaz — SciPy/statsmodels/
scikit-learn ile deterministik hesaplanır. Atıflar yalnızca gerçekten bulunan kaynaklardan `[n]` işaretiyle yapılır
ve kod tarafından APA'ya dönüştürülür; **uydurma kaynak yapısal olarak engellenir**.

## Kurulum

Python 3.10+ gerekir.

```bash
git clone https://github.com/gokhanbirsen1992-sketch/sunu-.git
cd sunu-
pip install -r requirements.txt
```

## Çalıştırma

```bash
uvicorn app.main:app
```

Tarayıcıda **http://127.0.0.1:8000** adresini açın.

## Ücretsiz yapay zekâ anahtarı (önerilir)

Anahtar olmadan da uygulama **şablon modunda** eksiksiz bir taslak üretir (gerçek istatistikler +
gerçek kaynaklar, ancak daha kuru bir metin). Çok daha kaliteli Giriş/Tartışma ve gerçek bir
Reviewer 2 deneyimi için ücretsiz bir anahtar girin:

1. **Google Gemini (önerilen)** — <https://aistudio.google.com/apikey> adresinden Google hesabıyla
   ücretsiz anahtar alın (kredi kartı istemez).
2. Uygulamadaki **⚙️ Ayarlar** panelinde anahtarı yapıştırın → **Kaydet** → **Test et**.

Alternatifler: [Groq](https://console.groq.com/keys), [OpenRouter](https://openrouter.ai/keys)
(":free" modeller). Birden fazla anahtar girerseniz kota dolduğunda otomatik olarak sıradakine geçilir.

Anahtarlar yalnızca bilgisayarınızda `data/keys.json` dosyasında saklanır; hiçbir yere gönderilmez
(yalnızca ilgili sağlayıcının API'sine).

## Kullanım

1. **Veri Yükleme** — .sav dosyanızı seçin, makale dilini (TR/EN) belirleyin ve çalışmanın konusunu
   1-2 cümleyle yazın (literatür taramasının isabetini artırır).
2. **Değişkenler** — otomatik tespit edilen değişken tiplerini kontrol edin; gerekirse düzeltin
   (örn. Likert → "Sıralayıcı"). Regresyon istiyorsanız bir değişkeni "Bağımlı değişken" olarak işaretleyin.
3. **Analizi Başlat** — pipeline'ı canlı izleyin: her aşama kartında ajan çipleri (🤖 işçi,
   🔍 doğrulayıcı, ⚖️ seçici) gerçek zamanlı renklenir; bulgular ve kaynaklar geldikçe listelenir.
4. **Sonuç** — Word dosyasını indirin. Ekinde veri temizleme raporu da bulunur.

## Canlıya alma — kurulum gerektirmeyen web sitesi

Uygulamayı kendi bilgisayarınıza kurmak istemiyorsanız ücretsiz bulut seçenekleri:

### Seçenek A: Render.com (önerilen, ~5 dakika)

1. <https://render.com> adresinde ücretsiz hesap açın (GitHub ile giriş yapın).
2. **New + → Blueprint** deyin ve bu depoyu (`gokhanbirsen1992-sketch/sunu-`) seçin —
   depodaki `render.yaml` her şeyi otomatik yapılandırır.
   **Önemli:** Dal (branch) soran ekranda **`main`** dalını seçin — `render.yaml` bu daldadır.
   "render.yaml bulunamadı" hatası alırsanız sebebi yanlış dalın seçili olmasıdır.
3. Sorulan ortam değişkenini doldurun:
   - `GEMINI_API_KEY`: <https://aistudio.google.com/apikey> adresinden alacağınız ücretsiz anahtar.
   - İsteğe bağlı: siteyi parolayla korumak isterseniz `APP_PASSWORD` adında bir değişken
     ekleyin (girişte tarayıcı parola sorar; kullanıcı adı boş bırakılır). Eklenmezse site
     adresi bilen herkese açıktır ve Gemini kotanızı başkaları da kullanabilir.
4. **Apply** → birkaç dakika içinde `https://paperforge-xxxx.onrender.com` gibi bir adresiniz olur.

Not: Ücretsiz planda site 15 dk kullanılmayınca uyur; ilk açılış ~1 dk sürebilir. Disk kalıcı
değildir — anahtarı arayüz yerine `GEMINI_API_KEY` ortam değişkeniyle vermeniz bu yüzden önemlidir.

### Seçenek B: Hugging Face Spaces (ücretsiz)

1. <https://huggingface.co> hesabı açın → **New Space** → SDK olarak **Docker** seçin.
2. Bu deponun dosyalarını Space'e yükleyin (depodaki `Dockerfile` hazır).
3. Space ayarlarından **Settings → Variables and secrets** ile `APP_PASSWORD` ve
   `GEMINI_API_KEY` ekleyin. Space'i **private** yapmanız da yeterli koruma sağlar.

### iPhone/Android'de uygulama gibi kullanma

Site adresinizi telefonda Safari/Chrome ile açın → **Paylaş → Ana Ekrana Ekle**.
PaperForge, PWA desteği sayesinde tam ekran, kendi simgesiyle bir uygulama gibi açılır.
(App Store'a girmek Apple geliştirici hesabı ve ayrı bir native uygulama gerektirir;
bu yol onun ücretsiz ve pratik karşılığıdır.)

## Test

```bash
pytest -q
```

## Mimari

```
app/
├── main.py, config.py, models.py      # FastAPI, ayarlar, veri modelleri
├── api/          # REST uçları + SSE canlı olay akışı
├── jobs/         # iş deposu (JSON kalıcılık) + arkaplan çalıştırıcı
├── pipeline/     # aşama tabanı (işçi+doğrulayıcı+retry) ve 8 aşama
├── agents/       # prompt şablonları (TR/EN) + deterministik doğrulayıcılar
├── llm/          # Gemini / Groq / OpenRouter + şablon modu + yönlendirici
├── statistics/   # yükleme, tipleme, temizlik, karar motoru, testler, keşifsel analiz, APA raporu
├── literature/   # OpenAlex, Crossref, PubMed istemcileri + skorlama + APA 7
├── manuscript/   # [n] atıf sistemi, APA dönüşümü, Word üretici
└── static/       # Türkçe tek sayfa web paneli (vanilla JS + SSE)
```

## Önemli notlar

- Sunucu varsayılan olarak yalnızca yerel makinede çalışır; kimlik doğrulama yoktur, internete açmayın.
- Üretilen makale bir **taslaktır**: göndermeden önce mutlaka okuyun, kaynakları doğrulayın.
  Yayın etiği gereği içerik sorumluluğu yazara aittir; derginizin yapay zekâ kullanım politikasını kontrol edin.
- Literatür API'leri (OpenAlex/Crossref/PubMed) ücretsizdir ve anahtar istemez; nadiren yavaş
  yanıt verebilirler — pipeline tek API çökse bile devam eder.

## Lisans

MIT
