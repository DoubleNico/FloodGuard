from __future__ import annotations

import json
import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.config import Settings, get_settings
from app.database import connect, utc_now_iso

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/push", tags=["push"])


class PushRegisterIn(BaseModel):
    token: str = Field(..., min_length=10)
    site_ids: list[int] = Field(default_factory=list)
    platform: str = Field("android")
    mobile_user_id: str | None = None


def _row_to_token(row: Any) -> dict[str, Any]:
    return {
        "id": row["id"],
        "token": row["token"],
        "platform": row["platform"],
        "mobile_user_id": row["mobile_user_id"],
        "site_ids": json.loads(row["site_ids_json"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


@router.post("/register", status_code=201)
def register_push_token(
    payload: PushRegisterIn,
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    """Persist a device push token. Currently used as a registry only — push
    delivery is handled in-app via the WebSocket stream + flutter_local_notifications.
    The endpoint is kept so a future push provider (ntfy, OneSignal, FCM) can
    consume the registry without a mobile-side migration.
    """
    now = utc_now_iso()
    site_ids_json = json.dumps(payload.site_ids)
    with connect(settings) as conn:
        existing = conn.execute("SELECT * FROM push_tokens WHERE token = ?", (payload.token,)).fetchone()
        if existing:
            conn.execute(
                """
                UPDATE push_tokens
                SET site_ids_json = ?, platform = ?, mobile_user_id = ?, updated_at = ?
                WHERE token = ?
                """,
                (site_ids_json, payload.platform, payload.mobile_user_id, now, payload.token),
            )
        else:
            conn.execute(
                """
                INSERT INTO push_tokens (
                    token, platform, mobile_user_id, site_ids_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (payload.token, payload.platform, payload.mobile_user_id, site_ids_json, now, now),
            )
        row = conn.execute("SELECT * FROM push_tokens WHERE token = ?", (payload.token,)).fetchone()
    return _row_to_token(row)


@router.delete("/register/{token}", status_code=204)
def unregister_push_token(
    token: str,
    settings: Settings = Depends(get_settings),
) -> None:
    with connect(settings) as conn:
        cursor = conn.execute("DELETE FROM push_tokens WHERE token = ?", (token,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="token not found")


def tokens_for_site(conn: Any, site_id: int) -> list[str]:
    rows = conn.execute("SELECT token, site_ids_json FROM push_tokens").fetchall()
    matches: list[str] = []
    for row in rows:
        site_ids = json.loads(row["site_ids_json"]) or []
        if not site_ids or site_id in site_ids:
            matches.append(row["token"])
    return matches
