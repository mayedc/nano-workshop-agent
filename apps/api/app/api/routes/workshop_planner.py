from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import AgentContext
from app.agents.registry import agent_registry
from app.agents.workshop_planner_agent import WorkshopPlannerAgent, _extract_preview
from app.db.session import get_db
from app.services import asset as asset_service
from app.services import project as project_service
from app.services.storage import get_storage
from app.templates.loader import TemplateRegistry

router = APIRouter()

PREVIEWABLE_MIME_TYPES = {
    "text/csv",
    "text/comma-separated-values",
    "text/plain",
    "text/markdown",
    "application/json",
    "application/xml",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-excel",
}


class WorkshopPlanRequest(BaseModel):
    asset_ids: list[str] = Field(..., min_length=1, description="Selected asset IDs")
    workshop_purpose: str = Field(..., min_length=10, description="What is the workshop goal?")


class SuggestedWorkflowStep(BaseModel):
    id: int
    name: str
    agent_name: str
    description: str
    depends_on: list[int] = Field(default_factory=list)
    expected_output: str = ""


class WorkshopPlanResponse(BaseModel):
    project_id: str
    workshop_title: str
    reasoning: str
    suggested_modules: list[str] = Field(default_factory=list)
    workflow_steps: list[SuggestedWorkflowStep] = Field(default_factory=list)
    estimated_duration: str = ""
    confidence: str = "medium"
    assumptions: list[str] = Field(default_factory=list)


def _build_asset_meta(asset: Any, storage: Any) -> dict[str, Any]:
    """Build asset metadata dict with optional content preview for readable types."""
    meta: dict[str, Any] = {
        "filename": asset.filename,
        "mime_type": asset.mime_type,
        "asset_type": asset.asset_type,
        "semantic_role": asset.semantic_role or "",
        "storage_key": asset.storage_key,
        "size": asset.size or 0,
        "extra_metadata": asset.extra_metadata or {},
    }
    if asset.mime_type in PREVIEWABLE_MIME_TYPES:
        try:
            file_bytes = storage.get_object(asset.storage_key)
            meta["content_preview"] = _extract_preview(file_bytes, asset.mime_type)
        except Exception:
            meta["content_preview"] = "(could not read file content)"
    return meta


@router.post("/projects/{project_id}/workshop-planner/plan", response_model=WorkshopPlanResponse)
async def plan_workshop(
    project_id: str,
    req: WorkshopPlanRequest,
    db: AsyncSession = Depends(get_db),
) -> WorkshopPlanResponse:
    project = await project_service.get(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    config = project.config or {}
    storage = get_storage()

    asset_metas: list[dict[str, Any]] = []
    for asset_id in req.asset_ids:
        asset = await asset_service.get(db, asset_id)
        if not asset or asset.project_id != project_id:
            raise HTTPException(status_code=404, detail=f"Asset '{asset_id}' not found in project")
        asset_metas.append(_build_asset_meta(asset, storage))

    templates = TemplateRegistry.all()
    available_agents = sorted(agent_registry.list_agents())

    context = AgentContext(
        project_id=project_id,
        goal=req.workshop_purpose,
        inputs={
            "assets": asset_metas,
            "available_agents": available_agents,
            "templates": [t.model_dump() for t in templates],
        },
        project_config=config,
    )

    agent = WorkshopPlannerAgent()
    result = await agent.run(context)

    outputs = result.outputs
    steps_raw = outputs.get("workflow_steps", [])
    workflow_steps = [SuggestedWorkflowStep(**s) for s in steps_raw if isinstance(s, dict)]

    return WorkshopPlanResponse(
        project_id=project_id,
        workshop_title=outputs.get("workshop_title", ""),
        reasoning=outputs.get("reasoning", ""),
        suggested_modules=outputs.get("suggested_modules", []),
        workflow_steps=workflow_steps,
        estimated_duration=outputs.get("estimated_duration", ""),
        confidence=outputs.get("confidence", "medium"),
        assumptions=outputs.get("assumptions", []),
    )
