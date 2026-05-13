from typing import Any

from app.processors.base import BaseProcessor, ProcessingResult
from app.providers.base import ProviderRegistry


class Model3DProcessor(BaseProcessor):
    supported_types = {
        "model/gltf+json",
        "model/gltf-binary",
        "application/octet-stream",
    }

    async def process(self, file_bytes: bytes, filename: str, mime_type: str, **kwargs: Any) -> ProcessingResult:
        vision = ProviderRegistry.vision()
        llm = ProviderRegistry.llm()

        # Metadata extraction (mock: parse filename and size)
        metadata = {
            "filename": filename,
            "mime_type": mime_type,
            "file_size_bytes": len(file_bytes),
            "format": filename.split(".")[-1].lower() if "." in filename else "unknown",
        }

        # Thumbnail rendering (mock: generate placeholder description)
        thumbnail_desc = await vision.describe_image(file_bytes[:1024])

        # Visual description
        visual_prompt = f"Describe a 3D model named '{filename}' with format {metadata['format']}."
        visual_desc = await llm.generate(visual_prompt)

        # Design feature tagging
        design_prompt = f"Tag design features for this 3D model: {visual_desc[:500]}"
        design_tags = await llm.generate(design_prompt)

        evidence = [
            {"type": "3d_metadata", "content": str(metadata), "metadata": {"source": "parser"}},
            {"type": "visual_description", "content": visual_desc, "metadata": {"source": "llm"}},
            {"type": "design_tags", "content": design_tags, "metadata": {"source": "llm"}},
        ]

        return ProcessingResult(
            normalized_text=visual_desc,
            metadata={
                "filename": filename,
                "mime_type": mime_type,
                "format": metadata["format"],
                "thumbnail_description": thumbnail_desc,
                "design_tags": design_tags[:200],
            },
            evidence_candidates=evidence,
        )
