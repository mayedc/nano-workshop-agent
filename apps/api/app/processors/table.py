from typing import Any

from app.processors.base import BaseProcessor, ProcessingResult
from app.providers.base import ProviderRegistry


class TableProcessor(BaseProcessor):
    supported_types = {
        "text/csv",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel",
    }

    async def process(
        self, file_bytes: bytes, filename: str, mime_type: str, **kwargs: Any
    ) -> ProcessingResult:
        llm = ProviderRegistry.llm()

        # For mock: simulate parsing
        if mime_type == "text/csv":
            text = file_bytes.decode("utf-8", errors="replace")
            rows = text.splitlines()
        else:
            text = "[Binary Excel content - parsed mock]"
            rows = ["col1,col2,col3", "1,2,3", "4,5,6"]

        # Schema inference
        schema_prompt = "Infer schema for this data (first 5 rows):\n" + "\n".join(rows[:5])
        schema = await llm.generate(schema_prompt)

        # Descriptive statistics
        stats_prompt = "Compute descriptive statistics for:\n" + "\n".join(rows[:10])
        stats = await llm.generate(stats_prompt)

        # Scale grouping (detect Likert vs continuous vs categorical)
        scale_prompt = "Classify variable types in this dataset:\n" + "\n".join(rows[:5])
        scale_groups = await llm.generate(scale_prompt)

        tables = [
            {
                "name": filename,
                "schema": schema[:500],
                "row_count": len(rows) - 1,
                "column_count": len(rows[0].split(",")) if rows else 0,
            }
        ]

        evidence = [
            {"type": "table_schema", "content": schema, "metadata": {"source": "llm"}},
            {"type": "statistics", "content": stats, "metadata": {"source": "llm"}},
            {"type": "scale_grouping", "content": scale_groups, "metadata": {"source": "llm"}},
        ]

        return ProcessingResult(
            normalized_text="\n".join(rows),
            extracted_tables=tables,
            metadata={
                "filename": filename,
                "mime_type": mime_type,
                "row_count": len(rows) - 1,
                "column_count": len(rows[0].split(",")) if rows else 0,
                "missing_value_detected": "N/A" in text or "" in rows,
            },
            evidence_candidates=evidence,
        )
