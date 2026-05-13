import pytest

from app.agents.base import AgentContext, AgentResult
from app.agents.mock_agents import (
    DesignInsightAgent,
    GoalUnderstandingAgent,
    QualitativeAnalysisAgent,
    QuantitativeAnalysisAgent,
    ReportGenerationAgent,
)
from app.agents.registry import AgentRegistry
from app.agents.tools import ToolRegistry


@pytest.mark.asyncio
async def test_goal_understanding_agent():
    agent = GoalUnderstandingAgent()
    ctx = AgentContext(project_id="proj-1", goal="Test goal")
    result = await agent.run(ctx)
    assert result.status == "completed"
    assert "structured_goal" in result.outputs
    assert result.confidence > 0


@pytest.mark.asyncio
async def test_qualitative_analysis_agent():
    agent = QualitativeAnalysisAgent()
    ctx = AgentContext(project_id="proj-1", inputs={"evidence": [{"id": "ev-1"}]})
    result = await agent.run(ctx)
    assert result.status == "completed"
    assert "codes" in result.outputs
    assert len(result.evidence_ids) > 0


@pytest.mark.asyncio
async def test_quantitative_analysis_agent():
    agent = QuantitativeAnalysisAgent()
    ctx = AgentContext(project_id="proj-1", inputs={"quantitative_data": {"n": 50}})
    result = await agent.run(ctx)
    assert result.status == "completed"
    assert "likert_means" in result.outputs


@pytest.mark.asyncio
async def test_design_insight_agent():
    agent = DesignInsightAgent()
    ctx = AgentContext(project_id="proj-1", inputs={"themes": ["trust"]})
    result = await agent.run(ctx)
    assert result.status == "completed"
    assert "insights" in result.outputs
    assert len(result.evidence_ids) > 0


@pytest.mark.asyncio
async def test_report_generation_agent():
    agent = ReportGenerationAgent()
    ctx = AgentContext(project_id="proj-1", inputs={"insights": ["i1", "i2"]})
    result = await agent.run(ctx)
    assert result.status == "completed"
    assert "report_sections" in result.outputs


def test_agent_registry():
    registry = AgentRegistry()
    registry.register(GoalUnderstandingAgent())
    assert registry.has_agent("GoalUnderstandingAgent")
    assert "GoalUnderstandingAgent" in registry.list_agents()

    agent = registry.get("GoalUnderstandingAgent")
    assert agent.name == "GoalUnderstandingAgent"


def test_agent_registry_missing():
    registry = AgentRegistry()
    with pytest.raises(KeyError):
        registry.get("MissingAgent")


def test_tool_registry():
    registry = ToolRegistry()
    registry.register("add", lambda a, b: a + b)
    assert registry.has_tool("add")
    assert registry.call("add", 1, 2) == 3


def test_tool_registry_missing():
    registry = ToolRegistry()
    with pytest.raises(KeyError):
        registry.get("missing")
