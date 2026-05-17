from __future__ import annotations

import json
import logging
import math
import sqlite3
from typing import Any

import httpx
from pydantic import BaseModel

from app.config import Settings, get_settings
from app.database import utc_now_iso

logger = logging.getLogger(__name__)


class ForecastDrivers(BaseModel):
    precip_mm_24h: float | None = None
    precip_mm_48h: float | None = None
    efas_probability: float | None = None
    glofas_probability: float | None = None
    river_discharge_max_m3s: float | None = None
    river_discharge_baseline_m3s: float | None = None


class ForecastSnapshot(BaseModel):
    site_id: int
    generated_at: str
    horizon_hours: int
    risk_score: float
    risk_class: str
    drivers: ForecastDrivers
    inundation_geojson: dict[str, Any] | None = None


_RISK_CLASSES: tuple[tuple[float, str], ...] = (
    (0.85, "extreme"),
    (0.65, "high"),
    (0.4, "medium"),
    (0.15, "low"),
    (0.0, "minimal"),
)


def _classify(score: float) -> str:
    for threshold, label in _RISK_CLASSES:
        if score >= threshold:
            return label
    return "minimal"


async def fetch_open_meteo_precip(
    lat: float,
    lng: float,
    settings: Settings,
) -> tuple[float | None, float | None]:
    url = f"{settings.open_meteo_base_url}/forecast"
    params = {
        "latitude": lat,
        "longitude": lng,
        "hourly": "precipitation",
        "forecast_days": 3,
        "timezone": "UTC",
    }
    try:
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            payload = response.json()
    except httpx.HTTPError as exc:
        logger.warning("open-meteo fetch failed for %s,%s: %s", lat, lng, exc)
        return None, None

    hourly = payload.get("hourly") or {}
    precip = hourly.get("precipitation") or []
    if not precip:
        return None, None

    next_24h = sum(precip[:24])
    next_48h = sum(precip[:48])
    return float(next_24h), float(next_48h)


async def fetch_glofas_discharge(
    lat: float,
    lng: float,
    settings: Settings,
) -> tuple[float | None, float | None]:
    """Fetch GloFAS river-discharge forecast via Open-Meteo Flood API.

    Returns (max_discharge_m3s_next_2d, mean_baseline_m3s_30d) or (None, None).
    The Flood API is keyless and proxies the official GloFAS dataset.
    """
    url = f"{settings.open_meteo_flood_base_url}/flood"
    params = {
        "latitude": lat,
        "longitude": lng,
        "daily": "river_discharge,river_discharge_max,river_discharge_mean",
        "forecast_days": 30,
        "past_days": 0,
    }
    try:
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            payload = response.json()
    except httpx.HTTPError as exc:
        logger.warning("GloFAS (open-meteo flood) fetch failed for %s,%s: %s", lat, lng, exc)
        return None, None

    daily = payload.get("daily") or {}
    discharge_max = daily.get("river_discharge_max") or daily.get("river_discharge") or []
    discharge_mean = daily.get("river_discharge_mean") or daily.get("river_discharge") or []

    discharge_max = [v for v in discharge_max if isinstance(v, (int, float))]
    discharge_mean = [v for v in discharge_mean if isinstance(v, (int, float))]

    if not discharge_max:
        return None, None

    next_48h_max = max(discharge_max[:2]) if len(discharge_max) >= 2 else float(discharge_max[0])
    baseline_30d = (
        sum(discharge_mean) / len(discharge_mean) if discharge_mean else None
    )
    return float(next_48h_max), (float(baseline_30d) if baseline_30d is not None else None)


def _glofas_probability(
    forecast_max: float | None,
    site_baseline: float | None,
    fetched_baseline: float | None,
) -> float | None:
    """Convert forecast discharge into a 0-1 flood probability proxy.

    Uses the site-configured baseline if present, otherwise the rolling 30-day
    mean returned by the Flood API. Probability ramps from 0 at 1.0× baseline
    to 1.0 at 3.0× baseline (typical bankfull-to-major-flood ratio).
    """
    if forecast_max is None:
        return None
    baseline = site_baseline or fetched_baseline
    if not baseline or baseline <= 0:
        return None
    ratio = forecast_max / baseline
    if ratio <= 1.0:
        return 0.0
    if ratio >= 3.0:
        return 1.0
    return round((ratio - 1.0) / 2.0, 3)


async def fetch_efas_probability(
    lat: float,
    lng: float,
    settings: Settings,
) -> float | None:
    """Stub: real implementation would proxy to app.efas.get_location_warnings.

    Returns None if EFAS is unreachable. Replace with a real probability extracted
    from EFAS feature-info once the WMS feature mapping is wired through the
    forecast pipeline.
    """
    try:
        from app.efas import get_location_warnings

        result = await get_location_warnings(
            latitude=lat,
            longitude=lng,
            radius_meters=50_000,
            settings=settings,
        )
    except Exception as exc:  # noqa: BLE001 -- defensive aggregation
        logger.warning("EFAS lookup failed for %s,%s: %s", lat, lng, exc)
        return None

    layers = result.get("layers") or []
    probabilities: list[float] = []
    for layer in layers:
        score = layer.get("probability") or layer.get("value")
        if isinstance(score, (int, float)):
            probabilities.append(float(score))
    if not probabilities:
        return None
    return max(probabilities)


def _compose_risk(
    drivers: ForecastDrivers,
    thresholds: dict[str, float],
) -> float:
    components: list[float] = []
    if drivers.precip_mm_24h is not None and thresholds.get("precip_mm_24h"):
        components.append(min(1.0, drivers.precip_mm_24h / thresholds["precip_mm_24h"]))
    if drivers.precip_mm_48h is not None and thresholds.get("precip_mm_48h"):
        components.append(min(1.0, drivers.precip_mm_48h / thresholds["precip_mm_48h"]))
    if drivers.efas_probability is not None:
        components.append(min(1.0, drivers.efas_probability / max(thresholds.get("efas_probability", 0.4), 0.05)))
    if drivers.glofas_probability is not None:
        components.append(
            min(1.0, drivers.glofas_probability / max(thresholds.get("glofas_probability", 0.4), 0.05))
        )

    if not components:
        return 0.0

    return min(1.0, sum(components) / len(components))


def _inundation_polygon_for(site: dict[str, Any], risk_score: float) -> dict[str, Any] | None:
    """Approximate inundation polygon centered on the site as a circle whose
    radius scales with the risk score. Replace with a real polygon derived from
    EFAS/GloFAS rasters intersected with the site's terrain footprint.
    """
    if risk_score < 0.15:
        return None

    radius_m = 200 + risk_score * 1500
    lat = site["location"]["lat"]
    lng = site["location"]["lng"]

    points: list[list[float]] = []
    n = 32
    for i in range(n):
        theta = 2 * math.pi * i / n
        d_lat = (radius_m * math.cos(theta)) / 111_320.0
        d_lng = (radius_m * math.sin(theta)) / (111_320.0 * max(0.1, math.cos(math.radians(lat))))
        points.append([lng + d_lng, lat + d_lat])
    points.append(points[0])

    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"risk_class": _classify(risk_score), "risk_score": risk_score},
                "geometry": {"type": "Polygon", "coordinates": [points]},
            }
        ],
    }


def latest_snapshot(conn: sqlite3.Connection, site_id: int) -> ForecastSnapshot | None:
    row = conn.execute(
        """
        SELECT id, site_id, generated_at, horizon_hours, risk_score, risk_class,
               drivers_json, inundation_geojson
        FROM forecast_snapshots
        WHERE site_id = ?
        ORDER BY generated_at DESC
        LIMIT 1
        """,
        (site_id,),
    ).fetchone()
    if row is None:
        return None
    return ForecastSnapshot(
        site_id=row["site_id"],
        generated_at=row["generated_at"],
        horizon_hours=row["horizon_hours"],
        risk_score=row["risk_score"],
        risk_class=row["risk_class"],
        drivers=ForecastDrivers(**json.loads(row["drivers_json"])),
        inundation_geojson=json.loads(row["inundation_geojson"]) if row["inundation_geojson"] else None,
    )


async def generate_forecast_snapshot(
    site: dict[str, Any],
    conn: sqlite3.Connection,
    settings: Settings | None = None,
) -> ForecastSnapshot:
    settings = settings or get_settings()

    lat = site["location"]["lat"]
    lng = site["location"]["lng"]
    thresholds = site["thresholds"]

    precip_24h, precip_48h = await fetch_open_meteo_precip(lat, lng, settings)
    efas_prob = await fetch_efas_probability(lat, lng, settings)
    discharge_max, baseline = await fetch_glofas_discharge(lat, lng, settings)

    site_baseline = thresholds.get("river_discharge_baseline_m3s")
    glofas_prob = _glofas_probability(discharge_max, site_baseline, baseline)

    drivers = ForecastDrivers(
        precip_mm_24h=precip_24h,
        precip_mm_48h=precip_48h,
        efas_probability=efas_prob,
        glofas_probability=glofas_prob,
        river_discharge_max_m3s=discharge_max,
        river_discharge_baseline_m3s=site_baseline or baseline,
    )

    score = _compose_risk(drivers, thresholds)
    risk_class = _classify(score)
    inundation = _inundation_polygon_for(site, score)

    snapshot = ForecastSnapshot(
        site_id=site["id"],
        generated_at=utc_now_iso(),
        horizon_hours=48,
        risk_score=round(score, 3),
        risk_class=risk_class,
        drivers=drivers,
        inundation_geojson=inundation,
    )

    conn.execute(
        """
        INSERT INTO forecast_snapshots (
            site_id, generated_at, horizon_hours, risk_score, risk_class,
            drivers_json, inundation_geojson
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            snapshot.site_id,
            snapshot.generated_at,
            snapshot.horizon_hours,
            snapshot.risk_score,
            snapshot.risk_class,
            snapshot.drivers.model_dump_json(),
            json.dumps(snapshot.inundation_geojson) if snapshot.inundation_geojson else None,
        ),
    )

    from app.floodguard import manager

    await manager.broadcast(
        "forecast:updated",
        {
            "site_id": site["id"],
            "site_name": site["name"],
            "risk_class": snapshot.risk_class,
            "risk_score": snapshot.risk_score,
            "generated_at": snapshot.generated_at,
        },
    )

    if snapshot.risk_class in {"high", "extreme"}:
        await manager.broadcast(
            "alert:new",
            {
                "id": f"forecast-{site['id']}-{snapshot.generated_at}",
                "site_id": site["id"],
                "title": f"{snapshot.risk_class.upper()} flood risk at {site['name']}",
                "message": (
                    f"48h precipitation: {snapshot.drivers.precip_mm_48h or 0:.0f} mm. "
                    f"Risk score: {snapshot.risk_score:.2f}."
                ),
                "risk_class": snapshot.risk_class,
                "risk_score": snapshot.risk_score,
                "generated_at": snapshot.generated_at,
            },
        )

    return snapshot
