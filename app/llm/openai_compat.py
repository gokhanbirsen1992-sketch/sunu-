"""OpenAI-uyumlu chat/completions sağlayıcıları: Groq ve OpenRouter."""
from __future__ import annotations

import httpx

from app.llm.provider import LLMError, LLMProvider, LLMResponse


class OpenAICompatProvider(LLMProvider):
    def __init__(self, name: str, base_url: str, api_key: str, model: str):
        self.name = name
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model

    async def complete(self, system, user, *, json_mode=False, temperature=0.7, max_tokens=4096) -> LLMResponse:
        payload: dict = {
            "model": self.model,
            "messages": (
                ([{"role": "system", "content": system}] if system else [])
                + [{"role": "user", "content": user}]
            ),
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
        if resp.status_code == 429:
            val = resp.headers.get("retry-after")
            try:
                retry_after = float(val) if val else None
            except ValueError:
                retry_after = None
            raise LLMError(f"{self.name} kota/limit (429)", retryable=True, retry_after=retry_after)
        if resp.status_code in (401, 403):
            raise LLMError(f"{self.name} anahtar hatası ({resp.status_code})")
        if resp.status_code >= 500:
            raise LLMError(f"{self.name} sunucu hatası ({resp.status_code})", retryable=True)
        if resp.status_code != 200:
            raise LLMError(f"{self.name} hata {resp.status_code}: {resp.text[:200]}")
        data = resp.json()
        try:
            text = data["choices"][0]["message"]["content"] or ""
        except (KeyError, IndexError) as exc:
            raise LLMError(f"{self.name} beklenmedik yanıt: {exc}") from exc
        if not text.strip():
            raise LLMError(f"{self.name} boş yanıt döndürdü", retryable=True)
        return LLMResponse(text=text, provider=self.name, model=self.model)


def groq_provider(api_key: str, model: str) -> OpenAICompatProvider:
    return OpenAICompatProvider("groq", "https://api.groq.com/openai/v1", api_key, model)


def openrouter_provider(api_key: str, model: str) -> OpenAICompatProvider:
    return OpenAICompatProvider("openrouter", "https://openrouter.ai/api/v1", api_key, model)
