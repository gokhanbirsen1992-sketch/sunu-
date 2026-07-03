"""Bağımsız istatistik analiz aracı: standalone_stats.report.analyze / CLI."""
from __future__ import annotations

import pytest
from docx import Document

from standalone_stats.cli import main
from standalone_stats.report import analyze


def test_analyze_xlsx_produces_report(tmp_path, synthetic_df):
    xlsx_path = tmp_path / "veri.xlsx"
    synthetic_df.to_excel(xlsx_path, index=False)

    result = analyze(xlsx_path, dv="cinsiyet", lang="tr")

    assert result.out_path.exists()
    assert result.n_rows_before == 120
    assert result.n_rows_after < result.n_rows_before  # kopya satırlar temizlendi
    assert len(result.findings) > 0
    assert result.discovery.clustering is not None or result.discovery.skipped_reasons
    assert result.discovery.risk_score is not None
    assert result.discovery.risk_score.dv == "cinsiyet"

    doc = Document(str(result.out_path))
    text = "\n".join(p.text for p in doc.paragraphs)
    assert "Değişken Özeti" in text
    assert "Bulgular" in text
    assert "Keşifsel Bulgular" in text


def test_analyze_csv_default_output_path(tmp_path, synthetic_df):
    csv_path = tmp_path / "veri.csv"
    synthetic_df.to_csv(csv_path, index=False)

    result = analyze(csv_path)

    assert result.out_path == tmp_path / "veri_rapor.docx"
    assert result.out_path.exists()
    assert result.discovery.risk_score is None  # dv işaretlenmedi


def test_analyze_sav_reuses_existing_fixture(sav_path):
    result = analyze(sav_path, lang="tr")
    assert result.out_path.exists()
    assert any(v.name == "kaygi" and v.kind == "continuous" for v in result.variables)


def test_analyze_unknown_dv_raises(tmp_path, synthetic_df):
    csv_path = tmp_path / "veri.csv"
    synthetic_df.to_csv(csv_path, index=False)
    with pytest.raises(ValueError, match="Değişken bulunamadı"):
        analyze(csv_path, dv="olmayan_sutun")


def test_cli_end_to_end(tmp_path, synthetic_df, capsys):
    csv_path = tmp_path / "veri.csv"
    synthetic_df.to_csv(csv_path, index=False)
    out_path = tmp_path / "cikti.docx"

    code = main([str(csv_path), "--dv", "cinsiyet", "--out", str(out_path)])

    assert code == 0
    assert out_path.exists()
    captured = capsys.readouterr()
    assert "Rapor kaydedildi" in captured.out


def test_cli_missing_file_reports_error(capsys):
    code = main(["dosya_yok.csv"])
    assert code == 1
    captured = capsys.readouterr()
    assert "Hata" in captured.err
