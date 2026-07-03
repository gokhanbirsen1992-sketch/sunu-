"""Aşama 7: Uçtan uca son doğrulama + atıf montajı + Word çıktısı."""
from __future__ import annotations

import asyncio

from app.agents import validators
from app.manuscript import citations
from app.manuscript.docx_builder import build_docx
from app.models import ValidationIssue
from app.pipeline.stage import PipelineContext, Stage

SECTION_ORDER = ["intro", "methods", "results", "exploratory", "discussion", "limitations"]


class AssembleStage(Stage):
    stage_id = "assemble"
    name = "Son Doğrulama ve Çıktı"
    max_attempts = 1
    allow_degraded = False

    async def run(self, ctx: PipelineContext, attempt: int):
        m = ctx.manuscript
        lang = m.language

        async with self.agent(ctx, "Atıf Montajcısı", "worker", attempt) as h:
            ordered = [(k, m.sections.get(k, "")) for k in SECTION_ORDER]
            renumbered, cited_refs = citations.renumber(ordered, ctx.references)
            final_sections = {k: citations.to_intext(t, cited_refs, lang) for k, t in renumbered.items()}
            cited_refs.sort(key=lambda r: (r.authors[0].split()[-1].lower() if r.authors else "zzz", r.year or 0))
            await h.passed(f"{len(cited_refs)} kaynak atıf sırasına göre derlendi ve APA'ya dönüştürüldü")

        issues: list[ValidationIssue] = []
        async with self.agent(ctx, "Uçtan Uca Denetçi", "validator", attempt) as h:
            issues.extend(validators.check_required_sections(final_sections))
            leftover = citations.extract_marker_ids(" ".join(final_sections.values()))
            if leftover:
                issues.append(ValidationIssue(
                    severity="block", target="assemble",
                    message=f"Dönüştürülmemiş atıf işareti kaldı: {sorted(set(leftover))}",
                ))
            issues.extend(validators.check_pvalues_match(final_sections.get("results", ""), ctx.findings, "results"))
            blocks = [i for i in issues if i.severity == "block"]
            if blocks:
                await h.failed("; ".join(i.message for i in blocks))
                raise RuntimeError("Uçtan uca doğrulama başarısız: " + "; ".join(i.message for i in blocks))
            await h.passed("bölümler, atıflar ve sayılar uçtan uca tutarlı")

        m.sections = final_sections
        m.references = cited_refs

        async with self.agent(ctx, "Word Üretici", "worker", attempt) as h:
            out_path = ctx.job_dir / "output.docx"
            await asyncio.to_thread(build_docx, m, ctx.findings, ctx.cleaning_report, ctx.discovery, out_path)
            await h.passed(f"{out_path.name} oluşturuldu")

        return str(out_path), issues

    def accept(self, ctx: PipelineContext, output) -> None:
        out_path, issues = output
        ctx.job.output_docx = "output.docx"
        sr = ctx.job.stages[self.stage_id]
        sr.warnings.extend(i.message for i in issues if i.severity == "warn")
        sr.summary = (
            f"Makale {len(ctx.manuscript.references)} kaynakla derlendi; Word dosyası hazır."
        )
        sr.artifacts["manuscript"] = ctx.manuscript.model_dump()
