from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, **kwargs: Any) -> str:
        pass


class OCRProvider(ABC):
    @abstractmethod
    async def extract_text(self, image_bytes: bytes, **kwargs: Any) -> str:
        pass


class STTProvider(ABC):
    @abstractmethod
    async def transcribe(self, audio_bytes: bytes, mime_type: str, **kwargs: Any) -> dict[str, Any]:
        pass


class VisionProvider(ABC):
    @abstractmethod
    async def describe_image(self, image_bytes: bytes, **kwargs: Any) -> str:
        pass

    @abstractmethod
    async def detect_objects(self, image_bytes: bytes, **kwargs: Any) -> list[dict[str, Any]]:
        pass


class EmbeddingProvider(ABC):
    @abstractmethod
    async def embed(self, texts: list[str], **kwargs: Any) -> list[list[float]]:
        pass


class ImageGenerationProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, **kwargs: Any) -> bytes:
        pass


class ProviderRegistry:
    _llm: LLMProvider | None = None
    _ocr: OCRProvider | None = None
    _stt: STTProvider | None = None
    _vision: VisionProvider | None = None
    _embedding: EmbeddingProvider | None = None
    _image_gen: ImageGenerationProvider | None = None

    @classmethod
    def set_llm(cls, provider: LLMProvider) -> None:
        cls._llm = provider

    @classmethod
    def set_ocr(cls, provider: OCRProvider) -> None:
        cls._ocr = provider

    @classmethod
    def set_stt(cls, provider: STTProvider) -> None:
        cls._stt = provider

    @classmethod
    def set_vision(cls, provider: VisionProvider) -> None:
        cls._vision = provider

    @classmethod
    def set_embedding(cls, provider: EmbeddingProvider) -> None:
        cls._embedding = provider

    @classmethod
    def set_image_gen(cls, provider: ImageGenerationProvider) -> None:
        cls._image_gen = provider

    @classmethod
    def llm(cls) -> LLMProvider:
        if cls._llm is None:
            raise RuntimeError("LLM provider not configured")
        return cls._llm

    @classmethod
    def ocr(cls) -> OCRProvider:
        if cls._ocr is None:
            raise RuntimeError("OCR provider not configured")
        return cls._ocr

    @classmethod
    def stt(cls) -> STTProvider:
        if cls._stt is None:
            raise RuntimeError("STT provider not configured")
        return cls._stt

    @classmethod
    def vision(cls) -> VisionProvider:
        if cls._vision is None:
            raise RuntimeError("Vision provider not configured")
        return cls._vision

    @classmethod
    def embedding(cls) -> EmbeddingProvider:
        if cls._embedding is None:
            raise RuntimeError("Embedding provider not configured")
        return cls._embedding

    @classmethod
    def image_gen(cls) -> ImageGenerationProvider:
        if cls._image_gen is None:
            raise RuntimeError("Image generation provider not configured")
        return cls._image_gen
