"""Deterministik doğrulayıcılar — LLM çıktısını kod ile denetler."""
from __future__ import annotations

import re

from app.manuscript.citations import validate_citations
from app.models import Finding, ValidationIssue

P_VALUE_RE = re.compile(r"p\s*[=<>]\s*\.?\d+(?:\.\d+)?")


def check_citations(text: str, valid_ids: set[int], section: str) -> list[ValidationIssue]:
    return validate_citations(text, valid_ids, section)


def check_min_length(text: str, min_words: int, section: str) -> list[ValidationIssue]:
    n = len(text.split())
    if n < min_words:
        return [
            ValidationIssue(
                severity="block", target=section,
                message=f"'{section}' bölümü çok kısa ({n} kelime; en az {min_words} beklenir).",
            )
        ]
    return []


def check_not_collapsed(original: str, edited: str, section: str) -> list[ValidationIssue]:
    """Dil düzenlemesi metni aşırı kısaltmamalı."""
    if len(original.split()) >= 30 and len(edited.split()) < 0.6 * len(original.split()):
        return [
            ValidationIssue(
                severity="block", target=section,
                message=f"Düzenleme '{section}' bölümünü aşırı kısaltmış; içerik korunmalı.",
            )
        ]
    return []


def check_markers_preserved(original: str, edited: str, section: str) -> list[ValidationIssue]:
    from app.manuscript.citations import extract_marker_ids

    before, after = set(extract_marker_ids(original)), set(extract_marker_ids(edited))
    if before != after:
        return [
            ValidationIssue(
                severity="block", target=section,
                message=f"Düzenleme '{section}' bölümündeki atıf işaretlerini değiştirmiş "
                f"(önce: {sorted(before)}, sonra: {sorted(after)}).",
            )
        ]
    return []


def check_pvalues_match(text: str, findings: list[Finding], section: str) -> list[ValidationIssue]:
    """Metinde geçen p-değerleri gerçek bulgulardan biriyle eşleşmeli (uydurma sayı tespiti)."""
    valid_ps: set[str] = set()
    for f in findings:
        for p in (f.p_value, f.p_adjusted):
            if p is None:
                continue
            valid_ps.add(f"{p:.3f}".replace("0.", "."))
            valid_ps.add(f"{p:.2f}".replace("0.", "."))
    issues = []
    for m in P_VALUE_RE.finditer(text):
        expr = m.group(0)
        if "<" in expr:  # p < .001 gibi eşiksel ifadeler serbest
            continue
        num = re.search(r"\.?\d+(?:\.\d+)?$", expr)
        if num and num.group(0).lstrip("0") not in {v.lstrip("0") for v in valid_ps} and num.group(0) not in valid_ps:
            issues.append(
                ValidationIssue(
                    severity="warn", target=section,
                    message=f"'{section}' bölümündeki '{expr}' değeri bulgularla birebir eşleşmiyor.",
                )
            )
    return issues


def check_required_sections(sections: dict[str, str]) -> list[ValidationIssue]:
    required = ["intro", "methods", "results", "discussion", "limitations"]
    issues = []
    for key in required:
        if not sections.get(key, "").strip():
            issues.append(
                ValidationIssue(severity="block", target=key, message=f"Zorunlu bölüm eksik: {key}")
            )
    return issues
