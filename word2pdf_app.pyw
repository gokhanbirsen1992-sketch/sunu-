#!/usr/bin/env python3
"""word2pdf masaüstü uygulaması.

Çift tıklayıp çalıştır (Windows/macOS'ta konsol penceresi açılmaz).
Komut satırından da çalışır:  python word2pdf_app.pyw
"""

import os
import sys

# Çift tıklamayla farklı bir çalışma dizininden açılsa bile 'word2pdf'
# paketini bulabilmek için bu dosyanın klasörünü yola ekle.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from word2pdf.gui import main

if __name__ == "__main__":
    main()
