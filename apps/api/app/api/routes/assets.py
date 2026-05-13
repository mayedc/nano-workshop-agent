from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas import AssetCreate, AssetResponse, AssetUpdate
from app.services import asset as asset_service

router = APIRouter()


@router.get("/", response_model=list[AssetResponse])
async def list_assets(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    return await asset_service.get_multi(db, skip=skip, limit=limit)


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
    return None
