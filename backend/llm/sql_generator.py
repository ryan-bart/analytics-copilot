"""Natural language to SQL generation using Claude."""

import json
import logging
from dataclasses import dataclass, field

from backend.database.engine import execute_readonly
from backend.database.inspector import get_schema_ddl
from backend.llm.client import MODEL, get_client
from backend.llm.guardrails import sanitize_sql, validate_sql
from backend.llm.prompts import CHART_TYPE_OPTIONS, SQL_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


@dataclass
class SqlGenerationResult:
    sql: str
    explanation: str
    suggested_chart_type: str
    error: str | None = None


@dataclass
class QueryResult:
    columns: list[str] = field(default_factory=list)
    rows: list[dict] = field(default_factory=list)
    row_count: int = 0
    error: str | None = None


def generate_sql(question: str) -> SqlGenerationResult:
    """Generate SQL from a natural language question using Claude."""
    schema_ddl = get_schema_ddl()
    system_prompt = SQL_SYSTEM_PROMPT.format(
        schema_ddl=schema_ddl,
        chart_types=", ".join(CHART_TYPE_OPTIONS),
    )

    client = get_client()
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": question}],
    )

    raw_text = response.content[0].text.strip()

    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError:
        logger.error("Failed to parse LLM response as JSON: %s", raw_text[:200])
        return SqlGenerationResult(
            sql="", explanation="", suggested_chart_type="table",
            error="Failed to parse AI response",
        )

    sql = parsed.get("sql", "")
    is_valid, error_msg = validate_sql(sql)
    if not is_valid:
        return SqlGenerationResult(
            sql=sql, explanation=parsed.get("explanation", ""),
            suggested_chart_type="table", error=f"SQL validation failed: {error_msg}",
        )

    return SqlGenerationResult(
        sql=sanitize_sql(sql),
        explanation=parsed.get("explanation", ""),
        suggested_chart_type=parsed.get("suggested_chart_type", "table"),
    )


def execute_sql(sql: str) -> QueryResult:
    """Execute a validated SQL query and return results."""
    is_valid, error_msg = validate_sql(sql)
    if not is_valid:
        return QueryResult(error=f"SQL validation failed: {error_msg}")

    try:
        rows = execute_readonly(sql)
        columns = list(rows[0].keys()) if rows else []
        return QueryResult(columns=columns, rows=rows, row_count=len(rows))
    except Exception as e:
        logger.error("SQL execution error: %s", e)
        return QueryResult(error=f"Query execution failed: {e}")
