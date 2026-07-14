"""Tur rehberi statik dosyalarının sunulduğunu ve sayfaya bağlandığını doğrular."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("PAPERFORGE_OFFLINE", "1")
    monkeypatch.setenv("PAPERFORGE_DATA_DIR", str(tmp_path / "data"))

    import importlib

    from app import config

    importlib.reload(config)
    from app.main import app

    with TestClient(app) as c:
        yield c


def test_tour_js_served(client):
    resp = client.get("/static/tour.js")
    assert resp.status_code == 200
    body = resp.text
    # sonsuz döngü: son duraktan sonra başa sarma ve tur sayacı
    assert "state.lap += 1" in body
    assert "PaperForgeTour" in body


def test_index_links_tour(client):
    resp = client.get("/static/index.html")
    assert resp.status_code == 200
    assert "tour.js" in resp.text
    assert 'id="tour-btn"' in resp.text


def test_tour_step_targets_exist_in_index(client):
    """tour.js'teki her durağın hedef seçicisi index.html'de bulunmalı."""
    import re

    tour = client.get("/static/tour.js").text
    index = client.get("/static/index.html").text
    targets = re.findall(r'target:\s*["\']([^"\']+)["\']', tour)
    assert len(targets) >= 15  # tam teşekküllü tur: uygulamanın tamamını gezmeli
    for sel in targets:
        # basit seçici -> index.html'de karşılığını ara
        if sel.startswith("#"):
            assert f'id="{sel[1:]}"' in index, f"{sel} hedefi index.html'de yok"
        elif "data-provider" in sel:
            assert 'data-provider="gemini"' in index
        else:  # "header h1", "footer" gibi etiket seçicileri
            tag = sel.split()[-1]
            assert f"<{tag}" in index, f"{sel} hedefi index.html'de yok"
