from pydantic import BaseModel


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    question: str
    sql: str
    explanation: str
    suggested_chart_type: str
    columns: list[str]
    rows: list[dict]
    row_count: int
    chart_json: dict | None = None
    error: str | None = None


class ColumnInfo(BaseModel):
    name: str
    type: str
    nullable: bool
    primary_key: bool


class TableInfo(BaseModel):
    name: str
    columns: list[ColumnInfo]
    sample_data: list[dict]


class SchemaResponse(BaseModel):
    tables: list[TableInfo]


class HistoryItem(BaseModel):
    id: int
    question: str
    sql: str
    explanation: str
    chart_type: str
    row_count: int
    created_at: str


class HistoryListResponse(BaseModel):
    items: list[HistoryItem]


class DaxRequest(BaseModel):
    question: str
    sql: str
    columns: list[str]


class DaxMeasureSchema(BaseModel):
    name: str
    expression: str
    description: str


class DaxResponse(BaseModel):
    measures: list[DaxMeasureSchema]
    error: str | None = None
