---
name: cocuk-ge-algoritma
description: >-
  Bir çocuk (pediyatrik) gastroenteroloji/hepatoloji şikâyeti, semptomu, muayene
  bulgusu, laboratuvar veya görüntüleme anormalliği yazıldığında onu bu depodaki
  seriyle aynı uzman-düzeyi klinik algoritma formatında anlatır: tanım, mekanizma/
  şiddet, karar akışı, basamaklı tetkik, kırmızı bayraklar, DOZLU tedavi ve izlem.
  Tetikleyiciler: "X için algoritma/yaklaşım yap", "şu şikâyeti anlat", "bunu da
  aynı formatta yap", ya da doğrudan bir semptom/bulgu adı (reflü, safralı kusma,
  rektal kanama, transaminaz yüksekliği, hepatomegali, kabızlık, Crohn, pankreatit…).
  Hedef kitle çocuk gastroenteroloji uzmanıdır.
---

# Çocuk GE Algoritma Üretici

Bu depo (`gokhanbirsen1992-sketch/sunu-`) bir **çocuk gastroenterolojisi klinik
algoritma kütüphanesidir** (`docs/` altında 88+ belge + aranabilir `index.html` /
tek-dosya `app.html` + birleşik PDF kitaplık). Bu skill, yeni bir başlık
istendiğinde **aynı formatta** belge üretmeni ve kütüphaneye eklemeni sağlar.

## Ne zaman kullanılır
Kullanıcı bir pediyatrik GİS/hepatoloji **şikâyeti / semptomu / muayene bulgusu /
lab anormalliği / görüntüleme bulgusu / hastalığı** verip anlatılmasını, algoritma
yapılmasını veya "aynı formatta" üretilmesini istediğinde. Tek bir başlık adı bile
(ör. "safralı kusma", "hematokezya", "Wilson") bu skill'i tetikler.

## Altın kurallar (klinik)
1. **Hedef kitle uzmandır** → "pediatrik gastroenterolojiye/uzmana sevk et" gibi
   ifade YAZMA. Bunun yerine somut tanı, tetkik, **dozlu tedavi** ve izlem ver.
   Yönlendirme gerekiyorsa cerrahi/yoğun bakım/nakil gibi **somut** eşiği yaz.
2. **Dozlar** daima **mg/kg + maksimum** ile; güncel kılavuza dayan (Rome IV,
   ESPGHAN/NASPGHAN/ECCO ve konuya özgü kaynaklar). Emin olmadığın dozu uydurma.
3. **Dil: Türkçe.** Kiril veya kaçak karakter kullanma.
4. Her belgede **kırmızı bayraklar** eksiksiz olmalı.

## Zorunlu bölüm iskeleti (her belge)
`<section>` sırası, `<h2><span class="n">0X</span> …</h2>` ile:
1. **01 Tanım ve ilk değerlendirme** — + öykü/muayene için `grid two` içinde iki `card`.
2. **02 Etiyoloji/mekanizma VEYA şiddet sınıflaması** — `mech` kartları (t1..t6) veya `sev` bantları (mild/mod/sev/rem).
3. **03 Karar akışı** — `flow` içinde `node start/action/decision` ve `branches` ile gerçek karar ağacı.
4. **04 Basamaklı tetkik** — `table-scroll` tablo (td.step; gerekiyorsa td.dose).
5. **05 Kırmızı bayraklar** — `alarm-grid`.
6. **06 Tedavi** — DOZLU; ilaç varsa `table-scroll` tablo (td.dose = mg/kg + maks).
7. **07 İzlem / yönetim ilkeleri**.
+ `<footer>` 2–4 gerçek kılavuz/kaynak + `<div class="disclaimer">` uyarı.

HTML sınıf sözlüğü ve örnek iskelet: **`reference/sablon.md`** (üretmeden önce oku).

## İş akışı
1. **Başlığı belirle** ve kısa, ASCII, tireli bir `slug` seç
   (ör. "Kronik karın ağrısı" → `kronik-karin-agrisi`).
2. **Gövdeyi yaz:** yalnızca `<div class="wrap"> … </div>` — `<style>`/`<title>` YOK.
   `reference/sablon.md`'deki sınıfları ve bölüm iskeletini kullan. Masthead h1 =
   başlık; 3–4 `span.tag` etiketi.
3. **Belgeyi kaydet:** gövdeyi geçici olarak `docs/frag/<slug>.frag.html`'e yaz
   (bu klasör `.gitignore`'da), sonra `python3 tools/build.py` ÇALIŞTIR — araç
   commit'li standalone belgelerden `index.html` + `app.html`'i yeniden üretir.
   **ÖNEMLİ:** `tools/build.py` yalnızca `docs/pediatrik-<slug>-algoritmasi.html`
   standalone dosyalarını okur; bu yüzden gövdeyi standalone dosyaya sarmalaman
   gerekir:
   ```bash
   python3 - <<'PY'
   import re
   slug="<slug>"; title="<Başlık>"
   style=re.search(r"<style>.*?</style>", open("tools/series_style.css").read()
       .replace("<style>","<style>",1), re.S)  # ya da tools/series_style.css'i olduğu gibi göm
   body=open(f"docs/frag/{slug}.frag.html",encoding="utf-8").read()
   css=open("tools/series_style.css",encoding="utf-8").read()
   doc=f'<title>{title} — Pediyatrik Algoritma</title>\n<meta name="viewport" content="width=device-width, initial-scale=1">\n{css}\n{body}\n'
   open(f"docs/pediatrik-{slug}-algoritmasi.html","w",encoding="utf-8").write(doc)
   PY
   python3 tools/build.py
   ```
   (`tools/series_style.css` dosyası tüm bileşen sınıflarını içeren ortak stildir;
   başlık kategoriye düşmezse araç "Diğer / yeni" grubuna yerleştirir — kategoriye
   doğru yerleştirmek için `tools/build.py` içindeki `CATS` listesine slug'ı ekle.)
4. **Doğrula:** üretilen app.html JS'ini `node --check` ile ve Kiril taramasıyla
   (`grep -lP '[\x{0400}-\x{04FF}]'`) kontrol et.
5. **PDF (istenirse):** Chromium ile standalone HTML'i yazdır:
   `/opt/pw-browsers/chromium-1194/chrome-linux/chrome --headless=new --no-sandbox
   --print-to-pdf=docs/pediatrik-<slug>-algoritmasi.pdf <sarmalı-html>`.
6. **Commit + push:** `claude/pediatric-gastro-constipation-algo-kfrmkq` dalına,
   açıklayıcı mesajla (`docs/frag/` commit'lenmez).

## Yalnızca chat'te anlatım istenirse
Dosya/kütüphane istenmiyorsa, aynı 7 bölümü **markdown** olarak ver (aynı başlıklar,
aynı klinik kurallar, dozlar mg/kg + maks, kırmızı bayraklar, kaynaklar). HTML/PDF
adımlarını atla.

## Kalite kontrol
- "Uzmana sevk" dili yok · dozlar mg/kg + maks · kırmızı bayraklar tam · Türkçe,
  Kiril yok · gövde `<div class="wrap">` ile başlayıp `</div>` ile biter · yalnızca
  izin verilen sınıflar · 2–4 gerçek kaynak.
