import pytest

from app.agents.base import AgentContext
from app.agents.mock_agents import register_mock_agents
from app.agents.registry import AgentRegistry
from app.providers.mock import register_mock_providers


@pytest.fixture
def registry():
    register_mock_providers()
    reg = AgentRegistry()
    register_mock_agents(reg)
    return reg


ALL_AGENTS = [
    "ProjectSetupAgent",
    "MaterialIntakeAgent",
    "PreprocessingAgent",
    "MetadataFusionAgent",
    "GoalUnderstandingAgent",
    "WorkshopPlannerAgent",
    "QualitativeAnalysisAgent",
    "CodingAgent",
    "ThemeExtractionAgent",
    "QuantitativeAnalysisAgent",
    "PrototypeAnalysisAgent",
    "DesignInsightAgent",
    "DesignConceptAgent",
    "ExpertReviewAgent",
    "IterationAgent",
    "ReportGenerationAgent",
    "ExportAgent",
    "MeetingRealtimeAgent",
    "MCPConnectorAgent",
    "EvaluationAgent",
]


def test_all_agents_registered(registry):
    agents = registry.list_agents()
    for name in ALL_AGENTS:
        assert name in agents, f"{name} not registered"


@pytest.mark.asyncio
async def test_core_agents(registry):
    for name in ["ProjectSetupAgent", "GoalUnderstandingAgent", "WorkshopPlannerAgent"]:
        agent = registry.get(name)
        ctx = AgentContext(project_id="proj-1", goal="Test goal")
        result = await agent.run(ctx)
        assert result.status == "completed"
        assert result.agent_name == name
        assert result.confidence > 0


@pytest.mark.asyncio
async def test_analysis_agents(registry):
    for name in [
        "QualitativeAnalysisAgent",
        "CodingAgent",
        "ThemeExtractionAgent",
        "QuantitativeAnalysisAgent",
    ]:
        agent = registry.get(name)
        ctx = AgentContext(
            project_id="proj-1",
            inputs={"evidence": [{"id": "ev-1", "content": "test"}], "codes": [{"label": "test"}]},
        )
        result = await agent.run(ctx)
        assert result.status == "completed"
        assert result.agent_name == name


@pytest.mark.asyncio
async def test_design_agents(registry):
    for name in ["PrototypeAnalysisAgent", "DesignInsightAgent", "DesignConceptAgent"]:
        agent = registry.get(name)
        ctx = AgentContext(project_id="proj-1", inputs={"insights": [{"title": "test"}]})
        result = await agent.run(ctx)
        assert result.status == "completed"
        assert result.agent_name == name


@pytest.mark.asyncio
async def test_reporting_agents(registry):
    for name in ["ExpertReviewAgent", "IterationAgent", "ReportGenerationAgent", "ExportAgent"]:
        agent = registry.get(name)
        ctx = AgentContext(project_id="proj-1", inputs={"review_targets": [{"id": "r1"}]})
        result = await agent.run(ctx)
        assert result.status == "completed"
        assert result.agent_name == name


@pytest.mark.asyncio
async def test_realtime_and_eval_agents(registry):
    for name in ["MeetingRealtimeAgent", "MCPConnectorAgent", "EvaluationAgent"]:
        agent = registry.get(name)
        ctx = AgentContext(project_id="proj-1")
        result = await agent.run(ctx)
        assert result.status == "completed"
        assert result.agent_name == name
