"""Telefon / tarayıcı arayüzü.

Çalıştırma:
    uvicorn megastat.web:app --host 0.0.0.0 --port 8000

Sonra telefondan veya bilgisayardan adrese girip dosyayı yükleyin;
özet ekranda görünür, tam Excel raporu indirilir.
"""
from __future__ import annotations

import html
import io
import threading
import urllib.parse
import uuid

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse

from megastat.engine import analyze_dataframe
from megastat.loader import DESTEKLENEN_UZANTILAR, load_bytes
from megastat.report import excel_raporu, metin_ozeti

app = FastAPI(title="MegaStat", version="1.2.0")

# Son raporlar ve işler bellekte tutulur (küçük, tek kullanıcılı araç için yeterli)
_raporlar: dict[str, tuple[str, bytes]] = {}
_MAX_RAPOR = 20
# Analiz ARKA PLANDA çalışır: ücretsiz sunucularda uzun HTTP istekleri ~100 sn'de
# kesilir; iş kuyruğu + durum sorgusu bu sınırı tamamen devre dışı bırakır.
_isler: dict[str, dict[str, str]] = {}
_MAX_IS = 20

_SAYFA = """<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MegaStat — Sınırsız İstatistik</title>
<style>
  body {{ font-family: -apple-system, "Segoe UI", Roboto, sans-serif; margin: 0;
         background: #f4f6fb; color: #1a2333; }}
  .kutu {{ max-width: 680px; margin: 0 auto; padding: 20px; }}
  h1 {{ font-size: 1.5rem; }} h1 span {{ color: #2563eb; }}
  .kart {{ background: #fff; border-radius: 14px; padding: 20px;
           box-shadow: 0 2px 10px rgba(15,30,80,.08); margin-bottom: 16px; }}
  input[type=file] {{ width: 100%; padding: 12px; border: 2px dashed #94a3b8;
                      border-radius: 10px; background: #f8fafc; }}
  button {{ width: 100%; margin-top: 14px; padding: 14px; font-size: 1.05rem;
            background: #2563eb; color: #fff; border: 0; border-radius: 10px; }}
  button:disabled {{ background: #94a3b8; }}
  pre {{ white-space: pre-wrap; word-break: break-word; font-size: .85rem;
         background: #0f172a; color: #e2e8f0; padding: 14px; border-radius: 10px; }}
  a.indir {{ display: block; text-align: center; margin-top: 12px; padding: 14px;
             background: #16a34a; color: #fff; border-radius: 10px; text-decoration: none; }}
  .hata {{ color: #b91c1c; font-weight: 600; }}
  .kucuk {{ color: #64748b; font-size: .85rem; }}
</style>
</head>
<body>
<div class="kutu">
  <h1>📊 Mega<span>Stat</span></h1>
  <div class="kart">
    <p>Veri dosyanızı seçin (<b>{uzantilar}</b>). Program <b>9 katmanlı tam analiz</b> yapar:</p>
    <ol style="font-size:.9rem; padding-left:20px; margin-top:4px">
      <li>Betimseller + 4 normallik testi</li>
      <li>Tüm klasik testler (t/ANOVA/Mann-Whitney/Kruskal/ki-kare/korelasyon) + FDR düzeltmesi</li>
      <li>Gelişmiş klasik: eşleştirilmiş t/Wilcoxon, Friedman, kappa/McNemar,
          Cronbach α + madde analizi, faktör analizi (KMO), çoklu &amp; lojistik regresyon, ROC</li>
      <li>Gizli formüller: 7 aday eğri modeli → en iyisi <b>açık denklem</b> olarak
          (örn. etki = 5.1 + 7.9·ln(doz)) + X×Z etkileşim (moderasyon) taraması</li>
      <li>Doğrusal-olmayan gizli ilişkiler (Karşılıklı Bilgi — Pearson'ın kaçırdıkları)</li>
      <li>Gradient Boosting ML: çok değişkenli öngörü + değişken önem sıralaması</li>
      <li>Kısmi korelasyon: sahte/aracılı ilişki ayıklama</li>
      <li>Gizli alt gruplar (PCA + K-Means kümeleme) + sıra dışı vaka tespiti</li>
      <li>Risk skoru: ikili sonuçlar için çapraz-doğrulamalı risk modeli (AUC)</li>
    </ol>
    <p>Sonuç çok sayfalı Excel raporu olarak iner; apaçık/tanımsal korelasyonlar keşiflerden ayrı tutulur.</p>
    <form id="form">
      <input type="file" name="dosya" id="dosya" required>
      <button type="submit" id="btn">Analiz Et</button>
    </form>
    <p class="kucuk">Veriniz sunucuda saklanmaz; analiz bellekte yapılır.</p>
  </div>
  <div class="kart" id="sonucKart" style="display:none">
    <div id="sonuc"></div>
  </div>
</div>
<script>
const form = document.getElementById("form");
const bekle = (ms) => new Promise((r) => setTimeout(r, ms));
form.addEventListener("submit", async (e) => {{
  e.preventDefault();
  const btn = document.getElementById("btn");
  const kart = document.getElementById("sonucKart");
  const alan = document.getElementById("sonuc");
  const dosya = document.getElementById("dosya").files[0];
  if (!dosya) return;
  btn.disabled = true;
  kart.style.display = "block";
  alan.innerHTML = "<p>⏳ Analiz başlatılıyor…</p>";
  const fd = new FormData(); fd.append("dosya", dosya);
  try {{
    const yanit = await fetch("/analiz", {{ method: "POST", body: fd }});
    const veri = await yanit.json();
    if (!yanit.ok) throw new Error(veri.detail || "Analiz başlatılamadı");
    const basla = Date.now();
    while (true) {{
      await bekle(3000);
      const sn = Math.round((Date.now() - basla) / 1000);
      btn.textContent = "Hesaplanıyor… " + sn + " sn";
      alan.innerHTML = "<p>⏳ 9 katman hesaplanıyor… (" + sn +
        " sn) Büyük veride birkaç dakika sürebilir; sayfayı kapatmayın.</p>";
      let d;
      try {{
        const dy = await fetch("/durum/" + veri.is_id);
        d = await dy.json();
        if (!dy.ok) throw new Error(d.detail || "durum alınamadı");
      }} catch (agHata) {{ continue; }}  // geçici ağ hatasında sormaya devam et
      if (d.durum === "bitti") {{
        alan.innerHTML = "<pre>" + d.ozet_html + "</pre>" +
          '<a class="indir" href="' + d.indir + '">⬇️ Tam Excel Raporunu İndir</a>';
        break;
      }}
      if (d.durum === "hata") throw new Error(d.hata || "analiz hatası");
    }}
  }} catch (err) {{
    alan.innerHTML = '<p class="hata">Hata: ' + err.message + "</p>";
  }} finally {{
    btn.disabled = false; btn.textContent = "Analiz Et";
  }}
}});
</script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
def anasayfa() -> str:
    return _SAYFA.format(uzantilar=", ".join(DESTEKLENEN_UZANTILAR))


def _analizi_calistir(is_id: str, icerik: bytes, dosya_adi: str) -> None:
    try:
        df = load_bytes(icerik, dosya_adi)
        sonuc = analyze_dataframe(df)
        rapor = excel_raporu(sonuc)
        rapor_id = uuid.uuid4().hex
        temel_ad = dosya_adi.rsplit(".", 1)[0]
        _raporlar[rapor_id] = (f"{temel_ad}_megastat.xlsx", rapor)
        while len(_raporlar) > _MAX_RAPOR:
            _raporlar.pop(next(iter(_raporlar)))
        _isler[is_id] = {
            "durum": "bitti",
            "ozet_html": html.escape(metin_ozeti(sonuc)),
            "indir": f"/indir/{rapor_id}",
        }
    except Exception as exc:  # okunur mesaj; ayrıntı sunucu logunda
        _isler[is_id] = {"durum": "hata", "hata": str(exc)}


@app.post("/analiz")
async def analiz(dosya: UploadFile = File(...)) -> dict[str, str]:
    icerik = await dosya.read()
    if not icerik:
        raise HTTPException(status_code=400, detail="Boş dosya yüklendi.")
    is_id = uuid.uuid4().hex
    _isler[is_id] = {"durum": "calisiyor"}
    while len(_isler) > _MAX_IS:
        _isler.pop(next(iter(_isler)))
    threading.Thread(
        target=_analizi_calistir,
        args=(is_id, icerik, dosya.filename or "veri.csv"),
        daemon=True,
    ).start()
    return {"is_id": is_id}


@app.get("/durum/{is_id}")
def durum(is_id: str) -> dict[str, str]:
    kayit = _isler.get(is_id)
    if kayit is None:
        raise HTTPException(status_code=404, detail="İş bulunamadı; lütfen analizi yeniden başlatın.")
    return kayit


@app.get("/indir/{rapor_id}")
def indir(rapor_id: str) -> StreamingResponse:
    kayit = _raporlar.get(rapor_id)
    if kayit is None:
        raise HTTPException(status_code=404, detail="Rapor bulunamadı; lütfen analizi yeniden çalıştırın.")
    ad, veri = kayit
    guvenli_ad = urllib.parse.quote(ad)
    return StreamingResponse(
        io.BytesIO(veri),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{guvenli_ad}"},
    )
