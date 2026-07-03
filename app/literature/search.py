"""Literatür arama orkestrasyonu: sorgu üret → 3 API'ye paralel sor → dedupe → skorla → seç."""
from __future__ import annotations

import asyncio
import re
from datetime import date
from typing import Awaitable, Callable

import httpx

from app import config
from app.literature import crossref, openalex, pubmed
from app.models import Finding, Reference

TIMEOUT = httpx.Timeout(15.0)

EmitRef = Callable[[Reference], Awaitable[None]] | None


def _norm_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", title.lower())[:80]


def _dedupe(refs: list[Reference]) -> list[Reference]:
    seen: dict[str, Reference] = {}
    for r in refs:
        key = r.doi.lower() if r.doi else ("t:" + _norm_title(r.title))
        if key in seen:
            old = seen[key]
            old.abstract = old.abstract or r.abstract
            old.cited_by = max(old.cited_by, r.cited_by)
            old.pmid = old.pmid or r.pmid
            old.linked_findings = sorted(set(old.linked_findings + r.linked_findings))
        else:
            seen[key] = r
    return list(seen.values())


def _score(r: Reference, query_terms: set[str]) -> float:
    import math

    title_terms = set(re.findall(r"[a-zçğıöşü]+", r.title.lower()))
    overlap = len(query_terms & title_terms) / max(len(query_terms), 1)
    recency = 0.0
    if r.year:
        age = max(date.today().year - r.year, 0)
        recency = max(0.0, 1.0 - age / 20.0)
    return overlap * 2.0 + math.log1p(r.cited_by) / 10.0 + recency + (0.5 if r.abstract else 0.0)


async def _query_all(client: httpx.AsyncClient, query: str) -> list[Reference]:
    async def safe(coro) -> list[Reference]:
        try:
            return await coro
        except Exception:
            return []

    results = await asyncio.gather(
        safe(openalex.search(client, query)),
        safe(crossref.search(client, query)),
        safe(pubmed.search(client, query)),
    )
    return [r for batch in results for r in batch]


async def gather_literature(
    queries_by_finding: dict[str, list[str]],
    intro_queries: list[str],
    max_refs_per_finding: int = 5,
    intro_pool_size: int = 8,
    emit_ref: EmitRef = None,
    emit_progress: Callable[[str], Awaitable[None]] | None = None,
) -> tuple[list[Reference], dict[str, list[int]]]:
    """Kaynak listesi (id atanmış) + bulgu→kaynak id eşlemesi döndürür.

    queries_by_finding: {"F1": ["query a", "query b"], ...}; intro havuzu "INTRO" anahtarıyla eklenir.
    """
    if config.is_offline():
        return [], {}

    selected: list[Reference] = []
    mapping: dict[str, list[int]] = {}

    async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
        all_targets = list(queries_by_finding.items()) + ([("INTRO", intro_queries)] if intro_queries else [])
        for target_id, queries in all_targets:
            candidates: list[Reference] = []
            for q in queries[:3]:
                if emit_progress:
                    await emit_progress(f"Aranıyor: “{q}”")
                batch = await _query_all(client, q)
                terms = set(re.findall(r"[a-zçğıöşü]+", q.lower()))
                for r in batch:
                    r.score = max(r.score, _score(r, terms))
                    if target_id != "INTRO":
                        r.linked_findings = sorted(set(r.linked_findings + [target_id]))
                candidates.extend(batch)
            candidates = _dedupe(candidates)
            candidates.sort(key=lambda r: r.score, reverse=True)
            limit = intro_pool_size if target_id == "INTRO" else max_refs_per_finding
            top = candidates[:limit]
            for r in top:
                selected.append(r)
                if emit_ref:
                    await emit_ref(r)

    selected = _dedupe(selected)
    selected.sort(key=lambda r: r.score, reverse=True)
    for i, r in enumerate(selected, start=1):
        r.id = i
        for fid in r.linked_findings:
            mapping.setdefault(fid, []).append(r.id)
    return selected, mapping
