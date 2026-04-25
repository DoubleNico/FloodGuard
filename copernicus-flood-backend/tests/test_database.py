from __future__ import annotations

from pathlib import Path

from app.config import Settings
from app.database import connect, initialize_database, next_prefixed_id
from app.hydralis import _alert_from_row, _create_token, _decode_token, _password_hash


def test_initialize_database_seeds_core_data(tmp_path: Path) -> None:
    settings = Settings(database_path=str(tmp_path / "hydralis-test.db"))

    initialize_database(settings)

    with connect(settings) as conn:
        assert conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 5
        assert conn.execute("SELECT COUNT(*) FROM alerts").fetchone()[0] >= 5
        assert conn.execute("SELECT COUNT(*) FROM safe_locations").fetchone()[0] >= 7
        assert conn.execute("SELECT COUNT(*) FROM factories").fetchone()[0] >= 4
        assert conn.execute("SELECT COUNT(*) FROM sensors").fetchone()[0] >= 30
        assert conn.execute("SELECT COUNT(*) FROM mobile_users").fetchone()[0] >= 5
        assert conn.execute("SELECT COUNT(*) FROM emergency_triggers").fetchone()[0] >= 2


def test_next_prefixed_id_increments_existing_ids(tmp_path: Path) -> None:
    settings = Settings(database_path=str(tmp_path / "hydralis-test.db"))
    initialize_database(settings)

    with connect(settings) as conn:
        assert next_prefixed_id(conn, "alerts", "ALR") == "ALR-006"


def test_alert_row_maps_to_api_shape(tmp_path: Path) -> None:
    settings = Settings(database_path=str(tmp_path / "hydralis-test.db"))
    initialize_database(settings)

    with connect(settings) as conn:
        row = conn.execute("SELECT * FROM alerts WHERE id = 'ALR-001'").fetchone()

    alert = _alert_from_row(row)

    assert alert["affectedAreas"]
    assert "createdAt" in alert
    assert "broadcastSent" in alert


def test_demo_auth_hash_and_token() -> None:
    assert _password_hash("password123") == _password_hash("password123")

    token = _create_token({"id": "usr_001", "username": "dispatcher_ion", "role": "dispatcher"}, "secret")

    assert token.count(".") == 2
    assert _decode_token(token, "secret")["id"] == "usr_001"
