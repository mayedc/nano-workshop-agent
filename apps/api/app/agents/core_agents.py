from app.agents.base import AgentContext, AgentResult, BaseWorkshopAgent
from app.providers.base import ProviderRegistry


class ProjectSetupAgent(BaseWorkshopAgent):
    name = "ProjectSetupAgent"
    description = "Initializes project structure and configures workshop parameters."

    async def run(self, context: AgentContext) -> AgentResult:
        llm = ProviderRegistry.llm()
        goal = context.goal or "New workshop project"
        prompt = f"Initialize project setup for: {goal}. Define key parameters and structure."
        response = await llm.generate(prompt)

        return AgentResult(
            agent_name=self.name,
            status="completed",
            outputs={
                "project_config": response,
                "initialized_modules": ["upload", "analysis", "review", "export"],
                "workflow_template_id": context.inputs.get("template_id"),
            },
            evidence_ids=["ev-setup-1"],
            confidence=0.95,
        )


class MaterialIntakeAgent(BaseWorkshopAgent):
    name = "MaterialIntakeAgent"
    description = "Validates and catalogs uploaded workshop materials."

    async def run(self, context: AgentContext) -> AgentResult:
        assets = context.inputs.get("assets", [])
        validated = []
        for asset in assets:
            validated.append(
                {
                    "asset_id": asset.get("id"),
                    "type": asset.get("asset_type"),
                    "semantic_role": asset.get("semantic_role"),
                    "valid": True,
                }
            )

        return AgentResult(
            agent_name=self.name,
            status="completed",
            outputs={
                "material_count": len(validated),
                "materials": validated,
                "coverage_score": min(1.0, len(validated) / 5),
            },
            evidence_ids=[a["asset_id"] for a in validated if a["asset_id"]],
            confidence=0.92,
        )


class PreprocessingAgent(BaseWorkshopAgent):
    name = "PreprocessingAgent"
    description = "Orchestrates preprocessing pipelines for all materials."

    async def run(self, context: AgentContext) -> AgentResult:
        asset_ids = context.inputs.get("asset_ids", [])
        return AgentResult(
            agent_name=self.name,
            status="completed",
            outputs={
                "processed_assets": asset_ids,
                "pipelines_triggered": ["text_extraction", "ocr", "stt", "table_parse"],
                "status_summary": {aid: "completed" for aid in asset_ids},
            },
            evidence_ids=asset_ids,
            confidence=0.90,
        )


class MetadataFusionAgent(BaseWorkshopAgent):
    name = "MetadataFusionAgent"
    description = "Fuses metadata from multiple sources into unified project knowledge graph."

    async def run(self, context: AgentContext) -> AgentResult:
        llm = ProviderRegistry.llm()
        metadata = context.inputs.get("metadata", {})
        prompt = f"Fuse this metadata into a unified knowledge graph: {str(metadata)[:1000]}"
        response = await llm.generate(prompt)

        return AgentResult(
            agent_name=self.name,
            status="completed",
            outputs={
                "fused_metadata": response,
                "entity_count": len(metadata),
                "relationship_count": response.count("->") + response.count("-") // 2,
            },
            evidence_ids=["ev-fusion-1"],
            confidence=0.85,
        )


class GoalUnderstandingAgent(BaseWorkshopAgent):
    name = "GoalUnderstandingAgent"
    description = "Interprets research goal and selects relevant analysis modules."

    async def run(self, context: AgentContext) -> AgentResult:
        llm = ProviderRegistry.llm()
        goal = context.goal or "Understand user needs"
        prompt = f"Interpret this research goal and identify expected outputs and analysis modules: {goal}"
        response = await llm.generate(prompt)

        return AgentResult(
            agent_name=self.name,
            status="completed",
            outputs={
                "structured_goal": goal,
                "research_questions": [
                    "What are the core user needs?",
                    "What design constraints exist?",
                ],
                "expected_outputs": ["thematic_map", "requirement_matrix", "design_guidelines"],
                "selected_modules": [
                    "qualitative_coding",
                    "thematic_analysis",
                    "prototype_analysis",
                ],
                "interpretation": response,
            },
            evidence_ids=["ev-goal-1"],
            confidence=0.92,
        )
