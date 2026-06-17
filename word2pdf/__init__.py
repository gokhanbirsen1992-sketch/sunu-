"""word2pdf — Word (.docx/.doc) dosyalarını PDF'e dönüştüren basit araç.

Kullanım (kod içinden):

    from word2pdf import convert_file
    convert_file("rapor.docx")                 # -> rapor.pdf
    convert_file("rapor.docx", "ciktilar/r.pdf", engine="libreoffice")

Kullanım (terminalden):

    python -m word2pdf rapor.docx
    python -m word2pdf belgeler/ -o pdfler/ -r
"""

from .converter import (
    ConversionError,
    convert_file,
    find_libreoffice,
    iter_word_files,
)

__all__ = [
    "ConversionError",
    "convert_file",
    "find_libreoffice",
    "iter_word_files",
]

__version__ = "1.0.0"
