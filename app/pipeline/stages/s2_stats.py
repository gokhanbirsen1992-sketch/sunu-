"""Aşama 2: Test seçimi + istatistik hesaplama (deterministik)."""
from __future__ import annotations

import asyncio

from app.models import ValidationIssue
from app.pipeline.stage import PipelineContext, Stage
from app.statistics.decision import plan_tests
from app.statistics.tests_runner import run_tests


class StatsStage(Stage):
    stage_id = "stats"
    name = "İstatistik Analizi"
    allow_degraded = False

    async def run(self, ctx: PipelineContext, attempt: int):
        async with self.agent(ctx, "Karar Motoru", "worker", attempt) as h:
            plans, notes = await asyncio.to_thread(plan_tests, ctx.df, ctx.job.variables)
            await h.passed(f"{len(plans)} test planlandı")
        for note in notes:
            await ctx.log(note, level="warn")

        async with self.agent(ctx, "Hesap Ordusu", "worker", attempt) as h:
            findings = await asyncio.to_thread(run_tests, ctx.df, plans, ctx.job.variables, ctx.job.config)
            n_sig = sum(1 for f in findings if f.significant)
            await h.passed(f"{len(findings)} test çalıştırıldı, {n_sig} anlamlı sonuç")

        for f in findings:
            if f.significant:
                await ctx.emit("finding", finding=f.model_dump())
        return plans, findings, notes

    async def validate(self, ctx: PipelineContext, output, attempt: int):
        plans, findings, _ = output
        issues: list[ValidationIssue] = []
        async with self.agent(ctx, "Sağlamlık Denetçisi", "validator", attempt) as h:
            valid = [f for f in findings if f.error is None]
            if not plans:
                issues.append(ValidationIssue(severity="block", message="Hiç test planlanamadı; değişken tiplerini kontrol edin.", target="stats"))
            elif not valid:
                issues.append(ValidationIssue(severity="block", message="Hiçbir test başarıyla çalıştırılamadı.", target="stats"))
            for f in findings:
                if f.error:
                    issues.append(ValidationIssue(severity="warn", message=f"{f.id} çalıştırılamadı: {f.error}", target="stats"))
                elif f.p_value is None or not (0 <= f.p_value <= 1):
                    issues.append(ValidationIssue(severity="block", message=f"{f.id} geçersiz p-değeri üretti.", target="stats"))
            if any(i.severity == "block" for i in issues):
                await h.failed("; ".join(i.message for i in issues if i.severity == "block"))
            else:
                await h.passed("tüm istatistikler tutarlı")
        return issues

    def accept(self, ctx: PipelineContext, output) -> None:
        plans, findings, notes = output
        ctx.plans, ctx.findings = plans, findings
        ctx.job.findings = findings
        n_sig = sum(1 for f in findings if f.significant)
        sr = ctx.job.stages[self.stage_id]
        sr.summary = f"{len(plans)} test çalıştırıldı; {n_sig} istatistiksel olarak anlamlı bulgu."
        sr.artifacts["notes"] = notes
