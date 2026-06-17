#!/usr/bin/env bash
# ============================================================
#  Word2PDF - bağımsız uygulama oluşturma (Linux)
#  Çalıştır:  bash build_linux.sh
#  dist/word2pdf adlı tek dosyalık çalıştırılabilir üretir.
#
#  NOT: GUI için tkinter gerekir. Yoksa kurun:
#    Debian/Ubuntu:  sudo apt install python3-tk
#    Fedora:         sudo dnf install python3-tkinter
# ============================================================
set -e

echo "Gerekli paketler kuruluyor..."
python3 -m pip install --upgrade pip
python3 -m pip install pyinstaller python-docx reportlab click

echo
echo "Uygulama oluşturuluyor (birkaç dakika sürebilir)..."
pyinstaller --noconfirm --onefile --name word2pdf \
  --collect-all docx --collect-all reportlab \
  word2pdf_app.pyw

echo
echo "============================================================"
echo " Bitti!  Çalıştırılabilir:  dist/word2pdf"
echo " Çalıştırmak için:  ./dist/word2pdf"
echo "============================================================"
