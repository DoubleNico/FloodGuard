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
            recipient_count INTEGER NOT NULL DEFAULT 0,
            user_name TEXT,
            mobility_info TEXT
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

        CREATE TABLE IF NOT EXISTS flood_heatmap (
            id TEXT PRIMARY KEY,
            zone TEXT NOT NULL,
            lat REAL NOT NULL,
            lng REAL NOT NULL,
            intensity REAL NOT NULL,
            polygon TEXT NOT NULL,
            risk_level TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS mobile_users (
            id TEXT PRIMARY KEY,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            birthday TEXT NOT NULL,
            primary_location TEXT NOT NULL,
            safety_level INTEGER NOT NULL CHECK (safety_level BETWEEN 0 AND 3),
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS user_status_updates (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            status TEXT NOT NULL,
            lat REAL NOT NULL,
            lng REAL NOT NULL,
            timestamp TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS emergency_triggers (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            user_name TEXT,
            mobility_info TEXT,
            lat REAL NOT NULL,
            lng REAL NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL,
            acknowledged INTEGER NOT NULL DEFAULT 0
        );
        """
    )


def seed_database(conn: sqlite3.Connection) -> None:
    now = utc_now_iso()
    conn.executemany(
        """
        INSERT OR IGNORE INTO users (id, username, password_hash, role, display_name)
        VALUES (?, ?, ?, ?, ?)
        """,
        [
            ("usr_001", "dispatcher_ion", _demo_password_hash("password123"), "dispatcher", "Dispatcher Ionescu"),
            ("usr_002", "industrial_maria", _demo_password_hash("password123"), "industrial", "Maria Industrial"),
            ("usr_003", "admin", _demo_password_hash("password123"), "admin", "Hydralis Admin"),
            ("usr_004", "dispatcher_ana", _demo_password_hash("password123"), "dispatcher", "Dispatcher Ana Popa"),
            ("usr_005", "industrial_vlad", _demo_password_hash("password123"), "industrial", "Vlad Industrial"),
        ],
    )

    conn.executemany(
        """
        INSERT OR IGNORE INTO alerts (
            id, type, severity, status, title, message, affected_areas, created_at,
            updated_at, published_at, closed_at, created_by, broadcast_sent, recipient_count
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
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
            (
                "ALR-002",
                "flash-flood",
                5,
                "approved",
                "Flash Flood Risk in Micro 17",
                "Radar precipitation and drainage models indicate rapid runoff risk in low streets.",
                json.dumps(["Micro 17", "Tiglina I"]),
                now,
                now,
                None,
                None,
                "Dispatcher Ana Popa",
                0,
                0,
            ),
            (
                "ALR-003",
                "storm",
                3,
                "review",
                "Severe Storm Watch",
                "Strong wind and heavy rainfall may affect city transport corridors.",
                json.dumps(["Centru", "Mazepa"]),
                now,
                now,
                None,
                None,
                "Dispatcher Ionescu",
                0,
                0,
            ),
            (
                "ALR-004",
                "evacuation",
                5,
                "draft",
                "Port Evacuation Route Preparation",
                "Prepare evacuation route signage and shelter intake staff near Port district.",
                json.dumps(["Port"]),
                now,
                now,
                None,
                None,
                "Hydralis Admin",
                0,
                0,
            ),
            (
                "ALR-005",
                "flood",
                2,
                "closed",
                "Prut Monitoring Notice Closed",
                "Previous monitoring notice closed after river level stabilized.",
                json.dumps(["Oancea", "Prut river corridor"]),
                now,
                now,
                None,
                now,
                "Dispatcher Ana Popa",
                0,
                3800,
            ),
        ],
    )

    conn.executemany(
        """
        INSERT OR IGNORE INTO safe_locations (
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
            (
                "SL-003",
                "City Hall Emergency Center",
                "medical",
                45.4368,
                28.0542,
                "Str. Domneasca 54, Galati",
                220,
                154,
                "filling",
                "+40 236 307 700",
                "Medical triage, generator backup",
                now,
            ),
            (
                "SL-004",
                "Colegiul National Vasile Alecsandri",
                "shelter",
                45.4389,
                28.0558,
                "Str. Nicolae Balcescu 41, Galati",
                360,
                338,
                "filling",
                "+40 236 411 222",
                "Second-floor sleeping area, limited parking",
                now,
            ),
            (
                "SL-005",
                "Metro Supply Depot",
                "supply-depot",
                45.4665,
                28.0281,
                "DN26, Galati",
                1200,
                410,
                "open",
                "+40 236 000 222",
                "Food, water, blankets, forklift access",
                now,
            ),
            (
                "SL-006",
                "Universitatea Dunarea de Jos Hall",
                "shelter",
                45.4459,
                28.0507,
                "Str. Domneasca 47, Galati",
                280,
                280,
                "full",
                "+40 236 460 000",
                "Full capacity, redirect to SL-001",
                now,
            ),
            (
                "SL-007",
                "Bariera Traian Assembly Point",
                "assembly-point",
                45.4641,
                28.0149,
                "Bariera Traian, Galati",
                700,
                42,
                "open",
                "+40 236 000 333",
                "Bus pickup point, outdoor lighting",
                now,
            ),
        ],
    )

    _upsert_named_rows(
        conn,
        "water_levels",
        "station",
        "INSERT INTO water_levels (station, level, warning_level, critical_level, trend) VALUES (?, ?, ?, ?, ?)",
        [
            ("Danube - Galati", 142, 150, 170, "rising"),
            ("Siret - Sendreni", 104, 130, 155, "stable"),
            ("Prut - Oancea", 96, 125, 150, "falling"),
            ("Lake Brates Outflow", 118, 135, 160, "rising"),
            ("Danube - Braila", 138, 152, 176, "stable"),
            ("Covurlui Canal", 72, 100, 130, "rising"),
        ],
    )
    _upsert_named_rows(
        conn,
        "ndwi",
        "zone",
        "INSERT INTO ndwi (zone, value, risk) VALUES (?, ?, ?)",
        [
            ("Port", 0.78, "high"),
            ("Faleza Dunarii", 0.52, "moderate"),
            ("Micro 17", 0.31, "low"),
            ("Tiglina I", 0.63, "high"),
            ("Mazepa", 0.44, "moderate"),
            ("Bariera Traian", 0.22, "low"),
            ("Filești Industrial", 0.83, "critical"),
        ],
    )
    _upsert_named_rows(
        conn,
        "precipitation",
        "date",
        "INSERT INTO precipitation (date, actual, forecast) VALUES (?, ?, ?)",
        [
            ("Apr 21", 0, None),
            ("Apr 22", 4, None),
            ("Apr 23", 6, None),
            ("Apr 24", 18, None),
            ("Apr 25", None, 25),
            ("Apr 26", None, 14),
            ("Apr 27", None, 9),
            ("Apr 28", None, 3),
        ],
    )
    conn.executemany(
        """
        INSERT OR IGNORE INTO galileo_satellites (id, name, status, signal)
        VALUES (?, ?, ?, ?)
        """,
        [
            ("GAL-101", "Galileo GSAT0211", "operational", 97),
            ("GAL-102", "Galileo GSAT0220", "operational", 94),
            ("GAL-103", "Galileo GSAT0204", "testing", 76),
            ("GAL-104", "Galileo GSAT0219", "operational", 91),
            ("GAL-105", "Galileo GSAT0223", "operational", 88),
            ("GAL-106", "Galileo GSAT0104", "unavailable", 0),
            ("GAL-107", "Galileo GSAT0206", "operational", 82),
        ],
    )

    conn.executemany(
        """
        INSERT OR IGNORE INTO factories (
            id, name, location, lat, lng, status, sensor_count, risk_level,
            water_proximity, last_inspection, employees
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
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
            (
                "F-002",
                "Damen Shipyards Galati",
                "Port Bazinul Nou",
                45.4281,
                28.0734,
                "operational",
                18,
                "moderate",
                80,
                "2026-04-20T00:00:00Z",
                2300,
            ),
            (
                "F-003",
                "Prutul SA Oil Processing",
                "Zona Industriala Est",
                45.4217,
                28.0386,
                "critical",
                15,
                "critical",
                55,
                "2026-04-16T00:00:00Z",
                680,
            ),
            (
                "F-004",
                "Galati Logistics Cold Storage",
                "Filești",
                45.4574,
                27.9862,
                "offline",
                9,
                "moderate",
                410,
                "2026-04-05T00:00:00Z",
                145,
            ),
        ],
    )

    conn.executemany(
        """
        INSERT OR IGNORE INTO sensors (
            id, factory_id, name, type, value, unit, threshold, status, last_update
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            ("S-001", "F-001", "Danube Proximity Gauge", "water-level", 142, "cm", 150, "warning", now),
            ("S-002", "F-001", "Pump Station Pressure", "pressure", 6.8, "bar", 8.5, "online", now),
            ("S-003", "F-001", "Storage Hall Humidity", "humidity", 72, "%", 85, "online", now),
            ("S-004", "F-001", "Blast Furnace Foundation Tilt", "structural", 2.4, "mm", 4.0, "online", now),
            ("S-005", "F-002", "Dock Gate Water Gauge", "water-level", 131, "cm", 155, "online", now),
            ("S-006", "F-002", "Paint Hall Humidity", "humidity", 66, "%", 80, "online", now),
            ("S-007", "F-002", "Crane Rail Strain", "structural", 3.1, "mm", 5.0, "warning", now),
            ("S-008", "F-003", "Oil Tank Bund Water Level", "water-level", 163, "cm", 150, "critical", now),
            ("S-009", "F-003", "Valve Station Pressure", "pressure", 9.4, "bar", 8.5, "critical", now),
            ("S-010", "F-003", "Warehouse Temperature", "temperature", 31.5, "C", 40.0, "online", now),
            ("S-011", "F-004", "Cold Room Temperature", "temperature", -8.0, "C", -5.0, "offline", now),
            ("S-012", "F-004", "Loading Dock Water Sensor", "water-level", 44, "cm", 90, "offline", now),
            ("S-013", "F-001", "Virtual River Embankment Gauge A", "water-level", 148, "cm", 155, "warning", now),
            ("S-014", "F-001", "Virtual Control Room Humidity", "humidity", 61, "%", 80, "online", now),
            ("S-015", "F-001", "Virtual Conveyor Bearing Temperature", "temperature", 58.4, "C", 75.0, "online", now),
            ("S-016", "F-001", "Virtual Drain Pump Pressure", "pressure", 7.9, "bar", 8.5, "warning", now),
            ("S-017", "F-001", "Virtual Flood Wall Displacement", "structural", 3.7, "mm", 4.0, "warning", now),
            ("S-018", "F-002", "Virtual Quay Wall Water Level", "water-level", 146, "cm", 160, "online", now),
            ("S-019", "F-002", "Virtual Dry Dock Gate Pressure", "pressure", 5.4, "bar", 7.5, "online", now),
            ("S-020", "F-002", "Virtual Hull Assembly Humidity", "humidity", 79, "%", 82, "warning", now),
            ("S-021", "F-002", "Virtual Workshop Temperature", "temperature", 27.8, "C", 38.0, "online", now),
            ("S-022", "F-002", "Virtual Pier Settlement Sensor", "structural", 1.6, "mm", 3.5, "online", now),
            ("S-023", "F-003", "Virtual Chemical Bund Flood Probe", "water-level", 171, "cm", 150, "critical", now),
            ("S-024", "F-003", "Virtual Nitrogen Line Pressure", "pressure", 10.1, "bar", 9.0, "critical", now),
            ("S-025", "F-003", "Virtual Solvent Store Humidity", "humidity", 88, "%", 85, "critical", now),
            ("S-026", "F-003", "Virtual Reactor Hall Temperature", "temperature", 42.5, "C", 40.0, "critical", now),
            ("S-027", "F-003", "Virtual Tank Pad Crack Monitor", "structural", 4.8, "mm", 4.0, "critical", now),
            ("S-028", "F-004", "Virtual Backup Generator Temperature", "temperature", 0.0, "C", 70.0, "offline", now),
            ("S-029", "F-004", "Virtual Yard Drain Water Level", "water-level", 62, "cm", 95, "offline", now),
            ("S-030", "F-004", "Virtual Warehouse Roof Deflection", "structural", 0.0, "mm", 5.0, "offline", now),
        ],
    )

    conn.execute(
        """
        INSERT OR IGNORE INTO subscription_status (
            id, current_tier, alerts_sent, locations_configured, sensors_connected, active_users
        ) VALUES (1, 'operations', 47, 7, 12, 4)
        """
    )

    if conn.execute("SELECT COUNT(*) FROM flood_heatmap").fetchone()[0] == 0:
        import math
        heatmap_seed = []
        lat_start = 45.39
        lng_start = 28.00
        lat_step = 0.008
        lng_step = 0.012
        
        idx = 1
        for i in range(12):
            for j in range(12):
                lat1 = lat_start + i * lat_step
                lat2 = lat1 + lat_step
                lng1 = lng_start + j * lng_step
                lng2 = lng1 + lng_step
                
                center_lat = (lat1 + lat2) / 2
                center_lng = (lng1 + lng2) / 2
                
                # Distance to "danger" center (Port)
                dist = math.sqrt((center_lat - 45.425)**2 + ((center_lng - 28.055) * 0.7)**2)
                
                # Base intensity
                intensity = max(0.0, 1.0 - (dist / 0.04))
                # Add some noise to make it look realistic
                import random
                intensity = min(1.0, max(0.0, intensity + random.uniform(-0.15, 0.15)))
                
                if intensity >= 0.75:
                    risk = "critical"
                elif intensity >= 0.5:
                    risk = "high"
                elif intensity >= 0.25:
                    risk = "moderate"
                else:
                    risk = "low"
                    
                polygon = [[lat1, lng1], [lat2, lng1], [lat2, lng2], [lat1, lng2]]
                
                heatmap_seed.append((
                    f"HZ-G{idx:03d}",
                    f"Grid {i}-{j}",
                    center_lat,
                    center_lng,
                    intensity,
                    json.dumps(polygon),
                    risk
                ))
                idx += 1
                
        conn.executemany(
            "INSERT INTO flood_heatmap (id, zone, lat, lng, intensity, polygon, risk_level) VALUES (?, ?, ?, ?, ?, ?, ?)",
            heatmap_seed
        )
    conn.execute(
        """
        UPDATE subscription_status
        SET locations_configured = (SELECT COUNT(*) FROM safe_locations),
            sensors_connected = (SELECT COUNT(*) FROM sensors),
            active_users = (SELECT COUNT(*) FROM users)
        WHERE id = 1
        """
    )

    conn.executemany(
        """
        INSERT OR IGNORE INTO mobile_users (
            id, full_name, email, password_hash, birthday, primary_location,
            safety_level, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                "mob_001",
                "John Doe",
                "john@example.com",
                _demo_password_hash("securepassword123"),
                "05/14/1990",
                "Galati, Romania",
                1,
                now,
                now,
            ),
            (
                "mob_002",
                "Elena Marin",
                "elena.marin@example.com",
                _demo_password_hash("securepassword123"),
                "09/21/1984",
                "Mazepa, Galati",
                2,
                now,
                now,
            ),
            (
                "mob_003",
                "Mihai Stan",
                "mihai.stan@example.com",
                _demo_password_hash("securepassword123"),
                "01/08/1978",
                "Port, Galati",
                3,
                now,
                now,
            ),
            (
                "mob_004",
                "Ioana Radu",
                "ioana.radu@example.com",
                _demo_password_hash("securepassword123"),
                "12/02/1995",
                "Tiglina I, Galati",
                1,
                now,
                now,
            ),
            (
                "mob_005",
                "Andrei Pavel",
                "andrei.pavel@example.com",
                _demo_password_hash("securepassword123"),
                "07/30/2001",
                "Micro 17, Galati",
                2,
                now,
                now,
            ),
        ],
    )

    conn.executemany(
        """
        INSERT OR IGNORE INTO user_status_updates (id, user_id, status, lat, lng, timestamp, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        [
            ("UST-001", "mob_002", "Monitor", 45.4419, 28.0455, now, now),
            ("UST-002", "mob_003", "Need Help", 45.4248, 28.0731, now, now),
            ("UST-003", "mob_004", "Safe", 45.4382, 28.0309, now, now),
            ("UST-004", "mob_005", "Emergency", 45.4572, 28.0024, now, now),
        ],
    )

    conn.executemany(
        """
        INSERT OR IGNORE INTO emergency_triggers (id, user_id, lat, lng, message, created_at, acknowledged)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        [
            ("EMG-001", "mob_003", 45.4248, 28.0731, "Water entering ground floor near port warehouse.", now, 0),
            ("EMG-002", "mob_005", 45.4572, 28.0024, "Blocked road and rising water near Micro 17.", now, 0),
        ],
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


def _upsert_named_rows(
    conn: sqlite3.Connection,
    table: str,
    unique_column: str,
    sql: str,
    rows: list[tuple[Any, ...]],
) -> None:
    for row in rows:
        if not conn.execute(f"SELECT 1 FROM {table} WHERE {unique_column} = ?", (row[0],)).fetchone():
            conn.execute(sql, row)


def _demo_password_hash(password: str) -> str:
    import hashlib

    return hashlib.sha256(f"hydralis-demo:{password}".encode("utf-8")).hexdigest()
