"""REST + SSE uçları."""
from __future__ import annotations

import asyncio
import json
from typing import Literal, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from app import config
from app.api.events import bus
from app.jobs.runner import run_job
from app.jobs.store import store
from app.llm.router import build_providers
from app.models import Job, JobConfig, JobStatus
from app.pipeline.orchestrator import STAGE_ORDER
from app.statistics.loader import load_dataset
from app.statistics.vartypes import infer_types

router = APIRouter()

MAX_UPLOAD_MB = 50


@router.post("/jobs")
async def create_job(
    file: UploadFile = File(...),
    language: Literal["tr", "en"] = Form("tr"),
    provider: Literal["auto", "gemini", "groq", "openrouter", "template"] = Form("auto"),
    alpha: float = Form(0.05),
    p_adjust: Literal["none", "holm", "fdr_bh"] = Form("holm"),
    topic_hint: Optional[str] = Form(None),
):
    name = file.filename or "veri.sav"
    suffix = "." + name.rsplit(".", 1)[-1].lower() if "." in name else ""
    if suffix not in (".sav", ".zsav", ".csv"):
        raise HTTPException(400, "Yalnızca SPSS .sav/.zsav (veya .csv) dosyaları kabul edilir.")
    content = await file.read()
    if len(content) > MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(400, f"Dosya çok büyük (en fazla {MAX_UPLOAD_MB} MB).")

    job = Job(
        filename=name,
        config=JobConfig(
            language=language, provider=provider, alpha=alpha,
            p_adjust=p_adjust, topic_hint=(topic_hint or None),
        ),
    )
    job_dir = store.job_dir(job.id)
    input_path = job_dir / f"input{suffix}"
    input_path.write_bytes(content)

    try:
        df, meta = await asyncio.to_thread(load_dataset, input_path)
    except Exception as exc:
        import traceback

        traceback.print_exc()
        store.delete(job.id)
        raise HTTPException(400, f"Dosya okunamadı: {exc}")
    if df.empty:
        store.delete(job.id)
        raise HTTPException(400, "Dosya boş görünüyor.")

    job.variables = infer_types(df, meta)
    store.add(job)
    return {"job": job.model_dump(mode="json"), "stage_order": STAGE_ORDER}


class VarOverride(BaseModel):
    kind: Optional[str] = None
    role: Optional[str] = None


class StartRequest(BaseModel):
    overrides: dict[str, VarOverride] = {}


@router.post("/jobs/{job_id}/start")
async def start_job(job_id: str, body: StartRequest | None = None):
    job = store.get(job_id)
    if job is None:
        raise HTTPException(404, "İş bulunamadı.")
    if job.status == JobStatus.running:
        raise HTTPException(409, "İş zaten çalışıyor.")
    valid_kinds = {"continuous", "ordinal", "nominal", "binary", "id", "date", "excluded"}
    valid_roles = {"auto", "dv", "iv", "exclude"}
    if body:
        for var in job.variables:
            ov = body.overrides.get(var.name)
            if not ov:
                continue
            if ov.kind and ov.kind in valid_kinds:
                var.kind = ov.kind  # type: ignore[assignment]
            if ov.role and ov.role in valid_roles:
                var.role = ov.role  # type: ignore[assignment]
    job.status = JobStatus.pending
    job.stages = {}
    job.findings = []
    job.error = None
    job.output_docx = None
    job.warnings = []
    store.save(job)
    asyncio.create_task(run_job(job_id))
    return {"ok": True}


@router.get("/jobs")
async def list_jobs():
    jobs = sorted(store.jobs.values(), key=lambda j: j.created_at, reverse=True)
    return [
        {
            "id": j.id, "created_at": j.created_at.isoformat(), "status": j.status,
            "filename": j.filename, "language": j.config.language,
            "output": bool(j.output_docx), "error": j.error,
        }
        for j in jobs[:50]
    ]


@router.get("/jobs/{job_id}")
async def get_job(job_id: str):
    job = store.get(job_id)
    if job is None:
        raise HTTPException(404, "İş bulunamadı.")
    return {"job": job.model_dump(mode="json"), "stage_order": STAGE_ORDER}


@router.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    job = store.get(job_id)
    if job is None:
        raise HTTPException(404, "İş bulunamadı.")
    if job.status == JobStatus.running:
        store.request_cancel(job_id)
        return {"ok": True, "cancelled": True}
    store.delete(job_id)
    return {"ok": True, "deleted": True}


@router.get("/jobs/{job_id}/download")
async def download(job_id: str):
    job = store.get(job_id)
    if job is None or not job.output_docx:
        raise HTTPException(404, "Çıktı henüz hazır değil.")
    path = store.job_dir(job_id) / job.output_docx
    if not path.exists():
        raise HTTPException(404, "Çıktı dosyası bulunamadı.")
    stem = (job.filename.rsplit(".", 1)[0] or "makale")[:40]
    return FileResponse(
        path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=f"{stem}-makale.docx",
    )


@router.get("/jobs/{job_id}/events")
async def job_events(job_id: str):
    job = store.get(job_id)
    if job is None:
        raise HTTPException(404, "İş bulunamadı.")

    async def generator():
        q = bus.subscribe(job_id)
        try:
            current = store.get(job_id)
            yield {"event": "message", "data": json.dumps(
                {"type": "snapshot", "job": current.model_dump(mode="json"),
                 "stage_order": STAGE_ORDER}, ensure_ascii=False)}
            while True:
                try:
                    event = await asyncio.wait_for(q.get(), timeout=15.0)
                    yield {"event": "message", "data": json.dumps(event, ensure_ascii=False, default=str)}
                    if event.get("type") == "job_finished":
                        # son durumu da gönder
                        current = store.get(job_id)
                        if current:
                            yield {"event": "message", "data": json.dumps(
                                {"type": "snapshot", "job": current.model_dump(mode="json"),
                                 "stage_order": STAGE_ORDER}, ensure_ascii=False)}
                except asyncio.TimeoutError:
                    yield {"event": "message", "data": json.dumps({"type": "heartbeat"})}
        finally:
            bus.unsubscribe(job_id, q)

    return EventSourceResponse(generator())


@router.get("/settings")
async def get_settings():
    keys = config.get_api_keys()
    return {
        "providers": {p: bool(keys.get(p)) for p in ("gemini", "groq", "openrouter")},
        "mode": "llm" if any(keys.values()) else "template",
        "offline": config.is_offline(),
    }


class KeyRequest(BaseModel):
    provider: Literal["gemini", "groq", "openrouter"]
    key: str = ""


@router.post("/settings/keys")
async def set_key(body: KeyRequest):
    config.save_api_key(body.provider, body.key)
    return await get_settings()


@router.post("/settings/test-key")
async def test_key(body: KeyRequest):
    providers = build_providers({body.provider: body.key} if body.key else config.get_api_keys(), body.provider)
    providers = [p for p in providers if p.name == body.provider]
    if not providers:
        raise HTTPException(400, "Bu sağlayıcı için anahtar bulunamadı.")
    try:
        resp = await providers[0].complete("", "Yanıt olarak yalnızca 'OK' yaz.", max_tokens=10, temperature=0.0)
        return {"ok": True, "model": resp.model, "sample": resp.text.strip()[:40]}
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:300]}
