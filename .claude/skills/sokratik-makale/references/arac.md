# Karar ağacı aracı kalıbı

Yalnız kullanıcı isterse. Depoda `docs/ortak.js` ve `docs/ortak.css` varsa bu kalıbı kullan; yoksa aynı yapıda tek dosya yaz.

## Dosyalar
- `docs/<arac>/index.html` — tek sayfa. Sekmeler: **Karar ağacı**, **Doz** (varsa), **Testler/Alarm**, **Notlar** (kaynağın iç tutarsızlıkları).
- `docs/ortak.css` — `body[data-tool="<ad>"]{--accent:...}` + koyu tema varyantları (üç yer).
- `docs/sw.js` — önbellek adını bir artır, yeni yolları FILES'a ekle.
- `docs/index.html` — yeni kart.
- Diğer araçların `nav.crumb` satırına bağlantı.
- `araclar/derle.py` — HEDEF sözlüğüne ve göreli bağlantı değişimine ekle; `python3 araclar/derle.py`.
- `paylas/<ad>-karar-araci.html` — ortak.css/js gömülü tek dosya (kullanıcıya gönderilecek sürüm).

## Sihirbaz motoru (ortak.js `Ortak.wizard`)
```js
var Q=[{k:'anahtar',step:'Bölüm',label:'Soru?',hint:'...',show:function(s){return ...;},opts:[['deger','Metin']],keep:true}];
function decide(s){ /* null = cevap bekleniyor; R(k,lvl,sub,act[],ev[],flags[]) */ }
Ortak.wizard({Q,decide,LV,tool,source,form:'#form',result:'#result',reset:'#reset',sticky:'#sticky'});
```
- `k` (renk): `acil`, `ivedi`, `elektif`, `kons`, `izlem`, `bireysel`, `info`.
- `flags` = sarı şerit: kaynağın tutarsızlığı, uzlaşı eşiğini geçmeyen öneri, araç kararı.
- Kaynakta olmayan dalda araç karar veriyorsa `bireysel` rengi ve "(araç kararı)" etiketi.
- `window.__<ad>={decide,dose,Q}` dışa aç (test için).

## Doğrulama (zorunlu)
1. Tüm yolları tara — çıkmaz ve istisna 0 olmalı:
   ```python
   # Playwright, executable_path=glob('/opt/pw-browsers/chromium-*/chrome-linux/chrome')[0]
   # DFS: decide(S) null ve görünür cevapsız soru yoksa → çıkmaz
   ```
   (Betik adını `enum.py` koyma — stdlib ile çakışır.)
2. 390 px genişlikte ekran görüntüsü; yatay kaydırma yok; koyu tema.
3. Doz fonksiyonunu bant sınırlarında çağırıp elle karşılaştır.
4. Sonra commit + push (designated branch), tek dosya sürümünü kullanıcıya gönder.
