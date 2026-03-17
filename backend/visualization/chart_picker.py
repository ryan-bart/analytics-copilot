"""Heuristic chart type detection based on query result shape."""


def pick_chart_type(
    columns: list[str],
    rows: list[dict],
    suggested: str,
) -> str:
    """Pick the best chart type based on data shape, falling back to the LLM suggestion."""
    if not rows or not columns:
        return "table"

    # Single scalar value -> number card
    if len(rows) == 1 and len(columns) == 1:
        return "number"

    # Classify columns
    numeric_cols = []
    categorical_cols = []
    date_cols = []

    for col in columns:
        sample_values = [row[col] for row in rows[:10] if row.get(col) is not None]
        if not sample_values:
            continue

        if _looks_like_date(sample_values):
            date_cols.append(col)
        elif _looks_like_numeric(sample_values):
            numeric_cols.append(col)
        else:
            categorical_cols.append(col)

    num_rows = len(rows)

    # Time series: date column + numeric -> line
    if date_cols and numeric_cols:
        return "line"

    # Proportional: 1 categorical + 1 numeric with few categories -> pie
    if len(categorical_cols) == 1 and len(numeric_cols) == 1 and 2 <= num_rows <= 7:
        return "pie"

    # Categorical comparison -> bar
    if categorical_cols and numeric_cols:
        return "bar"

    # Fall back to LLM suggestion
    if suggested in ("bar", "line", "pie", "number", "table"):
        return suggested

    return "table"


def _looks_like_numeric(values: list) -> bool:
    for v in values[:5]:
        if isinstance(v, (int, float)):
            continue
        try:
            float(str(v))
        except (ValueError, TypeError):
            return False
    return True


def _looks_like_date(values: list) -> bool:
    for v in values[:5]:
        s = str(v)
        if len(s) >= 7 and (
            "-" in s[:5] or "/" in s[:5]  # YYYY-MM or MM/DD patterns
        ):
            continue
        return False
    return True
