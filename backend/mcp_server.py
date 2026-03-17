"""MCP server exposing analytics copilot tools for Claude Desktop."""

from mcp.server.fastmcp import FastMCP

from backend.database.inspector import get_schema_ddl
from backend.database.seed import seed_database
from backend.llm.dax_generator import suggest_dax
from backend.llm.sql_generator import execute_sql, generate_sql

mcp = FastMCP("analytics-copilot")

# Ensure database is seeded on startup
seed_database()


@mcp.tool()
def query_data(question: str) -> dict:
    """Ask a natural language question about the insurance database.

    Generates SQL from the question, executes it, and returns the results.

    Args:
        question: A plain English analytics question (e.g. "How many active policies are there?")

    Returns:
        Dict with sql, explanation, columns, rows, and row_count.
    """
    gen_result = generate_sql(question)
    if gen_result.error:
        return {"error": gen_result.error}

    query_result = execute_sql(gen_result.sql)
    return {
        "sql": gen_result.sql,
        "explanation": gen_result.explanation,
        "columns": query_result.columns,
        "rows": query_result.rows[:50],
        "row_count": query_result.row_count,
        "error": query_result.error,
    }


@mcp.tool()
def get_schema() -> str:
    """Get the database schema as CREATE TABLE DDL statements.

    Returns the full schema definition for the insurance database,
    including all tables, columns, types, and foreign key relationships.
    """
    return get_schema_ddl()


@mcp.tool()
def suggest_dax_measures(question: str, sql: str, columns: list[str]) -> dict:
    """Suggest Power BI DAX measures for a given analytics query.

    Args:
        question: The original analytics question.
        sql: The SQL query that was generated.
        columns: The result column names.

    Returns:
        Dict with a list of DAX measures, each having name, expression, and description.
    """
    result = suggest_dax(question, sql, columns)
    return {
        "measures": [
            {"name": m.name, "expression": m.expression, "description": m.description}
            for m in result.measures
        ],
        "error": result.error,
    }


if __name__ == "__main__":
    mcp.run()
