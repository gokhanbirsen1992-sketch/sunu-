#!/usr/bin/env python3
"""Matris ve seçilmiş dolap denetimi. Çıkış kodu 0 = temiz, 1 = ihlal var.
Kullanım: python3 denetim.py
Denetimler:
  A) matris kural ihlali (yüz, koyu alt, deri tek ton, mavi yalnızca denim, büyük yüzeyde vurgu)
  B) komşu ton çelişkisi (aynı ailede bitişik iki tonun biri I diğeri X)
  C) dolap: her parçanın matris hücresi X olmamalı; vurgu sayımı; ekru gömlek sayısı; deri tonu tekliği
  D) dolap: hastane içi kombin sayısı ve parça başına kullanım (kullanılmayan parça = uyarı)
"""
import json, os, sys, itertools

HERE = os.path.dirname(os.path.abspath(__file__))
P = json.load(open(os.path.join(HERE, "..", "ref", "palet.json"), encoding="utf-8"))
W = json.load(open(os.path.join(HERE, "..", "ref", "dolap.json"), encoding="utf-8"))
R = P["renk_sirasi"]; M = P["matris"]; ix = {c: i for i, c in enumerate(R)}
vurgu = set(P["roller"]["vurgu"]); bad = []

# A
for u in ["Gömlek", "Tişört", "Örgü polo"]:
    bad += [f"A yüz: {u}/{c}" for c in ["Camel", "Taupe", "Taba"] if M[u][ix[c]] != "X"]
for u in ["Pantolon", "Kaban", "Denim", "Ayakkabı deri", "Kemer/çanta"]:
    bad += [f"A koyu alt/deri: {u}/{c}" for c in ["Ekru", "Kum/krem", "Camel"] + sorted(vurgu) if M[u][ix[c]] != "X"]
bad += [f"A mavi: {u}/Koyu indigo" for u in M if u != "Denim" and M[u][ix["Koyu indigo"]] != "X"]
for u in ["Hırka", "Blazer"]:
    bad += [f"A büyük yüzeyde vurgu ideal: {u}/{c}" for c in vurgu if M[u][ix[c]] == "I"]
# B
fams = [["Ekru", "Kum/krem"], ["Koyu yeşil", "Koyu zeytin", "Zeytin", "Haki"], ["Çikolata", "Koyu kahve", "Tütün", "Taba", "Camel"],
        ["Pas", "Kiremit"], ["Bordo", "Şarap"], ["Hardal", "Okra"]]
rank = {"I": 2, "O": 1, "X": 0}
for u, row in M.items():
    for f in fams:
        for a, b in zip(f, f[1:]):
            if abs(rank[row[ix[a]]] - rank[row[ix[b]]]) >= 2: bad.append(f"B komşu ton: {u} {a}={row[ix[a]]} {b}={row[ix[b]]}")
# C
G = W["giysi"]
for g in G:
    if g["matris"] and M[g["matris"]][ix[g["renk"]]] == "X": bad.append(f"C yasak hücre: {g['urun']}/{g['renk']}")
s = P["sayim"]
nv = sum(g["renk"] in vurgu for g in G if g["matris"] in s["hastane_kapsam"])
if nv > s["hastane_vurgu_max"]: bad.append(f"C vurgu {nv} > {s['hastane_vurgu_max']}")
if sum(g["urun"] == "Gömlek" and g["renk"] == "Ekru" for g in G) < s["gomlek_min_ekru"]: bad.append("C ekru gömlek yetersiz")
deri = {g["renk"] for g in G if g["matris"] in ("Ayakkabı deri", "Kemer/çanta")}
if len(deri) > 1: bad.append(f"C deri tonu tek değil: {deri}")
# D
aile = {"Ekru": "ekru", "Kum/krem": "ekru", "Koyu yeşil": "yesil", "Koyu zeytin": "yesil", "Zeytin": "yesil", "Haki": "yesil",
        "Çikolata": "kahve", "Koyu kahve": "kahve"}
fam = lambda c: aile.get(c, c)
ic = [g for g in G if g["matris"] in ("Gömlek", "Örgü polo")]
orta = [None] + [g for g in G if g["matris"] in ("Kazak", "Hırka")]
pant = [g for g in G if g["matris"] == "Pantolon"]
seen = set(); use = {}
for i, o, p in itertools.product(ic, orta, pant):
    seq = [i["renk"]] + ([o["renk"]] if o else []) + [p["renk"]]
    f = [fam(c) for c in seq]
    if any(f[k] == f[k + 1] for k in range(len(f) - 1)): continue
    if sum(c in vurgu for c in seq) > 1: continue
    key = (i["urun"], i["renk"], o["urun"] if o else "", o["renk"] if o else "", p["renk"])
    if key in seen: continue
    seen.add(key)
    for x in (i, o, p):
        if x: use[(x["urun"], x["renk"])] = use.get((x["urun"], x["renk"]), 0) + 1  # aynı parçadan iki adet tek sayılır
print(f"Hastane içi kombin (blazersiz, tişörtsüz): {len(seen)}  | vurgu parça: {nv}/{s['hastane_vurgu_max']}")
for g in ic + orta[1:] + pant:
    n = use.get((g["urun"], g["renk"]), 0)
    print(f"  {g['no']:>2} {g['urun']:10} {g['renk']:12} {n}")
    if n == 0: bad.append(f"D kullanılmayan parça: {g['urun']}/{g['renk']}")
print("İHLAL:" if bad else "Temiz: 0 ihlal")
for b in bad: print("  ", b)
sys.exit(1 if bad else 0)
