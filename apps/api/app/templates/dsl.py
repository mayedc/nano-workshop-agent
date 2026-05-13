from typing import Any

from pydantic import BaseModel, Field, field_validator


class OntologyConcept(BaseModel):
    name: str
    description: str | None = None


class OntologyRelationship(BaseModel):
    source: str
    target: str
    relation_type: str = "related_to"


class Ontology(BaseModel):
    concepts: list[str] = Field(default_factory=list)
    relationships: list[str] = Field(default_factory=list)
    participant_groups: list[str] = Field(default_factory=list)
    need_categories: list[str] = Field(default_factory=list)


class WorkflowStep(BaseModel):
    id: int
    name: str
    agent_name: str
    status: str = "pending"
    depends_on: list[int] = Field(default_factory=list)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        allowed = {"pending", "in_progress", "awaiting_input", "completed", "failed"}
        if v not in allowed:
            raise ValueError(f"status must be one of {allowed}")
        return v


class ReportSection(BaseModel):
    title: str
    type: str
    source_steps: list[int] = Field(default_factory=list)

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        allowed = {"text", "chart", "table", "image"}
        if v not in allowed:
            raise ValueError(f"type must be one of {allowed}")
        return v


class WorkshopTemplateDSL(BaseModel):
    id: str
    name: str
    description: str
    input_roles: list[str] = Field(default_factory=list)
    analysis_modules: list[str] = Field(default_factory=list)
    workflow_steps: list[WorkflowStep] = Field(default_factory=list)
    ontology: Ontology = Field(default_factory=Ontology)
    output_types: list[str] = Field(default_factory=list)
    report_structure: list[ReportSection] = Field(default_factory=list)

    @field_validator("workflow_steps")
    @classmethod
    def validate_step_ids(cls, steps: list[WorkflowStep]) -> list[WorkflowStep]:
        ids = {s.id for s in steps}
        for step in steps:
            for dep in step.depends_on:
                if dep not in ids:
                    raise ValueError(
                        f"step {step.id} depends on non-existent step {dep}"
                    )
        return steps

    def get_step(self, step_id: int) -> WorkflowStep | None:
        for step in self.workflow_steps:
            if step.id == step_id:
                return step
        return None

    def get_dependencies(self, step_id: int) -> list[int]:
        step = self.get_step(step_id)
        return step.depends_on if step else []

    def get_dependents(self, step_id: int) -> list[int]:
        return [
            s.id for s in self.workflow_steps
            if step_id in s.depends_on
        ]
