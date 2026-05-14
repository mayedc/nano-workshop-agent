from typing import Any

from app.core.config import settings
from app.core.encryption import decrypt_value
from app.providers.base import LLMProvider
from app.providers.claude import ClaudeLLMProvider
from app.providers.mock import MockLLMProvider
from app.providers.zhipu import ZhipuLLMProvider


def create_llm_provider(project_config: dict[str, Any] | None = None) -> LLMProvider:
    """Create an LLM provider from project config or fall back to global settings."""
    llm_config: dict[str, Any] | None = None
    if project_config:
        llm_config = project_config.get("llm_config")

    provider = (llm_config or {}).get("provider", settings.LLM_PROVIDER)
    model = (llm_config or {}).get("model", settings.LLM_MODEL)
    max_tokens = (llm_config or {}).get("max_tokens", settings.LLM_MAX_TOKENS)

    api_key = (llm_config or {}).get("api_key")
    if api_key:
        # Support both plain and encrypted keys
        try:
            api_key = decrypt_value(api_key)
        except Exception:
            pass  # assume plain text

    if provider == "anthropic":
        return ClaudeLLMProvider(api_key=api_key, model=model, max_tokens=max_tokens)

    if provider == "zhipu":
        return ZhipuLLMProvider(api_key=api_key, model=model, max_tokens=max_tokens)

    return MockLLMProvider()
