"""Tests for FastAPI endpoints."""


def test_health(test_client):
    response = test_client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_schema_endpoint(test_client):
    response = test_client.get("/api/schema")
    assert response.status_code == 200
    data = response.json()
    table_names = [t["name"] for t in data["tables"]]
    assert "customers" in table_names
    assert "policies" in table_names


def test_schema_single_table(test_client):
    response = test_client.get("/api/schema/customers")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "customers"
    assert len(data["columns"]) > 0


def test_history_endpoint(test_client):
    response = test_client.get("/api/history")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
