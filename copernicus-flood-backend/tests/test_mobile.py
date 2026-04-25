from __future__ import annotations

from pathlib import Path

from app.config import Settings
from app.database import connect, initialize_database
from app.mobile import distance_meters, parse_radius_meters, _mobile_user_from_row


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
