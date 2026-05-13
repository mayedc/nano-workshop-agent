from typing import Any

from app.processors.base import BaseProcessor, ProcessingResult
from app.providers.base import ProviderRegistry


class VideoProcessor(BaseProcessor):
    supported_types = {
        "video/mp4",
    }

    async def process(self, file_bytes: bytes, filename: str, mime_type: str, **kwargs: Any) -> ProcessingResult:
        stt = ProviderRegistry.stt()
        vision = ProviderRegistry.vision()
        llm = ProviderRegistry.llm()
        embedder = ProviderRegistry.embedding()

        # Audio extraction (mock: treat as audio)
        transcript_result = await stt.transcribe(file_bytes, "audio/mp4")
        transcript_text = transcript_result.get("transcript", "")

        # Keyframe extraction (mock: process as image)
        keyframe_desc = await vision.describe_image(file_bytes[:1024])

        # Visual scene description
        scene_prompt = f"Describe visual scenes in this video. Frame: {keyframe_desc}"
        scenes = await llm.generate(scene_prompt)

        # Multimodal summary
        summary_prompt = f"Summarize this video. Audio: {transcript_text[:1000]}. Visual: {scenes[:500]}"
        summary = await llm.generate(summary_prompt)

        # Embedding
        embeddings = await embedder.embed([summary, transcript_text[:500]])

        evidence = [
            {"type": "transcript", "content": transcript_text, "metadata": {"source": "stt"}},
            {"type": "visual_description", "content": scenes, "metadata": {"source": "vision"}},
            {"type": "summary", "content": summary, "metadata": {"source": "multimodal"}},
        ]

        return ProcessingResult(
            normalized_text=summary,
            transcript=transcript_result,
            metadata={
                "filename": filename,
                "mime_type": mime_type,
                "keyframe_description": keyframe_desc,
                "scene_summary": scenes[:200],
                "embedding_dim": len(embeddings[0]) if embeddings else 0,
            },
            evidence_candidates=evidence,
        )
