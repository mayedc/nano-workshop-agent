from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field


class AgentContext(BaseModel):
    project_id: str
    goal: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    inputs: dict[str, Any] = Field(default_factory=dict)
    memory: dict[str, Any] = Field(default_factory=dict)
    constraints: dict[str, Any] = Field(default_factory=dict)


class AgentResult(BaseModel):
    agent_name: str
    status: str
    outputs: dict[str, Any] = Field(default_factory=dict)
    evidence_ids: list[str] = Field(default_factory=list)
    confidence: float = 0.0
    errors: list[str] = Field(default_factory=list)


class BaseWorkshopAgent(ABC):
    name: str = ""
    description: str = ""

    @abstractmethod
    async def run(self, context: AgentContext) -> AgentResult:
        pass
