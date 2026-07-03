"""[n] atıf işaretleri: doğrulama, yeniden numaralama, APA metin-içi dönüşüm.

LLM'ler yalnızca [n] işaretleriyle atıf yapar; yazar-yıl dönüşümünü bu modül (kod) yapar.
Böylece uydurma atıf yapısal olarak engellenir.
"""
from __future__ import annotations

import re

from app.models import Reference, ValidationIssue

MARKER_RE = re.compile(r"\[(\d+(?:\s*,\s*\d+)*)\]")
# LLM'in işaret sistemi dışında uydurabileceği yazar-yıl atıfı kalıpları
FAKE_CITATION_RE = re.compile(
    r"\((?:e\.g\.,?\s*)?[A-ZÇĞİÖŞÜ][\wçğıöşü]+(?:\s+(?:et\s+al\.|vd\.|ve\s+ark\.|&\s+[A-ZÇĞİÖŞÜ][\wçğıöşü]+))?,?\s+(?:19|20)\d{2}[a-z]?\)"
)


def extract_marker_ids(text: str) -> list[int]:
    ids: list[int] = []
    for m in MARKER_RE.finditer(text):
        for part in m.group(1).split(","):
            ids.append(int(part.strip()))
    return ids


def validate_citations(text: str, valid_ids: set[int], section: str = "") -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for marker_id in sorted(set(extract_marker_ids(text))):
        if marker_id not in valid_ids:
            issues.append(
                ValidationIssue(
                    severity="block", target=section,
                    message=f"Geçersiz kaynak numarası [{marker_id}] kullanılmış; geçerli numaralar: "
                    + (f"1–{max(valid_ids)}" if valid_ids else "yok"),
                )
            )
    for m in FAKE_CITATION_RE.finditer(text):
        issues.append(
            ValidationIssue(
                severity="block", target=section,
                message=f"İşaret sistemi dışında yazar-yıl atıfı tespit edildi: “{m.group(0)}”. "
                "Yalnızca [n] işaretleri kullanılmalı.",
            )
        )
    return issues


def renumber(sections_in_order: list[tuple[str, str]], references: list[Reference]) -> tuple[dict[str, str], list[Reference]]:
    """Atıfları metindeki görünüm sırasına göre yeniden numaralar; atıfsız kaynakları eler."""
    by_id = {r.id: r for r in references}
    order: list[int] = []
    for _, text in sections_in_order:
        for marker_id in extract_marker_ids(text):
            if marker_id in by_id and marker_id not in order:
                order.append(marker_id)
    old_to_new = {old: i + 1 for i, old in enumerate(order)}

    def _replace(m: re.Match) -> str:
        ids = [int(p.strip()) for p in m.group(1).split(",")]
        kept = [old_to_new[i] for i in ids if i in old_to_new]
        return f"[{', '.join(str(i) for i in sorted(set(kept)))}]" if kept else ""

    new_sections = {name: MARKER_RE.sub(_replace, text) for name, text in sections_in_order}
    new_refs = []
    for old_id in order:
        r = by_id[old_id].model_copy()
        r.id = old_to_new[old_id]
        new_refs.append(r)
    return new_sections, new_refs


def _intext_label(ref: Reference, lang: str) -> str:
    def last(full: str) -> str:
        parts = [p for p in full.replace(",", " ").split() if p]
        return parts[-1] if parts else full

    year = str(ref.year) if ref.year else ("t.y." if lang == "tr" else "n.d.")
    names = [last(a) for a in ref.authors if a]
    if not names:
        title_short = ref.title[:30] + ("…" if len(ref.title) > 30 else "")
        return f"“{title_short}”, {year}"
    if len(names) == 1:
        return f"{names[0]}, {year}"
    if len(names) == 2:
        joiner = " ve " if lang == "tr" else " & "
        return f"{names[0]}{joiner}{names[1]}, {year}"
    suffix = " vd." if lang == "tr" else " et al."
    return f"{names[0]}{suffix}, {year}"


def to_intext(text: str, references: list[Reference], lang: str) -> str:
    """[1, 3] → (Smith, 2020; Kaya vd., 2021)"""
    by_id = {r.id: r for r in references}

    def _replace(m: re.Match) -> str:
        ids = [int(p.strip()) for p in m.group(1).split(",")]
        labels = [_intext_label(by_id[i], lang) for i in ids if i in by_id]
        return f"({'; '.join(labels)})" if labels else ""

    out = MARKER_RE.sub(_replace, text)
    return re.sub(r" {2,}", " ", out)
