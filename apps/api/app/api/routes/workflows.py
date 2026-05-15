from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import AgentContext
from app.agents.orchestrator import WorkflowOrchestrator, WorkflowPlan, WorkflowStep
from app.agents.registry import agent_registry
from app.db.session import get_db

router = APIRouter()


class WorkflowRunRequest(BaseModel):
    project_id: str
    steps: list[WorkflowStep]
    goal: str | None = None
    inputs: dict[str, Any] = Field(default_factory=dict)


class WorkflowRerunRequest(BaseModel):
    project_id: str
    step_id: str
    inputs: dict[str, Any] = Field(default_factory=dict)


@router.post("/run", response_model=dict[str, Any])
async def run_workflow(
    req: WorkflowRunRequest,
    db: AsyncSession = Depends(get_db),
):
    orchestrator = WorkflowOrchestrator(agent_registry)
    context = AgentContext(
        project_id=req.project_id,
        goal=req.goal,
        inputs=req.inputs,
    )
    plan = WorkflowPlan(project_id=req.project_id, steps=req.steps)

    results = await orchestrator.run(plan, context, db=db)

    return {
        "project_id": req.project_id,
        "results": {
            step_id: {
                "agent_name": r.agent_name,
                "status": r.status,
                "outputs": r.result.outputs if r.result else {},
                "confidence": r.result.confidence if r.result else None,
                "error": r.error,
            }
            for step_id, r in results.items()
        },
    }


@router.post("/rerun", response_model=dict[str, Any])
async def rerun_step(
    req: WorkflowRerunRequest,
    db: AsyncSession = Depends(get_db),
):
    orchestrator = WorkflowOrchestrator(agent_registry)
    context = AgentContext(
        project_id=req.project_id,
        inputs=req.inputs,
    )
    # Create a dummy plan with just the step to rerun
    plan = WorkflowPlan(project_id=req.project_id, steps=[])

    try:
        result = await orchestrator.rerun_step(plan, req.step_id, context, db=db)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    return {
        "project_id": req.project_id,
        "step_id": result.step_id,
        "agent_name": result.agent_name,
        "status": result.status,
        "outputs": result.result.outputs if result.result else {},
        "confidence": result.result.confidence if result.result else None,
        "error": result.error,
    }


@router.get("/agents", response_model=list[str])
async def list_agents():
    return agent_registry.list_agents()
