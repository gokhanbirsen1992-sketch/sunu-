#!/usr/bin/env python3
"""Seçilmiş dolabı (ref/dolap.json) PNG liste olarak çizer.
Kullanım: python3 liste.py [cikti.png]
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
P = json.load(open(os.path.join(HERE, "..", "ref", "palet.json"), encoding="utf-8"))
W = json.load(open(os.path.join(HERE, "..", "ref", "dolap.json"), encoding="utf-8"))
C = P["renkler"]
F = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"; FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
out = sys.argv[1] if len(sys.argv) > 1 else "liste.png"
ft = ImageFont.truetype(F, 15); fb = ImageFont.truetype(FB, 17); fh = ImageFont.truetype(FB, 14)

def wrap(t, font, width):
    res, cur = [], ""
    for w in t.split():
        test = (cur + " " + w).strip()
        if font.getlength(test) <= width: cur = test
        else: res.append(cur); cur = w
    if cur: res.append(cur)
    return res or [""]

def lum(hx):
    r, g, b = int(hx[1:3], 16), int(hx[3:5], 16), int(hx[5:7], 16); return .299 * r + .587 * g + .114 * b

Wd = 1640
X = {"no": 48, "sw": 100, "urun": 250, "renk": 430, "alt": 610, "sart": 960, "tur": Wd - 150, "box": Wd - 76}
w_alt = X["sart"] - X["alt"] - 16; w_sart = X["tur"] - X["sart"] - 16
rows = []
for g in W["giysi"]:
    la = wrap(" · ".join(g["alt"]) if g["alt"] else "—", ft, w_alt); ls = wrap(g["sart"] or "—", ft, w_sart)
    rows.append((g, la, ls, max(len(la), len(ls), 2) * 20 + 16))
acc = []
for a in W["aksesuar"]:
    la = wrap(a["alt"] or "—", ft, w_alt + w_sart)
    acc.append((a, la, max(len(la), 2) * 20 + 16))
H = 150 + 40 + sum(h + 5 for *_, h in rows) + 80 + sum(h + 5 for *_, h in acc) + 40 + len(W["zincir_kurallar"]) * 22 + 60
img = Image.new("RGB", (Wd, H), "#F6F3EC"); d = ImageDraw.Draw(img)
d.text((40, 26), f"{P['palet']} · Seçilmiş Dolap · {len(W['giysi'])} giysi + aksesuar", font=ImageFont.truetype(FB, 30), fill="#1E1E1E")
d.text((40, 68), "Seçim yoksa alternatife in (soldan sağa). Durum: alindi / mevcut / eksik. Dolu kare: dolapta.", font=ImageFont.truetype(F, 16), fill="#555")
m = P["magaza_modu"]["sartlar"]
d.text((40, 92), "Mağazada yalnızca 3 şart: " + "  ·  ".join(m), font=ImageFont.truetype(F, 15), fill="#8A2A2A")
y = 140
for k, t in [("no", "NO"), ("urun", "ÜRÜN"), ("renk", "SEÇİM"), ("alt", "ALTERNATİF"), ("sart", "ŞART"), ("tur", "DURUM")]:
    d.text((X[k], y), t, font=fh, fill="#777")
y += 30
for i, (g, la, ls, h) in enumerate(rows):
    d.rounded_rectangle((40, y, Wd - 40, y + h), radius=8, fill="#FFFFFF" if i % 2 == 0 else "#F9F6EF", outline="#E3DDD0")
    d.text((X["no"], y + 10), str(g["no"]), font=fb, fill="#1E1E1E")
    hx = C.get(g["renk"], "#D9D3C6")
    d.rounded_rectangle((X["sw"], y + 8, X["sw"] + 130, y + h - 8), radius=6, fill=hx, outline="#C9C2B4")
    d.text((X["urun"], y + 10), g["urun"], font=fb, fill="#1E1E1E")
    d.text((X["renk"], y + 11), g["renk"], font=ft, fill="#2E5A2E")
    for k, l in enumerate(la): d.text((X["alt"], y + 11 + k * 20), l, font=ft, fill="#444")
    for k, l in enumerate(ls): d.text((X["sart"], y + 11 + k * 20), l, font=ft, fill="#8A2A2A" if "değil" in l or "yok" in l or "AYNI" in l else "#444")
    du = g.get("durum")
    d.text((X["tur"] - 14, y + 11), du if du else f"tur {g['tur']}", font=ft, fill={"eksik": "#A33A33", "alindi": "#2E7D32", "mevcut": "#555"}.get(du, "#1E1E1E"))
    d.rectangle((X["box"], y + h // 2 - 10, X["box"] + 20, y + h // 2 + 10), outline="#888", width=2, fill="#2E7D32" if du in ("alindi", "mevcut") else None)
    y += h + 5
y += 20; d.line((40, y, Wd - 40, y), fill="#D9D3C6", width=2); d.text((40, y + 12), "AKSESUAR", font=ImageFont.truetype(FB, 20), fill="#1E1E1E"); y += 50
for i, (a, la, h) in enumerate(acc):
    d.rounded_rectangle((40, y, Wd - 40, y + h), radius=8, fill="#FFFFFF" if i % 2 == 0 else "#F9F6EF", outline="#E3DDD0")
    d.text((X["sw"], y + 10), a["urun"], font=fb, fill="#1E1E1E")
    d.text((X["renk"], y + 11), a["renk"], font=ft, fill="#2E5A2E")
    for k, l in enumerate(la): d.text((X["alt"] + 120, y + 11 + k * 20), l, font=ft, fill="#444")
    d.rectangle((X["box"], y + h // 2 - 10, X["box"] + 20, y + h // 2 + 10), outline="#888", width=2)
    y += h + 5
y += 20; d.line((40, y, Wd - 40, y), fill="#D9D3C6", width=2); d.text((40, y + 12), "ZİNCİR KURALLAR", font=ImageFont.truetype(FB, 18), fill="#1E1E1E"); y += 44
for k in W["zincir_kurallar"]:
    d.text((40, y), "•  " + k, font=ft, fill="#333"); y += 22
img.save(out); print(out, img.size)
