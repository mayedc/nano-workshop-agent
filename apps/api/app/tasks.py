import asyncio
from typing import Any

from app.core.celery import celery_app
from app.db.session import AsyncSessionLocal
from app.schemas import EvidenceCreate
from app.services import asset as asset_service
from app.services import evidence as evidence_service
from app.services.preprocessing import preprocessing_service
from app.services.storage import get_storage


@celery_app.task(bind=True, max_retries=3)
def process_asset_task(self, asset_id: str, project_id: str) -> dict[str, Any]:
    """Celery task to process an asset and create evidence records."""
    try:
        return asyncio.run(_process_asset_async(asset_id, project_id))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=10)


async def _process_asset_async(asset_id: str, project_id: str) -> dict[str, Any]:
    async with AsyncSessionLocal() as db:
        try:
            # Update status to in_progress
            asset = await asset_service.get(db, asset_id)
            if not asset:
                return {"error": f"Asset {asset_id} not found"}

            await asset_service.update(
                db,
                db_obj=asset,
                obj_in={"processing_status": "in_progress"},
            )

            # Read file from storage
            storage = get_storage()
            file_bytes = storage.get_object(asset.storage_key)

            # Process
            result = await preprocessing_service.process_asset(
                file_bytes=file_bytes,
                filename=asset.filename,
                mime_type=asset.mime_type,
                asset_type=asset.asset_type,
            )

            # Create evidence records
            evidence_ids: list[str] = []
            for candidate in result.evidence_candidates:
                ev = await evidence_service.create(
                    db,
                    obj_in=EvidenceCreate(
                        project_id=project_id,
                        asset_id=asset_id,
                        type=candidate["type"],
                        content=candidate["content"],
                        extra_metadata=candidate.get("metadata", {}),
                    ).model_dump(),
                )
                evidence_ids.append(ev.id)

            # Update asset status to completed
            await asset_service.update(
                db,
                db_obj=asset,
                obj_in={
                    "processing_status": "completed",
                    "extra_metadata": {
                        **(asset.extra_metadata or {}),
                        "processing_result": result.to_dict(),
                        "evidence_ids": evidence_ids,
                    },
                },
            )

            return {
                "asset_id": asset_id,
                "status": "completed",
                "evidence_count": len(evidence_ids),
                "evidence_ids": evidence_ids,
            }

        except Exception as exc:
            # Update status to failed
            asset = await asset_service.get(db, asset_id)
            if asset:
                await asset_service.update(
                    db,
                    db_obj=asset,
                    obj_in={
                        "processing_status": "failed",
                        "extra_metadata": {
                            **(asset.extra_metadata or {}),
                            "error": str(exc),
                        },
                    },
                )
            raise
