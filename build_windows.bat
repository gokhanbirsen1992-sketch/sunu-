@echo off
REM ============================================================
REM  Word2PDF - bagimsiz .exe olusturma (Windows)
REM  Bu dosyaya cift tikla. Tek bir Word2PDF.exe uretir.
REM  (Bilgisayarda Python kurulu olmali; cikan .exe icin gerekmez.)
REM ============================================================

echo Gerekli paketler kuruluyor...
python -m pip install --upgrade pip
python -m pip install pyinstaller python-docx reportlab click
if errorlevel 1 (
  echo.
  echo HATA: Python bulunamadi ya da paketler kurulamadi.
  echo Python'u kurun: https://www.python.org/downloads/  (PATH'e ekleyin)
  pause
  exit /b 1
)

echo.
echo EXE olusturuluyor (bu birkac dakika surebilir)...
pyinstaller --noconfirm --onefile --windowed --name Word2PDF ^
  --collect-all docx --collect-all reportlab ^
  word2pdf_app.pyw

echo.
echo ============================================================
echo  Bitti!  Uygulama:  dist\Word2PDF.exe
echo  Bu .exe'yi tek basina herhangi bir Windows'a kopyalayabilirsin.
echo ============================================================
pause
