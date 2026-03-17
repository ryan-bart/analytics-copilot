export interface QueryRequest {
  question: string;
}

export interface QueryResponse {
  question: string;
  sql: string;
  explanation: string;
  suggested_chart_type: string;
  columns: string[];
  rows: Record<string, unknown>[];
  row_count: number;
  chart_json?: Record<string, unknown> | null;
  error?: string | null;
}

export interface ColumnInfo {
  name: string;
  type: string;
  nullable: boolean;
  primary_key: boolean;
}

export interface TableInfo {
  name: string;
  columns: ColumnInfo[];
  sample_data: Record<string, unknown>[];
}

export interface SchemaResponse {
  tables: TableInfo[];
}
