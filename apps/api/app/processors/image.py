from typing import Any

from app.processors.base import BaseProcessor, ProcessingResult
from app.providers.base import ProviderRegistry


class ImageProcessor(BaseProcessor):
    supported_types = {
        "image/png",
        "image/jpeg",
        "image/webp",
    }

    async def process(self, file_bytes: bytes, filename: str, mime_type: str, **kwargs: Any) -> ProcessingResult:
        vision = ProviderRegistry.vision()
        ocr = ProviderRegistry.ocr()
        embedder = ProviderRegistry.embedding()

        # OCR
        ocr_text = await ocr.extract_text(file_bytes)

        # Image captioning
        caption = await vision.describe_image(file_bytes)

        # Object detection
        objects = await vision.detect_objects(file_bytes)

        # Design element extraction (via LLM from caption + OCR)
        llm = ProviderRegistry.llm()
        design_prompt = f"Describe design elements in this image. Caption: {caption}. OCR: {ocr_text[:500]}"
        design_features = await llm.generate(design_prompt)

        # Embedding
        embeddings = await embedder.embed([caption, ocr_text[:500]])

        evidence = [
            {"type": "image_description", "content": caption, "metadata": {"objects": objects}},
            {"type": "text", "content": ocr_text, "metadata": {"source": "ocr"}},
            {"type": "design_features", "content": design_features, "metadata": {"source": "llm"}},
        ]

        return ProcessingResult(
            normalized_text=ocr_text,
            image_descriptions=[caption],
            metadata={
                "filename": filename,
                "mime_type": mime_type,
                "detected_objects": objects,
                "design_features": design_features[:200],
                "embedding_dim": len(embeddings[0]) if embeddings else 0,
            },
            evidence_candidates=evidence,
        )
