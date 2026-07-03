"""OpenAlex istemcisi (anahtarsız, ücretsiz)."""
from __future__ import annotations

import httpx

from app.config import CONTACT_EMAIL
from app.models import Reference


def _abstract_from_inverted(inv: dict | None) -> str | None:
    if not inv:
        return None
    positions: list[tuple[int, str]] = []
    for word, idxs in inv.items():
        for i in idxs:
            positions.append((i, word))
    positions.sort()
    text = " ".join(w for _, w in positions)
    return text[:2000] or None


async def search(client: httpx.AsyncClient, query: str, per_page: int = 10) -> list[Reference]:
    resp = await client.get(
        "https://api.openalex.org/works",
        params={"search": query, "per-page": per_page, "mailto": CONTACT_EMAIL,
                "filter": "type:article"},
    )
    resp.raise_for_status()
    refs = []
    for item in resp.json().get("results", []):
        doi = (item.get("doi") or "").replace("https://doi.org/", "") or None
        loc = item.get("primary_location") or {}
        source = loc.get("source") or {}
        biblio = item.get("biblio") or {}
        pages = None
        if biblio.get("first_page"):
            pages = biblio["first_page"] + (f"-{biblio['last_page']}" if biblio.get("last_page") else "")
        refs.append(
            Reference(
                doi=doi,
                title=item.get("display_name") or "",
                authors=[
                    (a.get("author") or {}).get("display_name", "")
                    for a in (item.get("authorships") or [])[:20]
                ],
                year=item.get("publication_year"),
                journal=source.get("display_name"),
                volume=biblio.get("volume"),
                issue=biblio.get("issue"),
                pages=pages,
                abstract=_abstract_from_inverted(item.get("abstract_inverted_index")),
                cited_by=int(item.get("cited_by_count") or 0),
                source_api="openalex",
            )
        )
    return [r for r in refs if r.title]
