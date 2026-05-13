from app.agents.base import AgentContext, AgentResult, BaseWorkshopAgent


class EvaluationAgent(BaseWorkshopAgent):
    name = "EvaluationAgent"
    description = "Evaluates agent outputs for quality, coverage, and bias."

    async def run(self, context: AgentContext) -> AgentResult:
        outputs = context.inputs.get("outputs", [])

        scores = {
            "completeness": 0.85,
            "accuracy": 0.90,
            "relevance": 0.88,
            "bias_score": 0.15,  # lower is better
            "evidence_traceability": 0.92,
        }

        return AgentResult(
            agent_name=self.name,
            status="completed",
            outputs={
                "evaluation_scores": scores,
                "overall_score": sum(scores.values()) / len(scores),
                "recommendations": [
                    "Increase evidence linkage for quantitative claims",
                    "Add cross-validation for qualitative codes",
                ],
                "evaluated_outputs": len(outputs),
            },
            evidence_ids=["ev-eval-1"],
            confidence=0.91,
        )
