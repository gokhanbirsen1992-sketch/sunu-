#!/usr/bin/env python3
"""Bağımsız istatistik analiz aracı.

Kullanım:
    python analyze.py veri.xlsx
    python analyze.py veri.sav --dv sonuc --lang en --out rapor.docx

PaperForge web uygulamasından (literatür taraması, makale yazımı, LLM) tamamen bağımsızdır.
Detaylar için: python analyze.py --help
"""
from standalone_stats.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
