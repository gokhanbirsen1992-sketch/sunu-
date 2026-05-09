from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Iterable

import requests


PUBMED_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
USER_AGENT = "stats-lit-pipeline/0.1 (research)"


@dataclass
class Paper:
    pmid: str
    title: str
    journal: str
    year: str
    authors: list[str]
    abstract: str
    doi: str | None

    @property
    def url(self) -> str:
        if self.doi:
            return f"https://doi.org/{self.doi}"
        return f"https://pubmed.ncbi.nlm.nih.gov/{self.pmid}/"

    def short_citation(self) -> str:
        first = self.authors[0] if self.authors else "Anon"
        et_al = " et al." if len(self.authors) > 1 else ""
        return f"{first}{et_al} ({self.year}). {self.journal}. PMID:{self.pmid}"


def _esearch(query: str, retmax: int = 10, api_key: str | None = None) -> list[str]:
    params = {"db": "pubmed", "term": query, "retmode": "json", "retmax": retmax, "sort": "relevance"}
    if api_key:
        params["api_key"] = api_key
    r = requests.get(f"{PUBMED_BASE}/esearch.fcgi", params=params,
                     headers={"User-Agent": USER_AGENT}, timeout=30)
    r.raise_for_status()
    return r.json().get("esearchresult", {}).get("idlist", [])


def _efetch(pmids: Iterable[str], api_key: str | None = None) -> list[Paper]:
    pmids = list(pmids)
    if not pmids:
        return []
    params = {"db": "pubmed", "id": ",".join(pmids), "retmode": "xml"}
    if api_key:
        params["api_key"] = api_key
    r = requests.get(f"{PUBMED_BASE}/efetch.fcgi", params=params,
                     headers={"User-Agent": USER_AGENT}, timeout=60)
    r.raise_for_status()

    from xml.etree import ElementTree as ET
    root = ET.fromstring(r.content)
    out: list[Paper] = []
    for art in root.findall(".//PubmedArticle"):
        pmid = (art.findtext(".//PMID") or "").strip()
        title = (art.findtext(".//ArticleTitle") or "").strip()
        journal = (art.findtext(".//Journal/Title") or "").strip()
        year = (art.findtext(".//PubDate/Year")
                or art.findtext(".//PubDate/MedlineDate") or "").strip()[:4]
        authors = []
        for a in art.findall(".//Author"):
            ln = a.findtext("LastName") or ""
            fi = a.findtext("Initials") or ""
            if ln:
                authors.append(f"{ln} {fi}".strip())
        abs_chunks = [e.text or "" for e in art.findall(".//Abstract/AbstractText")]
        abstract = " ".join(abs_chunks).strip()
        doi = None
        for el in art.findall(".//ArticleId"):
            if el.get("IdType") == "doi":
                doi = (el.text or "").strip()
                break
        out.append(Paper(pmid=pmid, title=title, journal=journal, year=year,
                         authors=authors, abstract=abstract, doi=doi))
    return out


def search_pubmed(query: str, max_results: int = 8, api_key: str | None = None) -> list[Paper]:
    api_key = api_key or os.environ.get("PUBMED_API_KEY")
    pmids = _esearch(query, retmax=max_results, api_key=api_key)
    if not pmids:
        return []
    time.sleep(0.34 if not api_key else 0.11)
    return _efetch(pmids, api_key=api_key)


def build_query(feature: str, outcome: str, extra_terms: list[str] | None = None) -> str:
    parts = [f'"{feature}"', f'"{outcome}"']
    if extra_terms:
        parts.extend(f'"{t}"' for t in extra_terms)
    return " AND ".join(parts)


def search_for_findings(
    findings: list[dict],
    extra_terms: list[str] | None = None,
    max_per_finding: int = 5,
    api_key: str | None = None,
) -> dict[str, list[Paper]]:
    out: dict[str, list[Paper]] = {}
    for f in findings:
        q = build_query(f["feature"], f["outcome"], extra_terms)
        try:
            out[f["feature"]] = search_pubmed(q, max_results=max_per_finding, api_key=api_key)
        except Exception as e:
            out[f["feature"]] = []
            out.setdefault("_errors", []).append(f"{f['feature']}: {e}")
        time.sleep(0.34 if not api_key else 0.11)
    return out
