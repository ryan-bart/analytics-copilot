"""Tests for heuristic chart type detection."""

from backend.visualization.chart_picker import pick_chart_type


def test_single_value_is_number():
    result = pick_chart_type(["count"], [{"count": 42}], "table")
    assert result == "number"


def test_categorical_numeric_few_rows_is_pie():
    rows = [
        {"status": "Active", "count": 100},
        {"status": "Cancelled", "count": 30},
        {"status": "Expired", "count": 50},
    ]
    result = pick_chart_type(["status", "count"], rows, "bar")
    assert result == "pie"


def test_categorical_numeric_many_rows_is_bar():
    rows = [{"region": f"Region {i}", "total": i * 100} for i in range(10)]
    result = pick_chart_type(["region", "total"], rows, "table")
    assert result == "bar"


def test_date_numeric_is_line():
    rows = [
        {"month": "2024-01", "claims": 45},
        {"month": "2024-02", "claims": 52},
        {"month": "2024-03", "claims": 48},
    ]
    result = pick_chart_type(["month", "claims"], rows, "bar")
    assert result == "line"


def test_empty_rows_is_table():
    result = pick_chart_type([], [], "bar")
    assert result == "table"


def test_fallback_to_suggested():
    rows = [{"a": "x", "b": "y", "c": "z"}]
    result = pick_chart_type(["a", "b", "c"], rows, "bar")
    assert result == "bar"
