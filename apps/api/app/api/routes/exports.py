from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import (
    AgentRun,
    Asset,
    Code,
    ConceptDesign,
    DesignInsight,
    Evidence,
    ExpertFeedback,
    ExportRecord,
    Project,
    PrototypeReview,
    QuestionnaireResult,
    Requirement,
    Theme,
)
from app.schemas import ExportRecordCreate, ExportRecordResponse
from app.services import export_record as export_service
from app.services.export_generator import (
    build_report_data,
    generate_csv_tables,
    generate_docx,
    generate_json_export,
    generate_pptx,
)

router = APIRouter()

FORMAT_MIME = {
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "json": "application/json",
    "csv": "application/zip",
}


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
    result = await db.execute(
        select(ExportRecord).where(ExportRecord.project_id == project_id).offset(skip).limit(limit)
    )
    return list(result.scalars().all())


@router.get("/generate/{project_id}")
async def generate_export(
    project_id: str,
    format: str = Query("json", description="Export format: docx, pptx, json, csv"),
    db: AsyncSession = Depends(get_db),
):
    """Generate an export file for a project."""
    if format not in FORMAT_MIME:
        raise HTTPException(
            status_code=422, detail=f"Unsupported format. Choose: {list(FORMAT_MIME.keys())}"
        )

    # Gather all project data
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    data: dict = {}

    for model, key in [
        (Asset, "assets"),
        (Evidence, "evidence"),
        (Code, "codes"),
        (Theme, "themes"),
        (Requirement, "requirements"),
        (QuestionnaireResult, "questionnaire_results"),
        (DesignInsight, "design_insights"),
        (PrototypeReview, "prototype_reviews"),
        (ConceptDesign, "concept_designs"),
        (ExpertFeedback, "expert_feedback"),
        (AgentRun, "agent_runs"),
    ]:
        result = await db.execute(select(model).where(model.project_id == project_id))
        rows = result.scalars().all()
        data[key] = [_row_to_dict(r) for r in rows]

    project_dict = _row_to_dict(project)
    report = build_report_data(project_dict, data)

    # Generate file
    if format == "docx":
        content = generate_docx(report)
        filename = f"report_{project_id[:8]}.docx"
    elif format == "pptx":
        content = generate_pptx(report)
        filename = f"presentation_{project_id[:8]}.pptx"
    elif format == "json":
        content = generate_json_export(report)
        filename = f"metadata_{project_id[:8]}.json"
    elif format == "csv":
        tables = generate_csv_tables(data)
        if not tables:
            raise HTTPException(status_code=404, detail="No data to export as CSV")
        import zipfile

        buf = __import__("io").BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for name, csv_bytes in tables.items():
                zf.writestr(f"{name}.csv", csv_bytes)
        content = buf.getvalue()
        filename = f"csv_tables_{project_id[:8]}.zip"
    else:
        raise HTTPException(status_code=422, detail="Unsupported format")

    # Store export record
    rec = await export_service.create(
        db,
        obj_in={
            "project_id": project_id,
            "format": format,
            "file_url": f"/api/exports/download/{project_id}/{filename}",
            "config": {"filename": filename, "size_bytes": len(content)},
        },
    )

    return Response(
        content=content,
        media_type=FORMAT_MIME[format],
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "X-Export-Id": rec.id,
        },
    )


@router.get("/download/{project_id}/{filename}")
async def download_export(
    project_id: str,
    filename: str,
    format: str = Query("json"),
    db: AsyncSession = Depends(get_db),
):
    """Re-generate and download an export file. Redirects to generate_export logic."""
    return await generate_export(project_id=project_id, format=format, db=db)


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


def _row_to_dict(row) -> dict:
    """Convert a SQLAlchemy model instance to a dictionary."""
    result = {}
    for col in row.__table__.columns:
        val = getattr(row, col.name)
        if isinstance(val, datetime):
            val = val.isoformat()
        result[col.name] = val
    return result
