from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services import project as project_service

router = APIRouter()


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
