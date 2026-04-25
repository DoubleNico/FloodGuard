from __future__ import annotations

import asyncio
import sqlite3
from pathlib import Path

from app.config import Settings
from app.database import connect, create_schema, initialize_database, next_prefixed_id
from app.hydralis import (
    UpdateAlertStatusRequest,
    _alert_from_row,
    _create_token,
    _decode_token,
    _password_hash,
    get_alerts,
    update_alert_status,
)


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


def test_schema_backfills_mobile_alert_columns(tmp_path: Path) -> None:
    db_path = tmp_path / "legacy.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.executescript(
        """
        CREATE TABLE alerts (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            severity INTEGER NOT NULL,
            status TEXT NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            affected_areas TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            published_at TEXT,
            closed_at TEXT,
            created_by TEXT NOT NULL,
            broadcast_sent INTEGER NOT NULL DEFAULT 0,
            recipient_count INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE emergency_triggers (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            lat REAL NOT NULL,
            lng REAL NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL,
            acknowledged INTEGER NOT NULL DEFAULT 0
        );
        """
    )

    create_schema(conn)

    alert_columns = {row["name"] for row in conn.execute("PRAGMA table_info(alerts)").fetchall()}
    trigger_columns = {row["name"] for row in conn.execute("PRAGMA table_info(emergency_triggers)").fetchall()}
    conn.close()

    assert {"user_name", "mobility_info"} <= alert_columns
    assert {"user_name", "mobility_info"} <= trigger_columns


def test_initialize_backfills_existing_mobile_alert_metadata(tmp_path: Path) -> None:
    settings = Settings(database_path=str(tmp_path / "legacy-alert.db"))
    initialize_database(settings)
    with connect(settings) as conn:
        now = "2026-04-25T00:00:00Z"
        conn.execute(
            """
            INSERT INTO alerts (
                id, type, severity, status, title, message, affected_areas, created_at,
                updated_at, published_at, closed_at, created_by, broadcast_sent, recipient_count
            ) VALUES (?, 'evacuation', 5, 'published', 'Mobile Emergency Alert', 'MAN-DOWN', '[]', ?, ?, ?, NULL, ?, 1, 0)
            """,
            ("ALR-999", now, now, now, "mob_003"),
        )
        conn.commit()

    initialize_database(settings)

    with connect(settings) as conn:
        row = conn.execute("SELECT * FROM alerts WHERE id = 'ALR-999'").fetchone()
        alert = _alert_from_row(row)

    assert alert["user_name"] == "Mihai Stan"
    assert alert["userStatus"] == "Man Down"
    assert alert["mobilityInfo"]["level"] == "High Risk"


def test_alert_list_falls_back_to_mobile_user_metadata(tmp_path: Path) -> None:
    settings = Settings(database_path=str(tmp_path / "fallback-alert.db"))
    initialize_database(settings)
    with connect(settings) as conn:
        now = "2026-04-25T00:00:00Z"
        conn.execute(
            """
            INSERT INTO alerts (
                id, type, severity, status, title, message, affected_areas, created_at,
                updated_at, published_at, closed_at, created_by, broadcast_sent, recipient_count,
                user_name, mobility_info
            ) VALUES (?, 'evacuation', 5, 'published', 'Mobile Emergency Alert', 'MAN-DOWN', '[]', ?, ?, ?, NULL, ?, 1, 0, NULL, NULL)
            """,
            ("ALR-998", now, now, now, "mob_003"),
        )
        conn.commit()
        alerts = get_alerts(status=None, severity=None, conn=conn)["alerts"]

    alert = next(item for item in alerts if item["id"] == "ALR-998")
    assert alert["userName"] == "Mihai Stan"
    assert alert["userStatus"] == "Man Down"
    assert alert["mobilityInfo"]["level"] == "High Risk"


def test_alert_can_be_marked_accidental(tmp_path: Path) -> None:
    settings = Settings(database_path=str(tmp_path / "hydralis-test.db"))
    initialize_database(settings)

    with connect(settings) as conn:
        alert = asyncio.run(update_alert_status("ALR-001", UpdateAlertStatusRequest(status="accidental"), conn))

    assert alert["status"] == "accidental"
    assert alert["closedAt"] is not None


def test_demo_auth_hash_and_token() -> None:
    assert _password_hash("password123") == _password_hash("password123")

    token = _create_token({"id": "usr_001", "username": "dispatcher_ion", "role": "dispatcher"}, "secret")

    assert token.count(".") == 2
    assert _decode_token(token, "secret")["id"] == "usr_001"
