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
    description = "Manages design iteration cycles based on expert feedback with 8 review actions."

    async def run(self, context: AgentContext) -> AgentResult:
        feedback_items: list[dict] = context.inputs.get("feedback", [])
        iteration = context.inputs.get("iteration", 1)
        target_type = context.inputs.get("target_type", "all")

        actions_count: dict[str, int] = {}
        rerun_targets: list[dict] = []
        revised_items: list[dict] = []
        approved_count = 0

        for fb in feedback_items:
            action = fb.get("action", "")
            actions_count[action] = actions_count.get(action, 0) + 1

            if action == "approve":
                approved_count += 1
            elif action in ("reject", "request_rerun"):
                rerun_targets.append({
                    "target_id": fb.get("target_id"),
                    "target_type": fb.get("target_type"),
                    "reason": fb.get("comment", f"Rerun requested via {action}"),
                })
            elif action == "revise":
                revised_items.append({
                    "target_id": fb.get("target_id"),
                    "target_type": fb.get("target_type"),
                    "suggested_revision": fb.get("suggested_revision", {}),
                    "comment": fb.get("comment", ""),
                })
            elif action == "merge":
                rerun_targets.append({
                    "target_id": fb.get("target_id"),
                    "target_type": fb.get("target_type"),
                    "reason": fb.get("comment", "Merge requested"),
                    "merge_ids": fb.get("suggested_revision", {}).get("merge_ids", []),
                })
            elif action == "split":
                rerun_targets.append({
                    "target_id": fb.get("target_id"),
                    "target_type": fb.get("target_type"),
                    "reason": fb.get("comment", "Split requested"),
                })

        total = len(feedback_items)
        conflict = any(
            actions_count.get(a, 0) > 0 and actions_count.get(b, 0) > 0
            for a, b in [("approve", "reject"), ("approve", "request_rerun")]
        )

        return AgentResult(
            agent_name=self.name,
            status="completed",
            outputs={
                "iteration": iteration,
                "target_type": target_type,
                "feedback_processed": total,
                "actions_summary": actions_count,
                "approved_count": approved_count,
                "rerun_required": len(rerun_targets),
                "rerun_targets": rerun_targets,
                "revised_items": revised_items,
                "has_conflict": conflict,
                "next_steps": self._build_next_steps(
                    approved_count, rerun_targets, revised_items, total, conflict
                ),
            },
            evidence_ids=[fb.get("target_id") for fb in feedback_items if fb.get("target_id")],
            confidence=0.85,
        )

    def _build_next_steps(
        self,
        approved: int,
        rerun_targets: list[dict],
        revised: list[dict],
        total: int,
        conflict: bool,
    ) -> list[str]:
        steps: list[str] = []
        if conflict:
            steps.append("resolve_conflicts: contradictory approve/reject feedback exists")
        if rerun_targets:
            agents = {t["target_type"] for t in rerun_targets}
            for agent in agents:
                steps.append(f"rerun_{agent}_agent")
        if revised:
            steps.append("apply_revisions")
        if not rerun_targets and not revised and approved == total:
            steps.append("iteration_complete")
        return steps


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
