from app.models import (
    AgentRun,
    Asset,
    Code,
    Evidence,
    ExportRecord,
    Project,
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
