"""Sayı token çıkarımı ve normalizasyonu — SAF (yalnız `re`).

Hem ledger inşası hem de `verify-numeric` AYNI çıkarıcıyı kullanır; böylece
yazarın defterdeki hazır string'den kopyaladığı her sayı, birebir eşleşir.

Normalizasyon: ondalık ayırıcı virgüle çevrilir (İngilizce '.' da kabul),
baştaki '+' atılır. Vancouver atıf imleri [12], [3-5], [1, 2] taranmadan önce
çıkarılır (atıf numarası sayı sanılmasın).
"""

from __future__ import annotations

import re

_CITES = re.compile(r"\[[\d\s,–\-]+\]")
_NUM = re.compile(r"[-+]?\d+(?:[.,]\d+)?")
_YEAR = re.compile(r"^(19|20)\d{2}$")

# İstatistik-dışı, her yerde kabul edilebilir sabitler (GA düzeyi, p eşikleri, %100 tabanı).
GLOBAL_WHITELIST: set[str] = {"90", "95", "99", "100", "0,05", "0,01", "0,001"}


def strip_citation_markers(text: str) -> str:
    return _CITES.sub(" ", text)


def normalize(tok: str) -> str:
    t = tok.strip().lstrip("+")
    t = t.replace(".", ",")
    return t


def extract_tokens(text: str, strip_cites: bool = True) -> list[str]:
    """Metindeki tüm sayı token'larını normalize edilmiş biçimde döndürür."""
    if strip_cites:
        text = strip_citation_markers(text)
    return [normalize(m.group()) for m in _NUM.finditer(text)]


def is_year(tok: str) -> bool:
    return bool(_YEAR.match(tok.strip()))
