"""Query history persistence."""

import json
from datetime import datetime, timezone

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.engine import SessionLocal
from backend.database.models import Base


class QueryHistory(Base):
    __tablename__ = "query_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    question: Mapped[str] = mapped_column(String(500))
    sql: Mapped[str] = mapped_column(Text)
    explanation: Mapped[str] = mapped_column(Text)
    chart_type: Mapped[str] = mapped_column(String(20))
    row_count: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[str] = mapped_column(String(30))
    result_preview: Mapped[str] = mapped_column(Text, default="[]")


def save_query(
    question: str,
    sql: str,
    explanation: str,
    chart_type: str,
    row_count: int,
    rows: list[dict] | None = None,
) -> int:
    """Save a query to history and return the ID."""
    preview = json.dumps(rows[:5]) if rows else "[]"
    entry = QueryHistory(
        question=question,
        sql=sql,
        explanation=explanation,
        chart_type=chart_type,
        row_count=row_count,
        created_at=datetime.now(timezone.utc).isoformat(),
        result_preview=preview,
    )
    with SessionLocal() as session:
        session.add(entry)
        session.commit()
        session.refresh(entry)
        return entry.id


def get_history(limit: int = 50) -> list[dict]:
    """Return recent query history."""
    with SessionLocal() as session:
        entries = (
            session.query(QueryHistory)
            .order_by(QueryHistory.id.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": e.id,
                "question": e.question,
                "sql": e.sql,
                "explanation": e.explanation,
                "chart_type": e.chart_type,
                "row_count": e.row_count,
                "created_at": e.created_at,
            }
            for e in entries
        ]


def get_history_item(item_id: int) -> dict | None:
    """Return a single history item with result preview."""
    with SessionLocal() as session:
        entry = session.query(QueryHistory).filter_by(id=item_id).first()
        if not entry:
            return None
        return {
            "id": entry.id,
            "question": entry.question,
            "sql": entry.sql,
            "explanation": entry.explanation,
            "chart_type": entry.chart_type,
            "row_count": entry.row_count,
            "created_at": entry.created_at,
            "result_preview": json.loads(entry.result_preview),
        }
