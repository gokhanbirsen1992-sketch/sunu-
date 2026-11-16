# İyileştirme Kataloğu — önceliklendirilmiş

Her madde: **etki** (Y/O/D) · **efor** (S/M/L) · **tür** · uygulama notu.
Değerlendirme iki mercekle: 🖥️ yazılım mühendisi, 🩺 pediyatrik GE profesörü.

## Katman 1 — en yüksek kaldıraç
- **Barındırma (GitHub Pages / Render)** · Y · S · barındırma · 🖥️🩺
  `docs/` statik yayınla; URL + "ana ekrana ekle" ile telefonda çevrimdışı günlük
  kullanım. Diğer her şeyin önündeki kilit. `render.yaml` mevcut.
- **Hızlı-başvuru kutusu (her belge tepesinde)** · Y · M · içerik (workflow) · 🩺
  masthead altında `callout`: en kritik 3–5 madde + ilk-basamak doz + en önemli
  kırmızı bayrak. 89 belge → üret→denetle workflow, sonra `tools/build.py`.
- **Klinik hesaplayıcılar paneli** · Y · M · app-kabuğu · 🩺
  Holliday-Segar idame sıvı, dehidratasyon %/defisit, düzeltilmiş Na, anyon açığı,
  düzeltilmiş Ca; skorlar PUCAI/wPCDAI, PAS/Alvarado, PELD/MELD. Birim + "doğrulayın"
  uyarısı zorunlu; otomatik serbest-metin doz ayrıştırma YAPMA (güvenlik).

## Katman 2 — sorumluluk / güncellik
- **Doz güvenlik denetimi (89 belge)** · Y · M · içerik (workflow) · 🩺
  Adversaryal geçiş: doz/birim/maks/kontrendikasyon tutarlılığı; bulguları düzelt.
- **Künye + gözden geçirme tarihi** · O · S · içerik · 🩺
  Her belgeye "kaynak kılavuz + son gözden geçirme"; 12 ayı aşanı işaretle.
- **Kaynakları bağla (DOI/PubMed)** · O · S · içerik · 🩺
  Düz-metin referanslara link; doğrulanabilirlik.

## Katman 3 — navigasyon / performans / dağıtım
- **Çapraz bağlantı / konu kümeleri** · O · M · app+içerik · 🖥️🩺
  IBD; portal HT–varis–siroz–GİS kanaması; kolestaz–biliyer atrezi–Alagille/PFIC.
- **Lazy-render** · O · M · app-kabuğu · 🖥️
  89 gövdeyi başta DOM'a basmak yerine `<template>`/JSON; mobilde ilk yük/bellek.
- **Yazdırılabilir cep kartı** · O · S · app-kabuğu · 🩺
  Belge başına tek-sayfa `@media print` + "Yazdır" düğmesi.
- **PWA (manifest + SW)** · O · M · barındırma · 🖥️
  Barındırma sonrası; SW `file://`de çalışmaz.
- **Birleşik PDF'i otomatik tazele** · D · S · araç · 🖥️
  İçerik değişince kitaplığı yeniden üret (betikleri `tools/`e kalıcılaştır).

## Katman 4 — erişim / ölçek
- **Skill'i kişisel yap (telefon claude.ai)** · O · S · dağıtım · 🩺
  Vizitte "şu şikâyeti yap" ile anında üretim (şu an yalnız depo-içi aktif).
- **İngilizce sürüm** · O · L · içerik · 🩺 yayın/paylaşım için ikinci dil kolu.
- **Loop'u kaliteye çevir** · O · — · süreç · her tur bir belgeyi güncel kılavuza
  göre gözden geçir (yalnız kullanım değil, içerik bakımı).

## Yüksek-getirili içerik boşlukları (prof. gözü)
Varsa eksik başlıkları `cocuk-ge-algoritma` ile ekle: akut pankreatit şiddet (BISAP
yok—pediatride INSPPIRE), besin alerjisi spektrumu, motilite (gastroparezi), transplant
sonrası GVHD/rejeksiyon-GİS, kronik kusma/CVS örtüşmesi, demir-refrakter anemi-GİS.
