---
name: cocuk-ge-kutuphane-gelistirme
description: >-
  Bu depodaki çocuk gastroenterolojisi algoritma kütüphanesini (docs/ + index.html +
  app.html + birleşik PDF + cocuk-ge-algoritma skill'i + loop) iki-uzman gözüyle
  (kıdemli yazılım mühendisi + pediyatrik GE profesörü) denetler ve önceliklendirilmiş
  bir geliştirme + verimli-kullanım yol haritası üretir; istenirse maddeleri uygular,
  build.py ile yeniden üretir, doğrular ve commit eder. Tetikleyiciler: "ne eklemeliyiz",
  "nasıl daha verimli kullanırız", "kütüphaneyi/app'i geliştir", "iyileştirme öner",
  "gözden geçir", "backlog çıkar", "eksikleri bul".
---

# Çocuk GE Kütüphanesini Geliştirme / Değerlendirme

Bu skill, mevcut **çocuk gastroenterolojisi algoritma kütüphanesini** değerlendirip
nasıl daha iyi ve daha verimli kullanılır sorusuna yapılandırılmış, uygulanabilir
bir yanıt üretir. (İçerik üretmek için ayrı `cocuk-ge-algoritma` skill'i vardır; bu
skill kütüphanenin kendisini iyileştirir/sürdürür.)

## Depo haritası (doğruları buradan al)
- `docs/pediatrik-<slug>-algoritmasi.html` + `.pdf` — tekil algoritmalar (89+).
- `docs/index.html` — aranabilir hub; `docs/app.html` — tek-dosya uygulama (gömülü 89).
- `docs/pediatrik-gastroenteroloji-algoritma-kitapcigi.pdf` — birleşik kitaplık.
- `docs/pediatrik-gis-algoritma-yol-haritasi.html` — başvuru nedenleri dizini.
- `docs/USABILITY-BACKLOG.md` — **yaşayan backlog** (loop bunu izler).
- `tools/build.py` + `tools/series_style.css` — index/app'i standalone belgelerden
  **yeniden üreten** araç (frag gerektirmez; app şablonu + CATS burada).
- `.claude/skills/cocuk-ge-algoritma/` — şikâyetten algoritma üreten skill.
- Çalışan cron loop backlog'u işler (her ~30 dk).

## Nasıl değerlendirilir (iki-uzman merceği)
Her öneriyi iki açıdan üret ve **etki × efor** ile sırala:
- **Yazılım mühendisi:** erişilebilirlik, arama kalitesi, performans (app.html ~1.8 MB),
  mobil/PWA/barındırma, çevrimdışı, sürdürülebilir kod, geri-tuşu, baskı, test/doğrulama.
- **Pediyatrik GE profesörü:** başucu iş akışı (doğru algoritmaya saniyeler içinde),
  gerçek aciller, dozlu karar desteği, hesaplayıcılar/skorlar, **doz/birim güvenliği**,
  kılavuz güncelliği, kaynak doğrulanabilirliği, eksik yüksek-getirili başlıklar.

Her madde için şunları belirt: **etki (yüksek/orta/düşük), efor (S/M/L), tür**
(app-kabuğu=`tools/build.py` · içerik=`docs/` · yeni-özellik · barındırma/yönetişim),
ve kısa uygulama notu. Önceliklendirilmiş katalog: **`reference/iyilestirme-katalogu.md`**.

## Çıktı
1. Kısa, önceliklendirilmiş değerlendirme (en yüksek 3 + sorumluluk katmanı).
2. `docs/USABILITY-BACKLOG.md`'yi bu değerlendirmeyle **güncelle** (yaşayan liste;
   loop izler). Tamamlananları `[x]`, sıradakileri etki/efor ile.
3. Kullanıcı bir maddeyi seçerse **uygula** (aşağıdaki kurallar).

## Uygulama kuralları
- **App-kabuğu (arama, filtre, tema, a11y, hesaplayıcı, çapraz bağlantı, lazy-render,
  cep-kartı, PWA):** `tools/build.py` içindeki şablonu düzenle → `python3 tools/build.py`
  → üretilen `app.html`/`index.html` JS'ini `node --check` ile ve headless render ile
  doğrula (navitem sayısı, konsol hatasız) → Kiril taraması → commit.
- **İçerik (89 belgeye hızlı-başvuru kutusu, künye, kaynak linkleri, doz güvenlik
  denetimi):** ölçek nedeniyle **Workflow** (üret→denetle) ile tek turda yap; sonra
  `tools/build.py`. Klinik kural: dozlar mg/kg + maks, "uzmana sevk" dili yok, Türkçe.
- **Barındırma:** `docs/` statik; GitHub Pages veya Render ile yayınla (`render.yaml`
  mevcut). Yayınlandığında `manifest.webmanifest` + "ana ekrana ekle".
- **Birleşik PDF:** içerik değiştiyse per-doc PDF (Chrome: `google-chrome-stable` ya da
  `/opt/pw-browsers/...`) + `pdfrw` ile kapak/TOC birleştirme (betikler kalıcı değilse
  yeniden oluştur).
- Her değişiklikten sonra: doğrula → küçük, açıklayıcı commit →
  `claude/pediatric-gastro-constipation-algo-kfrmkq` dalına push.

## En yüksek kaldıraç (varsayılan öneri sırası)
1. **Barındırma** (günlük kullanımın kilidi) → 2. **Hızlı-başvuru kutuları** (bedside) →
3. **Klinik hesaplayıcılar** → 4. **Doz güvenlik denetimi** (sorumluluk). Ardından:
çapraz bağlantılar, lazy-render, cep-kartı, künye/güncellik, İngilizce sürüm.

## Kalite kontrol
app değişimlerinde `node --check` + headless render + Kiril taraması; içerik
değişimlerinde dozlar mg/kg + maks ve kırmızı bayraklar korunur; her şey commit+push.
