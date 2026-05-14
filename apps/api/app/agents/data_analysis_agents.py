import json
from typing import Any

from app.agents.base import AgentContext, AgentResult, BaseWorkshopAgent
from app.providers.factory import create_llm_provider


def _truncate(text: str, max_len: int = 6000) -> str:
    if len(text) <= max_len:
        return text
    return text[:max_len] + f"\n... ({len(text) - max_len} more chars truncated)"


def _extract_json(text: str) -> str:
    """Strip markdown fences and extraneous text to extract JSON payload."""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    # Some models wrap JSON in a single code block with language tag on same line
    lines = text.splitlines()
    # Remove leading language tag line if present
    if lines and lines[0].strip().lower() in ("json", "python", ""):
        lines = lines[1:]
    text = "\n".join(lines).strip()
    # Find first '{' and last '}' to isolate JSON object
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        text = text[start : end + 1]
    return text


class DataProfileAgent(BaseWorkshopAgent):
    name = "DataProfileAgent"
    description = "Analyzes a dataset and generates a structured profile."

    async def run(self, context: AgentContext) -> AgentResult:
        llm = create_llm_provider(context.project_config)
        columns = context.inputs.get("columns", [])
        shape = context.inputs.get("shape", [0, 0])
        head = context.inputs.get("head_preview", "")
        dtypes = context.inputs.get("dtypes", {})
        describe = context.inputs.get("describe_preview", "")
        null_counts = context.inputs.get("null_counts", {})
        sample_json = context.inputs.get("sample_json", "")

        prompt = f"""You are a senior data profiling assistant. Analyze the following dataset thoroughly.

=== DATASET OVERVIEW ===
Shape: {shape[0]} rows × {shape[1]} columns
Columns: {json.dumps(columns, ensure_ascii=False)}

=== COLUMN TYPES ===
{json.dumps(dtypes, ensure_ascii=False, indent=2)}

=== MISSING VALUES ===
{json.dumps(null_counts, ensure_ascii=False, indent=2)}

=== STATISTICAL SUMMARY (describe) ===
{describe}

=== FIRST 10 ROWS (raw) ===
{head}

=== SAMPLE DATA (JSON) ===
{sample_json}

=== YOUR TASK ===
Provide a structured JSON response with these keys:
- "overview": one-sentence summary of what this dataset contains
- "columns": list of column objects with:
  - "name": column name
  - "dtype": original dtype
  - "semantic_type": categorical | numerical | datetime | text | identifier | mixed
  - "description": inferred meaning of this column (1 sentence)
  - "null_rate": percentage of missing values
  - "unique_count": estimated unique values
- "relationships": list of likely relationships between columns (e.g. "Category determines Need")
- "quality_issues": list of data quality concerns with severity (high/medium/low)
- "suggested_analyses": list of specific analyses suitable for this dataset, ranked by relevance

Return ONLY valid JSON."""

        try:
            raw = await llm.generate(prompt, system="You are a data profiling expert. Output ONLY valid JSON.")
            output = json.loads(_extract_json(raw))
        except Exception as exc:
            output = {"error": str(exc), "raw": raw if "raw" in locals() else None}

        return AgentResult(
            agent_name=self.name,
            status="completed" if "error" not in output else "failed",
            outputs=output,
        )


class PlannerAgent(BaseWorkshopAgent):
    name = "PlannerAgent"
    description = "Generates a detailed analysis plan based on the user's question and data profile."

    async def run(self, context: AgentContext) -> AgentResult:
        llm = create_llm_provider(context.project_config)
        question = context.goal or context.inputs.get("user_question", "")
        profile = context.inputs.get("data_profile", {})

        prompt = f"""You are an expert analytics planner. Given the user's question and the detailed dataset profile, create a rigorous step-by-step analysis plan.

=== USER QUESTION ===
{question}

=== DATA PROFILE ===
{json.dumps(profile, ensure_ascii=False, indent=2)}

=== YOUR TASK ===
Provide a structured JSON response with:
- "objective": restated analysis objective (1 sentence)
- "reasoning": why this plan is appropriate (2-3 sentences)
- "steps": list of step objects with:
  - "step_number": integer
  - "title": short title
  - "description": what this step does
  - "technique": specific pandas/NumPy technique (e.g., value_counts, groupby().agg(), crosstab, pivot_table)
  - "input_columns": list of column names needed
  - "expected_output": what the result looks like
- "assumptions": list of assumptions made about the data
- "fallback_plan": what to do if the primary plan fails or data is insufficient

Return ONLY valid JSON."""

        try:
            raw = await llm.generate(prompt, system="You are an analytics planner. Output ONLY valid JSON.")
            output = json.loads(_extract_json(raw))
        except Exception as exc:
            output = {"error": str(exc), "raw": raw if "raw" in locals() else None}

        return AgentResult(
            agent_name=self.name,
            status="completed" if "error" not in output else "failed",
            outputs=output,
        )


class CodeAgent(BaseWorkshopAgent):
    name = "CodeAgent"
    description = "Generates pandas Python code to execute the analysis plan using actual column names."

    async def run(self, context: AgentContext) -> AgentResult:
        llm = create_llm_provider(context.project_config)
        plan = context.inputs.get("analysis_plan", {})
        profile = context.inputs.get("data_profile", {})
        columns = context.inputs.get("columns", [])
        dtypes = context.inputs.get("dtypes", {})
        head = context.inputs.get("head_preview", "")

        prompt = f"""You are a senior Python data analyst. Generate clean, runnable pandas code to execute the following analysis plan using the ACTUAL column names from the dataset.

=== AVAILABLE COLUMNS ===
{json.dumps(columns, ensure_ascii=False)}

=== COLUMN DTYPES ===
{json.dumps(dtypes, ensure_ascii=False, indent=2)}

=== DATA SAMPLE (first 10 rows) ===
{head}

=== ANALYSIS PLAN ===
{json.dumps(plan, ensure_ascii=False, indent=2)}

=== CODING REQUIREMENTS ===
1. The DataFrame is already loaded as a variable named `df`. Do NOT read from any file.
2. You MUST use the exact column names shown above. Do NOT guess column names.
3. Handle missing values appropriately (dropna() or fillna()) if needed.
4. If grouping, ensure group keys are handled correctly (e.g., forward-fill merged header rows before analysis).
5. Include matplotlib plotting code if visualization is helpful (save to a variable or print summary).
6. Assign the FINAL consolidated result to a variable named `result`. `result` can be a dict of DataFrames/Series, a single DataFrame, or a summary string.
7. Use only pandas, numpy, and matplotlib.
8. Include inline comments for each major step.
9. Return ONLY the Python code block. No markdown fences, no explanations outside the code.

Python code:"""

        try:
            code = await llm.generate(prompt, system="You write only Python pandas code. Use exact column names from the dataset.")
            code = code.strip()
            if code.startswith("```"):
                lines = code.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                code = "\n".join(lines).strip()
            output = {"code": code, "language": "python"}
        except Exception as exc:
            output = {"error": str(exc)}

        return AgentResult(
            agent_name=self.name,
            status="completed" if "error" not in output else "failed",
            outputs=output,
        )


class RepairAgent(BaseWorkshopAgent):
    name = "RepairAgent"
    description = "Fixes Python code errors based on the traceback and data context."

    async def run(self, context: AgentContext) -> AgentResult:
        llm = create_llm_provider(context.project_config)
        code = context.inputs.get("code", "")
        error = context.inputs.get("error", "")
        columns = context.inputs.get("columns", [])
        head = context.inputs.get("head_preview", "")

        prompt = f"""You are a Python debugging assistant. Fix the following pandas code based on the error traceback and dataset context.

=== AVAILABLE COLUMNS ===
{json.dumps(columns, ensure_ascii=False)}

=== DATA SAMPLE ===
{head}

=== ORIGINAL CODE ===
{code}

=== ERROR TRACEBACK ===
{error}

=== REPAIR INSTRUCTIONS ===
1. The DataFrame is available as `df`. Do NOT read from files.
2. Use ONLY the exact column names listed above.
3. Assign the final result to `result`.
4. Return ONLY the corrected Python code block, no markdown fences, no extra explanations.

Corrected Python code:"""

        try:
            fixed = await llm.generate(prompt, system="You write only Python code.")
            fixed = fixed.strip()
            if fixed.startswith("```"):
                lines = fixed.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                fixed = "\n".join(lines).strip()
            output = {"code": fixed, "language": "python"}
        except Exception as exc:
            output = {"error": str(exc)}

        return AgentResult(
            agent_name=self.name,
            status="completed" if "error" not in output else "failed",
            outputs=output,
        )


class ResultExplainerAgent(BaseWorkshopAgent):
    name = "ResultExplainerAgent"
    description = "Explains analysis results in natural language with structured findings."

    async def run(self, context: AgentContext) -> AgentResult:
        llm = create_llm_provider(context.project_config)
        question = context.goal or context.inputs.get("user_question", "")
        result = context.inputs.get("execution_result", "")
        plan = context.inputs.get("analysis_plan", {})
        profile = context.inputs.get("data_profile", {})

        prompt = f"""You are a senior data analyst presenting results to a stakeholder. Explain the following analysis result in clear, structured Chinese.

=== USER QUESTION ===
{question}

=== ANALYSIS PLAN ===
{json.dumps(plan, ensure_ascii=False, indent=2)}

=== DATA PROFILE SUMMARY ===
{json.dumps(profile.get("overview", ""), ensure_ascii=False)}

=== EXECUTION RESULT ===
{json.dumps(result, ensure_ascii=False, indent=2) if isinstance(result, dict) else str(result)[:6000]}

=== YOUR TASK ===
Provide a structured JSON response with:
- "summary": 2-3 sentence executive summary in Chinese
- "key_findings": list of 3-5 bullet-point findings with supporting numbers
- "details": paragraph-level detailed explanation of patterns and distributions
- "recommendations": list of 2-3 actionable recommendations
- "confidence": high | medium | low, with brief justification
- "limitations": any caveats about the data or analysis

Return ONLY valid JSON."""

        try:
            raw = await llm.generate(prompt, system="You are a data storytelling expert. Output ONLY valid JSON in Chinese.")
            output = json.loads(_extract_json(raw))
        except Exception as exc:
            output = {"summary": "解释生成失败", "error": str(exc), "raw": raw if "raw" in locals() else None}

        return AgentResult(
            agent_name=self.name,
            status="completed" if "error" not in output else "failed",
            outputs=output,
        )
