from typing import Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas import AssetCreate, AssetResponse, AssetUpdate
from app.services import asset as asset_service
from app.services.storage import detect_file_type, generate_storage_key, get_storage
from app.templates.loader import TemplateRegistry

router = APIRouter()


@router.get("/", response_model=list[AssetResponse])
async def list_assets(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    return await asset_service.get_multi(db, skip=skip, limit=limit)


@router.get("/project/{project_id}", response_model=list[AssetResponse])
async def list_project_assets(
    project_id: str,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select
    from app.models import Asset

    result = await db.execute(
        select(Asset).where(Asset.project_id == project_id).offset(skip).limit(limit)
    )
    return list(result.scalars().all())


@router.post("/project/{project_id}/upload", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
async def upload_asset(
    project_id: str,
    file: UploadFile = File(...),
    semantic_role: str | None = Form(None),
    source_stage: str | None = Form(None),
    db: AsyncSession = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    # Validate semantic_role against template if provided
    if semantic_role:
        from app.models import Project
        from sqlalchemy import select

        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()
        if project and project.template_id:
            template = TemplateRegistry.get(project.template_id)
            if template and semantic_role not in template.input_roles:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid semantic_role '{semantic_role}' for this project template. "
                    f"Valid roles: {template.input_roles}",
                )

    # Detect file type
    file_info = detect_file_type(file.filename)
    content = await file.read()
    size = len(content)

    # Store in object storage
    storage = get_storage()
    storage_key = generate_storage_key(project_id, file.filename)
    storage.put_object(
        storage_key,
        content,
        length=size,
        content_type=file_info["mime_type"],
    )

    # Create DB record
    obj_in = AssetCreate(
        project_id=project_id,
        filename=file.filename,
        mime_type=file_info["mime_type"],
        asset_type=file_info["asset_type"],
        size=size,
        storage_key=storage_key,
        semantic_role=semantic_role,
        source_stage=source_stage,
        uploaded_by="system",
        processing_status="pending",
    )
    return await asset_service.create(db, obj_in=obj_in.model_dump())


@router.post("/", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
async def create_asset(
    obj_in: AssetCreate,
    db: AsyncSession = Depends(get_db),
):
    return await asset_service.create(db, obj_in=obj_in.model_dump())


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: str,
    db: AsyncSession = Depends(get_db),
):
    obj = await asset_service.get(db, asset_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Asset not found")
    return obj


@router.put("/{asset_id}", response_model=AssetResponse)
async def update_asset(
    asset_id: str,
    obj_in: AssetUpdate,
    db: AsyncSession = Depends(get_db),
):
    db_obj = await asset_service.get(db, asset_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Asset not found")
    return await asset_service.update(db, db_obj=db_obj, obj_in=obj_in.model_dump(exclude_unset=True))


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(
    asset_id: str,
    db: AsyncSession = Depends(get_db),
):
    obj = await asset_service.delete(db, id=asset_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Asset not found")

    # Also remove from object storage
    if obj.storage_key:
        storage = get_storage()
        storage.remove_object(obj.storage_key)

    return None
