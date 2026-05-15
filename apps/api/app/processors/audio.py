from typing import Any

from app.processors.base import BaseProcessor, ProcessingResult
from app.providers.base import ProviderRegistry


class AudioProcessor(BaseProcessor):
    supported_types = {
        "audio/mpeg",
        "audio/wav",
        "audio/x-wav",
    }

    async def process(
        self, file_bytes: bytes, filename: str, mime_type: str, **kwargs: Any
    ) -> ProcessingResult:
        stt = ProviderRegistry.stt()
        llm = ProviderRegistry.llm()
        embedder = ProviderRegistry.embedding()

        # Speech-to-text
        transcript_result = await stt.transcribe(file_bytes, mime_type)
        transcript_text = transcript_result.get("transcript", "")
        segments = transcript_result.get("segments", [])

        # Transcript cleaning
        clean_prompt = f"Clean this transcript:\n{transcript_text}"
        cleaned = await llm.generate(clean_prompt)

        # Emotion / sentiment signal
        sentiment_prompt = f"Analyze sentiment in this transcript:\n{transcript_text[:1000]}"
        sentiment = await llm.generate(sentiment_prompt)

        # Embedding
        chunks = [s["text"] for s in segments[:10]]
        embeddings = await embedder.embed(chunks) if chunks else []

        evidence = []
        for seg in segments:
            evidence.append(
                {
                    "type": "transcript_segment",
                    "content": seg["text"],
                    "metadata": {
                        "speaker": seg.get("speaker", "unknown"),
                        "start": seg.get("start", 0),
                        "end": seg.get("end", 0),
                    },
                }
            )
        evidence.append(
            {
                "type": "sentiment_analysis",
                "content": sentiment,
                "metadata": {"source": "llm", "type": "audio"},
            }
        )

        return ProcessingResult(
            normalized_text=cleaned,
            transcript=transcript_result,
            metadata={
                "filename": filename,
                "mime_type": mime_type,
                "duration_sec": segments[-1]["end"] if segments else 0,
                "speaker_count": len(set(s.get("speaker", "unknown") for s in segments)),
                "sentiment_summary": sentiment[:200],
                "embedding_dim": len(embeddings[0]) if embeddings else 0,
            },
            evidence_candidates=evidence,
        )
