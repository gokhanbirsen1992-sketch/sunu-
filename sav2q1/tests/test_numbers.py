"""Sayı çıkarımı/normalizasyonu testleri — verify-numeric'in temeli."""

from sav2q1.engine.numbers import extract_tokens, is_year


def test_extract_basic():
    assert extract_tokens("U = 3596,5, p < 0,001, r = 0,41") == ["3596,5", "0,001", "0,41"]


def test_strip_citation_markers():
    assert extract_tokens("etkilidir [12].") == []
    assert extract_tokens("etkilidir [3-5].") == []
    assert extract_tokens("birden çok [1, 2] kaynak.") == []


def test_dot_decimal_normalized():
    assert extract_tokens("mean 1.5") == ["1,5"]


def test_percent():
    assert extract_tokens("%62,3 kadın") == ["62,3"]


def test_is_year():
    assert is_year("2020")
    assert is_year("1998")
    assert not is_year("0,05")
    assert not is_year("220")
