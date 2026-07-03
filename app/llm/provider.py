"""LLM sağlayıcı soyutlaması."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


class LLMError(Exception):
    """Sağlayıcıdan kalıcı hata (kota, kimlik, servis)."""

    def __init__(self, message: str, retryable: bool = False, retry_after: float | None = None):
        super().__init__(message)
        self.retryable = retryable
        self.retry_after = retry_after


class LLMUnavailable(Exception):
    """Hiçbir LLM sağlayıcı yanıt veremedi — şablon moduna düşülmeli."""


@dataclass
class LLMResponse:
    text: str
    provider: str
    model: str


class LLMProvider(ABC):
    name: str = "base"
    model: str = ""

    @abstractmethod
    async def complete(
        self,
        system: str,
        user: str,
        *,
        json_mode: bool = False,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> LLMResponse: ...
