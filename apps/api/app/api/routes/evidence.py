from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas import EvidenceCreate, EvidenceResponse, EvidenceUpdate
from app.services import evidence as evidence_service

router = APIRouter()


@router.get("/", response_model=list[EvidenceResponse])
async def list_evidence(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    return await evidence_service.get_multi(db, skip=skip, limit=limit)


@router.get("/project/{project_id}", response_model=list[EvidenceResponse])
async def list_project_evidence(
    project_id: str,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select
    from app.models import Evidence

    result = await db.execute(
        select(Evidence).where(Evidence.project_id == project_id).offset(skip).limit(limit)
    )
    return list(result.scalars().all())


@router.post("/", response_model=EvidenceResponse, status_code=status.HTTP_201_CREATED)
async def create_evidence(
    obj_in: EvidenceCreate,
    db: AsyncSession = Depends(get_db),
):
    return await evidence_service.create(db, obj_in=obj_in.model_dump())


@router.get("/{evidence_id}", response_model=EvidenceResponse)
async def get_evidence(
    evidence_id: str,
    db: AsyncSession = Depends(get_db),
):
    obj = await evidence_service.get(db, evidence_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return obj


@router.put("/{evidence_id}", response_model=EvidenceResponse)
async def update_evidence(
    evidence_id: str,
    obj_in: EvidenceUpdate,
    db: AsyncSession = Depends(get_db),
):
    db_obj = await evidence_service.get(db, evidence_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return await evidence_service.update(
        db, db_obj=db_obj, obj_in=obj_in.model_dump(exclude_unset=True)
    )


@router.delete("/{evidence_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_evidence(
    evidence_id: str,
    db: AsyncSession = Depends(get_db),
):
    obj = await evidence_service.delete(db, id=evidence_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return None
