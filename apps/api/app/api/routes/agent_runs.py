from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas import AgentRunCreate, AgentRunResponse, AgentRunUpdate
from app.services import agent_run as agent_run_service

router = APIRouter()


@router.get("/", response_model=list[AgentRunResponse])
async def list_agent_runs(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    return await agent_run_service.get_multi(db, skip=skip, limit=limit)


@router.post("/", response_model=AgentRunResponse, status_code=status.HTTP_201_CREATED)
async def create_agent_run(
    obj_in: AgentRunCreate,
    db: AsyncSession = Depends(get_db),
):
    return await agent_run_service.create(db, obj_in=obj_in.model_dump())


@router.get("/{run_id}", response_model=AgentRunResponse)
async def get_agent_run(
    run_id: str,
    db: AsyncSession = Depends(get_db),
):
    obj = await agent_run_service.get(db, run_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Agent run not found")
    return obj


@router.put("/{run_id}", response_model=AgentRunResponse)
async def update_agent_run(
    run_id: str,
    obj_in: AgentRunUpdate,
    db: AsyncSession = Depends(get_db),
):
    db_obj = await agent_run_service.get(db, run_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Agent run not found")
    return await agent_run_service.update(
        db, db_obj=db_obj, obj_in=obj_in.model_dump(exclude_unset=True)
    )


@router.delete("/{run_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent_run(
    run_id: str,
    db: AsyncSession = Depends(get_db),
):
    obj = await agent_run_service.delete(db, id=run_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Agent run not found")
    return None
