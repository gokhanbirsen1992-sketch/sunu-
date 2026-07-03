"""Tüm pipeline'ın paylaştığı veri modelleri."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


def new_id(prefix: str = "") -> str:
    return prefix + uuid.uuid4().hex[:12]


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class JobStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class JobConfig(BaseModel):
    language: Literal["tr", "en"] = "tr"
    provider: Literal["auto", "gemini", "groq", "openrouter", "template"] = "auto"
    alpha: float = 0.05
    p_adjust: Literal["none", "holm", "fdr_bh"] = "holm"
    max_refs_per_finding: int = 5
    n_workers: int = 2  # aşama başına paralel işçi ajan sayısı
    topic_hint: Optional[str] = None


VarKind = Literal["continuous", "ordinal", "nominal", "binary", "id", "date", "excluded"]


class VariableInfo(BaseModel):
    name: str
    label: Optional[str] = None
    kind: VarKind = "excluded"
    role: Literal["auto", "dv", "iv", "exclude"] = "auto"
    n_missing: int = 0
    n_unique: int = 0
    value_labels: Optional[dict[str, str]] = None

    @property
    def display(self) -> str:
        return self.label or self.name


class NormalityResult(BaseModel):
    n: int
    shapiro_w: Optional[float] = None
    shapiro_p: Optional[float] = None
    skew: Optional[float] = None
    kurtosis: Optional[float] = None
    normal: bool = False
    basis: str = ""


class PlannedTest(BaseModel):
    id: str = Field(default_factory=lambda: new_id("t"))
    test_id: str  # ttest_ind | welch_t | mannwhitney | anova | kruskal | chi2 | fisher | pearson | spearman | linreg
    family: Literal["group", "correlation", "association", "regression"]
    dv: str
    iv: Optional[str] = None
    extra_vars: list[str] = Field(default_factory=list)
    rationale_tr: str = ""
    rationale_en: str = ""
    checks: dict[str, Any] = Field(default_factory=dict)


class Finding(BaseModel):
    id: str = ""
    planned: PlannedTest
    statistic_name: str = ""
    statistic: Optional[float] = None
    df: Any = None
    p_value: Optional[float] = None
    p_adjusted: Optional[float] = None
    effect_size_name: Optional[str] = None
    effect_size: Optional[float] = None
    group_stats: list[dict[str, Any]] = Field(default_factory=list)
    posthoc: list[dict[str, Any]] = Field(default_factory=list)
    significant: bool = False
    apa_tr: str = ""
    apa_en: str = ""
    keywords: list[str] = Field(default_factory=list)
    error: Optional[str] = None


class Reference(BaseModel):
    id: int = 0
    doi: Optional[str] = None
    pmid: Optional[str] = None
    title: str
    authors: list[str] = Field(default_factory=list)
    year: Optional[int] = None
    journal: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    abstract: Optional[str] = None
    source_api: str = ""
    score: float = 0.0
    cited_by: int = 0
    linked_findings: list[str] = Field(default_factory=list)


class AgentRun(BaseModel):
    agent_id: str = Field(default_factory=lambda: new_id("a"))
    name: str
    role: Literal["worker", "validator", "selector"]
    status: Literal["pending", "running", "passed", "failed"] = "pending"
    attempt: int = 1
    detail: Optional[str] = None


class StageResult(BaseModel):
    stage_id: str
    name: str
    status: Literal["pending", "running", "passed", "failed", "skipped"] = "pending"
    attempts: int = 0
    agents: list[AgentRun] = Field(default_factory=list)
    summary: Optional[str] = None
    warnings: list[str] = Field(default_factory=list)
    artifacts: dict[str, Any] = Field(default_factory=dict)


class CleaningReport(BaseModel):
    rows_before: int = 0
    rows_after: int = 0
    duplicates_removed: int = 0
    high_missing_rows_removed: int = 0
    constant_columns: list[str] = Field(default_factory=list)
    missing_summary: dict[str, int] = Field(default_factory=dict)
    outliers: dict[str, int] = Field(default_factory=dict)
    actions: list[str] = Field(default_factory=list)


class ReviewCritique(BaseModel):
    id: str = Field(default_factory=lambda: new_id("c"))
    section: str = "general"
    critique: str
    requires_new_literature: bool = False
    addressed: bool = False
    response: str = ""


class Manuscript(BaseModel):
    title: str = ""
    language: Literal["tr", "en"] = "tr"
    sections: dict[str, str] = Field(default_factory=dict)  # intro/methods/results/discussion/limitations
    references: list[Reference] = Field(default_factory=list)
    reviewer_rounds: list[dict[str, Any]] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class ValidationIssue(BaseModel):
    severity: Literal["block", "warn"]
    message: str
    target: str = ""


class Job(BaseModel):
    id: str = Field(default_factory=lambda: new_id("j"))
    created_at: datetime = Field(default_factory=utcnow)
    status: JobStatus = JobStatus.pending
    config: JobConfig = Field(default_factory=JobConfig)
    filename: str = ""
    variables: list[VariableInfo] = Field(default_factory=list)
    current_stage: Optional[str] = None
    stages: dict[str, StageResult] = Field(default_factory=dict)
    findings: list[Finding] = Field(default_factory=list)
    n_references: int = 0
    error: Optional[str] = None
    output_docx: Optional[str] = None
    warnings: list[str] = Field(default_factory=list)
