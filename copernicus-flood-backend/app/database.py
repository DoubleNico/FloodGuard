from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.config import Settings, get_settings


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def connect(settings: Settings | None = None) -> sqlite3.Connection:
    settings = settings or get_settings()
    db_path = Path(settings.database_path)
    if db_path.parent != Path("."):
        db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_database(settings: Settings | None = None) -> None:
    settings = settings or get_settings()
    with connect(settings) as conn:
        create_schema(conn)
        seed_database(conn)


def create_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK (role IN ('dispatcher', 'industrial', 'admin')),
            display_name TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS alerts (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            severity INTEGER NOT NULL CHECK (severity BETWEEN 1 AND 5),
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

        CREATE TABLE IF NOT EXISTS safe_locations (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            lat REAL NOT NULL,
            lng REAL NOT NULL,
            address TEXT NOT NULL,
            capacity INTEGER NOT NULL,
            current_occupancy INTEGER NOT NULL,
            status TEXT NOT NULL,
            contact_phone TEXT,
            accessibility_notes TEXT,
            last_updated TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS water_levels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station TEXT NOT NULL,
            level INTEGER NOT NULL,
            warning_level INTEGER NOT NULL,
            critical_level INTEGER NOT NULL,
            trend TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS ndwi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            zone TEXT NOT NULL,
            value REAL NOT NULL,
            risk TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS precipitation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            actual REAL,
            forecast REAL
        );

        CREATE TABLE IF NOT EXISTS galileo_satellites (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            status TEXT NOT NULL,
            signal INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS factories (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            location TEXT NOT NULL,
            lat REAL NOT NULL,
            lng REAL NOT NULL,
            status TEXT NOT NULL,
            sensor_count INTEGER NOT NULL,
            risk_level TEXT NOT NULL,
            water_proximity INTEGER NOT NULL,
            last_inspection TEXT NOT NULL,
            employees INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS sensors (
            id TEXT PRIMARY KEY,
            factory_id TEXT NOT NULL REFERENCES factories(id) ON DELETE CASCADE,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            value REAL NOT NULL,
            unit TEXT NOT NULL,
            threshold REAL NOT NULL,
            status TEXT NOT NULL,
            last_update TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS subscription_status (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            current_tier TEXT NOT NULL,
            alerts_sent INTEGER NOT NULL,
            locations_configured INTEGER NOT NULL,
            sensors_connected INTEGER NOT NULL,
            active_users INTEGER NOT NULL
        );
        """
    )


def seed_database(conn: sqlite3.Connection) -> None:
    if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        conn.executemany(
            "INSERT INTO users (id, username, password_hash, role, display_name) VALUES (?, ?, ?, ?, ?)",
            [
                ("usr_001", "dispatcher_ion", _demo_password_hash("password123"), "dispatcher", "Dispatcher Ionescu"),
                ("usr_002", "industrial_maria", _demo_password_hash("password123"), "industrial", "Maria Industrial"),
                ("usr_003", "admin", _demo_password_hash("password123"), "admin", "Hydralis Admin"),
            ],
        )

    now = utc_now_iso()
    if conn.execute("SELECT COUNT(*) FROM alerts").fetchone()[0] == 0:
        conn.execute(
            """
            INSERT INTO alerts (
                id, type, severity, status, title, message, affected_areas, created_at,
                updated_at, published_at, closed_at, created_by, broadcast_sent, recipient_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "ALR-001",
                "flood",
                4,
                "published",
                "Danube River Level Critical",
                "Water levels at Galati require increased public attention.",
                json.dumps(["Port", "Faleza Dunarii"]),
                now,
                now,
                now,
                None,
                "Dispatcher Ionescu",
                1,
                12847,
            ),
        )

    if conn.execute("SELECT COUNT(*) FROM safe_locations").fetchone()[0] == 0:
        conn.executemany(
            """
            INSERT INTO safe_locations (
                id, name, type, lat, lng, address, capacity, current_occupancy,
                status, contact_phone, accessibility_notes, last_updated
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    "SL-001",
                    "Sala Sporturilor - Dunarea",
                    "shelter",
                    45.4353,
                    28.0497,
                    "Str. Stadionului 2, Galati",
                    500,
                    187,
                    "open",
                    "+40 236 412 000",
                    "Wheelchair accessible",
                    now,
                ),
                (
                    "SL-002",
                    "Parcul Viva Assembly Point",
                    "assembly-point",
                    45.4421,
                    28.0432,
                    "Bulevardul George Cosbuc, Galati",
                    900,
                    120,
                    "open",
                    "+40 236 000 111",
                    "Outdoor area with bus access",
                    now,
                ),
            ],
        )

    _seed_if_empty(
        conn,
        "water_levels",
        "INSERT INTO water_levels (station, level, warning_level, critical_level, trend) VALUES (?, ?, ?, ?, ?)",
        [
            ("Danube - Galati", 142, 150, 170, "rising"),
            ("Siret - Sendreni", 104, 130, 155, "stable"),
            ("Prut - Oancea", 96, 125, 150, "falling"),
        ],
    )
    _seed_if_empty(
        conn,
        "ndwi",
        "INSERT INTO ndwi (zone, value, risk) VALUES (?, ?, ?)",
        [
            ("Port", 0.78, "high"),
            ("Faleza Dunarii", 0.52, "moderate"),
            ("Micro 17", 0.31, "low"),
        ],
    )
    _seed_if_empty(
        conn,
        "precipitation",
        "INSERT INTO precipitation (date, actual, forecast) VALUES (?, ?, ?)",
        [
            ("Apr 23", 6, None),
            ("Apr 24", 18, None),
            ("Apr 25", None, 25),
            ("Apr 26", None, 14),
        ],
    )
    _seed_if_empty(
        conn,
        "galileo_satellites",
        "INSERT INTO galileo_satellites (id, name, status, signal) VALUES (?, ?, ?, ?)",
        [
            ("GAL-101", "Galileo GSAT0211", "operational", 97),
            ("GAL-102", "Galileo GSAT0220", "operational", 94),
            ("GAL-103", "Galileo GSAT0204", "testing", 76),
        ],
    )

    if conn.execute("SELECT COUNT(*) FROM factories").fetchone()[0] == 0:
        conn.execute(
            """
            INSERT INTO factories (
                id, name, location, lat, lng, status, sensor_count, risk_level,
                water_proximity, last_inspection, employees
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "F-001",
                "Liberty Galati Steelworks",
                "Siderurgistilor",
                45.4315,
                28.0098,
                "warning",
                24,
                "high",
                120,
                "2026-04-18T00:00:00Z",
                4200,
            ),
        )
    if conn.execute("SELECT COUNT(*) FROM sensors").fetchone()[0] == 0:
        conn.executemany(
            """
            INSERT INTO sensors (
                id, factory_id, name, type, value, unit, threshold, status, last_update
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                ("S-001", "F-001", "Danube Proximity Gauge", "water-level", 142, "cm", 150, "warning", now),
                ("S-002", "F-001", "Pump Station Pressure", "pressure", 6.8, "bar", 8.5, "online", now),
                ("S-003", "F-001", "Storage Hall Humidity", "humidity", 72, "%", 85, "online", now),
            ],
        )

    conn.execute(
        """
        INSERT OR IGNORE INTO subscription_status (
            id, current_tier, alerts_sent, locations_configured, sensors_connected, active_users
        ) VALUES (1, 'operations', 47, 7, 12, 4)
        """
    )


def row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return dict(row)


def next_prefixed_id(conn: sqlite3.Connection, table: str, prefix: str) -> str:
    rows = conn.execute(f"SELECT id FROM {table} WHERE id LIKE ? ORDER BY id DESC", (f"{prefix}-%",)).fetchall()
    max_number = 0
    for row in rows:
        try:
            max_number = max(max_number, int(str(row["id"]).split("-")[-1]))
        except ValueError:
            continue
    return f"{prefix}-{max_number + 1:03d}"


def _seed_if_empty(
    conn: sqlite3.Connection,
    table: str,
    sql: str,
    rows: list[tuple[Any, ...]],
) -> None:
    if conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] == 0:
        conn.executemany(sql, rows)


def _demo_password_hash(password: str) -> str:
    import hashlib

    return hashlib.sha256(f"hydralis-demo:{password}".encode("utf-8")).hexdigest()
