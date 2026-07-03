"""Aşama 6: Reviewer 2 — düşmanca eleştiri, ek literatür ve revizyon döngüsü."""
from __future__ import annotations

from app import config
from app.agents import prompts, validators
from app.literature.search import gather_literature
from app.llm import template_provider as tpl
from app.llm.provider import LLMUnavailable
from app.models import ReviewCritique
from app.pipeline.stage import PipelineContext, Stage

MAX_ROUNDS = 2


class ReviewStage(Stage):
    stage_id = "review"
    name = "Reviewer 2 Değerlendirmesi"
    max_attempts = 1

    async def _get_critiques(self, ctx: PipelineContext, round_no: int) -> list[ReviewCritique]:
        lang = ctx.job.config.language
        async with self.agent(ctx, f"Reviewer 2 (tur {round_no})", "worker") as h:
            if ctx.router.mode == "llm":
                try:
                    data = await ctx.router.complete_json(
                        prompts.system_reviewer(lang),
                        prompts.user_reviewer(ctx.manuscript.sections, ctx.findings, lang),
                    )
                    items = data if isinstance(data, list) else data.get("critiques", []) if isinstance(data, dict) else []
                    critiques = []
                    for it in items[:5]:
                        if isinstance(it, dict) and it.get("critique"):
                            critiques.append(ReviewCritique(
                                section=str(it.get("section", "general"))[:30],
                                critique=str(it["critique"])[:600],
                                requires_new_literature=bool(it.get("requires_new_literature")),
                            ))
                    await h.passed(f"{len(critiques)} eleştiri üretti")
                    return critiques
                except LLMUnavailable as exc:
                    await h.failed(str(exc))
            raw = tpl.template_critiques(ctx.manuscript.sections, len(ctx.references), lang)
            critiques = [ReviewCritique(**c) for c in raw]
            await h.passed(f"{len(critiques)} kontrol listesi eleştirisi (şablon modu)")
            return critiques

    async def _extra_literature(self, ctx: PipelineContext, critique: ReviewCritique) -> int:
        if config.is_offline() or ctx.router.mode != "llm":
            return 0
        async with self.agent(ctx, "Ek Literatür Tarayıcı", "worker") as h:
            try:
                data = await ctx.router.complete_json(
                    "Akademik arama sorgusu üreten bir uzmansın. Yalnızca JSON dizisi döndür.",
                    f"Hakem eleştirisi: {critique.critique}\n\nBu eleştiriyi karşılamak için 2 İngilizce "
                    'literatür arama sorgusu üret. JSON: ["query1", "query2"]',
                )
                queries = [str(q)[:120] for q in data if str(q).strip()][:2] if isinstance(data, list) else []
            except LLMUnavailable:
                queries = []
            if not queries:
                await h.failed("sorgu üretilemedi")
                return 0
            refs, _ = await gather_literature({}, queries, intro_pool_size=4)
            start_id = max((r.id for r in ctx.references), default=0)
            added = 0
            existing = {(r.doi or "t:" + r.title[:60].lower()) for r in ctx.references}
            for r in refs:
                key = r.doi or "t:" + r.title[:60].lower()
                if key in existing:
                    continue
                start_id += 1
                r.id = start_id
                ctx.references.append(r)
                added += 1
            ctx.manuscript.references = ctx.references
            ctx.job.n_references = len(ctx.references)
            await h.passed(f"{added} yeni kaynak eklendi")
            return added

    async def _revise(self, ctx: PipelineContext, critique: ReviewCritique) -> None:
        lang = ctx.job.config.language
        section = critique.section if critique.section in ctx.manuscript.sections else "discussion"
        original = ctx.manuscript.sections.get(section, "")
        if ctx.router.mode != "llm" or not original.strip():
            critique.addressed = False
            critique.response = (
                "Şablon modunda otomatik revizyon sınırlıdır; eleştiri makale raporuna not edildi."
                if lang == "tr" else
                "Automatic revision is limited in template mode; the critique was noted in the report."
            )
            ctx.manuscript.warnings.append(f"Hakem eleştirisi ({section}): {critique.critique}")
            return
        async with self.agent(ctx, f"Revizyon Yazarı ({section})", "worker") as h:
            try:
                resp = await ctx.router.complete(
                    prompts.system_revisor(lang),
                    prompts.user_revisor(section, original, critique.critique, ctx.references, ctx.findings, lang),
                )
                candidate = resp.text.strip()
            except LLMUnavailable as exc:
                await h.failed(str(exc))
                critique.response = "Revizyon yapılamadı (LLM erişilemedi)."
                return
            valid_ids = {r.id for r in ctx.references}
            issues = validators.check_citations(candidate, valid_ids, section)
            issues += validators.check_not_collapsed(original, candidate, section)
            if any(i.severity == "block" for i in issues):
                await h.failed("revizyon doğrulamayı geçemedi; özgün metin korundu")
                critique.response = "Revizyon doğrulama nedeniyle uygulanamadı."
                return
            ctx.manuscript.sections[section] = candidate
            critique.addressed = True
            critique.response = ("Bölüm eleştiri doğrultusunda revize edildi." if lang == "tr"
                                 else "The section was revised in line with the critique.")
            await h.passed("revize edildi ve doğrulandı")

    async def run(self, ctx: PipelineContext, attempt: int):
        rounds_done = []
        n_rounds = MAX_ROUNDS if ctx.router.mode == "llm" else 1
        for round_no in range(1, n_rounds + 1):
            ctx.check_cancelled()
            critiques = await self._get_critiques(ctx, round_no)
            if not critiques:
                await ctx.log(f"Reviewer 2 tur {round_no}: eleştiri kalmadı.")
                break
            for critique in critiques:
                if critique.requires_new_literature:
                    await self._extra_literature(ctx, critique)
                await self._revise(ctx, critique)
            async with self.agent(ctx, f"Yanıt Denetçisi (tur {round_no})", "validator") as h:
                addressed = sum(1 for c in critiques if c.addressed)
                await h.passed(f"{addressed}/{len(critiques)} eleştiri giderildi")
            rounds_done.append({
                "round": round_no,
                "critiques": [c.model_dump() for c in critiques],
            })
            if all(c.addressed for c in critiques):
                pass  # bir tur daha bakılır (LLM modunda), kalan sorun var mı diye
        return rounds_done

    def accept(self, ctx: PipelineContext, output) -> None:
        ctx.manuscript.reviewer_rounds = output
        total = sum(len(r["critiques"]) for r in output)
        addressed = sum(1 for r in output for c in r["critiques"] if c["addressed"])
        sr = ctx.job.stages[self.stage_id]
        sr.summary = f"{len(output)} hakem turu; {total} eleştiriden {addressed} tanesi revizyonla giderildi."
        sr.artifacts["reviewer_rounds"] = output
