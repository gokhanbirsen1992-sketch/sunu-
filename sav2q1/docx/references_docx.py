"""Kaynakça biçimlendirme — Vancouver (varsayılan) ve APA-7.

Kaynak alanları YALNIZCA doğrulanmış evidence_store girdisinden gelir; yazar
metninden asla. Böylece atıf bilgileri uydurulamaz.
"""

from __future__ import annotations


def _authors_vancouver(authors: list[str]) -> str:
    if not authors:
        return ""
    if len(authors) <= 6:
        return ", ".join(authors)
    return ", ".join(authors[:6]) + ", et al"


def format_vancouver(entry: dict, n: int) -> str:
    """Tek bir kaynağı Vancouver biçiminde numaralı string olarak döndürür."""
    au = _authors_vancouver(entry.get("authors", []))
    title = (entry.get("title") or "").rstrip(".")
    journal = entry.get("journal", "")
    year = entry.get("year", "")
    vol = entry.get("volume", "")
    issue = entry.get("issue", "")
    pages = entry.get("pages", "")
    doi = entry.get("doi", "")

    cite = f"{n}. "
    if au:
        cite += f"{au}. "
    cite += f"{title}. "
    if journal:
        cite += f"{journal}. "
    loc = f"{year}"
    if vol:
        loc += f";{vol}"
        if issue:
            loc += f"({issue})"
    if pages:
        loc += f":{pages}"
    cite += loc + "."
    if doi:
        cite += f" doi:{doi}"
    return cite


def format_apa7(entry: dict, _n: int = 0) -> str:
    """Tek bir kaynağı APA-7 (yazar-tarih) biçiminde döndürür (seçenek)."""
    au = "; ".join(entry.get("authors", []))
    year = entry.get("year", "")
    title = entry.get("title", "")
    journal = entry.get("journal", "")
    vol = entry.get("volume", "")
    issue = entry.get("issue", "")
    pages = entry.get("pages", "")
    doi = entry.get("doi", "")
    out = f"{au} ({year}). {title} {journal}"
    if vol:
        out += f", {vol}"
        if issue:
            out += f"({issue})"
    if pages:
        out += f", {pages}"
    out += "."
    if doi:
        out += f" https://doi.org/{doi}"
    return out
