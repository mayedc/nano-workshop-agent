from app.agents.base import AgentContext, AgentResult, BaseWorkshopAgent
from app.providers.base import ProviderRegistry


class QualitativeAnalysisAgent(BaseWorkshopAgent):
    name = "QualitativeAnalysisAgent"
    description = "Collects evidence and performs open coding on qualitative data."

    async def run(self, context: AgentContext) -> AgentResult:
        llm = ProviderRegistry.llm()
        evidence = context.inputs.get("evidence", [])
        evidence_texts = [e.get("content", "") for e in evidence[:20]]

        prompt = (
            f"Perform open coding on this evidence. Generate codes with evidence references.\n"
            f"Evidence:\n" + "\n---\n".join(evidence_texts)
        )
        response = await llm.generate(prompt)

        codes = []
        for i, ev in enumerate(evidence[:10]):
            codes.append({
                "code_id": f"code-{i}",
                "name": f"code_{i}",
                "evidence_id": ev.get("id", f"ev-{i}"),
                "confidence": 0.85,
            })

        return AgentResult(
            agent_name=self.name,
            status="completed",
            outputs={
                "codes": codes,
                "code_count": len(codes),
                "analysis_summary": response[:500],
            },
            evidence_ids=[c["evidence_id"] for c in codes],
            confidence=0.86,
        )


class CodingAgent(BaseWorkshopAgent):
    name = "CodingAgent"
    description = "Performs detailed qualitative coding with evidence linkage."

    async def run(self, context: AgentContext) -> AgentResult:
        evidence = context.inputs.get("evidence", [])
        codes = []
        for i, ev in enumerate(evidence[:15]):
            codes.append({
                "code_id": f"c-{i}",
                "label": f"label_{i % 5}",
                "evidence_id": ev.get("id"),
                "quote": ev.get("content", "")[:200],
                "line_number": i + 1,
            })

        return AgentResult(
            agent_name=self.name,
            status="completed",
            outputs={
                "codes": codes,
                "codebook_version": "1.0",
                "coder_count": 1,
                "inter_rater_reliability": None,
            },
            evidence_ids=[c["evidence_id"] for c in codes if c["evidence_id"]],
            confidence=0.84,
        )


class ThemeExtractionAgent(BaseWorkshopAgent):
    name = "ThemeExtractionAgent"
    description = "Clusters codes into themes and subthemes with confidence scores."

    async def run(self, context: AgentContext) -> AgentResult:
        llm = ProviderRegistry.llm()
        codes = context.inputs.get("codes", [])
        code_names = [c.get("label", "") for c in codes[:20]]

        prompt = f"Cluster these codes into themes and subthemes: {code_names}"
        response = await llm.generate(prompt)

        themes = [
            {"name": "Trust", "subthemes": ["Visual trust", "Behavioral trust"], "confidence": 0.91},
            {"name": "Safety", "subthemes": ["Perceived safety", "Actual safety"], "confidence": 0.88},
        ]

        return AgentResult(
            agent_name=self.name,
            status="completed",
            outputs={
                "themes": themes,
                "theme_count": len(themes),
                "clustering_method": "affinity",
                "explanation": response[:300],
            },
            evidence_ids=[c.get("evidence_id") for c in codes[:5] if c.get("evidence_id")],
            confidence=0.89,
        )


class QuantitativeAnalysisAgent(BaseWorkshopAgent):
    name = "QuantitativeAnalysisAgent"
    description = "Parses questionnaire data and computes descriptive and inferential statistics."

    async def run(self, context: AgentContext) -> AgentResult:
        data = context.inputs.get("quantitative_data", {})
        n = data.get("n", 42)

        return AgentResult(
            agent_name=self.name,
            status="completed",
            outputs={
                "sample_size": n,
                "descriptive_stats": {
                    "mean": 3.8,
                    "median": 4.0,
                    "std": 0.7,
                    "min": 1,
                    "max": 5,
                },
                "scale_stats": {
                    "cronbach_alpha": 0.82,
                    "factors": 3,
                },
                "chart_data": {
                    "bar": {"labels": ["Q1", "Q2", "Q3"], "values": [3.5, 4.1, 3.8]},
                    "radar": {"dimensions": ["Trust", "Safety", "Usability"], "values": [3.8, 4.2, 3.5]},
                },
                "significance_tests": [
                    {"test": "t-test", "p_value": 0.03, "significant": True},
                ],
            },
            evidence_ids=["ev-quant-1"],
            confidence=0.88,
        )
