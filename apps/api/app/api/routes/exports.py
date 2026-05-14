from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas import ExportRecordCreate, ExportRecordResponse
from app.services import export_record as export_service
from sqlalchemy import select

router = APIRouter()


@router.get("/", response_model=list[ExportRecordResponse])
async def list_exports(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    return await export_service.get_multi(db, skip=skip, limit=limit)


@router.get("/project/{project_id}", response_model=list[ExportRecordResponse])
async def list_project_exports(
    project_id: str,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    from app.models import ExportRecord

    result = await db.execute(
        select(ExportRecord).where(ExportRecord.project_id == project_id).offset(skip).limit(limit)
    )
    return list(result.scalars().all())


@router.post("/", response_model=ExportRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_export(
    obj_in: ExportRecordCreate,
    db: AsyncSession = Depends(get_db),
):
    return await export_service.create(db, obj_in=obj_in.model_dump())


@router.get("/{export_id}", response_model=ExportRecordResponse)
async def get_export(
    export_id: str,
    db: AsyncSession = Depends(get_db),
):
    obj = await export_service.get(db, export_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Export not found")
    return obj


@router.delete("/{export_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_export(
    export_id: str,
    db: AsyncSession = Depends(get_db),
):
    obj = await export_service.delete(db, id=export_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Export not found")
    return None
