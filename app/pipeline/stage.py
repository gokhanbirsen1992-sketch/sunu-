"""Ajan ordusu deseni: her aşama = işçi ajanlar + doğrulayıcı ajanlar + retry döngüsü."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

from app.api.events import EventBus
from app.jobs.store import JobStore
from app.llm.router import LLMRouter
from app.models import (
    AgentRun,
    CleaningReport,
    DiscoveryReport,
    Finding,
    Job,
    Manuscript,
    PlannedTest,
    Reference,
    StageResult,
    ValidationIssue,
)


class StageFailure(Exception):
    pass


class JobCancelled(Exception):
    pass


@dataclass
class PipelineContext:
    job: Job
    store: JobStore
    bus: EventBus
    router: LLMRouter
    job_dir: Path
    input_path: Path
    df: pd.DataFrame | None = None
    meta: dict = field(default_factory=dict)
    cleaning_report: CleaningReport | None = None
    plans: list[PlannedTest] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)
    discovery: DiscoveryReport | None = None
    references: list[Reference] = field(default_factory=list)
    refs_by_finding: dict[str, list[int]] = field(default_factory=dict)
    intro_ref_ids: list[int] = field(default_factory=list)
    manuscript: Manuscript = field(default_factory=Manuscript)
    feedback: list[str] = field(default_factory=list)

    async def emit(self, event_type: str, **data) -> None:
        await self.bus.publish(self.job.id, event_type, **data)

    async def log(self, message: str, level: str = "info") -> None:
        await self.emit("log", level=level, message=message)

    def save(self) -> None:
        self.store.save(self.job)

    def check_cancelled(self) -> None:
        if self.store.is_cancelled(self.job.id):
            raise JobCancelled()

    def refs_for(self, finding_id: str) -> list[Reference]:
        ids = set(self.refs_by_finding.get(finding_id, []))
        return [r for r in self.references if r.id in ids]

    def intro_refs(self) -> list[Reference]:
        ids = set(self.intro_ref_ids)
        pool = [r for r in self.references if r.id in ids]
        return pool or self.references[:8]


class AgentHandle:
    """Bir ajanın yaşam döngüsünü StageResult + SSE olaylarına yansıtır."""

    def __init__(self, ctx: PipelineContext, stage: StageResult, name: str, role: str, attempt: int):
        self.ctx = ctx
        self.stage = stage
        self.run = AgentRun(name=name, role=role, attempt=attempt, status="pending")
        stage.agents.append(self.run)

    async def _update(self, status: str, detail: str | None = None) -> None:
        self.run.status = status
        if detail:
            self.run.detail = detail[:500]
        await self.ctx.emit(
            "agent_update", stage_id=self.stage.stage_id,
            agent=self.run.model_dump(),
        )
        self.ctx.save()

    async def __aenter__(self) -> "AgentHandle":
        await self._update("running")
        return self

    async def __aexit__(self, exc_type, exc, tb) -> bool:
        if exc_type is None:
            if self.run.status == "running":
                await self._update("passed")
        else:
            await self._update("failed", detail=str(exc))
        return False

    async def passed(self, detail: str | None = None) -> None:
        await self._update("passed", detail)

    async def failed(self, detail: str | None = None) -> None:
        await self._update("failed", detail)


class Stage(ABC):
    stage_id: str = ""
    name: str = ""
    max_attempts: int = 2
    allow_degraded: bool = True  # doğrulama geçmese de (uyarıyla) devam edilebilir mi

    @abstractmethod
    async def run(self, ctx: PipelineContext, attempt: int) -> Any: ...

    async def validate(self, ctx: PipelineContext, output: Any, attempt: int) -> list[ValidationIssue]:
        return []

    def accept(self, ctx: PipelineContext, output: Any) -> None:
        pass

    def agent(self, ctx: PipelineContext, name: str, role: str = "worker", attempt: int = 1) -> AgentHandle:
        return AgentHandle(ctx, ctx.job.stages[self.stage_id], name, role, attempt)

    async def execute(self, ctx: PipelineContext) -> None:
        sr = StageResult(stage_id=self.stage_id, name=self.name, status="running")
        ctx.job.stages[self.stage_id] = sr
        ctx.job.current_stage = self.stage_id
        ctx.feedback = []
        ctx.save()

        last_output: Any = None
        last_issues: list[ValidationIssue] = []
        for attempt in range(1, self.max_attempts + 1):
            ctx.check_cancelled()
            sr.attempts = attempt
            await ctx.emit("stage_started", stage_id=self.stage_id, name=self.name, attempt=attempt)
            try:
                output = await self.run(ctx, attempt)
            except (JobCancelled, StageFailure):
                raise
            except Exception as exc:
                if attempt < self.max_attempts:
                    await ctx.log(f"{self.name}: hata ({exc}); yeniden deneniyor…", level="warn")
                    continue
                raise StageFailure(f"{self.name} aşaması başarısız: {exc}") from exc

            issues = await self.validate(ctx, output, attempt)
            blocks = [i for i in issues if i.severity == "block"]
            warns = [i.message for i in issues if i.severity == "warn"]
            sr.warnings.extend(w for w in warns if w not in sr.warnings)
            last_output, last_issues = output, issues

            if not blocks:
                self.accept(ctx, output)
                sr.status = "passed"
                await ctx.emit("stage_finished", stage_id=self.stage_id, status="passed",
                               summary=sr.summary, attempts=attempt)
                ctx.save()
                return

            ctx.feedback = [i.message for i in blocks]
            await ctx.log(
                f"{self.name}: doğrulayıcılar {len(blocks)} engelleyici sorun buldu"
                + ("; yeniden deneniyor…" if attempt < self.max_attempts else "."),
                level="warn",
            )

        # tüm denemeler bitti
        if self.allow_degraded and last_output is not None:
            for i in last_issues:
                if i.severity == "block" and i.message not in sr.warnings:
                    sr.warnings.append(i.message)
            self.accept(ctx, last_output)
            sr.status = "passed"
            sr.warnings.append(f"{self.name}: doğrulama tam geçilemedi; son sürüm uyarılarla kabul edildi.")
            await ctx.emit("stage_finished", stage_id=self.stage_id, status="passed",
                           summary=sr.summary, attempts=sr.attempts)
            ctx.save()
            return
        sr.status = "failed"
        await ctx.emit("stage_finished", stage_id=self.stage_id, status="failed",
                       summary=sr.summary, attempts=sr.attempts)
        ctx.save()
        raise StageFailure(f"{self.name} aşaması doğrulamayı geçemedi.")
