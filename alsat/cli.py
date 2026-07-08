"""Komut satırı arayüzü: ``python -m alsat [--sembol BTCUSDT ETHUSDT] [-o rapor.xlsx]``"""

from __future__ import annotations

import argparse
from pathlib import Path

from alsat import dongu, rapor, veri


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="alsat",
        description="Literatür temelli al-sat indikatörü laboratuvarı: aday göstergeleri "
                    "walk-forward sınar, Reviewer 2 gibi denetler ve kabul kriterleri "
                    "sağlanana kadar düzeltme döngüsü işletir.",
    )
    ap.add_argument("--sembol", nargs="+", default=["BTCUSDT", "ETHUSDT"],
                    help="işlem çiftleri (vars. BTCUSDT ETHUSDT)")
    ap.add_argument("--csv", nargs="*", default=[],
                    help="ağ yerine yerel günlük OHLCV/kapanış CSV'leri (sembol=yol biçiminde)")
    ap.add_argument("--tur", type=int, default=5, help="en fazla tur sayısı (vars. 5)")
    ap.add_argument("--maliyet", type=float, default=20.0,
                    help="tek yön işlem maliyeti + kayma, baz puan (vars. 20)")
    ap.add_argument("--veri-dizini", default="data/alsat_cache",
                    help="indirilen verilerin önbellek dizini")
    ap.add_argument("--yenile", action="store_true", help="önbelleği yok say, yeniden indir")
    ap.add_argument("-o", "--cikti", default=None,
                    help="Excel rapor yolu (vars. alsat_rapor.xlsx)")
    args = ap.parse_args(argv)

    seriler = {}
    csv_esleme = dict(p.split("=", 1) for p in args.csv)
    for sembol in args.sembol:
        if sembol in csv_esleme:
            seriler[sembol] = veri.csv_yukle(csv_esleme[sembol])
            print(f"{sembol}: {len(seriler[sembol])} gün (CSV: {csv_esleme[sembol]})")
        else:
            seri, kaynak = veri.veri_getir(sembol, args.veri_dizini, yenile=args.yenile)
            seriler[sembol] = seri
            print(f"{sembol}: {len(seri)} gün, {seri.index[0].date()} → "
                  f"{seri.index[-1].date()} (kaynak: {kaynak})")

    sonuc = dongu.calistir(seriler, maliyet_bps=args.maliyet, maks_tur=args.tur)

    cikti = Path(args.cikti or "alsat_rapor.xlsx")
    cikti.write_bytes(rapor.excel_raporu(sonuc))
    print(rapor.metin_ozeti(sonuc))
    print(f"\nExcel raporu: {cikti}")
    return 0
