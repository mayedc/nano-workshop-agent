from typing import Any

from app.agents.base import AgentContext, AgentResult, BaseWorkshopAgent


class GoalUnderstandingAgent(BaseWorkshopAgent):
    name = "GoalUnderstandingAgent"
    description = "Understands and structures the research goal from project inputs."

    async def run(self, context: AgentContext) -> AgentResult:
        goal = context.goal or "Understand user needs for autonomous vehicle eHMI"
        return AgentResult(
            agent_name=self.name,
            status="completed",
            outputs={
                "structured_goal": goal,
                "research_questions": [
                    "What information do road users need from AVs?",
                    "How should eHMI convey intent?",
                ],
                "success_criteria": ["Clear design guidelines", "Validated concepts"],
            },
            confidence=0.92,
        )


class QualitativeAnalysisAgent(BaseWorkshopAgent):
    name = "QualitativeAnalysisAgent"
    description = "Performs qualitative coding and thematic analysis on workshop data."

    async def run(self, context: AgentContext) -> AgentResult:
        evidence = context.inputs.get("evidence", [])
        return AgentResult(
            agent_name=self.name,
            status="completed",
            outputs={
                "codes": ["trust", "safety", "visibility", "intention"],
                "themes": [
                    {"name": "Trust Building", "description": "How eHMI builds trust", "code_count": 12},
                    {"name": "Safety Perception", "description": "Perceived safety factors", "code_count": 8},
                ],
                "evidence_count": len(evidence),
            },
            evidence_ids=[e.get("id", "ev-1") for e in evidence[:5]],
            confidence=0.85,
        )


class QuantitativeAnalysisAgent(BaseWorkshopAgent):
    name = "QuantitativeAnalysisAgent"
    description = "Analyzes questionnaire and statistical data."

    async def run(self, context: AgentContext) -> AgentResult:
        data = context.inputs.get("quantitative_data", {})
        return AgentResult(
            agent_name=self.name,
            status="completed",
            outputs={
                "sample_size": data.get("n", 42),
                "likert_means": {"trust": 3.8, "safety": 4.2, "visibility": 3.5},
                "significant_findings": [
                    {"variable": "trust", "p_value": 0.03, "effect_size": 0.45},
                ],
                "charts": ["bar_trust", "radar_safety"],
            },
            confidence=0.88,
        )


class DesignInsightAgent(BaseWorkshopAgent):
    name = "DesignInsightAgent"
    description = "Generates design insights and recommendations from analysis results."

    async def run(self, context: AgentContext) -> AgentResult:
        themes = context.inputs.get("themes", [])
        quant = context.inputs.get("quantitative", {})
        return AgentResult(
            agent_name=self.name,
            status="completed",
            outputs={
                "insights": [
                    {
                        "title": "Color-coded intent signals improve trust",
                        "confidence": 0.91,
                        "supporting_evidence": ["ev-1", "ev-3"],
                    },
                    {
                        "title": "Pedestrians prefer frontal displays",
                        "confidence": 0.87,
                        "supporting_evidence": ["ev-2"],
                    },
                ],
                "guidelines": [
                    "Use blue for safe/passing states",
                    "Display intent 2 seconds before action",
                ],
                "design_principles": ["Clarity", "Timeliness", "Cultural adaptability"],
            },
            evidence_ids=["ev-1", "ev-2", "ev-3"],
            confidence=0.89,
        )


class ReportGenerationAgent(BaseWorkshopAgent):
    name = "ReportGenerationAgent"
    description = "Generates structured academic reports from all analysis outputs."

    async def run(self, context: AgentContext) -> AgentResult:
        insights = context.inputs.get("insights", [])
        return AgentResult(
            agent_name=self.name,
            status="completed",
            outputs={
                "report_sections": [
                    {"title": "Executive Summary", "content": "..."},
                    {"title": "Methodology", "content": "..."},
                    {"title": "Findings", "content": "..."},
                    {"title": "Recommendations", "content": "..."},
                ],
                "export_formats": ["docx", "pdf", "pptx"],
                "insight_count": len(insights),
            },
            confidence=0.95,
        )


def register_mock_agents(registry: Any) -> None:
    from app.agents.analysis_agents import (
        CodingAgent,
        QualitativeAnalysisAgent,
        QuantitativeAnalysisAgent,
        ThemeExtractionAgent,
    )
    from app.agents.core_agents import (
        GoalUnderstandingAgent,
        MaterialIntakeAgent,
        MetadataFusionAgent,
        PreprocessingAgent,
        ProjectSetupAgent,
        WorkshopPlanningAgent,
    )
    from app.agents.design_agents import (
        DesignConceptAgent,
        DesignInsightAgent,
        PrototypeAnalysisAgent,
    )
    from app.agents.data_analysis_agents import (
        CodeAgent,
        DataProfileAgent,
        PlannerAgent,
        RepairAgent,
        ResultExplainerAgent,
    )
    from app.agents.eval_agents import EvaluationAgent
    from app.agents.realtime_agents import MCPConnectorAgent, MeetingRealtimeAgent
    from app.agents.reporting_agents import (
        ExpertReviewAgent,
        ExportAgent,
        IterationAgent,
        ReportGenerationAgent,
    )

    # Core agents
    registry.register(ProjectSetupAgent())
    registry.register(MaterialIntakeAgent())
    registry.register(PreprocessingAgent())
    registry.register(MetadataFusionAgent())
    registry.register(GoalUnderstandingAgent())
    registry.register(WorkshopPlanningAgent())

    # Analysis agents
    registry.register(QualitativeAnalysisAgent())
    registry.register(CodingAgent())
    registry.register(ThemeExtractionAgent())
    registry.register(QuantitativeAnalysisAgent())

    # Design agents
    registry.register(PrototypeAnalysisAgent())
    registry.register(DesignInsightAgent())
    registry.register(DesignConceptAgent())

    # Reporting agents
    registry.register(ExpertReviewAgent())
    registry.register(IterationAgent())
    registry.register(ReportGenerationAgent())
    registry.register(ExportAgent())

    # Realtime agents
    registry.register(MeetingRealtimeAgent())
    registry.register(MCPConnectorAgent())

    # Evaluation agents
    registry.register(EvaluationAgent())

    # Data analysis agents
    registry.register(DataProfileAgent())
    registry.register(PlannerAgent())
    registry.register(CodeAgent())
    registry.register(RepairAgent())
    registry.register(ResultExplainerAgent())
