"""Aşama 3: Anlamlı bulgular için literatür taraması."""
from __future__ import annotations

from app import config
from app.agents import prompts
from app.literature.search import gather_literature
from app.llm.provider import LLMUnavailable
from app.llm.template_provider import build_queries_template
from app.models import Reference, ValidationIssue
from app.pipeline.stage import PipelineContext, Stage


class LiteratureStage(Stage):
    stage_id = "literature"
    name = "Literatür Taraması"
    max_attempts = 1

    async def run(self, ctx: PipelineContext, attempt: int):
        sig = [f for f in ctx.findings if f.significant]
        if config.is_offline():
            await ctx.log("Çevrimdışı mod: literatür taraması atlandı.", level="warn")
            return [], {}
        if not sig:
            await ctx.log("Anlamlı bulgu yok; literatür taraması giriş kaynaklarıyla sınırlı tutuluyor.", level="warn")

        queries_by_finding: dict[str, list[str]] = {}
        intro_queries: list[str] = []
        lang = ctx.job.config.language

        async with self.agent(ctx, "Sorgu Yazarı", "worker", attempt) as h:
            if ctx.router.mode == "llm":
                try:
                    data = await ctx.router.complete_json(
                        "Akademik literatür arama sorguları üreten bir uzmansın. Yalnızca JSON döndür.",
                        prompts.user_queries(ctx.findings, ctx.job.config.topic_hint, lang),
                    )
                    if isinstance(data, dict):
                        valid_ids = {f.id for f in sig}
                        for key, qs in data.items():
                            if not isinstance(qs, list):
                                continue
                            qs = [str(q)[:120] for q in qs if str(q).strip()][:3]
                            if key == "INTRO":
                                intro_queries = qs
                            elif key in valid_ids:
                                queries_by_finding[key] = qs
                except LLMUnavailable:
                    pass
            if not queries_by_finding:
                for f in sig:
                    qs = build_queries_template(f)
                    if qs:
                        queries_by_finding[f.id] = qs
            if not intro_queries:
                seen: list[str] = []
                for f in sig:
                    for k in f.keywords:
                        if k not in seen:
                            seen.append(k)
                if ctx.job.config.topic_hint:
                    intro_queries.append(ctx.job.config.topic_hint[:100])
                if seen:
                    intro_queries.append(" ".join(seen[:4]))
            total_q = sum(len(v) for v in queries_by_finding.values()) + len(intro_queries)
            await h.passed(f"{total_q} arama sorgusu hazırlandı")

        async def emit_ref(r: Reference) -> None:
            await ctx.emit("reference_found", reference={
                "title": r.title, "year": r.year, "source": r.source_api,
                "journal": r.journal, "doi": r.doi,
            })

        async with self.agent(ctx, "Tarama Ordusu (OpenAlex · Crossref · PubMed)", "worker", attempt) as h:
            refs, mapping = await gather_literature(
                queries_by_finding, intro_queries,
                max_refs_per_finding=ctx.job.config.max_refs_per_finding,
                emit_ref=emit_ref,
                emit_progress=lambda m: ctx.emit("stage_progress", stage_id=self.stage_id, message=m),
            )
            await h.passed(f"{len(refs)} benzersiz kaynak bulundu")
        return refs, mapping

    async def validate(self, ctx: PipelineContext, output, attempt: int):
        refs, _ = output
        issues: list[ValidationIssue] = []
        async with self.agent(ctx, "Kaynak Denetçisi", "validator", attempt) as h:
            if not refs and not config.is_offline():
                issues.append(ValidationIssue(severity="warn", message="Hiç kaynak bulunamadı; makale atıfsız şablonla yazılacak.", target="literature"))
            incomplete = [r for r in refs if not r.year or not r.authors]
            if incomplete:
                issues.append(ValidationIssue(severity="warn", message=f"{len(incomplete)} kaynağın yıl/yazar bilgisi eksik.", target="literature"))
            await h.passed(f"{len(refs)} kaynak doğrulandı")
        return issues

    def accept(self, ctx: PipelineContext, output) -> None:
        refs, mapping = output
        ctx.references = refs
        ctx.refs_by_finding = {k: v for k, v in mapping.items() if k != "INTRO"}
        ctx.intro_ref_ids = mapping.get("INTRO", [])
        ctx.job.n_references = len(refs)
        sr = ctx.job.stages[self.stage_id]
        sr.summary = f"{len(refs)} benzersiz akademik kaynak toplandı (OpenAlex, Crossref, PubMed)."
        sr.artifacts["references"] = [r.model_dump() for r in refs]
