"""Bağımsız analiz aracının web ucu: /api/standalone/analyze + /download (telefon/tarayıcı akışı)."""
from __future__ import annotations

import io

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("PAPERFORGE_DATA_DIR", str(tmp_path / "data"))
    import importlib

    from app import config

    importlib.reload(config)
    from app.main import app

    with TestClient(app) as c:
        yield c


def test_standalone_page_served(client):
    resp = client.get("/analiz")
    assert resp.status_code == 200
    assert "İstatistik Analiz Arac" in resp.text


def test_analyze_csv_via_api(client, synthetic_df):
    buf = io.BytesIO()
    synthetic_df.to_csv(buf, index=False)
    buf.seek(0)

    resp = client.post(
        "/api/standalone/analyze",
        files={"file": ("veri.csv", buf, "text/csv")},
        data={"dv": "cinsiyet", "lang": "tr", "alpha": "0.05", "p_adjust": "holm"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["n_rows_before"] == 120
    assert data["n_tests"] > 0
    assert data["risk_score"] is not None
    assert data["risk_score"]["dv"] == "cinsiyet"

    dl = client.get(f"/api/standalone/download/{data['report_id']}")
    assert dl.status_code == 200
    assert dl.content[:2] == b"PK"  # geçerli .docx


def test_analyze_rejects_bad_extension(client):
    resp = client.post(
        "/api/standalone/analyze",
        files={"file": ("veri.txt", io.BytesIO(b"junk"), "text/plain")},
        data={},
    )
    assert resp.status_code == 400


def test_download_unknown_report_404(client):
    resp = client.get("/api/standalone/download/doesnotexist")
    assert resp.status_code == 404


def test_download_path_traversal_rejected(client):
    resp = client.get("/api/standalone/download/..%2F..%2Fetc%2Fpasswd")
    assert resp.status_code in (404, 422)
