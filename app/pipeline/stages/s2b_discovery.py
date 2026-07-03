"""Aşama 2b: Keşifsel örüntü ve risk analizi (deterministik, tamamen isteğe bağlı/bonus)."""
from __future__ import annotations

import asyncio

from app.models import ValidationIssue
from app.pipeline.stage import PipelineContext, Stage
from app.statistics.discovery import run_discovery


class DiscoveryStage(Stage):
    stage_id = "discovery"
    name = "Keşifsel Örüntü ve Risk Analizi"
    allow_degraded = True  # tamamen keşifsel — asla ana pipeline'ı bloklamaz

    async def run(self, ctx: PipelineContext, attempt: int):
        async with self.agent(ctx, "Örüntü Kaşifi", "worker", attempt) as h:
            report = await asyncio.to_thread(run_discovery, ctx.df, ctx.job.variables, ctx.job.config, ctx.findings)
            parts = []
            if report.clustering:
                parts.append(f"{report.clustering.k} gizli grup (silhouette={report.clustering.silhouette:.2f})")
            if report.anomalies:
                parts.append(f"{report.anomalies.n_flagged} sıra dışı vaka")
            if report.mutual_info:
                n_hidden = sum(1 for p in report.mutual_info if p.hidden)
                parts.append(f"{n_hidden} gizli bilgi-teorik ilişki")
            if report.risk_score:
                auc = report.risk_score.auc_logreg or report.risk_score.auc_rf
                parts.append(f"risk skoru AUC={auc:.2f}" if auc is not None else "risk skoru hesaplandı")
            summary = "; ".join(parts) if parts else "keşifsel örüntü bulunamadı"
            await h.passed(summary)
        for reason in report.skipped_reasons:
            await ctx.log(f"Keşifsel analiz: {reason}", level="warn")
        return report

    async def validate(self, ctx: PipelineContext, output, attempt: int):
        report = output
        issues: list[ValidationIssue] = []
        async with self.agent(ctx, "Sağlamlık Denetçisi", "validator", attempt) as h:
            for auc in (report.risk_score.auc_logreg if report.risk_score else None,
                        report.risk_score.auc_rf if report.risk_score else None):
                if auc is not None and not (0 <= auc <= 1):
                    issues.append(ValidationIssue(severity="warn", message="Risk skoru AUC geçersiz aralıkta.", target="discovery"))
            if report.clustering and not (-1 <= report.clustering.silhouette <= 1):
                issues.append(ValidationIssue(severity="warn", message="Silhouette skoru geçersiz aralıkta.", target="discovery"))
            if issues:
                await h.failed("; ".join(i.message for i in issues))
            else:
                await h.passed("keşifsel bulgular tutarlı")
        return issues

    def accept(self, ctx: PipelineContext, output) -> None:
        report = output
        ctx.discovery = report
        ctx.job.discovery = report
        sr = ctx.job.stages[self.stage_id]
        n_hidden = sum(1 for p in report.mutual_info if p.hidden)
        bits = []
        if report.clustering:
            bits.append(f"{report.clustering.k} gizli grup")
        if report.anomalies:
            bits.append(f"{report.anomalies.n_flagged} sıra dışı vaka")
        if n_hidden:
            bits.append(f"{n_hidden} gizli ilişki")
        if report.risk_score:
            bits.append("risk skoru modeli")
        sr.summary = ("; ".join(bits) if bits else "belirgin keşifsel bulgu yok") + " (hipotez üretici, doğrulayıcı değil)."
