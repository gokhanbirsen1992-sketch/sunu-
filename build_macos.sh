#!/usr/bin/env bash
# ============================================================
#  Word2PDF - bağımsız uygulama oluşturma (macOS)
#  Çalıştır:  bash build_macos.sh
#  dist/Word2PDF.app üretir (çift tıklanabilir).
# ============================================================
set -e

echo "Gerekli paketler kuruluyor..."
python3 -m pip install --upgrade pip
python3 -m pip install pyinstaller python-docx reportlab click

echo
echo "Uygulama oluşturuluyor (birkaç dakika sürebilir)..."
pyinstaller --noconfirm --onefile --windowed --name Word2PDF \
  --collect-all docx --collect-all reportlab \
  word2pdf_app.pyw

echo
echo "============================================================"
echo " Bitti!  Uygulama:  dist/Word2PDF.app"
echo " (Açarken 'tanımlanamayan geliştirici' uyarısı çıkarsa:"
echo "  sağ tık → Aç, ya da Sistem Ayarları → Gizlilik ve Güvenlik.)"
echo "============================================================"
