"""Tests for SQL validation guardrails."""

import pytest

from backend.llm.guardrails import sanitize_sql, validate_sql


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT COUNT(*) FROM policies",
        "SELECT p.product_line, SUM(p.premium) FROM policies p GROUP BY p.product_line",
        "WITH cte AS (SELECT * FROM customers) SELECT * FROM cte",
        "SELECT * FROM policies WHERE status = 'Active'",
    ],
)
def test_valid_selects_pass(sql):
    is_valid, error = validate_sql(sql)
    assert is_valid, f"Expected valid but got: {error}"


@pytest.mark.parametrize(
    "sql",
    [
        "DROP TABLE policies",
        "DELETE FROM customers WHERE id = 1",
        "INSERT INTO customers (first_name) VALUES ('test')",
        "UPDATE policies SET status = 'Cancelled'",
        "ALTER TABLE policies ADD COLUMN foo TEXT",
        "TRUNCATE TABLE claims",
    ],
)
def test_write_operations_blocked(sql):
    is_valid, error = validate_sql(sql)
    assert not is_valid
    assert error  # has an error message


def test_multi_statement_blocked():
    is_valid, error = validate_sql("SELECT 1; DROP TABLE policies")
    assert not is_valid
    assert "Multiple statements" in error


def test_non_select_blocked():
    is_valid, error = validate_sql("PRAGMA table_info(policies)")
    assert not is_valid


def test_empty_sql_blocked():
    is_valid, error = validate_sql("")
    assert not is_valid
    assert "Empty" in error


def test_sanitize_sql_normalizes():
    result = sanitize_sql("  SELECT  *  FROM   policies ;  ")
    assert result == "SELECT * FROM policies"


def test_select_with_blocked_keyword_in_subquery():
    """SELECT that contains a blocked keyword in a subquery-like context."""
    is_valid, error = validate_sql(
        "SELECT * FROM policies; DROP TABLE policies"
    )
    assert not is_valid
