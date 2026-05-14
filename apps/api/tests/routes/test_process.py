import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.services.storage import MemoryStorage, set_storage
from app.providers.mock import register_mock_providers


@pytest.fixture(autouse=True)
def setup():
    set_storage(MemoryStorage())
    register_mock_providers()


@pytest.fixture(autouse=True)
def _db_override(override_get_db):
    pass


@pytest.mark.asyncio
async def test_process_asset_sync():
    # First upload an asset
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        upload_resp = await ac.post(
            "/api/assets/project/proj-test/upload",
            files={"file": ("test.txt", b"hello world", "text/plain")},
        )
    assert upload_resp.status_code == 201
    asset_id = upload_resp.json()["id"]

    # Process it synchronously
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        process_resp = await ac.post(
            f"/api/assets/{asset_id}/process-sync?project_id=proj-test",
        )
    assert process_resp.status_code == 200
    data = process_resp.json()
    assert data["status"] == "completed"
    assert data["evidence_count"] > 0
    assert "result" in data


@pytest.mark.asyncio
async def test_process_asset_not_found():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/api/assets/nonexistent/process-sync?project_id=proj-test")
    assert resp.status_code == 404
