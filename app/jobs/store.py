"""İş deposu: bellek içi sözlük + iş klasöründe JSON kalıcılığı."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from app import config
from app.models import Job, JobStatus


class JobStore:
    def __init__(self) -> None:
        self.jobs: dict[str, Job] = {}
        self.cancel_flags: set[str] = set()

    def job_dir(self, job_id: str) -> Path:
        d = config.JOBS_DIR / job_id
        d.mkdir(parents=True, exist_ok=True)
        return d

    def add(self, job: Job) -> None:
        self.jobs[job.id] = job
        self.save(job)

    def get(self, job_id: str) -> Job | None:
        return self.jobs.get(job_id)

    def save(self, job: Job) -> None:
        path = self.job_dir(job.id) / "job.json"
        path.write_text(job.model_dump_json(indent=2), encoding="utf-8")

    def delete(self, job_id: str) -> None:
        self.jobs.pop(job_id, None)
        self.cancel_flags.discard(job_id)
        shutil.rmtree(config.JOBS_DIR / job_id, ignore_errors=True)

    def request_cancel(self, job_id: str) -> None:
        self.cancel_flags.add(job_id)

    def is_cancelled(self, job_id: str) -> bool:
        return job_id in self.cancel_flags

    def load_all(self) -> None:
        if not config.JOBS_DIR.exists():
            return
        for job_file in sorted(config.JOBS_DIR.glob("*/job.json")):
            try:
                job = Job.model_validate_json(job_file.read_text(encoding="utf-8"))
            except Exception:
                continue
            if job.status == JobStatus.running:
                job.status = JobStatus.failed
                job.error = "Sunucu yeniden başlatıldığı için iş yarıda kaldı."
            self.jobs[job.id] = job


store = JobStore()
