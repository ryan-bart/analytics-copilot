"""Database schema inspection utilities."""

from sqlalchemy import inspect as sa_inspect
from sqlalchemy import text

from backend.database.engine import engine


def get_schema() -> dict[str, list[dict]]:
    """Return schema info as {table_name: [{column, type, nullable, pk}]}."""
    inspector = sa_inspect(engine)
    schema = {}
    for table_name in inspector.get_table_names():
        columns = []
        pk_constraint = inspector.get_pk_constraint(table_name)
        pk_cols = set(pk_constraint.get("constrained_columns", []))
        for col in inspector.get_columns(table_name):
            columns.append({
                "name": col["name"],
                "type": str(col["type"]),
                "nullable": col.get("nullable", True),
                "primary_key": col["name"] in pk_cols,
            })
        schema[table_name] = columns
    return schema


def _get_distinct_values(table_name: str, column_name: str, limit: int = 10) -> list[str]:
    """Return distinct values for a VARCHAR column (up to limit)."""
    with engine.connect() as conn:
        result = conn.execute(
            text(f"SELECT DISTINCT {column_name} FROM {table_name} LIMIT :limit"),
            {"limit": limit},
        )
        return [str(row[0]) for row in result.fetchall() if row[0] is not None]


def get_schema_ddl() -> str:
    """Return CREATE TABLE DDL for all tables, with enum-like values annotated."""
    inspector = sa_inspect(engine)
    ddl_parts = []
    for table_name in inspector.get_table_names():
        columns = inspector.get_columns(table_name)
        pk_constraint = inspector.get_pk_constraint(table_name)
        pk_cols = set(pk_constraint.get("constrained_columns", []))
        fks = inspector.get_foreign_keys(table_name)

        col_defs = []
        for col in columns:
            parts = [col["name"], str(col["type"])]
            if col["name"] in pk_cols:
                parts.append("PRIMARY KEY")
            if not col.get("nullable", True):
                parts.append("NOT NULL")
            # Annotate low-cardinality string columns with their actual values
            if "VARCHAR" in str(col["type"]) and col["name"] not in pk_cols:
                distinct = _get_distinct_values(table_name, col["name"])
                if 1 < len(distinct) <= 10:
                    parts.append(f"-- values: {', '.join(repr(v) for v in distinct)}")
            col_defs.append("  " + " ".join(parts))

        for fk in fks:
            for local_col, ref_col in zip(fk["constrained_columns"], fk["referred_columns"]):
                col_defs.append(
                    f"  FOREIGN KEY ({local_col}) REFERENCES {fk['referred_table']}({ref_col})"
                )

        ddl = f"CREATE TABLE {table_name} (\n" + ",\n".join(col_defs) + "\n);"
        ddl_parts.append(ddl)

    return "\n\n".join(ddl_parts)


def get_sample_data(table_name: str, limit: int = 3) -> list[dict]:
    """Return a few sample rows from a table."""
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT * FROM {table_name} LIMIT :limit"), {"limit": limit})
        columns = list(result.keys())
        return [dict(zip(columns, row)) for row in result.fetchall()]
