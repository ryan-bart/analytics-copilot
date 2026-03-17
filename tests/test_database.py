"""Tests for database seeding and schema inspection."""

from backend.database.engine import execute_readonly
from backend.database.inspector import get_schema, get_schema_ddl, get_sample_data
from backend.database.seed import seed_database


def test_seed_creates_records():
    counts = seed_database()
    assert counts["customers"] == 200
    assert counts["policies"] > 300
    assert counts["claims"] > 100
    assert counts["payments"] > 500


def test_foreign_key_integrity():
    """All policy.customer_id values reference existing customers."""
    orphans = execute_readonly(
        "SELECT COUNT(*) AS cnt FROM policies p "
        "LEFT JOIN customers c ON p.customer_id = c.id "
        "WHERE c.id IS NULL"
    )
    assert orphans[0]["cnt"] == 0


def test_claim_fk_integrity():
    orphans = execute_readonly(
        "SELECT COUNT(*) AS cnt FROM claims cl "
        "LEFT JOIN policies p ON cl.policy_id = p.id "
        "WHERE p.id IS NULL"
    )
    assert orphans[0]["cnt"] == 0


def test_get_schema_returns_all_tables():
    schema = get_schema()
    assert "customers" in schema
    assert "policies" in schema
    assert "claims" in schema
    assert "payments" in schema


def test_get_schema_ddl_contains_create():
    ddl = get_schema_ddl()
    assert "CREATE TABLE" in ddl
    assert "customers" in ddl
    assert "policies" in ddl


def test_get_sample_data():
    rows = get_sample_data("customers", limit=3)
    assert len(rows) == 3
    assert "first_name" in rows[0]
