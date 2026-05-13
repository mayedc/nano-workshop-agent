import pytest

from app.agents.base import AgentContext
from app.agents.mock_agents import (
    DesignInsightAgent,
    GoalUnderstandingAgent,
    QualitativeAnalysisAgent,
)
from app.agents.orchestrator import WorkflowOrchestrator, WorkflowPlan, WorkflowStep
from app.agents.registry import AgentRegistry


@pytest.fixture
def registry():
    reg = AgentRegistry()
    reg.register(GoalUnderstandingAgent())
    reg.register(QualitativeAnalysisAgent())
    reg.register(DesignInsightAgent())
    return reg


@pytest.mark.asyncio
async def test_sequential_execution(registry):
    orchestrator = WorkflowOrchestrator(registry)
    plan = WorkflowPlan(
        project_id="proj-1",
        steps=[
            WorkflowStep(id="1", agent="GoalUnderstandingAgent"),
            WorkflowStep(id="2", agent="QualitativeAnalysisAgent"),
        ],
    )
    context = AgentContext(project_id="proj-1")
    results = await orchestrator.run(plan, context)

    assert len(results) == 2
    assert results["1"].status == "completed"
    assert results["2"].status == "completed"


@pytest.mark.asyncio
async def test_dependency_execution(registry):
    orchestrator = WorkflowOrchestrator(registry)
    plan = WorkflowPlan(
        project_id="proj-1",
        steps=[
            WorkflowStep(id="1", agent="GoalUnderstandingAgent"),
            WorkflowStep(id="2", agent="QualitativeAnalysisAgent", depends_on=["1"]),
            WorkflowStep(id="3", agent="DesignInsightAgent", depends_on=["1", "2"]),
        ],
    )
    context = AgentContext(project_id="proj-1")
    results = await orchestrator.run(plan, context)

    assert len(results) == 3
    assert results["3"].status == "completed"


@pytest.mark.asyncio
async def test_rerun_step(registry):
    orchestrator = WorkflowOrchestrator(registry)
    plan = WorkflowPlan(
        project_id="proj-1",
        steps=[WorkflowStep(id="1", agent="GoalUnderstandingAgent")],
    )
    context = AgentContext(project_id="proj-1")

    result = await orchestrator.rerun_step(plan, "1", context)
    assert result.status == "completed"
    assert result.agent_name == "GoalUnderstandingAgent"


@pytest.mark.asyncio
async def test_rerun_missing_step(registry):
    orchestrator = WorkflowOrchestrator(registry)
    plan = WorkflowPlan(project_id="proj-1", steps=[])
    context = AgentContext(project_id="proj-1")

    with pytest.raises(ValueError):
        await orchestrator.rerun_step(plan, "99", context)
