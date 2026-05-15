import asyncio
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

from app.agents.base import AgentContext, AgentResult
from app.agents.registry import AgentRegistry


class WorkflowStep(BaseModel):
    id: str
    agent: str
    depends_on: list[str] = Field(default_factory=list)
    inputs: dict[str, Any] = Field(default_factory=dict)


class WorkflowPlan(BaseModel):
    project_id: str
    steps: list[WorkflowStep]


class WorkflowResult(BaseModel):
    step_id: str
    agent_name: str
    status: str
    result: AgentResult | None = None
    error: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None


class WorkflowOrchestrator:
    def __init__(self, registry: AgentRegistry) -> None:
        self.registry = registry
        self._stop_on_failure: bool = True
        self._persist_lock = asyncio.Lock()

    def set_stop_on_failure(self, value: bool) -> None:
        self._stop_on_failure = value

    async def run(
        self,
        plan: WorkflowPlan,
        context: AgentContext,
        db: Any | None = None,
    ) -> dict[str, WorkflowResult]:
        """Execute a workflow plan. Supports dependency-based execution."""
        results: dict[str, WorkflowResult] = {}
        completed_steps: set[str] = set()

        async def execute_step(step: WorkflowStep) -> WorkflowResult:
            started_at = datetime.now(timezone.utc)
            agent = self.registry.get(step.agent)
            step_context = context.model_copy(deep=True)
            step_context.inputs.update(step.inputs)

            try:
                agent_result = await agent.run(step_context)
                status = agent_result.status
                error = None
            except Exception as exc:
                agent_result = None
                status = "failed"
                error = str(exc)

            completed_at = datetime.now(timezone.utc)

            # Persist to DB if available
            if db is not None:
                await self._persist_run(
                    db=db,
                    project_id=plan.project_id,
                    step_id=step.id,
                    agent_name=step.agent,
                    status=status,
                    result=agent_result,
                    error=error,
                )

            return WorkflowResult(
                step_id=step.id,
                agent_name=step.agent,
                status=status,
                result=agent_result,
                error=error,
                started_at=started_at,
                completed_at=completed_at,
            )

        async def run_step(step: WorkflowStep) -> None:
            # Wait for dependencies
            if step.depends_on:
                pending = set(step.depends_on) - completed_steps
                while pending:
                    await asyncio.sleep(0.1)
                    pending = set(step.depends_on) - completed_steps

            # Execute
            result = await execute_step(step)
            results[step.id] = result
            completed_steps.add(step.id)

        # Run all steps concurrently where dependencies allow
        tasks = [asyncio.create_task(run_step(s)) for s in plan.steps]

        for task in asyncio.as_completed(tasks):
            await task
            # Check if we should stop on failure
            if self._stop_on_failure:
                for step_id, result in results.items():
                    if result.status == "failed":
                        # Cancel remaining tasks
                        for t in tasks:
                            if not t.done():
                                t.cancel()
                        return results

        return results

    async def rerun_step(
        self,
        plan: WorkflowPlan,
        step_id: str,
        context: AgentContext,
        db: Any | None = None,
    ) -> WorkflowResult:
        """Rerun a single workflow step."""
        step = next((s for s in plan.steps if s.id == step_id), None)
        if step is None:
            raise ValueError(f"Step {step_id} not found in plan")

        started_at = datetime.now(timezone.utc)
        agent = self.registry.get(step.agent)
        step_context = context.model_copy(deep=True)
        step_context.inputs.update(step.inputs)

        try:
            agent_result = await agent.run(step_context)
            status = agent_result.status
            error = None
        except Exception as exc:
            agent_result = None
            status = "failed"
            error = str(exc)

        if db is not None:
            await self._persist_run(
                db=db,
                project_id=plan.project_id,
                step_id=step.id,
                agent_name=step.agent,
                status=status,
                result=agent_result,
                error=error,
            )

        return WorkflowResult(
            step_id=step.id,
            agent_name=step.agent,
            status=status,
            result=agent_result,
            error=error,
            started_at=started_at,
            completed_at=datetime.now(timezone.utc),
        )

    async def _persist_run(
        self,
        db: Any,
        project_id: str,
        step_id: str,
        agent_name: str,
        status: str,
        result: AgentResult | None,
        error: str | None,
    ) -> None:
        async with self._persist_lock:
            from app.schemas import AgentRunCreate
            from app.services import agent_run as agent_run_service

            output_data = result.outputs if result else {}
            evidence_ids = result.evidence_ids if result else []
            confidence = result.confidence if result else None

            await agent_run_service.create(
                db,
                obj_in=AgentRunCreate(
                    project_id=project_id,
                    agent_name=agent_name,
                    step_id=int(step_id) if step_id.isdigit() else None,
                    status=status,
                    input_data={"step_id": step_id},
                    output_data=output_data,
                    confidence=confidence,
                    evidence_ids=evidence_ids,
                    error=error,
                ).model_dump(),
            )
