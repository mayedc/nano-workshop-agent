import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture(autouse=True)
def _db_override(override_get_db):
    pass


@pytest.mark.asyncio
async def test_create_project():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/projects/", json={
            "name": "Test Project",
            "description": "A test project",
            "status": "draft",
        })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Project"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_projects():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/projects/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_project_not_found():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/projects/nonexistent-id")
    assert response.status_code == 404
