"""Build Plotly chart JSON from query results."""

import json

import plotly.graph_objects as go


def build_chart(
    chart_type: str,
    columns: list[str],
    rows: list[dict],
) -> dict | None:
    """Build a Plotly chart JSON dict from query results."""
    if not rows or not columns:
        return None

    if chart_type == "number":
        return _build_number_card(columns, rows)

    if chart_type == "bar":
        return _build_bar(columns, rows)

    if chart_type == "line":
        return _build_line(columns, rows)

    if chart_type == "pie":
        return _build_pie(columns, rows)

    return None


def _classify_columns(
    columns: list[str], rows: list[dict]
) -> tuple[list[str], list[str]]:
    """Split columns into label and value columns."""
    label_cols = []
    value_cols = []
    for col in columns:
        sample = [r[col] for r in rows[:5] if r.get(col) is not None]
        if sample and all(isinstance(v, (int, float)) for v in sample):
            value_cols.append(col)
        else:
            label_cols.append(col)
    return label_cols, value_cols


def _build_number_card(columns: list[str], rows: list[dict]) -> dict:
    """Build a big number card."""
    value = rows[0][columns[0]]
    label = columns[0].replace("_", " ").title()
    fig = go.Figure(go.Indicator(
        mode="number",
        value=float(value) if isinstance(value, (int, float)) else 0,
        title={"text": label},
    ))
    fig.update_layout(height=200, margin=dict(t=60, b=20, l=20, r=20))
    return json.loads(fig.to_json())


def _build_bar(columns: list[str], rows: list[dict]) -> dict:
    label_cols, value_cols = _classify_columns(columns, rows)
    if not label_cols or not value_cols:
        return _fallback_bar(columns, rows)

    x_col = label_cols[0]
    x_vals = [str(r[x_col]) for r in rows]
    fig = go.Figure()
    for v_col in value_cols:
        y_vals = [r[v_col] for r in rows]
        fig.add_trace(go.Bar(name=v_col.replace("_", " ").title(), x=x_vals, y=y_vals))

    fig.update_layout(
        xaxis_title=x_col.replace("_", " ").title(),
        barmode="group",
        height=400,
        margin=dict(t=40, b=60, l=60, r=20),
    )
    return json.loads(fig.to_json())


def _fallback_bar(columns: list[str], rows: list[dict]) -> dict:
    x_vals = [str(r[columns[0]]) for r in rows]
    y_vals = [r[columns[1]] if len(columns) > 1 else i for i, r in enumerate(rows)]
    fig = go.Figure(go.Bar(x=x_vals, y=y_vals))
    fig.update_layout(height=400, margin=dict(t=40, b=60, l=60, r=20))
    return json.loads(fig.to_json())


def _build_line(columns: list[str], rows: list[dict]) -> dict:
    label_cols, value_cols = _classify_columns(columns, rows)
    # Use first non-numeric column as x-axis (date)
    x_col = label_cols[0] if label_cols else columns[0]
    x_vals = [str(r[x_col]) for r in rows]

    fig = go.Figure()
    plot_cols = value_cols if value_cols else [c for c in columns if c != x_col]
    for v_col in plot_cols:
        y_vals = [r[v_col] for r in rows]
        fig.add_trace(go.Scatter(
            name=v_col.replace("_", " ").title(), x=x_vals, y=y_vals, mode="lines+markers"
        ))

    fig.update_layout(
        xaxis_title=x_col.replace("_", " ").title(),
        height=400,
        margin=dict(t=40, b=60, l=60, r=20),
    )
    return json.loads(fig.to_json())


def _build_pie(columns: list[str], rows: list[dict]) -> dict:
    label_cols, value_cols = _classify_columns(columns, rows)
    label_col = label_cols[0] if label_cols else columns[0]
    value_col = value_cols[0] if value_cols else columns[-1]

    labels = [str(r[label_col]) for r in rows]
    values = [r[value_col] for r in rows]

    fig = go.Figure(go.Pie(labels=labels, values=values, hole=0.3))
    fig.update_layout(height=400, margin=dict(t=40, b=40, l=20, r=20))
    return json.loads(fig.to_json())
