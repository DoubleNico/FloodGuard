from __future__ import annotations

import base64
import hashlib
import hmac
import json
import sqlite3
from collections.abc import Iterator
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from app.config import Settings, get_settings
from app.database import connect, next_prefixed_id, utc_now_iso

router = APIRouter(prefix="/api/v1", tags=["Hydralis"])


AlertType = Literal["flood", "flash-flood", "storm", "evacuation"]
AlertStatus = Literal["draft", "review", "approved", "published", "updated", "closed"]
LocationType = Literal["shelter", "assembly-point", "medical", "supply-depot"]
LocationStatus = Literal["open", "filling", "full", "closed"]
FactoryStatus = Literal["operational", "warning", "critical", "offline"]
RiskLevel = Literal["low", "moderate", "high", "critical"]
SensorStatus = Literal["online", "warning", "critical", "offline"]


class LoginRequest(BaseModel):
    username: str
    password: str


class CreateAlertRequest(BaseModel):
    type: AlertType
    severity: int = Field(..., ge=1, le=5)
    title: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    affectedAreas: list[str] = Field(default_factory=list)


class UpdateAlertStatusRequest(BaseModel):
    status: AlertStatus


class CreateLocationRequest(BaseModel):
    name: str
    type: LocationType
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    address: str
    capacity: int = Field(..., ge=0)
    currentOccupancy: int = Field(0, ge=0)
    status: LocationStatus = "open"
    contactPhone: str | None = None
    accessibilityNotes: str | None = None


class UpdateLocationRequest(BaseModel):
    name: str | None = None
    type: LocationType | None = None
    lat: float | None = Field(default=None, ge=-90, le=90)
    lng: float | None = Field(default=None, ge=-180, le=180)
    address: str | None = None
    capacity: int | None = Field(default=None, ge=0)
    currentOccupancy: int | None = Field(default=None, ge=0)
    status: LocationStatus | None = None
    contactPhone: str | None = None
    accessibilityNotes: str | None = None


class CreateFactoryRequest(BaseModel):
    name: str
    location: str
    lat: float
    lng: float
    status: FactoryStatus
    riskLevel: RiskLevel
    waterProximity: int
    employees: int


class CreateSensorRequest(BaseModel):
    factoryId: str
    name: str
    type: str
    value: float
    unit: str
    threshold: float
    status: SensorStatus


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.discard(websocket)

    async def broadcast(self, event: str, payload: dict[str, Any]) -> None:
        stale: list[WebSocket] = []
        message = {"event": event, "payload": payload}
        for websocket in self.active_connections:
            try:
                await websocket.send_json(message)
            except RuntimeError:
                stale.append(websocket)
        for websocket in stale:
            self.disconnect(websocket)


manager = ConnectionManager()


def db() -> Iterator[sqlite3.Connection]:
    conn = connect()
    try:
        yield conn
    finally:
        conn.close()


@router.post("/auth/login")
def login(
    request: LoginRequest,
    conn: sqlite3.Connection = Depends(db),
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    user = conn.execute("SELECT * FROM users WHERE username = ?", (request.username,)).fetchone()
    if not user or user["password_hash"] != _password_hash(request.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    user_payload = {"id": user["id"], "username": user["username"], "role": user["role"]}
    return {"token": _create_token(user_payload, settings.jwt_secret), "user": user_payload}


@router.get("/alerts")
def get_alerts(
    status: AlertStatus | None = Query(None),
    severity: int | None = Query(None, ge=1, le=5),
    conn: sqlite3.Connection = Depends(db),
) -> dict[str, list[dict[str, Any]]]:
    sql = "SELECT * FROM alerts"
    filters: list[str] = []
    params: list[Any] = []
    if status:
        filters.append("status = ?")
        params.append(status)
    if severity:
        filters.append("severity = ?")
        params.append(severity)
    if filters:
        sql += " WHERE " + " AND ".join(filters)
    sql += " ORDER BY created_at DESC"
    return {"alerts": [_alert_from_row(row) for row in conn.execute(sql, params).fetchall()]}


@router.post("/alerts", status_code=201)
async def create_alert(
    request: CreateAlertRequest,
    conn: sqlite3.Connection = Depends(db),
) -> dict[str, Any]:
    now = utc_now_iso()
    alert_id = next_prefixed_id(conn, "alerts", "ALR")
    conn.execute(
        """
        INSERT INTO alerts (
            id, type, severity, status, title, message, affected_areas, created_at,
            updated_at, published_at, closed_at, created_by, broadcast_sent, recipient_count
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            alert_id,
            request.type,
            request.severity,
            "draft",
            request.title,
            request.message,
            json.dumps(request.affectedAreas),
            now,
            now,
            None,
            None,
            "Dispatcher Ionescu",
            0,
            0,
        ),
    )
    conn.commit()
    alert = _get_alert_or_404(conn, alert_id)
    await manager.broadcast("alert:new", alert)
    return alert


@router.patch("/alerts/{alert_id}/status")
async def update_alert_status(
    alert_id: str,
    request: UpdateAlertStatusRequest,
    conn: sqlite3.Connection = Depends(db),
) -> dict[str, Any]:
    _get_alert_or_404(conn, alert_id)
    now = utc_now_iso()
    closed_at = now if request.status == "closed" else None
    conn.execute(
        "UPDATE alerts SET status = ?, updated_at = ?, closed_at = COALESCE(?, closed_at) WHERE id = ?",
        (request.status, now, closed_at, alert_id),
    )
    conn.commit()
    alert = _get_alert_or_404(conn, alert_id)
    await manager.broadcast("alert:updated", alert)
    return alert


@router.post("/alerts/{alert_id}/broadcast")
async def broadcast_alert(
    alert_id: str,
    conn: sqlite3.Connection = Depends(db),
) -> dict[str, Any]:
    alert = _get_alert_or_404(conn, alert_id)
    now = utc_now_iso()
    recipient_count = _estimate_recipients(alert["affectedAreas"], alert["severity"])
    conn.execute(
        """
        UPDATE alerts
        SET status = 'published', updated_at = ?, published_at = ?, broadcast_sent = 1, recipient_count = ?
        WHERE id = ?
        """,
        (now, now, recipient_count, alert_id),
    )
    conn.execute(
        """
        UPDATE subscription_status
        SET alerts_sent = alerts_sent + 1
        WHERE id = 1
        """
    )
    conn.commit()
    updated = _get_alert_or_404(conn, alert_id)
    await manager.broadcast("alert:updated", updated)
    return {"success": True, "recipientCount": recipient_count, "publishedAt": now}


@router.get("/locations")
def get_locations(conn: sqlite3.Connection = Depends(db)) -> dict[str, list[dict[str, Any]]]:
    rows = conn.execute("SELECT * FROM safe_locations ORDER BY name").fetchall()
    return {"locations": [_location_from_row(row) for row in rows]}


@router.post("/locations", status_code=201)
async def create_location(
    request: CreateLocationRequest,
    conn: sqlite3.Connection = Depends(db),
) -> dict[str, Any]:
    now = utc_now_iso()
    location_id = next_prefixed_id(conn, "safe_locations", "SL")
    conn.execute(
        """
        INSERT INTO safe_locations (
            id, name, type, lat, lng, address, capacity, current_occupancy,
            status, contact_phone, accessibility_notes, last_updated
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            location_id,
            request.name,
            request.type,
            request.lat,
            request.lng,
            request.address,
            request.capacity,
            request.currentOccupancy,
            request.status,
            request.contactPhone,
            request.accessibilityNotes,
            now,
        ),
    )
    conn.commit()
    location = _get_location_or_404(conn, location_id)
    await manager.broadcast("location:occupancy_update", location)
    return location


@router.patch("/locations/{location_id}")
async def update_location(
    location_id: str,
    request: UpdateLocationRequest,
    conn: sqlite3.Connection = Depends(db),
) -> dict[str, Any]:
    _get_location_or_404(conn, location_id)
    updates = request.model_dump(exclude_unset=True)
    if not updates:
        return _get_location_or_404(conn, location_id)
    field_map = {
        "currentOccupancy": "current_occupancy",
        "contactPhone": "contact_phone",
        "accessibilityNotes": "accessibility_notes",
    }
    assignments = []
    params: list[Any] = []
    for field, value in updates.items():
        column = field_map.get(field, field)
        assignments.append(f"{column} = ?")
        params.append(value)
    assignments.append("last_updated = ?")
    params.append(utc_now_iso())
    params.append(location_id)
    conn.execute(f"UPDATE safe_locations SET {', '.join(assignments)} WHERE id = ?", params)
    conn.commit()
    location = _get_location_or_404(conn, location_id)
    await manager.broadcast("location:occupancy_update", location)
    return location


@router.delete("/locations/{location_id}")
def delete_location(location_id: str, conn: sqlite3.Connection = Depends(db)) -> dict[str, bool]:
    _get_location_or_404(conn, location_id)
    conn.execute("DELETE FROM safe_locations WHERE id = ?", (location_id,))
    conn.commit()
    return {"success": True}


@router.get("/satellite/water-levels")
def water_levels(conn: sqlite3.Connection = Depends(db)) -> list[dict[str, Any]]:
    rows = conn.execute("SELECT station, level, warning_level, critical_level, trend FROM water_levels").fetchall()
    return [
        {
            "station": row["station"],
            "level": row["level"],
            "warningLevel": row["warning_level"],
            "criticalLevel": row["critical_level"],
            "trend": row["trend"],
        }
        for row in rows
    ]


@router.get("/satellite/ndwi")
def ndwi(conn: sqlite3.Connection = Depends(db)) -> list[dict[str, Any]]:
    return [dict(row) for row in conn.execute("SELECT zone, value, risk FROM ndwi").fetchall()]


@router.get("/satellite/precipitation")
def precipitation(conn: sqlite3.Connection = Depends(db)) -> list[dict[str, Any]]:
    return [dict(row) for row in conn.execute("SELECT date, actual, forecast FROM precipitation").fetchall()]


@router.get("/satellite/galileo")
def galileo(conn: sqlite3.Connection = Depends(db)) -> list[dict[str, Any]]:
    return [dict(row) for row in conn.execute("SELECT id, name, status, signal FROM galileo_satellites").fetchall()]


@router.get("/satellite/heatmap")
def heatmap(conn: sqlite3.Connection = Depends(db)) -> list[dict[str, Any]]:
    rows = conn.execute("SELECT * FROM flood_heatmap").fetchall()
    result = []
    for row in rows:
        result.append({
            "id": row["id"],
            "zone": row["zone"],
            "lat": row["lat"],
            "lng": row["lng"],
            "intensity": row["intensity"],
            "polygon": json.loads(row["polygon"]),
            "riskLevel": row["risk_level"]
        })
    return result


@router.get("/industrial/factories")
def factories(conn: sqlite3.Connection = Depends(db)) -> dict[str, list[dict[str, Any]]]:
    rows = conn.execute("SELECT * FROM factories ORDER BY name").fetchall()
    return {"factories": [_factory_from_row(row) for row in rows]}


@router.post("/industrial/factories", status_code=201)
def create_factory(
    request: CreateFactoryRequest,
    conn: sqlite3.Connection = Depends(db),
) -> dict[str, Any]:
    now = utc_now_iso()
    factory_id = next_prefixed_id(conn, "factories", "F")
    conn.execute(
        """
        INSERT INTO factories (
            id, name, location, lat, lng, status, sensor_count, risk_level,
            water_proximity, last_inspection, employees
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            factory_id, request.name, request.location, request.lat, request.lng,
            request.status, 0, request.riskLevel, request.waterProximity,
            now, request.employees
        )
    )
    conn.commit()
    row = conn.execute("SELECT * FROM factories WHERE id = ?", (factory_id,)).fetchone()
    return _factory_from_row(row)


@router.get("/industrial/sensors")
def sensors(
    factoryId: str | None = Query(None),
    conn: sqlite3.Connection = Depends(db),
) -> dict[str, list[dict[str, Any]]]:
    if factoryId:
        rows = conn.execute("SELECT * FROM sensors WHERE factory_id = ? ORDER BY name", (factoryId,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM sensors ORDER BY factory_id, name").fetchall()
    return {"sensors": [_sensor_from_row(row) for row in rows]}


@router.post("/industrial/sensors", status_code=201)
def create_sensor(
    request: CreateSensorRequest,
    conn: sqlite3.Connection = Depends(db),
) -> dict[str, Any]:
    now = utc_now_iso()
    sensor_id = next_prefixed_id(conn, "sensors", "S")
    conn.execute(
        """
        INSERT INTO sensors (
            id, factory_id, name, type, value, unit, threshold, status, last_update
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            sensor_id, request.factoryId, request.name, request.type, request.value,
            request.unit, request.threshold, request.status, now
        )
    )
    conn.execute(
        "UPDATE factories SET sensor_count = sensor_count + 1 WHERE id = ?",
        (request.factoryId,)
    )
    conn.commit()
    row = conn.execute("SELECT * FROM sensors WHERE id = ?", (sensor_id,)).fetchone()
    return _sensor_from_row(row)


@router.get("/subscription/status")
def subscription_status(conn: sqlite3.Connection = Depends(db)) -> dict[str, Any]:
    row = conn.execute("SELECT * FROM subscription_status WHERE id = 1").fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Subscription status not configured")
    return {
        "currentTier": row["current_tier"],
        "usage": {
            "alertsSent": row["alerts_sent"],
            "locationsConfigured": row["locations_configured"],
            "sensorsConnected": row["sensors_connected"],
            "activeUsers": row["active_users"],
        },
    }


@router.websocket("/stream")
async def stream(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    try:
        await websocket.send_json({"event": "connected", "payload": {"stream": "hydralis"}})
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


def _get_alert_or_404(conn: sqlite3.Connection, alert_id: str) -> dict[str, Any]:
    row = conn.execute("SELECT * FROM alerts WHERE id = ?", (alert_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Alert not found")
    return _alert_from_row(row)


def _get_location_or_404(conn: sqlite3.Connection, location_id: str) -> dict[str, Any]:
    row = conn.execute("SELECT * FROM safe_locations WHERE id = ?", (location_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Safe location not found")
    return _location_from_row(row)


def _alert_from_row(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "type": row["type"],
        "severity": row["severity"],
        "status": row["status"],
        "title": row["title"],
        "message": row["message"],
        "affectedAreas": json.loads(row["affected_areas"]),
        "createdAt": row["created_at"],
        "updatedAt": row["updated_at"],
        "publishedAt": row["published_at"],
        "closedAt": row["closed_at"],
        "createdBy": row["created_by"],
        "broadcastSent": bool(row["broadcast_sent"]),
        "recipientCount": row["recipient_count"],
    }


def _location_from_row(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "name": row["name"],
        "type": row["type"],
        "lat": row["lat"],
        "lng": row["lng"],
        "address": row["address"],
        "capacity": row["capacity"],
        "currentOccupancy": row["current_occupancy"],
        "status": row["status"],
        "contactPhone": row["contact_phone"],
        "accessibilityNotes": row["accessibility_notes"],
        "lastUpdated": row["last_updated"],
    }


def _factory_from_row(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "name": row["name"],
        "location": row["location"],
        "lat": row["lat"],
        "lng": row["lng"],
        "status": row["status"],
        "sensorCount": row["sensor_count"],
        "riskLevel": row["risk_level"],
        "waterProximity": row["water_proximity"],
        "lastInspection": row["last_inspection"],
        "employees": row["employees"],
    }


def _sensor_from_row(row: sqlite3.Row) -> dict[str, Any]:
    value: float | int = row["value"]
    if float(value).is_integer():
        value = int(value)
    threshold: float | int = row["threshold"]
    if float(threshold).is_integer():
        threshold = int(threshold)
    return {
        "id": row["id"],
        "factoryId": row["factory_id"],
        "name": row["name"],
        "type": row["type"],
        "value": value,
        "unit": row["unit"],
        "threshold": threshold,
        "status": row["status"],
        "lastUpdate": row["last_update"],
    }


def _estimate_recipients(affected_areas: list[str], severity: int) -> int:
    base = max(len(affected_areas), 1) * 4200
    return base + severity * 850


def _password_hash(password: str) -> str:
    return hashlib.sha256(f"hydralis-demo:{password}".encode("utf-8")).hexdigest()


def _create_token(user: dict[str, Any], secret: str) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {**user, "iss": "hydralis-backend"}
    signing_input = ".".join(
        [
            _b64url(json.dumps(header, separators=(",", ":")).encode("utf-8")),
            _b64url(json.dumps(payload, separators=(",", ":")).encode("utf-8")),
        ]
    )
    signature = hmac.new(secret.encode("utf-8"), signing_input.encode("utf-8"), hashlib.sha256).digest()
    return f"{signing_input}.{_b64url(signature)}"


def _decode_token(token: str, secret: str) -> dict[str, Any]:
    try:
        header_b64, payload_b64, signature_b64 = token.split(".")
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc
    signing_input = f"{header_b64}.{payload_b64}"
    expected = hmac.new(secret.encode("utf-8"), signing_input.encode("utf-8"), hashlib.sha256).digest()
    actual = _b64url_decode(signature_b64)
    if not hmac.compare_digest(expected, actual):
        raise HTTPException(status_code=401, detail="Invalid token")
    try:
        return json.loads(_b64url_decode(payload_b64).decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc


def _b64url(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _b64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(f"{value}{padding}")
