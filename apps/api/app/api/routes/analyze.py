import io
import json
import sys
from typing import Any

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import AgentContext
from app.agents.data_analysis_agents import (
    CodeAgent,
    DataProfileAgent,
    PlannerAgent,
    RepairAgent,
    ResultExplainerAgent,
)
from app.db.session import get_db
from app.services import asset as asset_service
from app.services import project as project_service
from app.services.storage import get_storage

router = APIRouter()


class AnalyzeRequest(BaseModel):
    asset_id: str
    user_question: str = Field(..., description="User's analysis question")


class ExecutionOutput(BaseModel):
    result: Any | None = None
    result_type: str = "unknown"
    stdout: str = ""
    error: str | None = None


class AnalyzeResponse(BaseModel):
    project_id: str
    steps: list[dict[str, Any]]
    final_answer: str
    code: str | None = None
    execution: ExecutionOutput | None = None


def _execute_pandas_code(code: str, df: pd.DataFrame) -> ExecutionOutput:
    """Execute pandas code safely and capture result, stdout, and errors."""
    restricted_globals: dict[str, Any] = {
        "__builtins__": {
            "len": len,
            "range": range,
            "print": print,
            "str": str,
            "int": int,
            "float": float,
            "list": list,
            "dict": dict,
            "tuple": tuple,
            "set": set,
            "zip": zip,
            "enumerate": enumerate,
            "sorted": sorted,
            "isinstance": isinstance,
            "hasattr": hasattr,
            "getattr": getattr,
            "sum": sum,
            "min": min,
            "max": max,
            "abs": abs,
            "round": round,
            "map": map,
            "filter": filter,
            "__import__": __import__,
        },
        "pd": pd,
        "np": __import__("numpy"),
    }
    local_vars: dict[str, Any] = {"df": df.copy(), "result": None}

    stdout_capture = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = stdout_capture

    try:
        exec(compile(code, "<string>", "exec"), restricted_globals, local_vars)
    except Exception as exc:
        sys.stdout = old_stdout
        return ExecutionOutput(
            result=None,
            result_type="error",
            stdout=stdout_capture.getvalue(),
            error=f"{type(exc).__name__}: {exc}",
        )

    sys.stdout = old_stdout
    stdout_text = stdout_capture.getvalue()

    result = local_vars.get("result")
    if result is None:
        for k, v in local_vars.items():
            if k != "df" and not k.startswith("_"):
                if isinstance(v, (pd.DataFrame, pd.Series, dict, list, str, int, float)):
                    result = v
                    break

    result_type = "unknown"
    if isinstance(result, pd.DataFrame):
        result_type = "dataframe"
    elif isinstance(result, pd.Series):
        result_type = "series"
    elif isinstance(result, dict):
        result_type = "dict"
    elif isinstance(result, list):
        result_type = "list"
    elif isinstance(result, str):
        result_type = "string"
    elif isinstance(result, (int, float)):
        result_type = "number"

    return ExecutionOutput(
        result=_serialize_result(result),
        result_type=result_type,
        stdout=stdout_text,
        error=None,
    )


@router.post("/projects/{project_id}/analyze", response_model=AnalyzeResponse)
async def analyze_project_data(
    project_id: str,
    req: AnalyzeRequest,
    db: AsyncSession = Depends(get_db),
) -> AnalyzeResponse:
    # 1. Load project and config
    project = await project_service.get(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    config = project.config or {}

    # 2. Load asset
    asset = await asset_service.get(db, req.asset_id)
    if not asset or asset.project_id != project_id:
        raise HTTPException(status_code=404, detail="Asset not found in project")

    storage = get_storage()
    file_bytes = storage.get_object(asset.storage_key)

    # 3. Read into DataFrame
    try:
        if asset.filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(file_bytes))
        else:
            df = pd.read_excel(io.BytesIO(file_bytes))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {exc}")

    # Compute rich dataset previews for LLM context
    try:
        describe_preview = df.describe(include="all").transpose().to_string()
    except Exception:
        describe_preview = df.describe().to_string()
    null_counts = df.isnull().sum().to_dict()
    sample_json = df.head(20).to_json(orient="records", force_ascii=False)

    base_inputs: dict[str, Any] = {
        "asset_id": req.asset_id,
        "columns": list(df.columns),
        "shape": list(df.shape),
        "dtypes": {str(c): str(t) for c, t in df.dtypes.items()},
        "head_preview": df.head(10).to_string(index=False),
        "describe_preview": describe_preview,
        "null_counts": {str(k): int(v) for k, v in null_counts.items()},
        "sample_json": sample_json,
        "user_question": req.user_question,
    }

    context = AgentContext(
        project_id=project_id,
        goal=req.user_question,
        inputs=base_inputs.copy(),
        project_config=config,
    )

    steps: list[dict[str, Any]] = []

    # 4. DataProfileAgent
    profile_agent = DataProfileAgent()
    profile_result = await profile_agent.run(context)
    steps.append(
        {
            "agent": profile_agent.name,
            "status": profile_result.status,
            "output": profile_result.outputs,
        }
    )

    # 5. PlannerAgent
    context.inputs["data_profile"] = profile_result.outputs
    planner_agent = PlannerAgent()
    plan_result = await planner_agent.run(context)
    steps.append(
        {
            "agent": planner_agent.name,
            "status": plan_result.status,
            "output": plan_result.outputs,
        }
    )

    # 6. CodeAgent
    context.inputs["analysis_plan"] = plan_result.outputs
    code_agent = CodeAgent()
    code_result = await code_agent.run(context)
    steps.append(
        {
            "agent": code_agent.name,
            "status": code_result.status,
            "output": code_result.outputs,
        }
    )

    code = code_result.outputs.get("code", "")

    # 7. Execute code with repair loop
    execution = _execute_pandas_code(code, df)
    steps.append(
        {
            "agent": "Executor",
            "status": "failed" if execution.error else "completed",
            "output": execution.result,
            "error": execution.error,
            "stdout": execution.stdout,
            "result_type": execution.result_type,
        }
    )

    max_repairs = 2
    repair_count = 0
    while execution.error and repair_count < max_repairs:
        context.inputs["code"] = code
        context.inputs["error"] = execution.error
        repair_agent = RepairAgent()
        repair_result = await repair_agent.run(context)
        steps.append(
            {
                "agent": repair_agent.name,
                "status": repair_result.status,
                "output": repair_result.outputs,
            }
        )
        code = repair_result.outputs.get("code", code)
        execution = _execute_pandas_code(code, df)
        steps.append(
            {
                "agent": "Executor",
                "status": "failed" if execution.error else "completed",
                "output": execution.result,
                "error": execution.error,
                "stdout": execution.stdout,
                "result_type": execution.result_type,
            }
        )
        repair_count += 1

    # 8. ResultExplainerAgent
    context.inputs["execution_result"] = (
        execution.result if execution.result else {"error": execution.error}
    )
    explainer_agent = ResultExplainerAgent()
    explain_result = await explainer_agent.run(context)
    steps.append(
        {
            "agent": explainer_agent.name,
            "status": explain_result.status,
            "output": explain_result.outputs,
        }
    )

    final_answer = (
        explain_result.outputs.get("summary", "")
        if isinstance(explain_result.outputs, dict)
        else str(explain_result.outputs)
    )

    return AnalyzeResponse(
        project_id=project_id,
        steps=steps,
        final_answer=final_answer,
        code=code,
        execution=execution.model_dump(),
    )


def _serialize_result(result: Any) -> Any:
    """Serialize execution result for JSON response."""
    if isinstance(result, pd.DataFrame):
        return result.head(100).to_dict(orient="records")
    if isinstance(result, pd.Series):
        return result.head(100).to_dict()
    try:
        json.dumps(result)
        return result
    except Exception:
        return str(result)
