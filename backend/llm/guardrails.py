"""SQL validation and sanitization guardrails."""

import re

BLOCKED_KEYWORDS = [
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "TRUNCATE",
    "EXEC", "EXECUTE", "GRANT", "REVOKE", "COMMIT", "ROLLBACK",
    "ATTACH", "DETACH", "PRAGMA",
]

BLOCKED_PATTERN = re.compile(
    r"\b(" + "|".join(BLOCKED_KEYWORDS) + r")\b",
    re.IGNORECASE,
)


def validate_sql(sql: str) -> tuple[bool, str]:
    """Validate that SQL is a read-only SELECT statement.

    Returns (is_valid, error_message).
    """
    stripped = sql.strip().rstrip(";").strip()

    if not stripped:
        return False, "Empty SQL query"

    # Check for multiple statements (injection via semicolons)
    # Allow semicolons inside string literals by simple heuristic
    without_strings = re.sub(r"'[^']*'", "", stripped)
    if ";" in without_strings:
        return False, "Multiple statements not allowed"

    # Must start with SELECT or WITH (for CTEs)
    if not re.match(r"^\s*(SELECT|WITH)\b", stripped, re.IGNORECASE):
        return False, "Only SELECT queries are allowed"

    # Check for blocked keywords
    match = BLOCKED_PATTERN.search(without_strings)
    if match:
        return False, f"Blocked keyword: {match.group(0).upper()}"

    return True, ""


def sanitize_sql(sql: str) -> str:
    """Normalize whitespace and strip trailing semicolons."""
    sql = sql.strip()
    sql = re.sub(r"\s+", " ", sql)
    sql = sql.rstrip(";")
    return sql
