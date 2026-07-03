"""Komut satırı arayüzü.

Kullanım:
    python -m megastat veri.sav
    python -m megastat veri.csv -o rapor.xlsx
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from megastat.engine import analyze_dataframe
from megastat.loader import load_dataset
from megastat.report import excel_raporu, metin_ozeti


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="megastat",
        description="MegaStat — veri dosyanızdaki HER istatistiği hesaplar, Excel raporu üretir.",
    )
    parser.add_argument("dosya", help="Veri dosyası (.csv, .xlsx, .xls, .sav, .zsav)")
    parser.add_argument(
        "-o", "--cikti", default=None,
        help="Excel rapor dosyası (varsayılan: <veri adı>_megastat.xlsx)",
    )
    args = parser.parse_args(argv)

    veri_yolu = Path(args.dosya)
    cikti = Path(args.cikti) if args.cikti else veri_yolu.with_name(veri_yolu.stem + "_megastat.xlsx")

    print(f"Veri yükleniyor: {veri_yolu}")
    df = load_dataset(veri_yolu)
    print(f"Yüklendi: {len(df)} satır × {df.shape[1]} sütun. Analiz başlıyor…")

    sonuc = analyze_dataframe(df)
    cikti.write_bytes(excel_raporu(sonuc))

    print()
    print(metin_ozeti(sonuc))
    print()
    print(f"Tam rapor yazıldı: {cikti}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
