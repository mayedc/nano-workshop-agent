import io
import json

from app.agents.base import AgentContext, AgentResult, BaseWorkshopAgent
from app.agents.registry import agent_registry
from app.providers.factory import create_llm_provider
from app.templates.loader import TemplateRegistry


def _extract_json(text: str) -> str:
    """Strip markdown fences and extraneous text to extract JSON payload."""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    lines = text.splitlines()
    if lines and lines[0].strip().lower() in ("json", "python", ""):
        lines = lines[1:]
    text = "\n".join(lines).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        text = text[start : end + 1]
    return text


def _extract_preview(file_bytes: bytes, mime_type: str) -> str:
    """Extract a human-readable preview from file bytes based on MIME type."""
    try:
        if mime_type in ("text/csv", "application/vnd.ms-excel", "text/comma-separated-values"):
            text = file_bytes.decode("utf-8", errors="replace")
            lines = text.splitlines()[:20]
            return "\n".join(lines)
        elif mime_type in ("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",):
            try:
                import openpyxl

                wb = openpyxl.load_workbook(io.BytesIO(file_bytes), read_only=True)
                ws = wb.active
                rows = []
                for i, row in enumerate(ws.iter_rows(max_row=20, values_only=True)):
                    rows.append("\t".join(str(c) if c is not None else "" for c in row))
                    if i >= 19:
                        break
                wb.close()
                return "\n".join(rows)
            except Exception:
                return "(binary Excel file, preview unavailable)"
        elif mime_type.startswith("text/") or mime_type in (
            "application/json",
            "application/xml",
            "text/markdown",
        ):
            text = file_bytes.decode("utf-8", errors="replace")
            return text[:1000]
        else:
            return f"(binary file, {mime_type})"
    except Exception as exc:
        return f"(preview unavailable: {exc})"


class WorkshopPlannerAgent(BaseWorkshopAgent):
    name = "WorkshopPlannerAgent"
    description = "Analyzes uploaded assets and workshop purpose to suggest an optimal workflow of workshop agents."

    async def run(self, context: AgentContext) -> AgentResult:
        llm = create_llm_provider(context.project_config)

        assets = context.inputs.get("assets", [])
        available_agents = sorted(agent_registry.list_agents())
        templates = TemplateRegistry.all()
        workshop_purpose = context.goal or ""

        asset_sections = []
        for a in assets:
            section = f"- {a.get('filename', '?')} | type={a.get('asset_type', '?')} | mime={a.get('mime_type', '?')} | role={a.get('semantic_role', '')}"
            preview = a.get("content_preview", "")
            if preview:
                section += f"\n  Content preview: {preview[:500]}"
            asset_sections.append(section)

        template_sections = []
        for t in templates:
            steps_summary = [
                {"id": s.id, "name": s.name, "agent_name": s.agent_name, "depends_on": s.depends_on}
                for s in t.workflow_steps
            ]
            template_sections.append(
                f"Template '{t.id}' ({t.name}):\n"
                f"  description: {t.description}\n"
                f"  modules: {t.analysis_modules}\n"
                f"  workflow: {json.dumps(steps_summary, ensure_ascii=False)}"
            )

        prompt = f"""You are a senior academic workshop planner. Based on the uploaded materials and the workshop purpose, suggest the optimal workflow of analysis agents to run.

=== WORKSHOP PURPOSE ===
{workshop_purpose}

=== UPLOADED ASSETS ===
{chr(10).join(asset_sections) if asset_sections else "(none)"}

=== AVAILABLE AGENTS ===
{json.dumps(available_agents, ensure_ascii=False)}

=== REFERENCE TEMPLATES ===
{chr(10).join(template_sections) if template_sections else "(none)"}

=== YOUR TASK ===
Produce a structured JSON response with:
- "workshop_title": a concise title for this workshop (in Chinese or English as appropriate)
- "reasoning": 3-4 sentences explaining why this workflow fits the purpose and assets
- "suggested_modules": list of analysis module names (e.g. "thematic_analysis", "quantitative_analysis", "design_insight")
- "workflow_steps": ordered list of step objects with:
  - "id": integer (starting from 1)
  - "name": short human-readable label
  - "agent_name": MUST be one of the available agents listed above
  - "description": 1-2 sentences explaining what this step does
  - "depends_on": list of integer step IDs this step depends on
  - "expected_output": what this step produces
- "estimated_duration": rough time estimate string
- "confidence": "high" | "medium" | "low"
- "assumptions": list of assumptions made about the data or workshop

Return ONLY valid JSON. Do NOT include markdown fences, explanations, or any text outside the JSON object."""

        try:
            raw = await llm.generate(
                prompt,
                system="You are a workshop planning expert. You output ONLY valid JSON with snake_case keys.",
            )
            output = json.loads(_extract_json(raw))
        except Exception as exc:
            output = {
                "error": str(exc),
                "workshop_title": "Planning Failed",
                "reasoning": "The agent was unable to generate a plan.",
                "suggested_modules": [],
                "workflow_steps": [],
                "confidence": "low",
                "assumptions": [],
            }

        return AgentResult(
            agent_name=self.name,
            status="completed" if "error" not in output else "failed",
            outputs=output,
            confidence={"high": 0.9, "medium": 0.6, "low": 0.3}.get(
                output.get("confidence", "low"), 0.5
            ),
        )
