from abc import ABC, abstractmethod
from typing import Any


class ProcessingResult:
    def __init__(
        self,
        normalized_text: str = "",
        extracted_tables: list[dict[str, Any]] | None = None,
        image_descriptions: list[str] | None = None,
        transcript: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        evidence_candidates: list[dict[str, Any]] | None = None,
    ):
        self.normalized_text = normalized_text
        self.extracted_tables = extracted_tables or []
        self.image_descriptions = image_descriptions or []
        self.transcript = transcript or {}
        self.metadata = metadata or {}
        self.evidence_candidates = evidence_candidates or []

    def to_dict(self) -> dict[str, Any]:
        return {
            "normalized_text": self.normalized_text,
            "extracted_tables": self.extracted_tables,
            "image_descriptions": self.image_descriptions,
            "transcript": self.transcript,
            "metadata": self.metadata,
            "evidence_candidates": self.evidence_candidates,
        }


class BaseProcessor(ABC):
    supported_types: set[str] = set()

    @abstractmethod
    async def process(self, file_bytes: bytes, filename: str, mime_type: str, **kwargs: Any) -> ProcessingResult:
        pass

    def can_process(self, mime_type: str) -> bool:
        return mime_type in self.supported_types
