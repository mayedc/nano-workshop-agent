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
    User,
    WorkshopTemplate,
)
from app.services.base import CRUDBase

user = CRUDBase(User)
template = CRUDBase(WorkshopTemplate)
project = CRUDBase(Project)
asset = CRUDBase(Asset)
evidence = CRUDBase(Evidence)
code = CRUDBase(Code)
theme = CRUDBase(Theme)
requirement = CRUDBase(Requirement)
agent_run = CRUDBase(AgentRun)
export_record = CRUDBase(ExportRecord)
feedback = CRUDBase(ExpertFeedback)
questionnaire = CRUDBase(QuestionnaireResult)
design_insight = CRUDBase(DesignInsight)
prototype_review = CRUDBase(PrototypeReview)
concept_design = CRUDBase(ConceptDesign)
