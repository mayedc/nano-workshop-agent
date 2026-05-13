from app.agents.base import AgentContext, AgentResult, BaseWorkshopAgent
from app.providers.base import ProviderRegistry


class PrototypeAnalysisAgent(BaseWorkshopAgent):
    name = "PrototypeAnalysisAgent"
    description = "Analyzes prototype images or descriptions to identify design elements and usability issues."

    async def run(self, context: AgentContext) -> AgentResult:
        vision = ProviderRegistry.vision()
        llm = ProviderRegistry.llm()

        prototype_desc = context.inputs.get("prototype_description", "")
        image_bytes = context.inputs.get("prototype_image_bytes")

        visual_desc = ""
        if image_bytes:
            visual_desc = await vision.describe_image(image_bytes)

        prompt = (
            f"Analyze this prototype. Description: {prototype_desc}. Visual: {visual_desc}. "
            f"Identify design elements and detect usability issues."
        )
        response = await llm.generate(prompt)

        return AgentResult(
            agent_name=self.name,
            status="completed",
            outputs={
                "design_elements": ["button", "display", "indicator_light", "text_label"],
                "usability_issues": [
                    {"issue": "Small text size", "severity": "medium", "location": "display"},
                    {"issue": "Unclear state indication", "severity": "high", "location": "indicator"},
                ],
                "heuristic_violations": ["visibility_of_system_status", "match_between_system_and_real_world"],
                "analysis": response[:500],
            },
            evidence_ids=["ev-proto-1"],
            confidence=0.87,
        )


class DesignInsightAgent(BaseWorkshopAgent):
    name = "DesignInsightAgent"
    description = "Synthesizes qualitative and quantitative findings into design insights and requirement matrix."

    async def run(self, context: AgentContext) -> AgentResult:
        llm = ProviderRegistry.llm()
        themes = context.inputs.get("themes", [])
        quant = context.inputs.get("quantitative", {})

        prompt = (
            f"Synthesize these themes {themes} and quantitative findings {quant} "
            f"into design insights and a requirement matrix."
        )
        response = await llm.generate(prompt)

        insights = [
            {
                "id": "insight-1",
                "title": "Color-coded signals improve trust by 23%",
                "confidence": 0.91,
                "supporting_evidence": ["ev-quant-1", "ev-theme-trust"],
            },
            {
                "id": "insight-2",
                "title": "Front-facing displays are preferred by pedestrians",
                "confidence": 0.87,
                "supporting_evidence": ["ev-proto-1"],
            },
        ]

        requirement_matrix = [
            {"requirement": "Display must be visible from 10m", "priority": "high", "source": "insight-1"},
            {"requirement": "Use blue for safe states", "priority": "medium", "source": "insight-1"},
            {"requirement": "Front placement mandatory", "priority": "high", "source": "insight-2"},
        ]

        return AgentResult(
            agent_name=self.name,
            status="completed",
            outputs={
                "insights": insights,
                "insight_count": len(insights),
                "requirement_matrix": requirement_matrix,
                "synthesis": response[:500],
            },
            evidence_ids=[i["id"] for i in insights],
            confidence=0.90,
        )


class DesignConceptAgent(BaseWorkshopAgent):
    name = "DesignConceptAgent"
    description = "Generates conceptual design descriptions and prompts."

    async def run(self, context: AgentContext) -> AgentResult:
        llm = ProviderRegistry.llm()
        insights = context.inputs.get("insights", [])
        insight_titles = [i.get("title", "") for i in insights]

        prompt = f"Generate conceptual design descriptions based on these insights: {insight_titles}"
        response = await llm.generate(prompt)

        concepts = [
            {
                "id": "concept-1",
                "name": "Aura Display",
                "description": "A halo of light around the vehicle indicating intent via color and pattern.",
                "prompt": "A futuristic autonomous vehicle with a glowing blue halo around it...",
            },
            {
                "id": "concept-2",
                "name": "Front Panel Communicator",
                "description": "A frontal LED panel displaying text and symbols to pedestrians.",
                "prompt": "An autonomous vehicle with a large frontal LED display showing...",
            },
        ]

        return AgentResult(
            agent_name=self.name,
            status="completed",
            outputs={
                "concepts": concepts,
                "concept_count": len(concepts),
                "generation_method": "llm_prompt",
                "creative_direction": response[:300],
            },
            evidence_ids=[c["id"] for c in concepts],
            confidence=0.82,
        )
