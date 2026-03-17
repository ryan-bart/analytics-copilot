from fastapi import APIRouter

from backend.api.schemas import (
    ColumnInfo,
    HistoryItem,
    HistoryListResponse,
    QueryRequest,
    QueryResponse,
    SchemaResponse,
    TableInfo,
)
from backend.database.inspector import get_sample_data, get_schema
from backend.history.store import get_history, get_history_item, save_query
from backend.llm.sql_generator import execute_sql, generate_sql
from backend.visualization.chart_builder import build_chart
from backend.visualization.chart_picker import pick_chart_type

router = APIRouter(prefix="/api")


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/schema", response_model=SchemaResponse)
def schema_overview():
    schema = get_schema()
    tables = []
    for table_name, columns in schema.items():
        tables.append(TableInfo(
            name=table_name,
            columns=[ColumnInfo(**col) for col in columns],
            sample_data=get_sample_data(table_name, limit=3),
        ))
    return SchemaResponse(tables=tables)


@router.get("/schema/{table_name}", response_model=TableInfo)
def schema_table(table_name: str):
    schema = get_schema()
    if table_name not in schema:
        return {"error": f"Table '{table_name}' not found"}
    columns = schema[table_name]
    return TableInfo(
        name=table_name,
        columns=[ColumnInfo(**col) for col in columns],
        sample_data=get_sample_data(table_name, limit=5),
    )


@router.post("/query", response_model=QueryResponse)
def query_data(request: QueryRequest):
    gen_result = generate_sql(request.question)

    if gen_result.error:
        return QueryResponse(
            question=request.question,
            sql=gen_result.sql,
            explanation=gen_result.explanation,
            suggested_chart_type=gen_result.suggested_chart_type,
            columns=[],
            rows=[],
            row_count=0,
            error=gen_result.error,
        )

    query_result = execute_sql(gen_result.sql)

    chart_type = pick_chart_type(
        query_result.columns, query_result.rows, gen_result.suggested_chart_type
    )
    chart_json = build_chart(chart_type, query_result.columns, query_result.rows)

    if not query_result.error:
        save_query(
            question=request.question,
            sql=gen_result.sql,
            explanation=gen_result.explanation,
            chart_type=chart_type,
            row_count=query_result.row_count,
            rows=query_result.rows,
        )

    return QueryResponse(
        question=request.question,
        sql=gen_result.sql,
        explanation=gen_result.explanation,
        suggested_chart_type=chart_type,
        columns=query_result.columns,
        rows=query_result.rows,
        row_count=query_result.row_count,
        chart_json=chart_json,
        error=query_result.error,
    )


@router.get("/history", response_model=HistoryListResponse)
def list_history():
    items = get_history()
    return HistoryListResponse(items=[HistoryItem(**item) for item in items])


@router.get("/history/{item_id}")
def history_detail(item_id: int):
    item = get_history_item(item_id)
    if not item:
        return {"error": "History item not found"}
    return item
