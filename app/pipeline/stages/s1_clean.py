"""Aşama 1: Veri yükleme + temizleme."""
from __future__ import annotations

import asyncio

import pandas as pd

from app.models import ValidationIssue, VariableInfo
from app.pipeline.stage import PipelineContext, Stage
from app.statistics.cleaning import clean
from app.statistics.loader import load_dataset
from app.statistics.vartypes import infer_types


def _apply_value_labels(df: pd.DataFrame, variables: list[VariableInfo]) -> pd.DataFrame:
    """Nominal/binary değişkenlerde ham kodları (1.0) etiketlere (Kadın) çevirir."""
    df = df.copy()
    for v in variables:
        if v.kind not in ("nominal", "binary") or not v.value_labels or v.name not in df.columns:
            continue
        labels = dict(v.value_labels)

        def _map(x):
            if pd.isna(x):
                return x
            for key in (str(x), str(int(x)) if isinstance(x, float) and float(x).is_integer() else None):
                if key is not None and key in labels:
                    return labels[key]
            return x

        df[v.name] = df[v.name].map(_map)
    return df


class CleanStage(Stage):
    stage_id = "clean"
    name = "Veri Temizleme"
    allow_degraded = False

    async def run(self, ctx: PipelineContext, attempt: int):
        async with self.agent(ctx, "Veri Yükleyici", "worker", attempt) as h:
            df, meta = await asyncio.to_thread(load_dataset, ctx.input_path)
            await h.passed(f"{len(df)} satır, {len(df.columns)} sütun yüklendi")

        async with self.agent(ctx, "Tip Müfettişi", "worker", attempt) as h:
            if not ctx.job.variables:
                ctx.job.variables = infer_types(df, meta)
            kinds = [v.kind for v in ctx.job.variables]
            await h.passed(
                f"{kinds.count('continuous')} sürekli, {kinds.count('ordinal')} sıralayıcı, "
                f"{kinds.count('nominal') + kinds.count('binary')} kategorik değişken"
            )

        async with self.agent(ctx, "Temizlik Ajanı", "worker", attempt) as h:
            df_clean, report = await asyncio.to_thread(clean, df, ctx.job.variables)
            df_clean = _apply_value_labels(df_clean, ctx.job.variables)
            await h.passed(f"{report.rows_before} → {report.rows_after} satır")

        return df_clean, meta, report

    async def validate(self, ctx: PipelineContext, output, attempt: int):
        df_clean, _, _ = output
        issues: list[ValidationIssue] = []
        async with self.agent(ctx, "Bütünlük Denetçisi", "validator", attempt) as h:
            usable = [v for v in ctx.job.variables if v.kind in ("continuous", "ordinal", "nominal", "binary")]
            if len(df_clean) < 10:
                issues.append(ValidationIssue(severity="block", message="Temizlik sonrası 10'dan az satır kaldı; analiz yapılamaz.", target="clean"))
            if len(usable) < 2:
                issues.append(ValidationIssue(severity="block", message="Analize uygun en az 2 değişken gerekli.", target="clean"))
            if len(df_clean) < 30:
                issues.append(ValidationIssue(severity="warn", message=f"Örneklem küçük (n={len(df_clean)}); testlerin gücü düşük olabilir.", target="clean"))
            if issues and any(i.severity == "block" for i in issues):
                await h.failed("; ".join(i.message for i in issues))
            else:
                await h.passed("veri bütünlüğü uygun")
        return issues

    def accept(self, ctx: PipelineContext, output) -> None:
        df_clean, meta, report = output
        ctx.df, ctx.meta, ctx.cleaning_report = df_clean, meta, report
        sr = ctx.job.stages[self.stage_id]
        sr.summary = (
            f"{report.rows_before} satırdan {report.rows_after} satıra temizlendi "
            f"({report.duplicates_removed} kopya, {report.high_missing_rows_removed} aşırı eksik satır, "
            f"{sum(report.outliers.values())} aykırı değer)."
        )
        sr.artifacts["cleaning_report"] = report.model_dump()
