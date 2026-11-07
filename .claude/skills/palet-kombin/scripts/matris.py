#!/usr/bin/env python3
"""Ürün × renk matrisini data/palet.json'dan okuyup PNG üretir.
Kullanım: python3 matris.py [cikti.png]
"""
import json, sys, os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, "..", "data", "palet.json"), encoding="utf-8"))
F = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"; FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
out = sys.argv[1] if len(sys.argv) > 1 else "matris.png"

colors = [(c, D["renkler"][c]) for c in D["renk_sirasi"]]
order = list(D["matris"].keys())
cw, rh, x0, y0 = 78, 46, 230, 200
W = x0 + cw * len(colors) + 40; H = y0 + rh * len(order) + 110
img = Image.new("RGB", (W, H), "#F6F3EC"); d = ImageDraw.Draw(img)
d.text((40, 26), f"{D['palet']} · Ürün × Renk Matrisi", font=ImageFont.truetype(FB, 30), fill="#1E1E1E")
d.text((40, 66), "Yeşil = ideal   Sarı = olabilir   Kırmızı = yasak.   Satırdan istediğin yeşil/sarı rengi seç.", font=ImageFont.truetype(F, 16), fill="#555")
s = D["sayim"]
d.text((40, 90), f"Sayım: hastanede {' + '.join(s['hastane_kapsam'])} içinde vurgu aile en fazla {s['hastane_vurgu_max']} parça; gömlekte en az {s['gomlek_min_ekru']} ekru.", font=ImageFont.truetype(F, 16), fill="#555")
for j, (cn, hx) in enumerate(colors):
    x = x0 + j * cw
    d.rounded_rectangle((x + 4, y0 - 80, x + cw - 4, y0 - 36), radius=6, fill=hx, outline="#C9C2B4")
    words = cn.split("/") if "/" in cn else cn.split(" ")
    for k, wd in enumerate(words[:2]):
        d.text((x + 6, y0 - 32 + k * 14), wd, font=ImageFont.truetype(FB, 12), fill="#1E1E1E")
sym = {"I": ("#2E7D32", "#E3F1E4", "✓"), "O": ("#9A6B00", "#FBF0D0", "○"), "X": ("#A33A33", "#F6DEDC", "✗")}
for i, p in enumerate(order):
    y = y0 + i * rh
    d.rectangle((40, y, W - 40, y + rh - 4), fill="#FFFFFF" if i % 2 == 0 else "#F9F6EF")
    d.text((48, y + 13), p, font=ImageFont.truetype(FB, 16), fill="#1E1E1E")
    row = D["matris"][p]
    for j, (cn, hx) in enumerate(colors):
        fg, bg, t = sym[row[j]]
        x = x0 + j * cw
        d.rounded_rectangle((x + 6, y + 5, x + cw - 6, y + rh - 9), radius=6, fill=bg)
        d.text((x + cw // 2 - 7, y + 9), t, font=ImageFont.truetype(FB, 20), fill=fg)
y = y0 + len(order) * rh + 16
for k, g in enumerate(D["gerekce"].values()):
    d.text((40, y + k * 22), g, font=ImageFont.truetype(F, 14), fill="#555")
img.save(out); print(out, img.size)
