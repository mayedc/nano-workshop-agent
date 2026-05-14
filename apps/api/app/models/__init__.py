import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    projects: Mapped[list["Project"]] = relationship("Project", back_populates="owner")


class WorkshopTemplate(Base):
    __tablename__ = "workshop_templates"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    slug: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    config: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    projects: Mapped[list["Project"]] = relationship("Project", back_populates="template")


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    template_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("workshop_templates.id"), nullable=True
    )
    owner_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="draft")
    config: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    owner: Mapped["User"] = relationship("User", back_populates="projects")
    template: Mapped["WorkshopTemplate | None"] = relationship("WorkshopTemplate", back_populates="projects")
    assets: Mapped[list["Asset"]] = relationship("Asset", back_populates="project")
    evidence: Mapped[list["Evidence"]] = relationship("Evidence", back_populates="project")
    codes: Mapped[list["Code"]] = relationship("Code", back_populates="project")
    themes: Mapped[list["Theme"]] = relationship("Theme", back_populates="project")
    requirements: Mapped[list["Requirement"]] = relationship("Requirement", back_populates="project")
    agent_runs: Mapped[list["AgentRun"]] = relationship("AgentRun", back_populates="project")
    exports: Mapped[list["ExportRecord"]] = relationship("ExportRecord", back_populates="project")
    feedback: Mapped[list["ExpertFeedback"]] = relationship("ExpertFeedback", back_populates="project")
    questionnaire_results: Mapped[list["QuestionnaireResult"]] = relationship("QuestionnaireResult", back_populates="project")
    design_insights: Mapped[list["DesignInsight"]] = relationship("DesignInsight", back_populates="project")
    prototype_reviews: Mapped[list["PrototypeReview"]] = relationship("PrototypeReview", back_populates="project")
    concept_designs: Mapped[list["ConceptDesign"]] = relationship("ConceptDesign", back_populates="project")


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    filename: Mapped[str] = mapped_column(String(512), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(128), nullable=False)
    asset_type: Mapped[str] = mapped_column(String(32), nullable=False)
    size: Mapped[int] = mapped_column(Integer, default=0)
    storage_key: Mapped[str] = mapped_column(String(512), nullable=False)
    semantic_role: Mapped[str | None] = mapped_column(String(128), nullable=True)
    source_stage: Mapped[str | None] = mapped_column(String(128), nullable=True)
    uploaded_by: Mapped[str | None] = mapped_column(String(128), nullable=True)
    processing_status: Mapped[str] = mapped_column(String(32), default="pending")
    extra_metadata: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    project: Mapped["Project"] = relationship("Project", back_populates="assets")
    evidence: Mapped[list["Evidence"]] = relationship("Evidence", back_populates="asset")


class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    asset_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("assets.id"), nullable=True
    )
    type: Mapped[str] = mapped_column(String(32), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    extra_metadata: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    extracted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    project: Mapped["Project"] = relationship("Project", back_populates="evidence")
    asset: Mapped["Asset | None"] = relationship("Asset", back_populates="evidence")


class Code(Base):
    __tablename__ = "codes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    evidence_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    created_by: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    project: Mapped["Project"] = relationship("Project", back_populates="codes")


class Theme(Base):
    __tablename__ = "themes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    code_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    evidence_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    confidence: Mapped[float | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    project: Mapped["Project"] = relationship("Project", back_populates="themes")


class Requirement(Base):
    __tablename__ = "requirements"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(String(16), default="medium")
    source_evidence_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(32), default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    project: Mapped["Project"] = relationship("Project", back_populates="requirements")


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    agent_name: Mapped[str] = mapped_column(String(64), nullable=False)
    step_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="pending")
    input_data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    output_data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    confidence: Mapped[float | None] = mapped_column(nullable=True)
    evidence_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    review_status: Mapped[str] = mapped_column(String(32), default="pending")
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    project: Mapped["Project"] = relationship("Project", back_populates="agent_runs")


class ExportRecord(Base):
    __tablename__ = "export_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    format: Mapped[str] = mapped_column(String(16), nullable=False)
    file_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    config: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    generated_by: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)

    project: Mapped["Project"] = relationship("Project", back_populates="exports")


class ExpertFeedback(Base):
    __tablename__ = "expert_feedback"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    reviewer_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    target_type: Mapped[str] = mapped_column(String(32), nullable=False)
    target_id: Mapped[str] = mapped_column(String(36), nullable=False)
    action: Mapped[str] = mapped_column(String(32), nullable=False)
    score: Mapped[int | None] = mapped_column(nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggested_revision: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    review_status: Mapped[str] = mapped_column(String(32), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    project: Mapped["Project"] = relationship("Project", back_populates="feedback")


class QuestionnaireResult(Base):
    __tablename__ = "questionnaire_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    respondent_count: Mapped[int] = mapped_column(Integer, default=0)
    scales: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    descriptive_stats: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    significance_tests: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    chart_data: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    extra_metadata: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    project: Mapped["Project"] = relationship("Project", back_populates="questionnaire_results")


class DesignInsight(Base):
    __tablename__ = "design_insights"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    confidence: Mapped[float | None] = mapped_column(nullable=True)
    supporting_evidence_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    severity: Mapped[str | None] = mapped_column(String(16), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    project: Mapped["Project"] = relationship("Project", back_populates="design_insights")


class PrototypeReview(Base):
    __tablename__ = "prototype_reviews"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    prototype_name: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str | None] = mapped_column(String(32), nullable=True)
    feedback: Mapped[str] = mapped_column(Text, nullable=True)
    usability_score: Mapped[float | None] = mapped_column(nullable=True)
    issues_found: Mapped[list[str]] = mapped_column(JSON, default=list)
    recommendations: Mapped[list[str]] = mapped_column(JSON, default=list)
    review_status: Mapped[str] = mapped_column(String(32), default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    project: Mapped["Project"] = relationship("Project", back_populates="prototype_reviews")


class ConceptDesign(Base):
    __tablename__ = "concept_designs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    confidence: Mapped[float | None] = mapped_column(nullable=True)
    review_status: Mapped[str] = mapped_column(String(32), default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    project: Mapped["Project"] = relationship("Project", back_populates="concept_designs")
