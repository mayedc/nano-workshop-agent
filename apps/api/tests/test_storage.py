import pytest

from app.services.storage import MemoryStorage, detect_file_type, generate_storage_key


def test_detect_file_type_pdf():
    info = detect_file_type("document.pdf")
    assert info["mime_type"] == "application/pdf"
    assert info["asset_type"] == "document"


def test_detect_file_type_png():
    info = detect_file_type("image.png")
    assert info["mime_type"] == "image/png"
    assert info["asset_type"] == "image"


def test_detect_file_type_wav():
    info = detect_file_type("audio.wav")
    assert info["mime_type"] == "audio/wav"
    assert info["asset_type"] == "audio"


def test_detect_file_type_mp4():
    info = detect_file_type("video.mp4")
    assert info["mime_type"] == "video/mp4"
    assert info["asset_type"] == "video"


def test_detect_file_type_csv():
    info = detect_file_type("data.csv")
    assert info["mime_type"] in ("text/csv", "application/vnd.ms-excel")
    assert info["asset_type"] == "table"


def test_detect_file_type_unknown():
    info = detect_file_type("weird.xyz")
    assert info["mime_type"] == "application/octet-stream"
    assert info["asset_type"] == "unknown"


def test_generate_storage_key():
    key = generate_storage_key("proj-1", "file.pdf")
    assert key.startswith("projects/proj-1/assets/")
    assert key.endswith(".pdf")


def test_memory_storage_put_and_get():
    storage = MemoryStorage()
    storage.put_object("key1", b"hello", 5, "text/plain")
    assert storage.get_object("key1") == b"hello"


def test_memory_storage_remove():
    storage = MemoryStorage()
    storage.put_object("key1", b"hello", 5, "text/plain")
    storage.remove_object("key1")
    with pytest.raises(FileNotFoundError):
        storage.get_object("key1")


def test_memory_storage_presigned_url():
    storage = MemoryStorage()
    url = storage.presigned_get_url("key1")
    assert url.startswith("memory://")
