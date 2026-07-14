#!/usr/bin/env python3
"""Çocuk GE algoritma kütüphanesi — gezinme katmanını yeniden üretir.

Commit'lenmiş standalone belgelerden (docs/pediatrik-<slug>-algoritmasi.html)
docs/index.html (aranabilir hub) ve docs/app.html (tek dosya uygulama) üretir.
Frag ara ürünleri GEREKMEZ. Kullanım:  python3 tools/build.py

Özellikler: canlı arama + klinik eş anlamlı genişletme, kategori + 🚨 Aciller
filtresi, klavye gezinme, son bakılanlar, elle tema düğmesi, erişilebilirlik
(landmark/ARIA/aria-live/odak yönetimi/atla-bağlantısı), geri-tuşu (hashchange).
"""
import re, os, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "docs")
STYLE_INNER = re.search(r"<style>(.*)</style>",
    open(os.path.join(ROOT, "tools", "series_style.css"), encoding="utf-8").read(), re.S).group(1)

CATS = [
 ("Semptomlar ve şikâyetler","semptom",["kabizlik","kronik-ishal","reflu-gorh","kusma","safrali-kusma","siklik-kusma","ruminasyon","disfaji-odinofaji","fonksiyonel-dispepsi","ibs","abdominal-migren","akut-karin-agrisi","kronik-karin-agrisi","karin-distansiyon","akut-gastroenterit","dizanteri","enkoprezis","alt-gis-kanamasi","ust-gis-kanamasi","steatore-malabsorpsiyon","buyume-geriligi-gis","beslenme-reddi","infantil-kolik","malnutrisyon-refeeding","sarilik-buyuk-cocuk","kolestatik-kasinti","yabanci-cisim","kostik-alim","gogus-yanma-globus","gegirme-hickirik-aerofaji"]),
 ("Muayene bulguları","muayene",["splenomegali","hepatomegali","hepatosplenomegali","asit","karin-kitlesi","perianal-hastalik","rektal-prolapsus","aftoz-ekstraintestinal"]),
 ("Laboratuvar anormallikleri","lab",["transaminaz-yuksekligi","hiperbilirubinemi","ggt-alp-yuksekligi","hipoalbuminemi-ple","koagulopati-inr","hiperamonyemi","kalprotektin-yuksekligi","gis-demir-eksikligi","colyak-seroloji-pozitif","amilaz-lipaz-yuksekligi","fekal-elastaz-dusuk","eozinofili-gis","vitamin-eksikligi-adek","elektrolit-bozuklugu-gis","diski-tetkik-anormallikleri"]),
 ("Görüntüleme / endoskopi / patoloji","goruntuleme",["kc-fokal-lezyon","safra-tasi-kolelitiazis","koledok-kisti","portal-hipertansiyon","barsak-duvari-kalinlasmasi","intususepsiyon","malrotasyon-volvulus","pilor-stenozu","apandisit","ozofagus-varisi","eozinofilik-ozofajit","gastrit-ulser-hp","kolon-polip"]),
 ("Hastalık / tanı temelli","hastalik",["yenidogan-kolestazi","ulseratif-kolit","masld","crohn","colyak-hastaligi","inek-sutu-alerjisi","otoimmun-hepatit","wilson","alagille-pfic","palf","kronik-kc-siroz","pankreatit","kistik-fibrozis-gis","kisa-barsak-sendromu","hirschsprung","konjenital-ishal","intestinal-lenfanjiektazi","ilac-hepatotoksisite","ifald","sibo","laktoz-malabsorpsiyon","akalazya"]),
]

# Klinik eş anlamlı/kısaltma kümeleri (hepsi ASCII-normalize; arama genişletmesi için)
CLUSTERS = [
 ["kanama","hematemez","melena","hematokezya","kanli","bleeding","rektal kanama"],
 ["sarilik","ikter","jaundice","bilirubin","kolestaz","acholik"],
 ["reflu","gorh","gord","regurjitasyon","reflux","pirozis"],
 ["kabizlik","konstipasyon","constipation"],
 ["ishal","diyare","diarrhea","gastroenterit","dizanteri"],
 ["kusma","emesis","vomiting","bulanti","safrali"],
 ["karin agrisi","abdominal","batin","gogus agrisi"],
 ["transaminaz","alt","ast","karaciger enzim","hipertransaminazemi"],
 ["ggt","alp","alkalen fosfataz","kolestaz belirteci"],
 ["ibd","crohn","ulseratif kolit","inflamatuar barsak","pucai","wpcdai"],
 ["portal hipertansiyon","varis","siroz","portal ven trombozu"],
 ["colyak","celiac","gluten","transglutaminaz","villoz atrofi"],
 ["pankreatit","amilaz","lipaz","pankreas"],
 ["eozinofilik","eozinofili","eoe","ozofajit"],
 ["h pylori","helikobakter","gastrit","ulser","peptik"],
 ["hepatomegali","karaciger buyuklugu"],
 ["splenomegali","dalak buyuklugu","hipersplenizm"],
 ["asit","ascites","batinda sivi","parasentez"],
 ["disfaji","yutma guclugu","odinofaji","akalazya"],
 ["buyume geriligi","ftt","gelisme geriligi","malnutrisyon"],
 ["wilson","bakir","seruloplazmin"],
 ["otoimmun hepatit","aih"],
 ["yabanci cisim","dugme pil","miknatis"],
 ["kostik","yakici madde","asit alkali"],
 ["hemoliz","anemi","demir eksikligi","retikulosit"],
 ["kalprotektin","fekal","gizli kan"],
 ["biliyer atrezi","koledok kisti","kolestaz","yenidogan"],
 ["hirschsprung","mekonyum","ganglion"],
 ["kistik fibrozis","ter testi","elastaz","pankreas yetmezligi"],
 ["akut karaciger yetmezligi","palf","ensefalopati","koagulopati","inr"],
]
CAT_ALIAS = {"semptom":"belirti sikayet","muayene":"fizik bulgu","lab":"laboratuvar tetkik","goruntuleme":"usg bt mr endoskopi radyoloji","hastalik":"tani hastalik"}

# Gerçekten zaman-kritik / cerrahi / yoğun bakım gerektiren (başucu "Aciller" görünümü)
EMERG = {
 "safrali-kusma","malrotasyon-volvulus","intususepsiyon","apandisit","kostik-alim",
 "yabanci-cisim","ust-gis-kanamasi","alt-gis-kanamasi","akut-karin-agrisi",
 "akut-gastroenterit","palf","ozofagus-varisi","portal-hipertansiyon","pilor-stenozu",
 "hiperamonyemi","yenidogan-kolestazi","koagulopati-inr",
}

def strip_tags(s): return re.sub(r"<[^>]+>","",s).strip()
def norm(s): return (s or "").lower().replace("ç","c").replace("ğ","g").replace("ı","i").replace("ö","o").replace("ş","s").replace("ü","u")

def load(slug):
    p = os.path.join(D, f"pediatrik-{slug}-algoritmasi.html")
    if not os.path.exists(p): return None
    t = open(p, encoding="utf-8").read()
    h = re.search(r"<h1[^>]*>(.*?)</h1>", t, re.S); title = strip_tags(h.group(1)) if h else slug
    s = re.search(r'<p class="sub">(.*?)</p>', t, re.S); sub = strip_tags(s.group(1)) if s else ""
    b = re.search(r'<div class="wrap">.*</div>\s*$', t, re.S); body = b.group(0) if b else ""
    emerg = slug in EMERG   # zaman-kritik acil mi (küratörlü liste)
    return title, sub, body, emerg

def haystack(title, sub, cat_key):
    base = norm(title + " " + sub) + " " + CAT_ALIAS.get(cat_key, "")
    extra = set()
    for cl in CLUSTERS:
        if any(term in base for term in cl): extra.update(cl)
    return html.escape((base + " " + " ".join(sorted(extra))).strip())

# yeni/haritada olmayan slug'ları keşfet
known = {s for _,_,ss in CATS for s in ss}
extra = sorted(
    m.group(1) for f in os.listdir(D)
    if (m := re.match(r"pediatrik-(.+)-algoritmasi\.html$", f)) and "yol-haritasi" not in f
    and m.group(1) not in known)
cats = list(CATS) + ([("Diğer / yeni","diger",extra)] if extra else [])

grouped = []; total = 0; emerg_count = 0
for cat_title, cat_key, slugs in cats:
    rows = []
    for slug in slugs:
        r = load(slug)
        if not r: continue
        title, sub, body, emerg = r
        rows.append((slug, title, sub, body, emerg, haystack(title, sub, cat_key)))
        total += 1; emerg_count += 1 if emerg else 0
    if rows: grouped.append((cat_title, cat_key, rows))

short = lambda t: t.split(" /")[0].split(" ve")[0]

# ============================== index.html ==============================
cards = []
for cat_title, cat_key, rows in grouped:
    for slug, title, sub, body, emerg, hay in rows:
        cards.append(f'''<a class="algo" href="pediatrik-{slug}-algoritmasi.html" data-cat="{cat_key}" data-emerg="{1 if emerg else 0}" data-search="{hay}">
      <span class="algo-cat">{html.escape(short(cat_title))}</span>
      <span class="algo-title">{html.escape(title)}</span>
      <span class="algo-sub">{html.escape(sub)}</span></a>''')
index_chips = ('<button class="chip active" data-filter="all">Tümü</button>'
    '<button class="chip chip-emerg" data-filter="emerg">🚨 Aciller</button>'
    + "".join(f'<button class="chip" data-filter="{k}">{html.escape(short(t))}</button>' for t,k,_ in grouped))
index_css = """
  *{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);line-height:1.5}
  .skip{position:absolute;left:-999px;top:0;background:var(--accent);color:#fff;padding:8px 12px;border-radius:0 0 8px 0;z-index:50}.skip:focus{left:0}
  .sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
  .wrap{max-width:1180px;margin:0 auto;padding:28px 20px 64px}
  header{border-left:4px solid var(--accent);padding:2px 0 2px 18px}
  .eyebrow{font-size:.72rem;letter-spacing:.16em;text-transform:uppercase;color:var(--accent);font-weight:700;margin:0 0 6px}
  h1{font-size:clamp(1.5rem,3.4vw,2.1rem);margin:0}.sub{color:var(--ink-soft);margin:8px 0 0;max-width:70ch;font-size:.96rem}
  .toolbar{position:sticky;top:0;z-index:5;background:color-mix(in srgb,var(--bg) 88%,transparent);backdrop-filter:blur(8px);padding:16px 0 12px;margin-top:14px;border-bottom:1px solid var(--line)}
  .search{width:100%;font-size:1rem;padding:12px 16px;border:1px solid var(--line);border-radius:12px;background:var(--surface);color:var(--ink);box-shadow:var(--shadow)}
  .search:focus{outline:2px solid var(--accent);outline-offset:1px}
  .chips{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}
  .chip{font:inherit;font-size:.84rem;padding:6px 13px;border-radius:100px;border:1px solid var(--line);background:var(--surface);color:var(--ink-soft);cursor:pointer}
  .chip.active{background:var(--accent);color:#fff;border-color:var(--accent)}
  .chip-emerg{color:var(--alarm);border-color:color-mix(in srgb,var(--alarm) 35%,transparent)}
  .chip-emerg.active{background:var(--alarm);color:#fff;border-color:var(--alarm)}
  .count{font-size:.82rem;color:var(--ink-soft);margin:14px 2px 8px;font-variant-numeric:tabular-nums}
  .grid{display:grid;gap:14px;grid-template-columns:repeat(auto-fill,minmax(270px,1fr))}
  .algo{display:flex;flex-direction:column;gap:6px;text-decoration:none;color:inherit;background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:15px 17px;box-shadow:var(--shadow);border-top:3px solid var(--tone,var(--accent));transition:transform .08s ease}
  .algo:hover{transform:translateY(-2px)}.algo:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
  .algo-cat{font-size:.68rem;letter-spacing:.08em;text-transform:uppercase;font-weight:700;color:var(--tone,var(--accent))}
  .algo-title{font-weight:600;font-size:1.02rem}.algo-sub{font-size:.85rem;color:var(--ink-soft)}
  .algo[data-cat=semptom]{--tone:#b45309}.algo[data-cat=muayene]{--tone:#0891b2}.algo[data-cat=lab]{--tone:#2563eb}
  .algo[data-cat=goruntuleme]{--tone:#7c3aed}.algo[data-cat=hastalik]{--tone:#b91c1c}.algo[data-cat=diger]{--tone:#0f766e}
  .empty{text-align:center;color:var(--ink-soft);padding:40px;display:none}
  footer{margin-top:40px;padding-top:18px;border-top:1px solid var(--line);font-size:.82rem;color:var(--ink-soft)}footer a{color:var(--accent)}
"""
index = f'''<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Çocuk Gastroenterolojisi — Algoritma Kütüphanesi</title>
<style>{STYLE_INNER}{index_css}</style></head><body>
<a class="skip" href="#grid">İçeriğe atla</a><div class="wrap">
<header><p class="eyebrow">Klinik Karar Kütüphanesi</p><h1>Çocuk Gastroenterolojisi — Algoritma Kütüphanesi</h1>
<p class="sub">{total} uzman-düzeyi algoritma. Başlığa/belirtiye göre arayın (klinik eş anlamlılar dahil); karta tıklayıp açın. <a href="app.html">Tek sayfa uygulama →</a></p></header>
<div class="toolbar" role="search"><input class="search" id="q" type="search" placeholder="Ara: reflü, kanama, ALT, Wilson, pankreatit…" autocomplete="off" aria-label="Algoritma ara" aria-controls="grid"><div class="chips" id="chips" role="group" aria-label="Filtreler">{index_chips}</div></div>
<div class="count" id="count" aria-live="polite"></div><div class="grid" id="grid">{"".join(cards)}</div>
<div class="empty" id="empty">Eşleşen algoritma yok.</div>
<footer>Tek PDF: <a href="pediatrik-gastroenteroloji-algoritma-kitapcigi.pdf">kitaplık</a> · <a href="pediatrik-gis-algoritma-yol-haritasi.html">yol haritası</a>. Eğitim amaçlıdır; kılavuz ve yerel protokollerin yerine geçmez.</footer>
</div><script>
const grid=document.getElementById('grid'),q=document.getElementById('q'),chips=document.getElementById('chips'),count=document.getElementById('count'),empty=document.getElementById('empty'),cards=[...grid.children];let filter='all';
function norm(s){{return s.toLowerCase().replace(/ç/g,'c').replace(/ğ/g,'g').replace(/ı/g,'i').replace(/ö/g,'o').replace(/ş/g,'s').replace(/ü/g,'u');}}
function apply(){{const term=norm(q.value.trim());let n=0;cards.forEach(c=>{{const okCat=(filter==='all')||(filter==='emerg'?c.dataset.emerg==='1':c.dataset.cat===filter);const ok=okCat&&(!term||norm(c.dataset.search).includes(term));c.style.display=ok?'':'none';if(ok)n++;}});count.textContent=n+' algoritma'+(term||filter!=='all'?' (filtreli)':'');empty.style.display=n?'none':'block';}}
q.addEventListener('input',apply);chips.addEventListener('click',e=>{{const b=e.target.closest('.chip');if(!b)return;filter=b.dataset.filter;[...chips.children].forEach(x=>x.classList.toggle('active',x===b));apply();}});apply();
</script></body></html>'''
open(os.path.join(D,"index.html"),"w",encoding="utf-8").write(index)

# ============================== app.html ==============================
navhtml=""; docshtml=""; statmeta=[]
for cat_title, cat_key, rows in grouped:
    statmeta.append((cat_key, short(cat_title), len(rows)))
    navhtml += f'<div class="navgroup" data-cat="{cat_key}"><div class="navcat cat-{cat_key}">{html.escape(cat_title)}</div>'
    for slug, title, sub, body, emerg, hay in rows:
        badge = '<span class="emerg" title="Kırmızı bayrak içerir" aria-label="acil">🚨</span>' if emerg else ''
        navhtml += f'<button class="navitem" data-slug="{slug}" data-emerg="{1 if emerg else 0}" data-search="{hay}"><span class="dot dot-{cat_key}"></span><span class="nt">{html.escape(title)}</span>{badge}</button>'
        docshtml += f'<article class="doc" id="a-{slug}" data-cat="{cat_key}" hidden>{body}</article>'
    navhtml += '</div>'
appchips=('<button class="chip active" data-filter="all">Tümü</button>'
    '<button class="chip chip-emerg" data-filter="emerg">🚨 Aciller</button>'
    + "".join(f'<button class="chip" data-filter="{k}">{html.escape(t)}</button>' for k,t,_ in statmeta))
stats="".join(f'<div class="stat cat-{k}"><b>{n}</b><span>{t}</span></div>' for k,t,n in statmeta)
app_css="""
html,body{height:100%}body{margin:0}
.skip{position:absolute;left:-999px;top:0;background:var(--accent);color:#fff;padding:8px 12px;border-radius:0 0 8px 0;z-index:50}.skip:focus{left:8px;top:8px;border-radius:8px}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.app{display:grid;grid-template-columns:330px 1fr;height:100vh;overflow:hidden}
.side{border-right:1px solid var(--line);background:var(--surface);display:flex;flex-direction:column;min-height:0}
.side .top{padding:12px 14px 10px;border-bottom:1px solid var(--line);position:sticky;top:0;background:var(--surface);z-index:2}
.brandrow{display:flex;align-items:flex-start;justify-content:space-between;gap:8px}
.brand{font-size:.7rem;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);font-weight:800}
.brand b{display:block;font-size:1.02rem;color:var(--ink);margin-top:2px;text-transform:none}
.themebtn{flex:none;font:inherit;font-size:.9rem;line-height:1;padding:7px 9px;border:1px solid var(--line);border-radius:9px;background:var(--bg);color:var(--ink);cursor:pointer}
.themebtn:hover{border-color:var(--accent);color:var(--accent)}
.search{width:100%;margin-top:10px;font-size:.95rem;padding:9px 12px;border:1px solid var(--line);border-radius:10px;background:var(--bg);color:var(--ink)}
.search:focus{outline:2px solid var(--accent);outline-offset:1px}
.chips{display:flex;flex-wrap:wrap;gap:6px;margin-top:9px}
.chip{font:inherit;font-size:.74rem;padding:4px 9px;border-radius:100px;border:1px solid var(--line);background:var(--bg);color:var(--ink-soft);cursor:pointer}
.chip.active{background:var(--accent);color:#fff;border-color:var(--accent)}
.chip-emerg{color:var(--alarm);border-color:color-mix(in srgb,var(--alarm) 35%,transparent)}
.chip-emerg.active{background:var(--alarm);color:#fff;border-color:var(--alarm)}
.recents{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin-top:9px}
.recents .rl{font-size:.72rem;color:var(--ink-soft);font-weight:600}
.rchip{font:inherit;font-size:.74rem;max-width:150px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;padding:4px 9px;border-radius:8px;border:1px solid var(--line);background:var(--bg);color:var(--ink);cursor:pointer}
.rchip:hover{border-color:var(--accent);color:var(--accent)}
.navlist{overflow:auto;padding:8px 8px 40px;min-height:0}
.navcat{font-size:.66rem;letter-spacing:.07em;text-transform:uppercase;font-weight:800;color:var(--tone,var(--accent));margin:12px 8px 4px}
.navitem{display:flex;align-items:center;gap:9px;width:100%;text-align:left;font:inherit;font-size:.88rem;color:var(--ink);background:none;border:0;border-radius:8px;padding:8px 9px;cursor:pointer;min-height:38px}
.navitem .nt{flex:1;min-width:0}
.navitem:hover{background:var(--surface-2)}.navitem.active{background:var(--accent-wash);color:var(--accent);font-weight:600}
.navitem:focus-visible{outline:2px solid var(--accent);outline-offset:-2px}
.navitem .emerg{font-size:.8rem;flex:none}
.dot{width:8px;height:8px;border-radius:50%;flex:none}
.cat-semptom{--tone:#b45309}.cat-muayene{--tone:#0891b2}.cat-lab{--tone:#2563eb}.cat-goruntuleme{--tone:#7c3aed}.cat-hastalik{--tone:#b91c1c}.cat-diger{--tone:#0f766e}
.dot-semptom{background:#b45309}.dot-muayene{background:#0891b2}.dot-lab{background:#2563eb}.dot-goruntuleme{background:#7c3aed}.dot-hastalik{background:#b91c1c}.dot-diger{background:#0f766e}
.main{overflow:auto;min-height:0}.main:focus{outline:none}.main .wrap{padding-top:22px}
.welcome{max-width:760px;margin:0 auto;padding:56px 24px}.welcome h1{font-size:clamp(1.6rem,3.2vw,2.2rem);margin:0 0 10px}.welcome p{color:var(--ink-soft)}
.stats{display:flex;flex-wrap:wrap;gap:10px;margin-top:20px}
.stat{background:var(--surface);border:1px solid var(--line);border-top:3px solid var(--tone,var(--accent));border-radius:12px;padding:12px 16px;box-shadow:var(--shadow)}
.stat b{font-size:1.4rem;font-variant-numeric:tabular-nums}.stat span{display:block;font-size:.8rem;color:var(--ink-soft)}
.menutoggle{display:none}
@media (max-width:820px){.app{grid-template-columns:1fr}.side{position:fixed;inset:0 40% 0 0;z-index:20;transform:translateX(-100%);transition:transform .2s;max-width:340px}.app.nav-open .side{transform:none;box-shadow:0 0 0 100vmax rgba(0,0,0,.4)}.menutoggle{display:inline-flex;position:fixed;top:10px;left:10px;z-index:15;background:var(--accent);color:#fff;border:0;border-radius:10px;padding:8px 12px;font:inherit;font-weight:600;cursor:pointer;box-shadow:var(--shadow)}.main .wrap{padding-top:56px}}
@media print{.side,.menutoggle,.skip{display:none}.app{display:block;height:auto}.doc[hidden]{display:none}}
"""
app = f'''<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Çocuk GE Algoritma Uygulaması</title><style>{STYLE_INNER}{app_css}</style></head><body>
<a class="skip" href="#main">İçeriğe atla</a>
<button class="menutoggle" id="menu" aria-label="Algoritma listesini aç">☰ Algoritmalar</button>
<div class="app" id="app"><aside class="side"><div class="top">
<div class="brandrow"><div class="brand">Klinik Karar Uygulaması<b>Çocuk Gastroenterolojisi</b></div>
<button class="themebtn" id="theme" aria-label="Aydınlık/karanlık tema değiştir" title="Tema">◐</button></div>
<input class="search" id="q" type="search" placeholder="Ara: reflü, kanama, Wilson, ALT…" autocomplete="off" aria-label="Algoritma ara" aria-controls="nav">
<div class="chips" id="chips" role="group" aria-label="Filtreler">{appchips}</div>
<div class="recents" id="recents" hidden></div>
<div class="sr" id="live" aria-live="polite"></div></div>
<nav class="navlist" id="nav" aria-label="Algoritma listesi">{navhtml}</nav></aside>
<main class="main" id="main" tabindex="-1"><div class="welcome" id="welcome"><h1>Çocuk Gastroenterolojisi — Algoritma Uygulaması</h1>
<p>{total} uzman-düzeyi tanı-tetkik-tedavi-izlem algoritması tek uygulamada; {emerg_count}'inde kırmızı bayrak bölümü var (🚨 Aciller ile süzün). Soldan arayın veya seçin.</p>
<div class="stats">{stats}</div>
<p style="margin-top:22px;font-size:.82rem">Eğitim ve hızlı başvuru amaçlıdır; kılavuz ve yerel protokollerin yerine geçmez. Dozları doğrulayın.</p></div>
{docshtml}</main></div><script>
const nav=document.getElementById('nav'),q=document.getElementById('q'),chips=document.getElementById('chips'),main=document.getElementById('main'),welcome=document.getElementById('welcome'),app=document.getElementById('app'),live=document.getElementById('live');
const items=[...nav.querySelectorAll('.navitem')],groups=[...nav.querySelectorAll('.navgroup')],docs=[...main.querySelectorAll('.doc')];let filter='all';
function norm(s){{return (s||'').toLowerCase().replace(/ç/g,'c').replace(/ğ/g,'g').replace(/ı/g,'i').replace(/ö/g,'o').replace(/ş/g,'s').replace(/ü/g,'u');}}
function show(slug,push){{docs.forEach(d=>d.hidden=(d.id!=='a-'+slug));welcome.hidden=!!slug;items.forEach(b=>{{const on=b.dataset.slug===slug;b.classList.toggle('active',on);if(on)b.setAttribute('aria-current','page');else b.removeAttribute('aria-current');}});main.scrollTop=0;app.classList.remove('nav-open');
  if(slug){{if(push!==false&&location.hash!=='#'+slug)history.pushState(null,'','#'+slug);pushRecent(slug);const h=document.querySelector('#a-'+CSS.escape(slug)+' h1');if(h){{h.setAttribute('tabindex','-1');h.focus({{preventScroll:true}});}}else main.focus();}}
}}
nav.addEventListener('click',e=>{{const b=e.target.closest('.navitem');if(b)show(b.dataset.slug);}});
function applyFilter(){{const term=norm(q.value.trim());let n=0;items.forEach(b=>{{const okCat=(filter==='all')||(filter==='emerg'?b.dataset.emerg==='1':b.closest('.navgroup').dataset.cat===filter);const ok=okCat&&(!term||norm(b.dataset.search).includes(term));b.style.display=ok?'':'none';if(ok)n++;}});groups.forEach(g=>{{const any=[...g.querySelectorAll('.navitem')].some(b=>b.style.display!=='none');g.style.display=any?'':'none';}});live.textContent=n+' algoritma';}}
q.addEventListener('input',applyFilter);
chips.addEventListener('click',e=>{{const c=e.target.closest('.chip');if(!c)return;filter=c.dataset.filter;[...chips.children].forEach(x=>x.classList.toggle('active',x===c));applyFilter();}});
document.getElementById('menu').addEventListener('click',()=>app.classList.toggle('nav-open'));
// tema
const root=document.documentElement,tbtn=document.getElementById('theme');
(function(){{const s=localStorage.getItem('ge-theme');if(s)root.setAttribute('data-theme',s);}})();
tbtn.addEventListener('click',()=>{{const cur=root.getAttribute('data-theme')||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light');const next=cur==='dark'?'light':'dark';root.setAttribute('data-theme',next);localStorage.setItem('ge-theme',next);}});
// son bakılanlar
const recents=document.getElementById('recents');
function titleOf(s){{const b=nav.querySelector('.navitem[data-slug="'+s+'"] .nt');return b?b.textContent.trim():s;}}
function readRecents(){{try{{return JSON.parse(localStorage.getItem('ge-recents')||'[]');}}catch(_){{return [];}}}}
function renderRecents(){{let a=readRecents().filter(s=>document.getElementById('a-'+s));if(!a.length){{recents.hidden=true;recents.innerHTML='';return;}}recents.hidden=false;recents.innerHTML='<span class="rl">Son:</span>'+a.slice(0,6).map(s=>'<button class="rchip" data-slug="'+s+'">'+titleOf(s).replace(/&/g,'&amp;').replace(/</g,'&lt;')+'</button>').join('');}}
function pushRecent(slug){{let a=[slug].concat(readRecents().filter(s=>s!==slug)).slice(0,6);localStorage.setItem('ge-recents',JSON.stringify(a));renderRecents();}}
recents.addEventListener('click',e=>{{const b=e.target.closest('.rchip');if(b)show(b.dataset.slug);}});
// klavye
function visibleItems(){{return items.filter(b=>b.style.display!=='none');}}
document.addEventListener('keydown',e=>{{if(e.key==='/'&&!/^(INPUT|TEXTAREA)$/.test(e.target.tagName)){{e.preventDefault();q.focus();q.select();return;}}if(e.key==='ArrowDown'&&e.target===q){{const v=visibleItems();if(v.length){{e.preventDefault();v[0].focus();}}}}}});
nav.addEventListener('keydown',e=>{{const v=visibleItems();const i=v.indexOf(document.activeElement);if(i<0)return;if(e.key==='ArrowDown'){{e.preventDefault();(v[i+1]||v[0]).focus();}}else if(e.key==='ArrowUp'){{e.preventDefault();(i===0?q:v[i-1]).focus();}}}});
// geri tuşu / derin bağlantı
window.addEventListener('popstate',()=>{{const s=location.hash.replace('#','');if(s&&document.getElementById('a-'+s))show(s,false);else{{docs.forEach(d=>d.hidden=true);welcome.hidden=false;items.forEach(b=>{{b.classList.remove('active');b.removeAttribute('aria-current');}});}}}});
renderRecents();applyFilter();
const start=location.hash.replace('#','');if(start&&document.getElementById('a-'+start))show(start,false);
</script></body></html>'''
open(os.path.join(D,"app.html"),"w",encoding="utf-8").write(app)

print(f"build.py OK — {total} algoritma ({emerg_count} acil) · index.html + app.html güncellendi"
      + (f" · yeni: {', '.join(extra)}" if extra else ""))
