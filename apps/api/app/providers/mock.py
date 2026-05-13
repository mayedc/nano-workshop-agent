import random
from typing import Any

from app.providers.base import (
    EmbeddingProvider,
    ImageGenerationProvider,
    LLMProvider,
    OCRProvider,
    STTProvider,
    VisionProvider,
)


class MockLLMProvider(LLMProvider):
    async def generate(self, prompt: str, **kwargs: Any) -> str:
        return f"[MOCK LLM] Generated response for prompt: {prompt[:50]}..."


class MockOCRProvider(OCRProvider):
    async def extract_text(self, image_bytes: bytes, **kwargs: Any) -> str:
        return "[MOCK OCR] Extracted text from image. Page 1: Sample document content."


class MockSTTProvider(STTProvider):
    async def transcribe(self, audio_bytes: bytes, mime_type: str, **kwargs: Any) -> dict[str, Any]:
        duration_sec = max(1, len(audio_bytes) // 16000)
        return {
            "transcript": "[MOCK STT] This is a simulated transcript from audio.",
            "segments": [
                {"speaker": "SPEAKER_1", "start": 0.0, "end": duration_sec / 2, "text": "Hello everyone."},
                {"speaker": "SPEAKER_2", "start": duration_sec / 2, "end": duration_sec, "text": "Thanks for joining."},
            ],
            "language": "en",
        }


class MockVisionProvider(VisionProvider):
    async def describe_image(self, image_bytes: bytes, **kwargs: Any) -> str:
        return "[MOCK VISION] An image showing a design prototype with colorful UI elements."

    async def detect_objects(self, image_bytes: bytes, **kwargs: Any) -> list[dict[str, Any]]:
        return [
            {"label": "button", "confidence": 0.95, "bbox": [10, 10, 50, 30]},
            {"label": "text_field", "confidence": 0.88, "bbox": [10, 50, 200, 30]},
        ]


class MockEmbeddingProvider(EmbeddingProvider):
    async def embed(self, texts: list[str], **kwargs: Any) -> list[list[float]]:
        dim = kwargs.get("dimensions", 128)
        return [[random.uniform(-1, 1) for _ in range(dim)] for _ in texts]


class MockImageGenerationProvider(ImageGenerationProvider):
    async def generate(self, prompt: str, **kwargs: Any) -> bytes:
        return b"[MOCK IMAGE]" + prompt.encode()


def register_mock_providers() -> None:
    from app.providers.base import ProviderRegistry

    ProviderRegistry.set_llm(MockLLMProvider())
    ProviderRegistry.set_ocr(MockOCRProvider())
    ProviderRegistry.set_stt(MockSTTProvider())
    ProviderRegistry.set_vision(MockVisionProvider())
    ProviderRegistry.set_embedding(MockEmbeddingProvider())
    ProviderRegistry.set_image_gen(MockImageGenerationProvider())
