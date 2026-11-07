#!/usr/bin/env python3
"""5 kombin kartı üretir. Girdi JSON (stdin veya dosya):
{"baslik": "...", "kombinler": [{"ad": "1 · Hastane", "katmanlar": [["ekru gömlek","Ekru"], ...], "pantolon": ["taupe pamuk","Taupe"], "ayakkabi": ["kahve loafer","Kahve deri"]}, ...]}
Renk adları data/palet.json'daki anahtarlardır.
Kullanım: python3 kombin.py girdi.json cikti.png
"""
import json, sys, os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
P = json.load(open(os.path.join(HERE, "..", "data", "palet.json"), encoding="utf-8"))
C = P["renkler"]; vurgu = set(P["roller"]["vurgu"])
F = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"; FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
src = json.load(open(sys.argv[1], encoding="utf-8")) if len(sys.argv) > 1 and sys.argv[1] != "-" else json.load(sys.stdin)
out = sys.argv[2] if len(sys.argv) > 2 else "kombin.png"
days = src["kombinler"]

def lum(hx):
    r, g, b = int(hx[1:3], 16), int(hx[3:5], 16), int(hx[5:7], 16); return .299 * r + .587 * g + .114 * b

col_w, gap = 245, 14
W = max(1340, 40 * 2 + len(days) * (col_w + gap) - gap); H = 720
img = Image.new("RGB", (W, H), "#F6F3EC"); d = ImageDraw.Draw(img)
d.text((40, 28), src.get("baslik", "Kombinler"), font=ImageFont.truetype(FB, 32), fill="#1E1E1E")
d.text((40, 72), "Yukarıdan aşağı: iç katman, orta/dış katman, pantolon, ayakkabı.  Kural: tek vurgu, bitişik aynı renk yok, koyu alt.", font=ImageFont.truetype(F, 17), fill="#555")
heights = {1: [250], 2: [70, 180], 3: [55, 95, 100], 4: [45, 60, 70, 75]}
for i, k in enumerate(days):
    x = 40 + i * (col_w + gap); y0 = 120
    d.rounded_rectangle((x, y0, x + col_w, H - 40), radius=14, fill="#FFFFFF", outline="#D9D3C6")
    d.text((x + 16, y0 + 14), k["ad"], font=ImageFont.truetype(FB, 22), fill="#1E1E1E")
    yy = y0 + 60
    layers = k["katmanlar"]
    for (name, ckey), h in zip(layers, heights[len(layers)]):
        hx = C[ckey]; tc = "#F6F3EC" if lum(hx) < 140 else "#1E1E1E"
        d.rounded_rectangle((x + 16, yy, x + col_w - 16, yy + h), radius=8, fill=hx, outline="#C9C2B4")
        d.text((x + 26, yy + 10), name, font=ImageFont.truetype(F, 16), fill=tc)
        if ckey in vurgu: d.text((x + 26, yy + 30), "vurgu", font=ImageFont.truetype(F, 13), fill=tc)
        yy += h + 4
    name, ckey = k["pantolon"]; hx = C[ckey]; tc = "#F6F3EC" if lum(hx) < 140 else "#1E1E1E"
    d.rounded_rectangle((x + 16, yy + 8, x + col_w - 16, yy + 178), radius=8, fill=hx, outline="#C9C2B4")
    d.text((x + 26, yy + 18), name, font=ImageFont.truetype(F, 16), fill=tc); yy += 182
    name, ckey = k["ayakkabi"]; hx = C[ckey]; tc = "#F6F3EC" if lum(hx) < 140 else "#1E1E1E"
    d.rounded_rectangle((x + 16, yy + 4, x + col_w - 16, yy + 38), radius=8, fill=hx, outline="#C9C2B4")
    d.text((x + 26, yy + 12), name, font=ImageFont.truetype(F, 15), fill=tc)
img.save(out); print(out, img.size)
