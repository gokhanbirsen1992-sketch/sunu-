import io

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("VERIKASIFI_DATA_DIR", str(tmp_path / "data"))
    import importlib

    import main

    importlib.reload(main)
    with TestClient(main.app) as c:
        yield c


def test_index_page_served(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Veri Kâşifi" in resp.text


def test_analyze_and_download(client, synthetic_df):
    buf = io.BytesIO()
    synthetic_df.to_csv(buf, index=False)
    buf.seek(0)

    resp = client.post(
        "/api/analyze",
        files={"file": ("veri.csv", buf, "text/csv")},
        data={"target": "sonuc"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["n_rows"] == 150
    assert data["n_tests"] > 0
    assert data["clustering"]["k"] == 2
    assert data["risk_score"]["target"] == "sonuc"

    dl = client.get(f"/api/download/{data['report_id']}")
    assert dl.status_code == 200
    assert dl.content[:2] == b"PK"


def test_analyze_rejects_bad_extension(client):
    resp = client.post(
        "/api/analyze",
        files={"file": ("veri.txt", io.BytesIO(b"junk"), "text/plain")},
    )
    assert resp.status_code == 400


def test_download_unknown_report_404(client):
    resp = client.get("/api/download/doesnotexist")
    assert resp.status_code == 404
