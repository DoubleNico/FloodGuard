from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from typing import Any, Literal

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel, Field

from app.config import Settings, get_settings
from app.database import connect, next_prefixed_id, utc_now_iso
from app.efas import get_location_warnings
from app.exceptions import AppError, MissingCredentialsError
from app.flood import detect_flood
from app.hydralis import (
    _alert_from_row,
    _create_token,
    _decode_token,
    _estimate_recipients,
    _get_alert_or_404,
    _location_from_row,
    _password_hash,
    manager,
)
from app.models import AreaInput, CenterRadius, FloodDetectionRequest
from app.sentinel_hub import SentinelHubClient

router = APIRouter(prefix="/api", tags=["FloodGuard Mobile"])

MobileStatus = Literal["Safe", "Monitor", "Need Help", "Emergency"]


class SignUpRequest(BaseModel):
    full_name: str = Field(..., min_length=1)
    email: str = Field(..., pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(..., min_length=8)
    birthday: str = Field(..., min_length=1)
    primary_location: str = Field(..., min_length=1)
    safety_level: int = Field(..., ge=0, le=3)


class MobileLoginRequest(BaseModel):
    email: str = Field(..., pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str


class CurrentLocation(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)


class UserStatusRequest(BaseModel):
    user_id: str
    status: MobileStatus
    current_location: CurrentLocation
    timestamp: str | None = None


class TriggerAlertRequest(BaseModel):
    user_id: str | None = None
    current_location: CurrentLocation
    message: str = "Mobile emergency alert"


def db() -> Iterator[sqlite3.Connection]:
    conn = connect()
    try:
        yield conn
    finally:
        conn.close()


@router.post("/auth/signup", status_code=201)
def signup(
    request: SignUpRequest,
    conn: sqlite3.Connection = Depends(db),
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    existing = conn.execute("SELECT id FROM mobile_users WHERE lower(email) = lower(?)", (request.email,)).fetchone()
    if existing:
        raise HTTPException(status_code=400, detail="Email already in use")
    now = utc_now_iso()
    user_id = next_prefixed_id(conn, "mobile_users", "mob")
    conn.execute(
        """
        INSERT INTO mobile_users (
            id, full_name, email, password_hash, birthday, primary_location,
            safety_level, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            request.full_name,
            request.email,
            _password_hash(request.password),
            request.birthday,
            request.primary_location,
            request.safety_level,
            now,
            now,
        ),
    )
    conn.commit()
    user = _get_mobile_user_or_404(conn, user_id)
    return {
        "token": _create_token({"id": user["user_id"], "email": user["email"], "role": "mobile"}, settings.jwt_secret),
        "user_id": user["user_id"],
        "message": "Sign up successful",
        "user": user,
    }


@router.post("/auth/login")
def mobile_login(
    request: MobileLoginRequest,
    conn: sqlite3.Connection = Depends(db),
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    row = conn.execute("SELECT * FROM mobile_users WHERE lower(email) = lower(?)", (request.email,)).fetchone()
    if not row or row["password_hash"] != _password_hash(request.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    user = _mobile_user_from_row(row)
    return {
        "token": _create_token({"id": user["user_id"], "email": user["email"], "role": "mobile"}, settings.jwt_secret),
        "user": user,
    }


@router.get("/map/data")
async def map_data(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    radius: str = Query("10km"),
    conn: sqlite3.Connection = Depends(db),
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    radius_meters = parse_radius_meters(radius)
    safe_locations = [
        _location_from_row(row)
        for row in conn.execute("SELECT * FROM safe_locations ORDER BY name").fetchall()
        if distance_meters(lat, lng, row["lat"], row["lng"]) <= radius_meters
    ]
    active_alerts = [
        _alert_from_row(row)
        for row in conn.execute(
            "SELECT * FROM alerts WHERE status IN ('approved', 'published', 'updated') ORDER BY updated_at DESC"
        ).fetchall()
    ]
    efas_summary: dict[str, Any] | None = None
    try:
        efas_summary = await get_location_warnings(
            latitude=lat,
            longitude=lng,
            radius_meters=max(radius_meters, 5_000),
            settings=settings,
        )
    except AppError as exc:
        efas_summary = {"error": exc.message, "details": exc.details}

    flood_detection: dict[str, Any] | None = None
    async with SentinelHubClient(settings) as client:
        try:
            result = await detect_flood(
                FloodDetectionRequest(
                    area=AreaInput(
                        center=CenterRadius(
                            latitude=lat,
                            longitude=lng,
                            radius_meters=min(max(radius_meters, 500), 100_000),
                        )
                    ),
                    lookback_days=30,
                    baseline={"enabled": False},
                ),
                client,
            )
            flood_detection = result.model_dump(mode="json")
        except MissingCredentialsError as exc:
            flood_detection = {"error": exc.message}
        except AppError as exc:
            flood_detection = {"error": exc.message, "details": exc.details}

    return {
        "location": {"lat": lat, "lng": lng, "radius_meters": radius_meters},
        "safe_locations": safe_locations,
        "alerts": active_alerts,
        "flood_warning": {
            "copernicus": flood_detection,
            "efas": efas_summary,
        },
    }


@router.post("/user/status")
async def update_user_status(
    request: UserStatusRequest,
    conn: sqlite3.Connection = Depends(db),
) -> dict[str, Any]:
    _get_mobile_user_or_404(conn, request.user_id)
    status_id = next_prefixed_id(conn, "user_status_updates", "UST")
    timestamp = request.timestamp or utc_now_iso()
    now = utc_now_iso()
    conn.execute(
        """
        INSERT INTO user_status_updates (id, user_id, status, lat, lng, timestamp, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            status_id,
            request.user_id,
            request.status,
            request.current_location.lat,
            request.current_location.lng,
            timestamp,
            now,
        ),
    )
    conn.commit()
    payload = {
        "id": status_id,
        "user_id": request.user_id,
        "status": request.status,
        "current_location": request.current_location.model_dump(),
        "timestamp": timestamp,
    }
    if request.status in {"Emergency", "Need Help"}:
        await manager.broadcast("user:status_emergency", payload)
    else:
        await manager.broadcast("user:status_update", payload)
    return {"success": True, "status": payload}


@router.post("/alerts/trigger")
async def trigger_alert(
    request: TriggerAlertRequest,
    authorization: str | None = Header(None),
    conn: sqlite3.Connection = Depends(db),
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    token_payload = _require_bearer_token(authorization, settings)
    user_id = request.user_id or token_payload.get("id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token does not include a user id")
    _get_mobile_user_or_404(conn, str(user_id))
    now = utc_now_iso()
    trigger_id = next_prefixed_id(conn, "emergency_triggers", "EMG")
    conn.execute(
        """
        INSERT INTO emergency_triggers (id, user_id, lat, lng, message, created_at, acknowledged)
        VALUES (?, ?, ?, ?, ?, ?, 0)
        """,
        (
            trigger_id,
            str(user_id),
            request.current_location.lat,
            request.current_location.lng,
            request.message,
            now,
        ),
    )
    alert_id = next_prefixed_id(conn, "alerts", "ALR")
    affected_area = f"{request.current_location.lat:.5f},{request.current_location.lng:.5f}"
    conn.execute(
        """
        INSERT INTO alerts (
            id, type, severity, status, title, message, affected_areas, created_at,
            updated_at, published_at, closed_at, created_by, broadcast_sent, recipient_count
        ) VALUES (?, 'evacuation', 5, 'published', ?, ?, ?, ?, ?, ?, NULL, ?, 1, ?)
        """,
        (
            alert_id,
            "Mobile Emergency Alert",
            request.message,
            f'["{affected_area}"]',
            now,
            now,
            now,
            str(user_id),
            _estimate_recipients([affected_area], 5),
        ),
    )
    conn.commit()
    alert = _get_alert_or_404(conn, alert_id)
    payload = {
        "success": True,
        "alert_id": alert_id,
        "trigger_id": trigger_id,
        "broadcast": alert,
        "message": "Emergency alert triggered",
    }
    await manager.broadcast(
        "alert:mobile_emergency",
        {
            **payload,
            "location": request.current_location.model_dump(),
            "user_id": str(user_id),
        },
    )
    return payload


def parse_radius_meters(value: str) -> float:
    normalized = value.strip().lower()
    if normalized.endswith("km"):
        return float(normalized[:-2]) * 1000
    if normalized.endswith("m"):
        return float(normalized[:-1])
    return float(normalized)


def distance_meters(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    import math

    radius = 6_371_000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * radius * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _get_mobile_user_or_404(conn: sqlite3.Connection, user_id: str) -> dict[str, Any]:
    row = conn.execute("SELECT * FROM mobile_users WHERE id = ?", (user_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Mobile user not found")
    return _mobile_user_from_row(row)


def _mobile_user_from_row(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "user_id": row["id"],
        "full_name": row["full_name"],
        "email": row["email"],
        "birthday": row["birthday"],
        "primary_location": row["primary_location"],
        "safety_level": row["safety_level"],
    }


def _require_bearer_token(authorization: str | None, settings: Settings) -> dict[str, Any]:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="Expected Bearer token")
    payload = _decode_token(token, settings.jwt_secret)
    if payload.get("role") != "mobile":
        raise HTTPException(status_code=403, detail="Mobile token required")
    return payload
