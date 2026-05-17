from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Any

import json

from app.config import Settings, get_settings
from app.database import connect
from app.forecast import generate_forecast_snapshot, latest_snapshot


def _row_to_site_dict(row: Any) -> dict[str, Any]:
    return {
        "id": row["id"],
        "name": row["name"],
        "country": row["country"],
        "location": {"lat": row["lat"], "lng": row["lng"]},
        "footprint_geojson": json.loads(row["footprint_geojson"]) if row["footprint_geojson"] else None,
        "thresholds": json.loads(row["thresholds_json"]),
        "contacts": json.loads(row["contacts_json"]),
    }

logger = logging.getLogger(__name__)


def _is_fresh(generated_at: str, max_age_seconds: int) -> bool:
    try:
        ts = datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
    except ValueError:
        return False
    return datetime.now(timezone.utc) - ts < timedelta(seconds=max_age_seconds)


async def run_forecast_cycle(settings: Settings) -> dict[str, int]:
    """Iterate every site once, refreshing snapshots that are older than the
    configured fresh window. Returns a counters dict for logging.
    """
    counters = {"checked": 0, "refreshed": 0, "skipped": 0, "failed": 0}
    fresh_seconds = max(60, settings.forecast_interval_seconds // 2)

    with connect(settings) as conn:
        site_rows = conn.execute("SELECT * FROM sites").fetchall()
        sites = [_row_to_site_dict(row) for row in site_rows]

    for site in sites:
        counters["checked"] += 1
        try:
            with connect(settings) as conn:
                existing = latest_snapshot(conn, site["id"])
                if existing and _is_fresh(existing.generated_at, fresh_seconds):
                    counters["skipped"] += 1
                    continue
                await generate_forecast_snapshot(site, conn, settings)
                counters["refreshed"] += 1
        except Exception:  # noqa: BLE001 -- one bad site must not kill the cycle
            logger.exception("forecast cycle failed for site %s", site.get("id"))
            counters["failed"] += 1

    return counters


async def forecast_loop(settings: Settings, stop_event: asyncio.Event) -> None:
    """Repeat run_forecast_cycle every FORECAST_INTERVAL_SECONDS until stop."""
    interval = max(60, settings.forecast_interval_seconds)
    logger.info("[scheduler] starting forecast loop, interval=%ss", interval)
    while not stop_event.is_set():
        try:
            counters = await run_forecast_cycle(settings)
            logger.info("[scheduler] forecast cycle complete: %s", counters)
        except Exception:  # noqa: BLE001 -- defensive: never break the outer loop
            logger.exception("[scheduler] forecast cycle crashed")

        try:
            await asyncio.wait_for(stop_event.wait(), timeout=interval)
        except asyncio.TimeoutError:
            continue
    logger.info("[scheduler] forecast loop stopped")


def start_forecast_scheduler(settings: Settings | None = None) -> tuple[asyncio.Task[Any], asyncio.Event]:
    settings = settings or get_settings()
    stop_event = asyncio.Event()
    task = asyncio.create_task(forecast_loop(settings, stop_event), name="floodguard-forecast-scheduler")
    return task, stop_event
