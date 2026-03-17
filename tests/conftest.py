import os
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database.models import Base


@pytest.fixture()
def in_memory_db():
    """Create an in-memory SQLite database with schema."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    return engine, session_factory


@pytest.fixture()
def mock_anthropic():
    """Mock Anthropic client that returns a canned SQL response."""
    mock_response = MagicMock()
    mock_response.content = [
        MagicMock(
            text='{"sql": "SELECT COUNT(*) AS count FROM policies WHERE status = \'Active\'", '
            '"explanation": "Counts active policies", '
            '"suggested_chart_type": "number"}'
        )
    ]
    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_response
    with patch("backend.llm.sql_generator.get_client", return_value=mock_client):
        yield mock_client


@pytest.fixture()
def test_client():
    """FastAPI test client with seeded database."""
    os.environ.setdefault("DATABASE_URL", "sqlite:///data/insurance.db")
    from backend.main import app

    with TestClient(app) as client:
        yield client
