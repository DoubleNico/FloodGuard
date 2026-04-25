from __future__ import annotations

import asyncio
from pathlib import Path

from app.config import Settings
from app.database import connect, initialize_database
from app.hydralis import _create_token
from app.mobile import (
    CurrentLocation,
    TriggerAlertRequest,
    _mobile_user_from_row,
    distance_meters,
    parse_radius_meters,
    trigger_alert,
)


def test_mobile_tables_seed_demo_user(tmp_path: Path) -> None:
    settings = Settings(database_path=str(tmp_path / "mobile-test.db"))
    initialize_database(settings)

    with connect(settings) as conn:
        row = conn.execute("SELECT * FROM mobile_users WHERE email = 'john@example.com'").fetchone()

    user = _mobile_user_from_row(row)

    assert user["user_id"] == "mob_001"
    assert user["email"] == "john@example.com"
    assert user["safety_level"] == 1


def test_radius_parser_supports_km_and_meters() -> None:
    assert parse_radius_meters("10km") == 10_000
    assert parse_radius_meters("750m") == 750
    assert parse_radius_meters("5000") == 5_000


def test_distance_meters_nearby_points() -> None:
    distance = distance_meters(45.4353, 28.0080, 45.4354, 28.0081)

    assert 0 < distance < 20


def test_mobile_sos_creates_dispatch_alert_with_user_and_mobility(tmp_path: Path) -> None:
    settings = Settings(database_path=str(tmp_path / "mobile-alert-test.db"))
    initialize_database(settings)
    token = _create_token({"id": "mob_001", "email": "john@example.com", "role": "mobile"}, settings.jwt_secret)
    request = TriggerAlertRequest(
        current_location=CurrentLocation(lat=45.4353, lng=28.0080),
        mobility_info={"has_issues": True, "gravity": "High", "level": "High"},
    )

    with connect(settings) as conn:
        response = asyncio.run(
            trigger_alert(request, authorization=f"Bearer {token}", conn=conn, settings=settings)
        )
        row = conn.execute("SELECT * FROM alerts WHERE id = ?", (response["alert_id"],)).fetchone()

    assert response["broadcast"]["user_name"] == "John Doe"
    assert response["broadcast"]["mobility_info"]["level"] == "High"
    assert "John Doe" in row["title"]
    assert "Mobility: High" in row["title"]
