from typing import Any

from app.core.config import settings
from app.core.encryption import decrypt_value
from app.providers.base import LLMProvider
from app.providers.claude import ClaudeLLMProvider
from app.providers.mock import MockLLMProvider
from app.providers.openai_compatible import OpenAICompatibleProvider
from app.providers.zhipu import ZhipuLLMProvider

DEFAULT_BASE_URLS: dict[str, str] = {
    "openai": "https://api.openai.com/v1",
    "deepseek": "https://api.deepseek.com/v1",
    "gemini": "https://generativelanguage.googleapis.com/v1beta/openai/",
}


def create_llm_provider(project_config: dict[str, Any] | None = None) -> LLMProvider:
    llm_config: dict[str, Any] | None = None
    if project_config:
        llm_config = project_config.get("llm_config")

    provider = (llm_config or {}).get("provider", settings.LLM_PROVIDER)
    model = (llm_config or {}).get("model", settings.LLM_MODEL)
    max_tokens = (llm_config or {}).get("max_tokens", settings.LLM_MAX_TOKENS)
    base_url = (llm_config or {}).get("base_url", "")

    api_key = (llm_config or {}).get("api_key")
    if api_key:
        try:
            api_key = decrypt_value(api_key)
        except Exception:
            pass

    if provider == "anthropic":
        return ClaudeLLMProvider(api_key=api_key, model=model, max_tokens=max_tokens)

    if provider == "zhipu":
        return ZhipuLLMProvider(api_key=api_key, model=model, max_tokens=max_tokens)

    if provider in ("openai", "deepseek", "gemini"):
        resolved_base_url = base_url or DEFAULT_BASE_URLS.get(provider, "")
        return OpenAICompatibleProvider(
            api_key=api_key,
            model=model,
            max_tokens=max_tokens,
            base_url=resolved_base_url,
        )

    return MockLLMProvider()
