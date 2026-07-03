"""Aşama 5: Dil düzenleme — atıf işaretleri ve sayılar korunarak."""
from __future__ import annotations

from app.agents import prompts, validators
from app.llm.provider import LLMUnavailable
from app.pipeline.stage import PipelineContext, Stage

EDITABLE = ("intro", "discussion", "limitations")


class EditingStage(Stage):
    stage_id = "editing"
    name = "Dil Düzenleme"
    max_attempts = 1

    async def run(self, ctx: PipelineContext, attempt: int):
        lang = ctx.job.config.language
        edited: dict[str, str] = {}
        if ctx.router.mode != "llm":
            async with self.agent(ctx, "Dil Editörü", "worker", attempt) as h:
                await h.passed("Şablon modunda metin zaten kural tabanlı; düzenleme atlandı")
            return edited

        for key in EDITABLE:
            original = ctx.manuscript.sections.get(key, "")
            if not original.strip():
                continue
            async with self.agent(ctx, f"Dil Editörü ({key})", "worker", attempt) as h:
                try:
                    resp = await ctx.router.complete(prompts.system_editor(lang), original, temperature=0.3)
                    candidate = resp.text.strip()
                except LLMUnavailable as exc:
                    await h.failed(str(exc))
                    continue
                issues = (
                    validators.check_markers_preserved(original, candidate, key)
                    + validators.check_not_collapsed(original, candidate, key)
                )
                if issues:
                    await h.failed("düzenleme reddedildi: " + issues[0].message)
                    ctx.job.stages[self.stage_id].warnings.append(
                        f"'{key}' düzenlemesi doğrulamayı geçemedi; özgün metin korundu."
                    )
                else:
                    edited[key] = candidate
                    await h.passed("düzenlendi ve doğrulandı")

        async with self.agent(ctx, "Atıf Koruması", "validator", attempt) as h:
            await h.passed(f"{len(edited)} bölümde işaretler ve sayılar korundu")
        return edited

    def accept(self, ctx: PipelineContext, output) -> None:
        for key, text in output.items():
            ctx.manuscript.sections[key] = text
        sr = ctx.job.stages[self.stage_id]
        sr.summary = (
            f"{len(output)} bölümde dil düzenlemesi uygulandı." if output
            else "Dil düzenlemesi uygulanmadı (şablon modu veya doğrulama koruması)."
        )
