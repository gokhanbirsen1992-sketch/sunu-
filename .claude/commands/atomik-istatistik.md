---
description: Atomik istatistik — 9 sütunlu istatistik/ML yöntem taksonomisini üret veya güncelle
---

`atomik-istatistik` skill'ini çalıştır.

Kaynak olarak şu öncelikle dosyaları kullan:
1. `docs/atomic-statistics-registry.md` (bu repo)
2. Skill klasöründeki `registry.md` (global)

Kullanıcının ek talebi (varsa): $ARGUMENTS

Davranış:
- Talep yoksa veya "göster/yap" ise → tam 9 sütunlu (Sütun 0–8) taksonomiyi sun.
- "ekle / düzelt / çıkar / güncelle" ise → `docs/atomic-statistics-registry.md`'yi güncelle
  ve belge sonuna sürüm/değişiklik notu ekle.
- "pdf" geçiyorsa → Markdown'ı stillenmiş HTML'e çevirip Chromium headless ile PDF üret ve gönder.
- "complete/eksiksiz" yerine "kapsamlı ve genişletilebilir referans" çerçevesini koru.
