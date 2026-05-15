from typing import Any

from app.providers.base import LLMProvider


class OpenAICompatibleProvider(LLMProvider):
    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        max_tokens: int = 4096,
        base_url: str | None = None,
    ) -> None:
        self.api_key = api_key or ""
        self.model = model or "gpt-4o"
        self.max_tokens = max_tokens
        self.base_url = base_url

    async def generate(self, prompt: str, **kwargs: Any) -> str:
        try:
            from openai import AsyncOpenAI
        except ImportError as exc:
            raise RuntimeError("openai SDK not installed. Run: pip install openai") from exc

        client_kwargs: dict[str, Any] = {"api_key": self.api_key}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url
        client = AsyncOpenAI(**client_kwargs)

        messages: list[dict[str, str]] = []
        system = kwargs.get("system")
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = await client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
        )
        return response.choices[0].message.content or ""
