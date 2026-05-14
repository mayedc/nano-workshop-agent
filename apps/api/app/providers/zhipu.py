import asyncio
from typing import Any

from app.core.config import settings
from app.providers.base import LLMProvider


class ZhipuLLMProvider(LLMProvider):
    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        max_tokens: int = 4096,
    ) -> None:
        self.api_key = api_key or settings.ZHIPU_API_KEY or ""
        self.model = model or settings.LLM_MODEL
        self.max_tokens = max_tokens

    async def generate(self, prompt: str, **kwargs: Any) -> str:
        try:
            from zhipuai import ZhipuAI
        except ImportError as exc:
            raise RuntimeError("zhipuai SDK not installed. Run: pip install zhipuai") from exc

        client = ZhipuAI(api_key=self.api_key)
        messages: list[dict[str, str]] = []
        system = kwargs.get("system")
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
            ),
        )
        return response.choices[0].message.content
