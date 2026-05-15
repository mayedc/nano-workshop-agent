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
        system = (kwargs.get("system") or "").lower()
        prompt_lower = prompt.lower()

        if "json" in system or "json" in prompt_lower:
            # DataProfileAgent
            if prompt_lower.startswith("you are a senior data profiling assistant"):
                return '{"overview": "Dataset contains eHMI requirement codes with categories and descriptions.", "columns": [{"name": "Category", "dtype": "object", "semantic_type": "categorical", "description": "High-level requirement category", "null_rate": 0, "unique_count": 5}, {"name": "Need", "dtype": "object", "semantic_type": "text", "description": "Specific need description", "null_rate": 0, "unique_count": 20}, {"name": "Session", "dtype": "int64", "semantic_type": "identifier", "description": "Session number", "null_rate": 0, "unique_count": 3}], "relationships": ["Category groups multiple Need entries"], "quality_issues": [{"issue": "Merged header rows may create nulls in group columns", "severity": "medium"}], "suggested_analyses": ["Category frequency distribution", "Need word frequency", "Cross-tabulation Category vs Need"]}'
            # PlannerAgent
            if prompt_lower.startswith("you are an expert analytics planner"):
                return '{"objective": "Analyze the distribution and patterns of eHMI requirement codes across categories and sessions.", "reasoning": "The dataset contains categorical groupings and textual descriptions. Frequency and cross-tabulation will reveal dominant requirement types.", "steps": [{"step_number": 1, "title": "Clean structure", "description": "Forward-fill merged header columns (Session, Num., Role) and rename Unnamed: 0 to Category", "technique": "ffill() + rename()", "input_columns": ["Unnamed: 0", "Session", "Num.", "Role"], "expected_output": "Clean DataFrame with filled group columns"}, {"step_number": 2, "title": "Category distribution", "description": "Compute value_counts of Category", "technique": "value_counts()", "input_columns": ["Category"], "expected_output": "Frequency table"}, {"step_number": 3, "title": "Need distribution", "description": "Compute value_counts of Need descriptions", "technique": "value_counts()", "input_columns": ["Need"], "expected_output": "Frequency table"}, {"step_number": 4, "title": "Cross-tabulation", "description": "Cross-tab Category vs Need", "technique": "pd.crosstab()", "input_columns": ["Category", "Need"], "expected_output": "Crosstab DataFrame"}], "assumptions": ["Merged headers use forward-fill"], "fallback_plan": "If crosstab is too sparse, aggregate Need into keywords."}'
            # ResultExplainerAgent
            if prompt_lower.startswith("you are a senior data analyst presenting results"):
                return '{"summary": "eHMI需求分析完成。安全类需求出现频率最高（35%），其次为交互类（28%）和信息展示类（20%）。", "key_findings": ["安全类需求共出现35次，占比最高", "交互反馈需求占28%，多为手势/语音控制", "信息展示类占20%，集中在HUD设计"], "details": "通过对Category列的频次统计，发现安全相关需求在3个Session中均为高频主题。Need描述中，“碰撞预警”、“行人识别”出现次数最多。", "recommendations": ["优先实现碰撞预警和行人识别功能", "统一信息展示层级，避免HUD信息过载", "增加多模态交互反馈机制"], "confidence": "high", "limitations": "数据仅来自定性编码，未包含用户优先级打分。"}'
            return '{"status": "mock", "message": "This is a mock JSON response."}'

        if "python" in system or "code" in system:
            # RepairAgent
            if prompt_lower.startswith("you are a python debugging assistant"):
                return "# Fix: use actual column names from dataset\nresult = df['Category'].value_counts().reset_index()\nresult.columns = ['Category', 'Count']"
            # CodeAgent
            return """# Step 1: Clean merged headers
import pandas as pd
import numpy as np

# Forward-fill group-level columns
df[['Session', 'Num.', 'Role']] = df[['Session', 'Num.', 'Role']].ffill()

# Step 2: Rename merged header column
df = df.rename(columns={'Unnamed: 0': 'Category'})

# Step 3: Category distribution
category_dist = df['Category'].value_counts().reset_index()
category_dist.columns = ['Category', 'Count']

# Step 4: Need distribution
need_dist = df['Need'].value_counts().reset_index()
need_dist.columns = ['Need', 'Count']

# Step 5: Cross-tab
crosstab = pd.crosstab(df['Category'], df['Need'])

result = {
    'category_distribution': category_dist,
    'need_distribution': need_dist,
    'category_need_crosstab': crosstab
}"""

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
                {
                    "speaker": "SPEAKER_1",
                    "start": 0.0,
                    "end": duration_sec / 2,
                    "text": "Hello everyone.",
                },
                {
                    "speaker": "SPEAKER_2",
                    "start": duration_sec / 2,
                    "end": duration_sec,
                    "text": "Thanks for joining.",
                },
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
