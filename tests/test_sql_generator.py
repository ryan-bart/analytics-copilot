"""Tests for SQL generation (mocked LLM)."""

from backend.llm.sql_generator import execute_sql, generate_sql


def test_generate_sql_returns_valid_result(mock_anthropic):
    result = generate_sql("How many active policies are there?")
    assert result.sql
    assert "SELECT" in result.sql.upper()
    assert result.explanation
    assert result.suggested_chart_type == "number"
    assert result.error is None


def test_generate_sql_calls_claude(mock_anthropic):
    generate_sql("test question")
    mock_anthropic.messages.create.assert_called_once()
    call_kwargs = mock_anthropic.messages.create.call_args
    assert "test question" in str(call_kwargs)


def test_execute_sql_returns_results():
    result = execute_sql("SELECT COUNT(*) AS cnt FROM policies")
    assert result.error is None
    assert result.row_count == 1
    assert result.columns == ["cnt"]
    assert result.rows[0]["cnt"] > 0


def test_execute_sql_blocks_writes():
    result = execute_sql("DROP TABLE policies")
    assert result.error is not None
    assert "validation failed" in result.error.lower()
