"""Atıf işareti doğrulama/dönüştürme ve APA biçimleme."""
from __future__ import annotations

from app.literature.apa import format_reference_text
from app.manuscript.citations import (
    extract_marker_ids,
    renumber,
    to_intext,
    validate_citations,
)
from app.models import Reference


def _ref(i, authors, year=2020, title="A study of things", journal="J Test"):
    return Reference(id=i, authors=authors, year=year, title=title, journal=journal,
                     volume="12", issue="3", pages="45-67", doi=f"10.1000/x{i}")


def test_extract_and_validate_markers():
    text = "Önceki çalışmalar [1] ve [2, 3] bunu göstermiştir."
    assert extract_marker_ids(text) == [1, 2, 3]
    assert validate_citations(text, {1, 2, 3}) == []
    issues = validate_citations(text, {1, 2})
    assert any("[3]" in i.message for i in issues if i.severity == "block")


def test_fake_author_year_citation_blocked():
    text = "Bu daha önce gösterilmiştir (Smith, 2019)."
    issues = validate_citations(text, {1})
    assert any(i.severity == "block" for i in issues)
    text_tr = "Benzer bulgular vardır (Kaya vd., 2021)."
    assert any(i.severity == "block" for i in validate_citations(text_tr, {1}))


def test_renumber_prunes_and_reorders():
    refs = [_ref(1, ["Ali Veli"]), _ref(2, ["Ayşe Kaya"]), _ref(3, ["John Smith"])]
    sections = [("intro", "İlk iddia [3]. İkinci iddia [1]."), ("discussion", "Yine [3].")]
    new_sections, new_refs = renumber(sections, refs)
    assert [r.id for r in new_refs] == [1, 2]
    assert new_refs[0].authors == ["John Smith"]  # [3] ilk görünen → 1 oldu
    assert "[1]" in new_sections["intro"] and "[2]" in new_sections["intro"]
    assert "[3]" not in new_sections["intro"] + new_sections["discussion"]


def test_to_intext_conversion():
    refs = [_ref(1, ["John Smith"]), _ref(2, ["Ayşe Kaya", "Ali Veli", "Can Demir"])]
    out_en = to_intext("Prior work shows this [1, 2].", refs, "en")
    assert "(Smith, 2020; Kaya et al., 2020)" in out_en
    out_tr = to_intext("Önceki çalışmalar [2].", refs, "tr")
    assert "(Kaya vd., 2020)" in out_tr
    assert "[" not in out_tr


def test_apa_reference_format():
    text = format_reference_text(_ref(1, ["Jane Q Doe", "John Smith"]))
    assert text.startswith("Doe, J. Q., & Smith, J. (2020).")
    assert "J Test" in text and "12" in text and "45-67" in text
    assert "https://doi.org/10.1000/x1" in text
