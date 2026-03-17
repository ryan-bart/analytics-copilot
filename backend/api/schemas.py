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
