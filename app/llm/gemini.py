"""Google Gemini (AI Studio ücretsiz katman) — saf REST, SDK bağımlılığı yok."""
from __future__ import annotations

import httpx

from app.llm.provider import LLMError, LLMProvider, LLMResponse

BASE = "https://generativelanguage.googleapis.com/v1beta"


class GeminiProvider(LLMProvider):
    name = "gemini"

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        self.api_key = api_key
        self.model = model

    async def complete(self, system, user, *, json_mode=False, temperature=0.7, max_tokens=4096) -> LLMResponse:
        payload: dict = {
            "contents": [{"role": "user", "parts": [{"text": user}]}],
            "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens},
        }
        if self.model.startswith("gemini-2.5"):
            # 2.5 modelleri varsayılan "düşünme" token'larını çıktı bütçesinden harcar; kapat
            payload["generationConfig"]["thinkingConfig"] = {"thinkingBudget": 0}
        if system:
            payload["systemInstruction"] = {"parts": [{"text": system}]}
        if json_mode:
            payload["generationConfig"]["responseMimeType"] = "application/json"
        url = f"{BASE}/models/{self.model}:generateContent"
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(url, params={"key": self.api_key}, json=payload)
        if resp.status_code == 429:
            raise LLMError("Gemini kota/limit (429)", retryable=True, retry_after=_retry_after(resp))
        if resp.status_code in (401, 403):
            raise LLMError(f"Gemini anahtar hatası ({resp.status_code})")
        if resp.status_code >= 500:
            raise LLMError(f"Gemini sunucu hatası ({resp.status_code})", retryable=True)
        if resp.status_code != 200:
            raise LLMError(f"Gemini hata {resp.status_code}: {resp.text[:200]}")
        data = resp.json()
        try:
            parts = data["candidates"][0]["content"]["parts"]
            text = "".join(p.get("text", "") for p in parts)
        except (KeyError, IndexError) as exc:
            raise LLMError(f"Gemini beklenmedik yanıt: {exc}") from exc
        if not text.strip():
            raise LLMError("Gemini boş yanıt döndürdü", retryable=True)
        return LLMResponse(text=text, provider=self.name, model=self.model)


def _retry_after(resp: httpx.Response) -> float | None:
    val = resp.headers.get("retry-after")
    try:
        return float(val) if val else None
    except ValueError:
        return None
