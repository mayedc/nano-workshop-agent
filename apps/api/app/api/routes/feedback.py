from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import ExpertFeedback
from app.schemas import (
    ExpertFeedbackCreate,
    ExpertFeedbackResponse,
    ExpertFeedbackUpdate,
    REVIEW_ACTIONS,
    TARGET_TYPES,
)
from app.services import feedback as feedback_service

router = APIRouter()


@router.get("/", response_model=list[ExpertFeedbackResponse])
async def list_feedback(
    skip: int = 0,
    limit: int = 100,
    project_id: str | None = Query(None),
    target_type: str | None = Query(None),
    target_id: str | None = Query(None),
    action: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(ExpertFeedback)
    if project_id:
        stmt = stmt.where(ExpertFeedback.project_id == project_id)
    if target_type:
        stmt = stmt.where(ExpertFeedback.target_type == target_type)
    if target_id:
        stmt = stmt.where(ExpertFeedback.target_id == target_id)
    if action:
        stmt = stmt.where(ExpertFeedback.action == action)
    stmt = stmt.order_by(ExpertFeedback.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.post("/", response_model=ExpertFeedbackResponse, status_code=status.HTTP_201_CREATED)
async def create_feedback(
    obj_in: ExpertFeedbackCreate,
    db: AsyncSession = Depends(get_db),
):
    if obj_in.target_type not in TARGET_TYPES:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid target_type. Must be one of: {TARGET_TYPES}",
        )
    if obj_in.action not in REVIEW_ACTIONS:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid action. Must be one of: {REVIEW_ACTIONS}",
        )

    feedback_data = obj_in.model_dump()

    # Apply review action side-effects on the target record
    await _apply_action_side_effects(db, feedback_data)

    return await feedback_service.create(db, obj_in=feedback_data)


@router.get("/{feedback_id}", response_model=ExpertFeedbackResponse)
async def get_feedback(
    feedback_id: str,
    db: AsyncSession = Depends(get_db),
):
    obj = await feedback_service.get(db, feedback_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return obj


@router.put("/{feedback_id}", response_model=ExpertFeedbackResponse)
async def update_feedback(
    feedback_id: str,
    obj_in: ExpertFeedbackUpdate,
    db: AsyncSession = Depends(get_db),
):
    db_obj = await feedback_service.get(db, feedback_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return await feedback_service.update(
        db, db_obj=db_obj, obj_in=obj_in.model_dump(exclude_unset=True)
    )


@router.delete("/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_feedback(
    feedback_id: str,
    db: AsyncSession = Depends(get_db),
):
    obj = await feedback_service.delete(db, id=feedback_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return None


@router.get("/targets/types", response_model=list[str])
async def list_target_types():
    return list(TARGET_TYPES)


@router.get("/actions/list", response_model=list[str])
async def list_actions():
    return list(REVIEW_ACTIONS)


async def _apply_action_side_effects(db: AsyncSession, feedback_data: dict) -> None:
    """Apply side effects of review actions on target records."""
    from app.models import AgentRun
    from app.services import agent_run as agent_run_service
    from app.services import code as code_service
    from app.services import requirement as requirement_service
    from app.services import theme as theme_service

    target_type = feedback_data["target_type"]
    target_id = feedback_data["target_id"]
    action = feedback_data["action"]
    new_status = feedback_data.get("review_status", "pending")

    # Map actions to review_status
    action_status_map = {
        "approve": "approved",
        "reject": "rejected",
        "revise": "revised",
        "request_rerun": "pending_rerun",
    }
    if action in action_status_map:
        new_status = action_status_map[action]
        feedback_data["review_status"] = new_status

    # Update the target entity's status based on action
    if target_type == "codes":
        obj = await code_service.get(db, target_id)
        if obj and action in ("approve", "reject", "revise"):
            await code_service.update(db, db_obj=obj, obj_in={"description": obj.description})
    elif target_type == "requirements":
        obj = await requirement_service.get(db, target_id)
        if obj:
            status_map = {
                "approve": "approved",
                "reject": "rejected",
                "revise": "draft",
                "request_rerun": "draft",
            }
            new_req_status = status_map.get(action, obj.status)
            await requirement_service.update(db, db_obj=obj, obj_in={"status": new_req_status})
    elif target_type == "themes":
        obj = await theme_service.get(db, target_id)
        if obj and action in ("approve", "reject", "revise"):
            await theme_service.update(db, db_obj=obj, obj_in={"confidence": obj.confidence})

    # Update related agent runs' review_status
    if target_type in (
        "codes",
        "themes",
        "requirements",
        "insights",
        "concepts",
        "report_sections",
    ):
        agent_name_map = {
            "codes": "CodingAgent",
            "themes": "ThemeExtractionAgent",
            "requirements": "GoalUnderstandingAgent",
            "insights": "DesignInsightAgent",
            "concepts": "DesignConceptAgent",
            "report_sections": "ReportGenerationAgent",
        }
        agent_name = agent_name_map.get(target_type)
        if agent_name:
            result = await db.execute(
                select(AgentRun).where(
                    AgentRun.agent_name == agent_name,
                    AgentRun.project_id == feedback_data["project_id"],
                )
            )
            runs = result.scalars().all()
            for run in runs:
                await agent_run_service.update(db, db_obj=run, obj_in={"review_status": new_status})
