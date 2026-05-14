from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.encryption import decrypt_value, encrypt_value
from app.db.session import get_db
from app.schemas import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services import project as project_service

router = APIRouter()


class ProjectConfigOut(BaseModel):
    agents: list[dict[str, Any]] = Field(default_factory=list)
    llm_config: dict[str, Any] = Field(default_factory=dict)


class ProjectConfigIn(BaseModel):
    agents: list[dict[str, Any]] | None = None
    llm_config: dict[str, Any] | None = None


@router.get("/", response_model=list[ProjectResponse])
async def list_projects(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    return await project_service.get_multi(db, skip=skip, limit=limit)


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    obj_in: ProjectCreate,
    db: AsyncSession = Depends(get_db),
):
    # TODO: derive owner_id from authenticated user
    data = obj_in.model_dump()
    data["owner_id"] = "system"
    return await project_service.create(db, obj_in=data)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    obj = await project_service.get(db, project_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Project not found")
    return obj


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    obj_in: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
):
    db_obj = await project_service.get(db, project_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Project not found")
    return await project_service.update(db, db_obj=db_obj, obj_in=obj_in.model_dump(exclude_unset=True))


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    obj = await project_service.delete(db, id=project_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Project not found")
    return None


def _mask_key(key: str) -> str:
    if not key:
        return ""
    if len(key) <= 8:
        return "***"
    return key[:4] + "..." + key[-4:]


@router.get("/{project_id}/config", response_model=ProjectConfigOut)
async def get_project_config(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    obj = await project_service.get(db, project_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Project not found")
    config = obj.config or {}
    llm_config = dict(config.get("llm_config", {}))
    if "api_key" in llm_config:
        llm_config["api_key"] = _mask_key(llm_config["api_key"])
    return ProjectConfigOut(
        agents=config.get("agents", []),
        llm_config=llm_config,
    )


@router.put("/{project_id}/config", response_model=ProjectConfigOut)
async def update_project_config(
    project_id: str,
    obj_in: ProjectConfigIn,
    db: AsyncSession = Depends(get_db),
):
    db_obj = await project_service.get(db, project_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Project not found")

    config = dict(db_obj.config or {})

    if obj_in.agents is not None:
        config["agents"] = obj_in.agents

    if obj_in.llm_config is not None:
        new_llm = dict(obj_in.llm_config)
        existing_llm = config.get("llm_config", {})
        api_key = new_llm.get("api_key")
        if api_key and not api_key.startswith("sk-") and "..." in api_key:
            # masked key submitted, keep existing encrypted key
            try:
                new_llm["api_key"] = existing_llm.get("api_key", "")
            except Exception:
                pass
        elif api_key:
            new_llm["api_key"] = encrypt_value(api_key)
        config["llm_config"] = new_llm

    await project_service.update(db, db_obj=db_obj, obj_in={"config": config})

    llm_config = dict(config.get("llm_config", {}))
    if "api_key" in llm_config:
        llm_config["api_key"] = _mask_key(llm_config["api_key"])
    return ProjectConfigOut(
        agents=config.get("agents", []),
        llm_config=llm_config,
    )
