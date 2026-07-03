"""Sağlayıcı yönlendirici: seçili sağlayıcı → yedekler → şablon modu.

Ücretsiz katman dostu: global eşzamanlılık kilidi + 429'da backoff + sıradakine düşme.
"""
from __future__ import annotations

import asyncio
import json
import re
from typing import Any, Awaitable, Callable

from app.config import DEFAULT_MODELS
from app.llm.gemini import GeminiProvider
from app.llm.openai_compat import groq_provider, openrouter_provider
from app.llm.provider import LLMError, LLMProvider, LLMResponse, LLMUnavailable

PROVIDER_ORDER = ["gemini", "groq", "openrouter"]
MAX_TRIES_PER_PROVIDER = 3


def build_providers(keys: dict[str, str], preferred: str = "auto") -> list[LLMProvider]:
    factories: dict[str, Callable[[str], LLMProvider]] = {
        "gemini": lambda k: GeminiProvider(k, DEFAULT_MODELS["gemini"]),
        "groq": lambda k: groq_provider(k, DEFAULT_MODELS["groq"]),
        "openrouter": lambda k: openrouter_provider(k, DEFAULT_MODELS["openrouter"]),
    }
    if preferred == "template":
        return []
    order = PROVIDER_ORDER if preferred == "auto" else [preferred] + [p for p in PROVIDER_ORDER if p != preferred]
    return [factories[p](keys[p]) for p in order if p in keys and keys[p]]


class LLMRouter:
    def __init__(self, keys: dict[str, str], preferred: str = "auto",
                 on_log: Callable[[str], Awaitable[None]] | None = None):
        self.providers = build_providers(keys, preferred)
        self._dead: set[str] = set()
        self._sem = asyncio.Semaphore(2)
        self._on_log = on_log

    @property
    def mode(self) -> str:
        return "llm" if [p for p in self.providers if p.name not in self._dead] else "template"

    async def _log(self, msg: str) -> None:
        if self._on_log:
            await self._on_log(msg)

    async def complete(self, system: str, user: str, *, json_mode: bool = False,
                       temperature: float = 0.7, max_tokens: int = 4096) -> LLMResponse:
        last_error: Exception | None = None
        for provider in self.providers:
            if provider.name in self._dead:
                continue
            for attempt in range(1, MAX_TRIES_PER_PROVIDER + 1):
                try:
                    async with self._sem:
                        return await provider.complete(
                            system, user, json_mode=json_mode,
                            temperature=temperature, max_tokens=max_tokens,
                        )
                except LLMError as exc:
                    last_error = exc
                    if exc.retryable and attempt < MAX_TRIES_PER_PROVIDER:
                        delay = exc.retry_after or (2.0 * 2 ** (attempt - 1))
                        await asyncio.sleep(min(delay, 30))
                        continue
                    if not exc.retryable:
                        self._dead.add(provider.name)
                        await self._log(f"{provider.name} devre dışı: {exc}")
                    break
                except Exception as exc:  # ağ hataları vb.
                    last_error = exc
                    if attempt < MAX_TRIES_PER_PROVIDER:
                        await asyncio.sleep(2.0 * 2 ** (attempt - 1))
                        continue
                    break
            else:
                continue
            await self._log(f"{provider.name} yanıt veremedi, sıradaki sağlayıcı deneniyor…")
        raise LLMUnavailable(str(last_error) if last_error else "LLM sağlayıcı yok")

    async def complete_json(self, system: str, user: str, *, temperature: float = 0.4,
                            max_tokens: int = 4096) -> Any:
        resp = await self.complete(system, user, json_mode=True, temperature=temperature, max_tokens=max_tokens)
        parsed = extract_json(resp.text)
        if parsed is not None:
            return parsed
        # tek onarım denemesi
        repair = await self.complete(
            "Yalnızca geçerli JSON döndür. Başka hiçbir şey yazma.",
            f"Şu metni geçerli JSON'a çevir:\n\n{resp.text[:6000]}",
            json_mode=True, temperature=0.0, max_tokens=max_tokens,
        )
        parsed = extract_json(repair.text)
        if parsed is None:
            raise LLMUnavailable("LLM geçerli JSON üretemedi")
        return parsed


def extract_json(text: str) -> Any:
    """Kod bloklarını soyup ilk JSON nesnesini/dizisini toleranslı biçimde çıkarır."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.MULTILINE).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    for opener, closer in (("{", "}"), ("[", "]")):
        start = text.find(opener)
        if start == -1:
            continue
        depth = 0
        for i in range(start, len(text)):
            if text[i] == opener:
                depth += 1
            elif text[i] == closer:
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start : i + 1])
                    except json.JSONDecodeError:
                        break
    return None
