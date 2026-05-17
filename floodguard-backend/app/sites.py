from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.config import Settings, get_settings
from app.database import connect, utc_now_iso
from app.forecast import ForecastSnapshot, generate_forecast_snapshot, latest_snapshot
from app.scheduler import run_forecast_cycle

router = APIRouter(prefix="/api", tags=["sites"])


class SiteThresholds(BaseModel):
    precip_mm_24h: float = Field(60.0, ge=0)
    precip_mm_48h: float = Field(90.0, ge=0)
    efas_probability: float = Field(0.4, ge=0, le=1)
    glofas_probability: float = Field(0.4, ge=0, le=1)
    river_discharge_baseline_m3s: float | None = Field(
        None,
        ge=0,
        description=(
            "Long-term mean river discharge in m³/s for the nearest GloFAS cell. "
            "If set, used to convert forecast discharge into a flood probability."
        ),
    )


class SiteIn(BaseModel):
    name: str
    country: str
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    footprint_geojson: dict[str, Any] | None = None
    thresholds: SiteThresholds = Field(default_factory=SiteThresholds)
    contacts: list[str] = Field(default_factory=list)


class SitePatch(BaseModel):
    name: str | None = None
    country: str | None = None
    lat: float | None = Field(None, ge=-90, le=90)
    lng: float | None = Field(None, ge=-180, le=180)
    footprint_geojson: dict[str, Any] | None = None
    thresholds: SiteThresholds | None = None
    contacts: list[str] | None = None


def _row_to_site(row: Any) -> dict[str, Any]:
    return {
        "id": row["id"],
        "name": row["name"],
        "country": row["country"],
        "location": {"lat": row["lat"], "lng": row["lng"]},
        "footprint_geojson": json.loads(row["footprint_geojson"]) if row["footprint_geojson"] else None,
        "thresholds": json.loads(row["thresholds_json"]),
        "contacts": json.loads(row["contacts_json"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


@router.get("/sites")
def list_sites(settings: Settings = Depends(get_settings)) -> list[dict[str, Any]]:
    with connect(settings) as conn:
        rows = conn.execute("SELECT * FROM sites ORDER BY id ASC").fetchall()
        return [_row_to_site(row) for row in rows]


@router.post("/sites", status_code=201)
def create_site(payload: SiteIn, settings: Settings = Depends(get_settings)) -> dict[str, Any]:
    now = utc_now_iso()
    footprint = json.dumps(payload.footprint_geojson) if payload.footprint_geojson else None
    with connect(settings) as conn:
        cursor = conn.execute(
            """
            INSERT INTO sites (
                name, country, lat, lng, footprint_geojson, thresholds_json, contacts_json,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.name,
                payload.country,
                payload.lat,
                payload.lng,
                footprint,
                payload.thresholds.model_dump_json(),
                json.dumps(payload.contacts),
                now,
                now,
            ),
        )
        site_id = cursor.lastrowid
        row = conn.execute("SELECT * FROM sites WHERE id = ?", (site_id,)).fetchone()
    return _row_to_site(row)


@router.patch("/sites/{site_id}")
def update_site(
    site_id: int,
    payload: SitePatch,
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    with connect(settings) as conn:
        row = conn.execute("SELECT * FROM sites WHERE id = ?", (site_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="site not found")

        fields = payload.model_dump(exclude_unset=True)
        if not fields:
            return _row_to_site(row)

        updates: list[str] = []
        params: list[Any] = []
        if "name" in fields:
            updates.append("name = ?")
            params.append(payload.name)
        if "country" in fields:
            updates.append("country = ?")
            params.append(payload.country)
        if "lat" in fields:
            updates.append("lat = ?")
            params.append(payload.lat)
        if "lng" in fields:
            updates.append("lng = ?")
            params.append(payload.lng)
        if "footprint_geojson" in fields:
            updates.append("footprint_geojson = ?")
            params.append(json.dumps(payload.footprint_geojson) if payload.footprint_geojson else None)
        if "thresholds" in fields and payload.thresholds is not None:
            updates.append("thresholds_json = ?")
            params.append(payload.thresholds.model_dump_json())
        if "contacts" in fields and payload.contacts is not None:
            updates.append("contacts_json = ?")
            params.append(json.dumps(payload.contacts))

        updates.append("updated_at = ?")
        params.append(utc_now_iso())
        params.append(site_id)

        conn.execute(f"UPDATE sites SET {', '.join(updates)} WHERE id = ?", params)
        row = conn.execute("SELECT * FROM sites WHERE id = ?", (site_id,)).fetchone()
    return _row_to_site(row)


@router.delete("/sites/{site_id}", status_code=204)
def delete_site(site_id: int, settings: Settings = Depends(get_settings)) -> None:
    with connect(settings) as conn:
        cursor = conn.execute("DELETE FROM sites WHERE id = ?", (site_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="site not found")


@router.get("/sites/{site_id}/forecast")
async def site_forecast(
    site_id: int,
    refresh: bool = False,
    settings: Settings = Depends(get_settings),
) -> ForecastSnapshot:
    with connect(settings) as conn:
        row = conn.execute("SELECT * FROM sites WHERE id = ?", (site_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="site not found")
        site = _row_to_site(row)

        if refresh:
            snapshot = await generate_forecast_snapshot(site, conn, settings)
        else:
            snapshot = latest_snapshot(conn, site_id)
            if snapshot is None:
                snapshot = await generate_forecast_snapshot(site, conn, settings)
    return snapshot


@router.post("/forecast/run")
async def run_forecast_now(settings: Settings = Depends(get_settings)) -> dict[str, int]:
    """Manually run one forecast cycle across all sites. For ops/debugging."""
    return await run_forecast_cycle(settings)


_SIMULATION_PRESETS: dict[str, dict[str, Any]] = {
    "low": {
        "risk_score": 0.25,
        "risk_class": "low",
        "precip_mm_24h": 18.0,
        "precip_mm_48h": 32.0,
        "efas_probability": 0.18,
        "glofas_probability": 0.12,
        "river_discharge_max_m3s": 1100.0,
    },
    "medium": {
        "risk_score": 0.55,
        "risk_class": "medium",
        "precip_mm_24h": 42.0,
        "precip_mm_48h": 72.0,
        "efas_probability": 0.35,
        "glofas_probability": 0.32,
        "river_discharge_max_m3s": 2200.0,
    },
    "high": {
        "risk_score": 0.78,
        "risk_class": "high",
        "precip_mm_24h": 78.0,
        "precip_mm_48h": 132.0,
        "efas_probability": 0.62,
        "glofas_probability": 0.58,
        "river_discharge_max_m3s": 4100.0,
    },
    "extreme": {
        "risk_score": 0.94,
        "risk_class": "extreme",
        "precip_mm_24h": 142.0,
        "precip_mm_48h": 218.0,
        "efas_probability": 0.86,
        "glofas_probability": 0.82,
        "river_discharge_max_m3s": 6800.0,
    },
}


@router.post("/sites/{site_id}/simulate")
async def simulate_site(
    site_id: int,
    level: str = "high",
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    """Inject a synthetic forecast snapshot for demo/testing.

    `level` accepts: low, medium, high, extreme, reset. `reset` runs the real
    pipeline once for the site, replacing any synthetic state with live data.
    """
    from app.floodguard import manager
    from app.forecast import (
        ForecastDrivers,
        ForecastSnapshot,
        _inundation_polygon_for,
        generate_forecast_snapshot,
    )

    level_normalized = level.lower().strip()

    with connect(settings) as conn:
        row = conn.execute("SELECT * FROM sites WHERE id = ?", (site_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="site not found")
        site = _row_to_site(row)

        if level_normalized == "reset":
            snapshot = await generate_forecast_snapshot(site, conn, settings)
            return snapshot.model_dump()

        preset = _SIMULATION_PRESETS.get(level_normalized)
        if preset is None:
            raise HTTPException(
                status_code=422,
                detail=f"level must be one of {list(_SIMULATION_PRESETS) + ['reset']}",
            )

        baseline = site["thresholds"].get("river_discharge_baseline_m3s") or 1500.0
        drivers = ForecastDrivers(
            precip_mm_24h=preset["precip_mm_24h"],
            precip_mm_48h=preset["precip_mm_48h"],
            efas_probability=preset["efas_probability"],
            glofas_probability=preset["glofas_probability"],
            river_discharge_max_m3s=preset["river_discharge_max_m3s"],
            river_discharge_baseline_m3s=baseline,
        )
        inundation = _inundation_polygon_for(site, preset["risk_score"])
        snapshot = ForecastSnapshot(
            site_id=site_id,
            generated_at=utc_now_iso(),
            horizon_hours=48,
            risk_score=preset["risk_score"],
            risk_class=preset["risk_class"],
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

    await manager.broadcast(
        "forecast:updated",
        {
            "site_id": site_id,
            "site_name": site["name"],
            "risk_class": snapshot.risk_class,
            "risk_score": snapshot.risk_score,
            "generated_at": snapshot.generated_at,
            "simulated": True,
        },
    )

    if snapshot.risk_class in {"high", "extreme"}:
        await manager.broadcast(
            "alert:new",
            {
                "id": f"sim-{site_id}-{snapshot.generated_at}",
                "site_id": site_id,
                "title": f"[DEMO] {snapshot.risk_class.upper()} flood risk at {site['name']}",
                "message": (
                    f"Simulated event. 48h precipitation: "
                    f"{snapshot.drivers.precip_mm_48h:.0f} mm. "
                    f"Risk score {snapshot.risk_score:.2f}. Evacuate now."
                ),
                "risk_class": snapshot.risk_class,
                "risk_score": snapshot.risk_score,
                "generated_at": snapshot.generated_at,
                "simulated": True,
            },
        )

    return snapshot.model_dump()


@router.get("/sites/{site_id}/inundation.geojson")
def site_inundation(
    site_id: int,
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    with connect(settings) as conn:
        snapshot = latest_snapshot(conn, site_id)
    if snapshot is None or snapshot.inundation_geojson is None:
        return {"type": "FeatureCollection", "features": []}
    return snapshot.inundation_geojson
