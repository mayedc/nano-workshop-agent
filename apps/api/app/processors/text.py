from typing import Any

from app.processors.base import BaseProcessor, ProcessingResult
from app.providers.base import ProviderRegistry


class TextProcessor(BaseProcessor):
    supported_types = {
        "text/plain",
        "text/markdown",
        "text/csv",
    }

    async def process(
        self, file_bytes: bytes, filename: str, mime_type: str, **kwargs: Any
    ) -> ProcessingResult:
        text = file_bytes.decode("utf-8", errors="replace")

        # Section detection (simple heuristic: headers by # or blank lines)
        sections = self._detect_sections(text, mime_type)

        # Normalization
        normalized = text.strip()

        # Chunking
        chunks = self._chunk_text(normalized, chunk_size=1000, overlap=100)

        # Embedding
        embedder = ProviderRegistry.embedding()
        embeddings = await embedder.embed(chunks[:10])  # limit for mock

        evidence = []
        for i, chunk in enumerate(chunks[:5]):
            evidence.append(
                {
                    "type": "text",
                    "content": chunk,
                    "metadata": {
                        "chunk_index": i,
                        "embedding_dim": len(embeddings[i]) if i < len(embeddings) else 0,
                    },
                }
            )

        return ProcessingResult(
            normalized_text=normalized,
            metadata={
                "filename": filename,
                "mime_type": mime_type,
                "char_count": len(text),
                "section_count": len(sections),
                "chunk_count": len(chunks),
            },
            evidence_candidates=evidence,
        )

    def _detect_sections(self, text: str, mime_type: str) -> list[dict[str, Any]]:
        sections = []
        if mime_type == "text/markdown":
            for line in text.splitlines():
                if line.startswith("#"):
                    sections.append({"title": line.lstrip("# ").strip(), "level": line.count("#")})
        else:
            current = []
            for line in text.splitlines():
                if line.strip() == "":
                    if current:
                        sections.append({"title": current[0][:50], "level": 1})
                        current = []
                else:
                    current.append(line)
            if current:
                sections.append({"title": current[0][:50], "level": 1})
        return sections

    def _chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 100) -> list[str]:
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunks.append(text[start:end])
            start += chunk_size - overlap
        return chunks
