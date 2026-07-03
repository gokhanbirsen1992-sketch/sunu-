"""Crossref istemcisi (anahtarsız, ücretsiz)."""
from __future__ import annotations

import re

import httpx

from app.config import CONTACT_EMAIL
from app.models import Reference

_TAG_RE = re.compile(r"<[^>]+>")


async def search(client: httpx.AsyncClient, query: str, rows: int = 10) -> list[Reference]:
    resp = await client.get(
        "https://api.crossref.org/works",
        params={"query": query, "rows": rows, "mailto": CONTACT_EMAIL,
                "filter": "type:journal-article"},
    )
    resp.raise_for_status()
    refs = []
    for item in resp.json().get("message", {}).get("items", []):
        titles = item.get("title") or []
        if not titles:
            continue
        year = None
        for key in ("published-print", "published-online", "issued"):
            parts = (item.get(key) or {}).get("date-parts") or []
            if parts and parts[0] and parts[0][0]:
                year = int(parts[0][0])
                break
        abstract = item.get("abstract")
        if abstract:
            abstract = _TAG_RE.sub(" ", abstract).strip()[:2000] or None
        refs.append(
            Reference(
                doi=(item.get("DOI") or "").lower() or None,
                title=titles[0],
                authors=[
                    " ".join(x for x in [a.get("given"), a.get("family")] if x)
                    for a in (item.get("author") or [])[:20]
                ],
                year=year,
                journal=(item.get("container-title") or [None])[0],
                volume=item.get("volume"),
                issue=item.get("issue"),
                pages=item.get("page"),
                abstract=abstract,
                cited_by=int(item.get("is-referenced-by-count") or 0),
                source_api="crossref",
            )
        )
    return refs
