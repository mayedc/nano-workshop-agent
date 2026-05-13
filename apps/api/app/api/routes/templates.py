from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas import (
    WorkshopTemplateCreate,
    WorkshopTemplateResponse,
    WorkshopTemplateUpdate,
)
from app.services import template as template_service

router = APIRouter()


@router.get("/", response_model=list[WorkshopTemplateResponse])
async def list_templates(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    return await template_service.get_multi(db, skip=skip, limit=limit)


@router.post("/", response_model=WorkshopTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    obj_in: WorkshopTemplateCreate,
    db: AsyncSession = Depends(get_db),
):
    return await template_service.create(db, obj_in=obj_in.model_dump())


@router.get("/{template_id}", response_model=WorkshopTemplateResponse)
async def get_template(
    template_id: str,
    db: AsyncSession = Depends(get_db),
):
    obj = await template_service.get(db, template_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Template not found")
    return obj


@router.put("/{template_id}", response_model=WorkshopTemplateResponse)
async def update_template(
    template_id: str,
    obj_in: WorkshopTemplateUpdate,
    db: AsyncSession = Depends(get_db),
):
    db_obj = await template_service.get(db, template_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Template not found")
    return await template_service.update(db, db_obj=db_obj, obj_in=obj_in.model_dump(exclude_unset=True))


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: str,
    db: AsyncSession = Depends(get_db),
):
    obj = await template_service.delete(db, id=template_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Template not found")
    return None
