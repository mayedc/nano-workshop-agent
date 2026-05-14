from typing import Any

import anthropic

from app.core.config import settings
from app.providers.base import LLMProvider


class ClaudeLLMProvider(LLMProvider):
    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        max_tokens: int = 4096,
    ) -> None:
        self.api_key = api_key or settings.ANTHROPIC_API_KEY or ""
        self.model = model or settings.LLM_MODEL
        self.max_tokens = max_tokens
        self._client = anthropic.AsyncAnthropic(api_key=self.api_key)

    async def generate(self, prompt: str, **kwargs: Any) -> str:
        system = kwargs.get("system")
        messages: list[dict[str, str]] = [{"role": "user", "content": prompt}]
        params: dict[str, Any] = {
            "model": self.model,
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "messages": messages,
        }
        if system:
            params["system"] = system
        response = await self._client.messages.create(**params)
        content = response.content[0].text if response.content else ""
        return content
