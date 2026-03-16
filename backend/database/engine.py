from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from backend.config import settings

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
    echo=False,
)

SessionLocal = sessionmaker(bind=engine)


def execute_readonly(sql: str) -> list[dict]:
    """Execute a read-only SQL query and return results as list of dicts."""
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        columns = list(result.keys())
        return [dict(zip(columns, row)) for row in result.fetchall()]
