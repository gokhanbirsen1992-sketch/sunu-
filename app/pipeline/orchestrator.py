"""Aşama sırası ve pipeline yürütücüsü."""
from __future__ import annotations

from app.pipeline.stage import PipelineContext, Stage
from app.pipeline.stages.s1_clean import CleanStage
from app.pipeline.stages.s2_stats import StatsStage
from app.pipeline.stages.s2b_discovery import DiscoveryStage
from app.pipeline.stages.s3_literature import LiteratureStage
from app.pipeline.stages.s4_writing import WritingStage
from app.pipeline.stages.s5_editing import EditingStage
from app.pipeline.stages.s6_review import ReviewStage
from app.pipeline.stages.s7_assemble import AssembleStage


def build_stages() -> list[Stage]:
    return [
        CleanStage(),
        StatsStage(),
        DiscoveryStage(),
        LiteratureStage(),
        WritingStage(),
        EditingStage(),
        ReviewStage(),
        AssembleStage(),
    ]


STAGE_ORDER = [
    ("clean", "Veri Temizleme"),
    ("stats", "İstatistik Analizi"),
    ("discovery", "Keşifsel Örüntü ve Risk Analizi"),
    ("literature", "Literatür Taraması"),
    ("writing", "Makale Yazımı"),
    ("editing", "Dil Düzenleme"),
    ("review", "Reviewer 2"),
    ("assemble", "Son Doğrulama ve Çıktı"),
]


async def run_pipeline(ctx: PipelineContext) -> None:
    for stage in build_stages():
        await stage.execute(ctx)
