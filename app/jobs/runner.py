"""Arkaplan iş çalıştırıcısı: pipeline'ı yürütür, olayları yayınlar, hataları toplar."""
from __future__ import annotations

import traceback

from app import config
from app.api.events import bus
from app.jobs.store import store
from app.llm.router import LLMRouter
from app.models import JobStatus
from app.pipeline.orchestrator import run_pipeline
from app.pipeline.stage import JobCancelled, PipelineContext, StageFailure


async def run_job(job_id: str) -> None:
    job = store.get(job_id)
    if job is None:
        return
    job.status = JobStatus.running
    job.error = None
    store.save(job)

    async def on_log(msg: str) -> None:
        await bus.publish(job_id, "log", level="info", message=msg)

    router = LLMRouter(config.get_api_keys(), job.config.provider, on_log=on_log)
    job_dir = store.job_dir(job_id)
    input_path = next(iter(job_dir.glob("input.*")), job_dir / "input.sav")

    ctx = PipelineContext(
        job=job, store=store, bus=bus, router=router,
        job_dir=job_dir, input_path=input_path,
    )
    await bus.publish(job_id, "log", level="info",
                      message=f"Pipeline başladı ({'LLM modu' if router.mode == 'llm' else 'şablon modu — API anahtarı yok'}).")
    try:
        await run_pipeline(ctx)
        job.status = JobStatus.completed
        for sr in job.stages.values():
            job.warnings.extend(w for w in sr.warnings if w not in job.warnings)
        await bus.publish(job_id, "job_finished", status="completed",
                          output_url=f"/api/jobs/{job_id}/download")
    except JobCancelled:
        job.status = JobStatus.cancelled
        await bus.publish(job_id, "job_finished", status="cancelled")
    except StageFailure as exc:
        job.status = JobStatus.failed
        job.error = str(exc)
        await bus.publish(job_id, "job_finished", status="failed", error=job.error)
    except Exception as exc:
        job.status = JobStatus.failed
        job.error = f"Beklenmedik hata: {exc}"
        traceback.print_exc()
        await bus.publish(job_id, "job_finished", status="failed", error=job.error)
    finally:
        job.current_stage = None
        store.cancel_flags.discard(job_id)
        store.save(job)
