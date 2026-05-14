import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.services.storage import MemoryStorage, detect_file_type, set_storage


@pytest.fixture(autouse=True)
def mock_storage():
    set_storage(MemoryStorage())
    yield


@pytest.fixture(autouse=True)
def _db_override(override_get_db):
    pass


@pytest.mark.asyncio
async def test_upload_asset():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/api/assets/project/proj-test/upload",
            files={"file": ("test.pdf", b"fake pdf content", "application/pdf")},
            data={"semantic_role": "road_user_needs", "source_stage": "interview"},
        )
    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "test.pdf"
    assert data["mime_type"] == "application/pdf"
    assert data["asset_type"] == "document"
    assert data["semantic_role"] == "road_user_needs"
    assert data["source_stage"] == "interview"
    assert data["processing_status"] == "pending"
    assert data["size"] == len(b"fake pdf content")


@pytest.mark.asyncio
async def test_upload_asset_no_filename():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/api/assets/project/proj-test/upload",
            files={"file": ("", b"content", "application/pdf")},
        )
    assert response.status_code in (400, 422)


@pytest.mark.asyncio
async def test_list_project_assets():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/assets/project/proj-test")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_asset_not_found():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/assets/nonexistent-id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_asset():
    # First create an asset
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        create_resp = await ac.post(
            "/api/assets/project/proj-test/upload",
            files={"file": ("delete_me.txt", b"hello", "text/plain")},
        )
    assert create_resp.status_code == 201
    asset_id = create_resp.json()["id"]

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        delete_resp = await ac.delete(f"/api/assets/{asset_id}")
    assert delete_resp.status_code == 204

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        get_resp = await ac.get(f"/api/assets/{asset_id}")
    assert get_resp.status_code == 404
