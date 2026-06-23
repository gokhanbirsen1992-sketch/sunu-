"""Resim -> PDF dönüştürücü için komut satırı arayüzü.

Kullanım örnekleri:

    # Tek tek resimleri sırayla birleştir
    python -m img2pdf.cli foto1.jpg foto2.png foto3.jpg -o sonuc.pdf

    # Bir klasördeki tüm resimleri birleştir
    python -m img2pdf.cli ./fotograflarim -o albums.pdf
"""

from __future__ import annotations

import argparse
import sys

from .converter import pdfe_cevir


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="img2pdf",
        description="Fotoğrafları (JPG/PNG/...) tek bir PDF dosyasına çevirir.",
    )
    parser.add_argument(
        "girdiler",
        nargs="+",
        metavar="RESIM_veya_KLASOR",
        help="Resim dosyaları ve/veya resim içeren klasörler.",
    )
    parser.add_argument(
        "-o",
        "--cikti",
        default="cikti.pdf",
        help="Oluşturulacak PDF dosyasının adı (varsayılan: cikti.pdf).",
    )
    parser.add_argument(
        "-q",
        "--kalite",
        type=int,
        default=90,
        help="JPEG sıkıştırma kalitesi 1-100 (varsayılan: 90).",
    )
    args = parser.parse_args(argv)

    try:
        sonuc = pdfe_cevir(args.girdiler, args.cikti, args.kalite)
    except (FileNotFoundError, ValueError) as hata:
        print(f"Hata: {hata}", file=sys.stderr)
        return 1

    print(f"✅ PDF oluşturuldu: {sonuc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
