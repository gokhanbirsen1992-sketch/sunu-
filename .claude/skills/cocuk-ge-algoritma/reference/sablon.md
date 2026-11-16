# HTML gövde şablonu — bileşen sözlüğü

Çıktı **yalnızca** `<div class="wrap"> … </div>` gövde parçasıdır. `<style>`,
`<title>`, `<head>`, `<body>`, markdown veya kod bloğu YOK. Stil başka yerde
(`tools/series_style.css`) tanımlı; sadece aşağıdaki sınıfları kullan. Etiketleri
dengeli kapat, çift tırnak kullan, Kiril harf kullanma.

## İzin verilen sınıflar

- **Kök:** `<div class="wrap"> … </div>`
- **Başlık:**
  ```html
  <header class="masthead">
    <p class="eyebrow">Pediyatrik Gastroenteroloji · Klinik Karar Aracı</p>
    <h1>BAŞLIK</h1>
    <p class="sub">1–2 cümle özet</p>
    <div class="meta"><span class="tag">etiket</span> …</div>
  </header>
  ```
- **Bölüm:** `<section><h2><span class="n">01</span> Başlık</h2><p class="lede">…</p> … </section>`
- **Kartlar:** `<div class="grid two"><div class="card"><h3>…</h3><ul class="clean"><li>…</li></ul></div><div class="card">…</div></div>` (`grid three` de var)
- **Şiddet bantları:** `<div class="sev"><div class="band mild"><div class="lvl">Hafif</div><div class="rng">aralık</div><p>…</p></div> …</div>` — tonlar: `mild mod sev rem`
- **Mekanizma/kategori kartları:** `<div class="mech"><div class="m t1"><div class="h">Başlık</div><ul><li>…</li></ul></div> …</div>` — tonlar: `t1 t2 t3 t4 t5 t6`
- **Karar akışı (ZORUNLU):**
  ```html
  <div class="flow">
    <div class="node start"><span class="k">Başlangıç</span><span class="t">…</span><p>…</p></div>
    <div class="connector"></div>
    <div class="node action"><span class="k">Adım 1</span><span class="t">…</span><p>…</p></div>
    <div class="connector"></div>
    <div class="node decision"><span class="k">Karar 1</span><span class="t">…soru?</span><p>…</p></div>
    <div class="branches">
      <div class="branch yes"><span class="label">EVET → …</span>
        <div class="node alarm"><span class="k">…</span><span class="t">…</span><p>…</p></div></div>
      <div class="branch no"><span class="label">HAYIR → …</span>
        <div class="node action safe"><span class="k">…</span><span class="t">…</span><p>…</p></div></div>
    </div>
  </div>
  ```
  Düğüm türleri: `node start` · `node action` · `node action safe` · `node alarm` · `node decision`.
- **Tablo:**
  ```html
  <div class="table-scroll"><table><caption>…</caption>
    <thead><tr><th>…</th></tr></thead>
    <tbody><tr><td class="step">Basamak/İlaç</td><td class="dose">2 mg/kg (maks 40 mg)</td><td>not</td></tr></tbody>
  </table></div>
  ```
  Hücre sınıfları: `td.step` (basamak/ilaç adı), `td.dose` (doz), `td.pts` (puan).
- **Uyarı kutusu:** `<div class="callout">…</div>` · `<div class="callout safe">…</div>` · `<div class="callout alarm">…</div>`
- **Kırmızı bayraklar:** `<div class="alarm-grid"><div class="alarm-item"><span class="dot"></span><span>…</span></div> …</div>`
- **Etiket satırı:** `<div class="pill-row"><span class="pill">…</span></div>`
- **Alt:** `<footer><b>Kaynaklar</b><ol><li>Yazar. Başlık. Dergi. Yıl.</li></ol></footer>` ve `<div class="disclaimer"><b>Uyarı:</b> …</div>`

## En kısa iskelet

```html
<div class="wrap">
  <header class="masthead">
    <p class="eyebrow">Pediyatrik Gastroenteroloji · Klinik Karar Aracı</p>
    <h1>BAŞLIK</h1>
    <p class="sub">…</p>
    <div class="meta"><span class="tag">…</span><span class="tag">0–18 yaş</span></div>
  </header>
  <section><h2><span class="n">01</span> Tanım ve ilk değerlendirme</h2>
    <p class="lede">…</p>
    <div class="grid two"><div class="card"><h3>Öykü</h3><ul class="clean"><li>…</li></ul></div>
      <div class="card"><h3>Muayene</h3><ul class="clean"><li>…</li></ul></div></div>
  </section>
  <section><h2><span class="n">02</span> … (mekanizma veya şiddet) …</h2> … </section>
  <section><h2><span class="n">03</span> Karar akışı</h2><p class="lede">…</p>
    <div class="flow"> … </div>
  </section>
  <section><h2><span class="n">04</span> Basamaklı tetkik</h2><div class="table-scroll"> … </div></section>
  <section><h2><span class="n">05</span> Kırmızı bayraklar</h2><div class="alarm-grid"> … </div></section>
  <section><h2><span class="n">06</span> Tedavi</h2><div class="table-scroll"> … dozlu … </div></section>
  <section><h2><span class="n">07</span> İzlem / yönetim ilkeleri</h2> … </section>
  <div class="disclaimer"><b>Uyarı:</b> Eğitim ve hızlı başvuru amaçlıdır; güncel kılavuz ve yerel protokollerin yerine geçmez. Dozları doğrulayın.</div>
  <footer><b>Kaynaklar</b><ol><li>…</li></ol></footer>
</div>
```
