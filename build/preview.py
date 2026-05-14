#!/usr/bin/env python3
"""
Pediatrik GE Algoritma — tek girdi önizleme derleyicisi (mini pipeline).

Kullanım:
    python build/preview.py sa_02        # data/entries/sa_02.yaml -> dist/sa_02.html
    python build/preview.py --all        # data/entries/*.yaml -> dist/*.html

Bu, "veri (YAML) -> derleme -> HTML" akışının küçük ölçekli örneğidir. Nihai
uygulamada tüm girdiler tek dosyalık, çevrimdışı bir HTML'e derlenecektir.
Önizlemede Mermaid CDN'den yüklenir; nihai derlemede gömülecektir.
"""
import sys
import html
import pathlib

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
ENTRIES = ROOT / "data" / "entries"
DIST = ROOT / "dist"

AXIS_LABEL = {"presentation": "Bulgu / Şikayet temelli", "condition": "Hastalık / Durum temelli"}


def esc(text):
    return html.escape(str(text), quote=True)


def ul(items):
    lis = "".join(f"<li>{esc(x)}</li>" for x in (items or []))
    return f"<ul>{lis}</ul>"


def section(title, body, css_class=""):
    if not body:
        return ""
    cls = f" {css_class}" if css_class else ""
    return f'<section class="card{cls}"><h2>{esc(title)}</h2>{body}</section>'


def render_entry(entry):
    title = esc(entry.get("title", entry.get("id", "?")))
    icon = esc(entry.get("icon", "📋"))
    axis = AXIS_LABEL.get(entry.get("axis", ""), entry.get("axis", ""))
    group = esc(entry.get("group", ""))
    disclaimer = esc(entry.get("disclaimer", ""))

    parts = []

    # Özet
    if entry.get("ozet"):
        parts.append(f'<section class="card ozet"><p>{esc(entry["ozet"])}</p></section>')

    # Akış şeması (Mermaid)
    if entry.get("mermaid"):
        parts.append(
            '<section class="card"><h2>🔀 Akış Şeması</h2>'
            f'<pre class="mermaid">{esc(entry["mermaid"])}</pre></section>'
        )

    parts.append(section("🟢 Bu algoritma ne zaman?", ul(entry.get("giris_kriteri")), "giris"))
    parts.append(section("🚨 Kırmızı Bayraklar", ul(entry.get("kirmizi_bayraklar")), "kirmizi"))
    parts.append(section("📋 Anamnez", ul(entry.get("anamnez"))))
    parts.append(section("🩺 Muayene", ul(entry.get("muayene"))))
    parts.append(section("🧪 İlk Basamak Testler", ul(entry.get("ilk_testler"))))
    parts.append(section("🔬 İleri Testler", ul(entry.get("ileri_testler"))))

    # Ayırıcı tanı (tablo)
    if entry.get("ayirici_tani"):
        rows = "".join(
            f"<tr><td>{esc(d.get('durum',''))}</td><td>{esc(d.get('ipucu',''))}</td></tr>"
            for d in entry["ayirici_tani"]
        )
        table = f"<table><thead><tr><th>Durum</th><th>İpucu</th></tr></thead><tbody>{rows}</tbody></table>"
        parts.append(section("🎭 Ayırıcı Tanı", table))

    parts.append(section("💊 Yönetim & Sevk", ul(entry.get("yonetim_sevk"))))
    parts.append(section("⚠️ Tuzaklar", ul(entry.get("tuzaklar")), "tuzak"))

    # Kaynaklar (PubMed'e çözümlenmiş)
    if entry.get("kaynaklar"):
        items = []
        for k in entry["kaynaklar"]:
            cite = esc(k.get("cite", ""))
            doi = k.get("doi", "")
            pmid = k.get("pmid", "")
            links = []
            if doi:
                links.append(f'<a href="https://doi.org/{esc(doi)}" target="_blank" rel="noopener">DOI</a>')
            if pmid:
                links.append(
                    f'<a href="https://pubmed.ncbi.nlm.nih.gov/{esc(pmid)}/" '
                    f'target="_blank" rel="noopener">PubMed {esc(pmid)}</a>'
                )
            items.append(f'<li>{cite} <span class="links">{" · ".join(links)}</span></li>')
        body = (
            '<p class="kaynak-note">Künyeler PubMed üzerinden doğrulanmıştır.</p>'
            f'<ol class="kaynaklar">{"".join(items)}</ol>'
        )
        parts.append(section("📚 Kaynaklar", body))

    return f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #f1f5f9; color: #1e293b; line-height: 1.55; padding: 16px; }}
  .wrap {{ max-width: 820px; margin: 0 auto; }}
  header.top {{ background: #fff; border: 1px solid #e2e8f0; border-radius: 12px;
    padding: 18px 20px; margin-bottom: 14px; }}
  header.top h1 {{ font-size: 20px; line-height: 1.35; }}
  .badges {{ margin-top: 8px; display: flex; gap: 6px; flex-wrap: wrap; }}
  .badge {{ font-size: 12px; background: #e0e7ff; color: #3730a3; padding: 3px 9px;
    border-radius: 999px; }}
  .disclaimer {{ margin-top: 10px; font-size: 12px; color: #64748b; font-style: italic; }}
  .card {{ background: #fff; border: 1px solid #e2e8f0; border-radius: 12px;
    padding: 16px 20px; margin-bottom: 14px; }}
  .card h2 {{ font-size: 15px; margin-bottom: 10px; color: #0f172a; }}
  .card.ozet {{ background: #ecfeff; border-color: #a5f3fc; }}
  .card.ozet p {{ font-size: 14.5px; }}
  .card.kirmizi {{ background: #fef2f2; border-color: #fecaca; }}
  .card.giris {{ background: #f0fdf4; border-color: #bbf7d0; }}
  .card.tuzak {{ background: #fffbeb; border-color: #fde68a; }}
  ul, ol {{ padding-left: 20px; }}
  li {{ margin-bottom: 5px; font-size: 14px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13.5px; }}
  th, td {{ text-align: left; padding: 7px 9px; border-bottom: 1px solid #e2e8f0;
    vertical-align: top; }}
  th {{ background: #f8fafc; }}
  td:first-child {{ font-weight: 600; white-space: nowrap; }}
  .mermaid {{ background: #fff; text-align: center; overflow-x: auto; }}
  .kaynaklar li {{ margin-bottom: 8px; }}
  .kaynak-note {{ font-size: 12px; color: #64748b; margin-bottom: 8px; }}
  .links a {{ font-size: 12px; margin-left: 4px; color: #2563eb; text-decoration: none;
    white-space: nowrap; }}
  footer {{ font-size: 11px; color: #94a3b8; text-align: center; margin: 18px 0; }}
</style>
</head>
<body>
<div class="wrap">
  <header class="top">
    <h1>{icon} {title}</h1>
    <div class="badges">
      <span class="badge">{esc(axis)}</span>
      <span class="badge">{group}</span>
      <span class="badge">id: {esc(entry.get("id",""))}</span>
    </div>
    <p class="disclaimer">{disclaimer}</p>
  </header>
  {"".join(p for p in parts if p)}
  <footer>Pediatrik GE — Literatür Temelli Algoritmalar · önizleme derlemesi</footer>
</div>
<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
<script>mermaid.initialize({{ startOnLoad: true, theme: 'default', flowchart: {{ htmlLabels: true }} }});</script>
</body>
</html>
"""


def build_one(entry_id):
    src = ENTRIES / f"{entry_id}.yaml"
    if not src.exists():
        sys.exit(f"Girdi bulunamadı: {src}")
    entry = yaml.safe_load(src.read_text(encoding="utf-8"))
    DIST.mkdir(exist_ok=True)
    out = DIST / f"{entry_id}.html"
    out.write_text(render_entry(entry), encoding="utf-8")
    print(f"  {src.name} -> {out.relative_to(ROOT)}")


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    if args[0] == "--all":
        ids = sorted(p.stem for p in ENTRIES.glob("*.yaml"))
    else:
        ids = args
    print(f"Derleniyor ({len(ids)} girdi):")
    for entry_id in ids:
        build_one(entry_id)
    print("Tamam.")


if __name__ == "__main__":
    main()
