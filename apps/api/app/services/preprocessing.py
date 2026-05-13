from typing import Any

from app.processors.audio import AudioProcessor
from app.processors.base import BaseProcessor, ProcessingResult
from app.processors.image import ImageProcessor
from app.processors.model3d import Model3DProcessor
from app.processors.pdf import PDFProcessor
from app.processors.table import TableProcessor
from app.processors.text import TextProcessor
from app.processors.video import VideoProcessor

_PROCESSORS: list[BaseProcessor] = [
    TextProcessor(),
    PDFProcessor(),
    ImageProcessor(),
    AudioProcessor(),
    VideoProcessor(),
    TableProcessor(),
    Model3DProcessor(),
]


def get_processor(mime_type: str) -> BaseProcessor | None:
    for processor in _PROCESSORS:
        if processor.can_process(mime_type):
            return processor
    return None


class PreprocessingService:
    async def process_asset(
        self,
        file_bytes: bytes,
        filename: str,
        mime_type: str,
        asset_type: str,
        **kwargs: Any,
    ) -> ProcessingResult:
        processor = get_processor(mime_type)
        if processor is None:
            # Fallback: treat as text if possible
            try:
                text = file_bytes.decode("utf-8", errors="replace")
                return ProcessingResult(
                    normalized_text=text,
                    metadata={
                        "filename": filename,
                        "mime_type": mime_type,
                        "fallback": True,
                        "asset_type": asset_type,
                    },
                    evidence_candidates=[
                        {
                            "type": "text",
                            "content": text[:2000],
                            "metadata": {"source": "fallback", "mime_type": mime_type},
                        }
                    ],
                )
            except Exception:
                return ProcessingResult(
                    metadata={
                        "filename": filename,
                        "mime_type": mime_type,
                        "error": "No processor available for this file type",
                        "asset_type": asset_type,
                    },
                )

        return await processor.process(file_bytes, filename, mime_type, **kwargs)


preprocessing_service = PreprocessingService()
