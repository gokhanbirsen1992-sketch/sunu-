#!/usr/bin/env python3
"""Bütçe kalemlerini JSON'dan okur, EUR ve TRY toplamlarını hesaplar, Markdown tablo basar.

Kullanım:
    python3 butce_hesapla.py kalemler.json

kalemler.json biçimi:
{
  "kur": {"EUR_TRY": 49.12, "kaynak": "https://...", "tarih": "2026-10-20"},
  "yedek_oran": 0.10,
  "kalemler": [
    {"ad": "Uçuş (AYT–HAM gidiş-dönüş)", "eur": 310.0, "etiket": "[kesin]", "kaynak": "01-ucus.md"},
    {"ad": "Otel 6 gece", "eur": 540.0, "etiket": "[kesin]", "kaynak": "02-otel.md"}
  ]
}
Sayılar yalnızca JSON'dan gelir; betik hiçbir değer uydurmaz.
"""
import json
import sys


def main(path: str) -> int:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    kur = data["kur"]
    rate = float(kur["EUR_TRY"])
    yedek_oran = float(data.get("yedek_oran", 0.10))
    kalemler = data["kalemler"]

    ara_toplam = sum(float(k["eur"]) for k in kalemler)
    yedek = ara_toplam * yedek_oran
    toplam = ara_toplam + yedek

    print(f"Kur: 1 EUR = {rate:.4f} TRY (kaynak: {kur['kaynak']}, tarih: {kur['tarih']})")
    print()
    print("| Kalem | EUR | TRY | Etiket | Kaynak |")
    print("|---|---:|---:|---|---|")
    for k in kalemler:
        eur = float(k["eur"])
        print(f"| {k['ad']} | {eur:,.2f} | {eur * rate:,.0f} | {k.get('etiket', '')} | {k.get('kaynak', '')} |")
    print(f"| **Ara toplam** | **{ara_toplam:,.2f}** | **{ara_toplam * rate:,.0f}** | [çıkarım] | toplama |")
    print(f"| Yedek (%{yedek_oran * 100:.0f}) | {yedek:,.2f} | {yedek * rate:,.0f} | [çıkarım] | ara toplam × {yedek_oran} |")
    print(f"| **GENEL TOPLAM** | **{toplam:,.2f}** | **{toplam * rate:,.0f}** | [çıkarım] | ara toplam + yedek |")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
