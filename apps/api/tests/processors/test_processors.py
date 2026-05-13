import pytest

from app.processors.audio import AudioProcessor
from app.processors.image import ImageProcessor
from app.processors.pdf import PDFProcessor
from app.processors.table import TableProcessor
from app.processors.text import TextProcessor
from app.processors.video import VideoProcessor
from app.processors.model3d import Model3DProcessor
from app.providers.mock import register_mock_providers
from app.services.preprocessing import get_processor, preprocessing_service


@pytest.fixture(autouse=True)
def setup_providers():
    register_mock_providers()


@pytest.mark.asyncio
async def test_text_processor():
    processor = TextProcessor()
    assert processor.can_process("text/plain")
    result = await processor.process(b"Hello world\n\nSection 2", "test.txt", "text/plain")
    assert result.normalized_text
    assert len(result.evidence_candidates) > 0


@pytest.mark.asyncio
async def test_pdf_processor():
    processor = PDFProcessor()
    assert processor.can_process("application/pdf")
    result = await processor.process(b"fake pdf", "test.pdf", "application/pdf")
    assert "[MOCK OCR]" in result.normalized_text
    assert len(result.evidence_candidates) > 0


@pytest.mark.asyncio
async def test_image_processor():
    processor = ImageProcessor()
    assert processor.can_process("image/png")
    result = await processor.process(b"fake image", "test.png", "image/png")
    assert len(result.image_descriptions) > 0
    assert "[MOCK VISION]" in result.image_descriptions[0]
    assert len(result.evidence_candidates) >= 3


@pytest.mark.asyncio
async def test_audio_processor():
    processor = AudioProcessor()
    assert processor.can_process("audio/wav")
    result = await processor.process(b"fake audio" * 1000, "test.wav", "audio/wav")
    assert result.transcript
    assert "[MOCK STT]" in result.transcript.get("transcript", "")
    assert len(result.evidence_candidates) > 0


@pytest.mark.asyncio
async def test_video_processor():
    processor = VideoProcessor()
    assert processor.can_process("video/mp4")
    result = await processor.process(b"fake video" * 1000, "test.mp4", "video/mp4")
    assert result.transcript
    assert len(result.evidence_candidates) >= 3


@pytest.mark.asyncio
async def test_table_processor():
    processor = TableProcessor()
    assert processor.can_process("text/csv")
    result = await processor.process(b"col1,col2\n1,2\n3,4", "test.csv", "text/csv")
    assert len(result.extracted_tables) > 0
    assert result.extracted_tables[0]["row_count"] == 2
    assert len(result.evidence_candidates) >= 3


@pytest.mark.asyncio
async def test_model3d_processor():
    processor = Model3DProcessor()
    assert processor.can_process("model/gltf-binary")
    result = await processor.process(b"fake 3d", "test.glb", "model/gltf-binary")
    assert result.normalized_text
    assert len(result.evidence_candidates) >= 3


@pytest.mark.asyncio
async def test_preprocessing_service():
    result = await preprocessing_service.process_asset(
        file_bytes=b"hello world",
        filename="test.txt",
        mime_type="text/plain",
        asset_type="text",
    )
    assert result.normalized_text == "hello world"
    assert len(result.evidence_candidates) > 0


def test_get_processor():
    assert get_processor("text/plain") is not None
    assert get_processor("image/png") is not None
    assert get_processor("audio/wav") is not None
    assert get_processor("unknown/type") is None
