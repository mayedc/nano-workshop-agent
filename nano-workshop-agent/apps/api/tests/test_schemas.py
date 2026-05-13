from app.schemas import ProjectCreate, ProjectUpdate, AgentRunCreate


def test_project_create_schema():
    data = {"name": "Workshop A", "description": "Desc"}
    project = ProjectCreate(**data)
    assert project.name == "Workshop A"
    assert project.status == "draft"


def test_project_update_schema():
    data = {"name": "Updated"}
    project = ProjectUpdate(**data)
    assert project.name == "Updated"
    assert project.description is None


def test_agent_run_create_schema():
    data = {
        "project_id": "proj-1",
        "agent_name": "TestAgent",
        "status": "pending",
    }
    run = AgentRunCreate(**data)
    assert run.agent_name == "TestAgent"
    assert run.confidence is None
