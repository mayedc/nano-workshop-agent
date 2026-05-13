import mimetypes
from abc import ABC, abstractmethod
from io import BytesIO
from pathlib import Path
from typing import Any

from minio import Minio

from app.core.config import settings


class StorageBackend(ABC):
    @abstractmethod
    def put_object(self, key: str, data: bytes, length: int, content_type: str) -> None:
        pass

    @abstractmethod
    def get_object(self, key: str) -> bytes:
        pass

    @abstractmethod
    def remove_object(self, key: str) -> None:
        pass

    @abstractmethod
    def presigned_get_url(self, key: str, expires: int = 3600) -> str:
        pass


class MinioStorage(StorageBackend):
    def __init__(self) -> None:
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=False,
        )
        self.bucket = settings.MINIO_BUCKET
        self._ensure_bucket()

    def _ensure_bucket(self) -> None:
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)

    def put_object(self, key: str, data: bytes, length: int, content_type: str) -> None:
        self.client.put_object(
            self.bucket,
            key,
            BytesIO(data),
            length,
            content_type=content_type,
        )

    def get_object(self, key: str) -> bytes:
        response = self.client.get_object(self.bucket, key)
        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()

    def remove_object(self, key: str) -> None:
        self.client.remove_object(self.bucket, key)

    def presigned_get_url(self, key: str, expires: int = 3600) -> str:
        return self.client.presigned_get_object(self.bucket, key, expires=expires)


class MemoryStorage(StorageBackend):
    """In-memory storage for tests."""

    def __init__(self) -> None:
        self._store: dict[str, bytes] = {}

    def put_object(self, key: str, data: bytes, length: int, content_type: str) -> None:
        self._store[key] = data

    def get_object(self, key: str) -> bytes:
        if key not in self._store:
            raise FileNotFoundError(f"Object not found: {key}")
        return self._store[key]

    def remove_object(self, key: str) -> None:
        self._store.pop(key, None)

    def presigned_get_url(self, key: str, expires: int = 3600) -> str:
        return f"memory://{key}"


_storage_instance: StorageBackend | None = None


def get_storage() -> StorageBackend:
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = MinioStorage()
    return _storage_instance


def set_storage(backend: StorageBackend) -> None:
    global _storage_instance
    _storage_instance = backend


def detect_file_type(filename: str) -> dict[str, str]:
    mime_type, _ = mimetypes.guess_type(filename)
    mime_type = mime_type or "application/octet-stream"

    type_mapping: dict[str, str] = {
        "application/pdf": "document",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "document",
        "application/msword": "document",
        "text/plain": "text",
        "text/markdown": "text",
        "text/csv": "table",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "table",
        "application/vnd.ms-excel": "table",
        "image/png": "image",
        "image/jpeg": "image",
        "image/webp": "image",
        "audio/mpeg": "audio",
        "audio/wav": "audio",
        "audio/x-wav": "audio",
        "video/mp4": "video",
        "model/gltf+json": "3d",
        "model/gltf-binary": "3d",
        "application/octet-stream": "3d",
        "application/json": "data",
        "application/zip": "archive",
    }

    return {
        "mime_type": mime_type,
        "asset_type": type_mapping.get(mime_type, "unknown"),
    }


def generate_storage_key(project_id: str, filename: str) -> str:
    import uuid

    ext = Path(filename).suffix
    return f"projects/{project_id}/assets/{uuid.uuid4().hex}{ext}"
