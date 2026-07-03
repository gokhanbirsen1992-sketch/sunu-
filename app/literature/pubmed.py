"""PubMed E-utilities istemcisi (anahtarsız; ≤3 istek/sn nezaket sınırı)."""
from __future__ import annotations

import asyncio
import xml.etree.ElementTree as ET

import httpx

from app.config import CONTACT_EMAIL
from app.models import Reference

BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
_sem = asyncio.Semaphore(2)


async def search(client: httpx.AsyncClient, query: str, retmax: int = 8) -> list[Reference]:
    common = {"tool": "paperforge", "email": CONTACT_EMAIL}
    async with _sem:
        resp = await client.get(
            f"{BASE}/esearch.fcgi",
            params={"db": "pubmed", "term": query, "retmax": retmax, "retmode": "json", **common},
        )
    resp.raise_for_status()
    ids = resp.json().get("esearchresult", {}).get("idlist", [])
    if not ids:
        return []
    await asyncio.sleep(0.34)
    async with _sem:
        resp = await client.get(
            f"{BASE}/efetch.fcgi",
            params={"db": "pubmed", "id": ",".join(ids), "retmode": "xml", **common},
        )
    resp.raise_for_status()
    return _parse_efetch(resp.text)


def _parse_efetch(xml_text: str) -> list[Reference]:
    refs = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []
    for art in root.findall(".//PubmedArticle"):
        title_el = art.find(".//ArticleTitle")
        title = "".join(title_el.itertext()).strip() if title_el is not None else ""
        if not title:
            continue
        pmid = (art.findtext(".//PMID") or "").strip() or None
        year_text = art.findtext(".//JournalIssue/PubDate/Year") or art.findtext(".//PubDate/MedlineDate", "")
        year = None
        for token in (year_text or "").split():
            if token[:4].isdigit():
                year = int(token[:4])
                break
        authors = []
        for a in art.findall(".//AuthorList/Author")[:20]:
            last, fore = a.findtext("LastName"), a.findtext("ForeName")
            if last:
                authors.append(f"{fore} {last}" if fore else last)
        abstract = " ".join(
            "".join(t.itertext()).strip() for t in art.findall(".//Abstract/AbstractText")
        ).strip()[:2000] or None
        doi = None
        for el in art.findall(".//ArticleIdList/ArticleId"):
            if el.get("IdType") == "doi" and el.text:
                doi = el.text.strip().lower()
        refs.append(
            Reference(
                pmid=pmid, doi=doi, title=title, authors=authors, year=year,
                journal=art.findtext(".//Journal/Title"),
                volume=art.findtext(".//JournalIssue/Volume"),
                issue=art.findtext(".//JournalIssue/Issue"),
                pages=art.findtext(".//Pagination/MedlinePgn"),
                abstract=abstract, source_api="pubmed",
            )
        )
    return refs
