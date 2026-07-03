"""Uçtan uca API testi: yükle → başlat → tamamlanana dek bekle → indir (şablon modu, çevrimdışı)."""
from __future__ import annotations

import time

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("PAPERFORGE_OFFLINE", "1")
    monkeypatch.setenv("PAPERFORGE_DATA_DIR", str(tmp_path / "data"))
    for env in ("GEMINI_API_KEY", "GROQ_API_KEY", "OPENROUTER_API_KEY"):
        monkeypatch.delenv(env, raising=False)

    import importlib

    from app import config

    importlib.reload(config)
    from app.jobs import store as store_mod

    store_mod.store.jobs.clear()
    from app.main import app

    with TestClient(app) as c:
        yield c


def test_rejects_wrong_extension(client):
    resp = client.post("/api/jobs", files={"file": ("veri.xlsx", b"junk")})
    assert resp.status_code == 400
    assert ".sav" in resp.json()["detail"]


def test_full_pipeline_template_mode(client, sav_path):
    with open(sav_path, "rb") as fh:
        resp = client.post(
            "/api/jobs",
            files={"file": ("veri.sav", fh)},
            data={"language": "tr", "topic_hint": "Kaygı ve yaşam doyumu ilişkisi"},
        )
    assert resp.status_code == 200, resp.text
    payload = resp.json()
    job_id = payload["job"]["id"]
    assert any(v["name"] == "kaygi" and v["kind"] == "continuous" for v in payload["job"]["variables"])

    resp = client.post(f"/api/jobs/{job_id}/start", json={"overrides": {}})
    assert resp.status_code == 200

    deadline = time.time() + 120
    status = None
    while time.time() < deadline:
        job = client.get(f"/api/jobs/{job_id}").json()["job"]
        status = job["status"]
        if status in ("completed", "failed", "cancelled"):
            break
        time.sleep(0.5)
    assert status == "completed", f"durum={status}, hata={job.get('error')}"

    stages = job["stages"]
    assert set(stages) == {"clean", "stats", "literature", "writing", "editing", "review", "assemble"}
    assert all(s["status"] == "passed" for s in stages.values())
    # her aşamada en az bir ajan koşmuş olmalı
    assert all(len(s["agents"]) >= 1 for s in stages.values())
    # anlamlı bulgular üretilmiş olmalı
    assert any(f["significant"] for f in job["findings"])

    resp = client.get(f"/api/jobs/{job_id}/download")
    assert resp.status_code == 200
    assert resp.content[:2] == b"PK"  # geçerli docx (zip)
    assert len(resp.content) > 5000


def test_settings_reports_template_mode(client):
    data = client.get("/api/settings").json()
    assert data["mode"] == "template"
    assert data["offline"] is True
