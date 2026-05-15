from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    email: str
    name: str


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: str | None = None
    name: str | None = None
    password: str | None = None


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    is_active: bool
    created_at: datetime


class WorkshopTemplateBase(BaseModel):
    slug: str
    name: str
    description: str | None = None
    config: dict[str, Any] = Field(default_factory=dict)


class WorkshopTemplateCreate(WorkshopTemplateBase):
    pass


class WorkshopTemplateUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    config: dict[str, Any] | None = None


class WorkshopTemplateResponse(WorkshopTemplateBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime


class ProjectBase(BaseModel):
    name: str
    description: str | None = None
    template_id: str | None = None
    status: str = "draft"
    config: dict[str, Any] = Field(default_factory=dict)


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None
    config: dict[str, Any] | None = None


class ProjectResponse(ProjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    owner_id: str
    created_at: datetime
    updated_at: datetime


class AssetBase(BaseModel):
    filename: str
    mime_type: str
    asset_type: str
    size: int = 0
    storage_key: str
    semantic_role: str | None = None
    source_stage: str | None = None
    uploaded_by: str | None = None
    processing_status: str = "pending"
    extra_metadata: dict[str, Any] = Field(default_factory=dict)


class AssetCreate(AssetBase):
    project_id: str


class AssetUpdate(BaseModel):
    processing_status: str | None = None
    extra_metadata: dict[str, Any] | None = None
    semantic_role: str | None = None


class AssetResponse(AssetBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    created_at: datetime


class EvidenceBase(BaseModel):
    type: str
    content: str
    extra_metadata: dict[str, Any] = Field(default_factory=dict)


class EvidenceCreate(EvidenceBase):
    project_id: str
    asset_id: str | None = None


class EvidenceUpdate(BaseModel):
    type: str | None = None
    content: str | None = None
    extra_metadata: dict[str, Any] | None = None


class EvidenceResponse(EvidenceBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    asset_id: str | None
    extracted_at: datetime


class CodeBase(BaseModel):
    name: str
    description: str | None = None
    evidence_ids: list[str] = Field(default_factory=list)


class CodeCreate(CodeBase):
    project_id: str


class CodeUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    evidence_ids: list[str] | None = None


class CodeResponse(CodeBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    created_by: str | None
    created_at: datetime


class ThemeBase(BaseModel):
    name: str
    description: str | None = None
    code_ids: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    confidence: float | None = None


class ThemeCreate(ThemeBase):
    project_id: str


class ThemeUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    code_ids: list[str] | None = None
    evidence_ids: list[str] | None = None
    confidence: float | None = None


class ThemeResponse(ThemeBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    created_at: datetime


class RequirementBase(BaseModel):
    text: str
    priority: str = "medium"
    source_evidence_ids: list[str] = Field(default_factory=list)
    status: str = "draft"


class RequirementCreate(RequirementBase):
    project_id: str


class RequirementUpdate(BaseModel):
    text: str | None = None
    priority: str | None = None
    source_evidence_ids: list[str] | None = None
    status: str | None = None


class RequirementResponse(RequirementBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    created_at: datetime


class AgentRunBase(BaseModel):
    agent_name: str
    step_id: int | None = None
    status: str = "pending"
    input_data: dict[str, Any] = Field(default_factory=dict)
    output_data: dict[str, Any] = Field(default_factory=dict)
    confidence: float | None = None
    evidence_ids: list[str] = Field(default_factory=list)
    review_status: str = "pending"
    error: str | None = None


class AgentRunCreate(AgentRunBase):
    project_id: str


class AgentRunUpdate(BaseModel):
    status: str | None = None
    output_data: dict[str, Any] | None = None
    confidence: float | None = None
    evidence_ids: list[str] | None = None
    review_status: str | None = None
    error: str | None = None
    completed_at: datetime | None = None


class AgentRunResponse(AgentRunBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    created_at: datetime
    completed_at: datetime | None


class ExportRecordBase(BaseModel):
    format: str
    file_url: str
    config: dict[str, Any] = Field(default_factory=dict)


class ExportRecordCreate(ExportRecordBase):
    project_id: str


class ExportRecordResponse(ExportRecordBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    generated_at: datetime
    generated_by: str | None


# --- Expert Feedback ---

TARGET_TYPES = ["codes", "themes", "requirements", "insights", "concepts", "report_sections"]
REVIEW_ACTIONS = [
    "approve",
    "reject",
    "revise",
    "merge",
    "split",
    "score",
    "comment",
    "request_rerun",
]


class ExpertFeedbackBase(BaseModel):
    target_type: str
    target_id: str
    action: str
    score: int | None = None
    comment: str | None = None
    suggested_revision: dict[str, Any] | None = None
    review_status: str = "pending"


class ExpertFeedbackCreate(ExpertFeedbackBase):
    project_id: str


class ExpertFeedbackUpdate(BaseModel):
    action: str | None = None
    score: int | None = None
    comment: str | None = None
    suggested_revision: dict[str, Any] | None = None
    review_status: str | None = None


class ExpertFeedbackResponse(ExpertFeedbackBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    reviewer_id: str | None
    created_at: datetime


# --- Questionnaire Results ---


class QuestionnaireResultBase(BaseModel):
    name: str
    respondent_count: int = 0
    scales: dict[str, Any] = Field(default_factory=dict)
    descriptive_stats: dict[str, Any] = Field(default_factory=dict)
    significance_tests: dict[str, Any] | None = None
    chart_data: dict[str, Any] | None = None
    extra_metadata: dict[str, Any] = Field(default_factory=dict)


class QuestionnaireResultCreate(QuestionnaireResultBase):
    project_id: str


class QuestionnaireResultUpdate(BaseModel):
    name: str | None = None
    respondent_count: int | None = None
    scales: dict[str, Any] | None = None
    descriptive_stats: dict[str, Any] | None = None
    significance_tests: dict[str, Any] | None = None
    chart_data: dict[str, Any] | None = None
    extra_metadata: dict[str, Any] | None = None


class QuestionnaireResultResponse(QuestionnaireResultBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    created_at: datetime


# --- Design Insight ---


class DesignInsightBase(BaseModel):
    title: str
    description: str | None = None
    category: str | None = None
    confidence: float | None = None
    supporting_evidence_ids: list[str] = Field(default_factory=list)
    severity: str | None = None


class DesignInsightCreate(DesignInsightBase):
    project_id: str


class DesignInsightUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    category: str | None = None
    confidence: float | None = None
    supporting_evidence_ids: list[str] | None = None
    severity: str | None = None


class DesignInsightResponse(DesignInsightBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    created_at: datetime


# --- Prototype Review ---


class PrototypeReviewBase(BaseModel):
    prototype_name: str
    version: str | None = None
    feedback: str | None = None
    usability_score: float | None = None
    issues_found: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    review_status: str = "draft"


class PrototypeReviewCreate(PrototypeReviewBase):
    project_id: str


class PrototypeReviewUpdate(BaseModel):
    prototype_name: str | None = None
    version: str | None = None
    feedback: str | None = None
    usability_score: float | None = None
    issues_found: list[str] | None = None
    recommendations: list[str] | None = None
    review_status: str | None = None


class PrototypeReviewResponse(PrototypeReviewBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    created_at: datetime


# --- Concept Design ---


class ConceptDesignBase(BaseModel):
    name: str
    description: str | None = None
    prompt: str | None = None
    evidence_ids: list[str] = Field(default_factory=list)
    confidence: float | None = None
    review_status: str = "draft"


class ConceptDesignCreate(ConceptDesignBase):
    project_id: str


class ConceptDesignUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    prompt: str | None = None
    evidence_ids: list[str] | None = None
    confidence: float | None = None
    review_status: str | None = None


class ConceptDesignResponse(ConceptDesignBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    created_at: datetime
