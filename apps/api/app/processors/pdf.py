from typing import Any

from app.processors.base import BaseProcessor, ProcessingResult
from app.providers.base import ProviderRegistry


class PDFProcessor(BaseProcessor):
    supported_types = {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
    }

    async def process(
        self, file_bytes: bytes, filename: str, mime_type: str, **kwargs: Any
    ) -> ProcessingResult:
        # For mock: treat as text extraction via OCR/LLM
        ocr = ProviderRegistry.ocr()
        llm = ProviderRegistry.llm()

        # Simulate OCR on PDF pages
        extracted_text = await ocr.extract_text(file_bytes)

        # Section detection via LLM
        section_prompt = f"Detect sections in this document:\n{extracted_text[:2000]}"
        section_response = await llm.generate(section_prompt)

        # Chunking
        chunks = [extracted_text[i : i + 1000] for i in range(0, len(extracted_text), 900)]

        evidence = []
        for i, chunk in enumerate(chunks[:5]):
            evidence.append(
                {
                    "type": "text",
                    "content": chunk,
                    "metadata": {"chunk_index": i, "source": "pdf_extraction"},
                }
            )

        return ProcessingResult(
            normalized_text=extracted_text,
            metadata={
                "filename": filename,
                "mime_type": mime_type,
                "char_count": len(extracted_text),
                "section_analysis": section_response[:200],
                "chunk_count": len(chunks),
            },
            evidence_candidates=evidence,
        )
