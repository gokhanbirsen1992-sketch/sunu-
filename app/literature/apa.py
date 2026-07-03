"""APA 7 kaynakça biçimleme — deterministik, LLM'siz."""
from __future__ import annotations

from app.models import Reference


def _apa_author(full_name: str) -> str:
    """'Jane Q Doe' → 'Doe, J. Q.'"""
    parts = [p for p in full_name.replace(",", " ").split() if p]
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0]
    last = parts[-1]
    initials = " ".join(f"{p[0].upper()}." for p in parts[:-1])
    return f"{last}, {initials}"


def format_authors(authors: list[str]) -> str:
    formatted = [a for a in (_apa_author(x) for x in authors) if a]
    if not formatted:
        return ""
    if len(formatted) == 1:
        return formatted[0]
    if len(formatted) <= 20:
        return ", ".join(formatted[:-1]) + ", & " + formatted[-1]
    return ", ".join(formatted[:19]) + ", ... " + formatted[-1]


def format_reference_runs(ref: Reference) -> list[tuple[str, bool]]:
    """(metin, italik_mi) çiftleri — docx üreticisi italik dergi adı için kullanır."""
    runs: list[tuple[str, bool]] = []
    authors = format_authors(ref.authors)
    year = f"({ref.year})." if ref.year else "(t.y.)."
    head = f"{authors} {year} {ref.title.rstrip('.')}." if authors else f"{ref.title.rstrip('.')}. {year}"
    runs.append((head + " ", False))
    if ref.journal:
        runs.append((ref.journal.rstrip(",. "), True))
        tail = ""
        if ref.volume:
            tail += ", "
            runs.append((tail, False))
            runs.append((ref.volume, True))
            tail = ""
            if ref.issue:
                runs.append((f"({ref.issue})", False))
        if ref.pages:
            runs.append((f", {ref.pages}", False))
        runs.append((". ", False))
    if ref.doi:
        runs.append((f"https://doi.org/{ref.doi}", False))
    elif ref.pmid:
        runs.append((f"https://pubmed.ncbi.nlm.nih.gov/{ref.pmid}/", False))
    return runs


def format_reference_text(ref: Reference) -> str:
    return "".join(text for text, _ in format_reference_runs(ref)).strip()
