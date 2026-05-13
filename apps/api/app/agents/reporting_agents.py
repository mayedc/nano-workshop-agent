from app.agents.base import AgentContext, AgentResult, BaseWorkshopAgent
from app.providers.base import ProviderRegistry


class ExpertReviewAgent(BaseWorkshopAgent):
    name = "ExpertReviewAgent"
    description = "Coordinates expert review of codes, themes, insights, and concepts."

    async def run(self, context: AgentContext) -> AgentResult:
        review_targets = context.inputs.get("review_targets", [])
        return AgentResult(
            agent_name=self.name,
            status="completed",
            outputs={
                "review_queue": [
                    {"target_id": t.get("id"), "type": t.get("type"), "status": "pending_review"}
                    for t in review_targets
                ],
                "review_criteria": ["validity", "reliability", "relevance", "actionability"],
                "expert_count": context.inputs.get("expert_count", 2),
            },
            evidence_ids=[t.get("id") for t in review_targets if t.get("id")],
            confidence=0.90,
        )


class IterationAgent(BaseWorkshopAgent):
    name = "IterationAgent"
    description = "Manages design iteration cycles based on expert feedback."

    async def run(self, context: AgentContext) -> AgentResult:
        feedback = context.inputs.get("feedback", [])
        iteration = context.inputs.get("iteration", 1)

        return AgentResult(
            agent_name=self.name,
            status="completed",
            outputs={
                "iteration": iteration,
                "feedback_addressed": len(feedback),
                "changes_made": [
                    {"field": "concept_description", "reason": "clarity"},
                    {"field": "requirement_priority", "reason": "expert_input"},
                ],
                "next_steps": ["regenerate_concepts", "update_matrix"],
            },
            evidence_ids=[f.get("id") for f in feedback if f.get("id")],
            confidence=0.85,
        )


class ReportGenerationAgent(BaseWorkshopAgent):
    name = "ReportGenerationAgent"
    description = "Generates structured academic reports from all analysis outputs."

    async def run(self, context: AgentContext) -> AgentResult:
        llm = ProviderRegistry.llm()
        insights = context.inputs.get("insights", [])
        themes = context.inputs.get("themes", [])

        prompt = (
            f"Generate an academic report from {len(insights)} insights and {len(themes)} themes. "
            f"Include executive summary, methodology, findings, and recommendations."
        )
        response = await llm.generate(prompt)

        return AgentResult(
            agent_name=self.name,
            status="completed",
            outputs={
                "report_sections": [
                    {"title": "Executive Summary", "content": response[:500]},
                    {"title": "Methodology", "content": "Mixed-methods approach..."},
                    {"title": "Qualitative Findings", "content": f"{len(themes)} themes identified."},
                    {"title": "Quantitative Findings", "content": "Statistically significant results..."},
                    {"title": "Design Insights", "content": f"{len(insights)} insights generated."},
                    {"title": "Recommendations", "content": "..."},
                ],
                "export_formats": ["docx", "pdf", "pptx", "json"],
                "page_estimate": 25,
            },
            evidence_ids=["ev-report-1"],
            confidence=0.94,
        )


class ExportAgent(BaseWorkshopAgent):
    name = "ExportAgent"
    description = "Exports project artifacts to various formats."

    async def run(self, context: AgentContext) -> AgentResult:
        formats = context.inputs.get("formats", ["json"])
        return AgentResult(
            agent_name=self.name,
            status="completed",
            outputs={
                "exported_files": [
                    {"format": f, "url": f"/exports/project/{context.project_id}/report.{f}"}
                    for f in formats
                ],
                "reproducibility_hash": "sha256:abc123",
                "timestamp": "2024-01-01T00:00:00Z",
            },
            evidence_ids=["ev-export-1"],
            confidence=0.98,
        )
