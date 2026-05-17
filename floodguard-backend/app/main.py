from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response

from app.admin_boundaries import DEFAULT_ADMIN_LEVELS, fetch_admin_boundaries
from app.config import Settings, get_settings
from app.database import initialize_database
from app.efas import EfasMapRequest, get_efas_layers, get_location_warnings, get_map_png
from app.exceptions import AppError
from app.flood import build_heatmap_png, detect_flood
from app.floodguard import router as floodguard_router
from app.map_page import MAP_HTML
from app.mobile import router as mobile_router
from app.push import router as push_router
from app.scheduler import start_forecast_scheduler
from app.sites import router as sites_router
from app.models import (
    AreaInput,
    CenterRadius,
    FloodDetectionRequest,
    FloodDetectionResponse,
    FloodHeatmapRequest,
    LatestSceneRequest,
    SatelliteScene,
)
from app.sentinel_hub import SentinelHubClient

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    initialize_database(settings)
    scheduler_task = None
    stop_event = None
    if settings.forecast_scheduler_enabled:
        scheduler_task, stop_event = start_forecast_scheduler(settings)
    try:
        yield
    finally:
        if stop_event is not None:
            stop_event.set()
        if scheduler_task is not None:
            try:
                await scheduler_task
            except Exception:  # noqa: BLE001 -- shutdown should not raise
                pass


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description=(
        "FloodGuard backend. Aggregates Open-Meteo, EFAS, GloFAS, and Copernicus "
        "Sentinel-1 data into per-site 48h flood-risk forecasts and pushes alerts "
        "to the FloodGuard mobile app."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials="*" not in settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(floodguard_router)
app.include_router(mobile_router)
app.include_router(sites_router)
app.include_router(push_router)


async def copernicus_client(
    settings_dependency: Settings = Depends(get_settings),
) -> AsyncIterator[SentinelHubClient]:
    async with SentinelHubClient(settings_dependency) as client:
        yield client


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/map", response_class=HTMLResponse)
async def flood_map() -> HTMLResponse:
    return HTMLResponse(MAP_HTML)


@app.get("/v1/config")
async def config(settings_dependency: Settings = Depends(get_settings)) -> dict[str, object]:
    return {
        "environment": settings_dependency.environment,
        "sentinel_hub_base_url": settings_dependency.sentinel_hub_base_url,
        "credentials_configured": bool(
            settings_dependency.cdse_client_id and settings_dependency.cdse_client_secret
        ),
    }


@app.post("/v1/catalog/latest", response_model=list[SatelliteScene])
async def latest_scenes(
    request: LatestSceneRequest,
    client: SentinelHubClient = Depends(copernicus_client),
) -> list[SatelliteScene]:
    try:
        return await client.catalog_latest(request)
    except AppError as exc:
        raise _http_error(exc) from exc


@app.post("/v1/flood/detect", response_model=FloodDetectionResponse)
async def flood_detect(
    request: FloodDetectionRequest,
    client: SentinelHubClient = Depends(copernicus_client),
) -> FloodDetectionResponse:
    try:
        return await detect_flood(request, client)
    except AppError as exc:
        raise _http_error(exc) from exc


@app.get("/v1/flood/heatmap.png")
async def flood_heatmap_png(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    radius_meters: float = Query(1_000, gt=0, le=100_000),
    lookback_days: int = Query(30, ge=1, le=180),
    water_threshold_db: float = Query(-17.0, ge=-30, le=-5),
    width: int = Query(768, ge=64, le=2048),
    height: int = Query(768, ge=64, le=2048),
    client: SentinelHubClient = Depends(copernicus_client),
) -> Response:
    request = FloodHeatmapRequest(
        area=AreaInput(
            center=CenterRadius(
                latitude=latitude,
                longitude=longitude,
                radius_meters=radius_meters,
            )
        ),
        lookback_days=lookback_days,
        water_threshold_db=water_threshold_db,
        width=width,
        height=height,
    )
    try:
        image, latest_scene = await build_heatmap_png(request, client)
    except AppError as exc:
        raise _http_error(exc) from exc
    return Response(
        content=image,
        media_type="image/png",
        headers={
            "Cache-Control": "no-store",
            "X-Sentinel-Scene-Id": latest_scene.id,
            "X-Sentinel-Scene-Datetime": latest_scene.datetime.isoformat(),
        },
    )


@app.get("/v1/admin/boundaries")
async def admin_boundaries(
    west: float = Query(..., ge=-180, le=180),
    south: float = Query(..., ge=-90, le=90),
    east: float = Query(..., ge=-180, le=180),
    north: float = Query(..., ge=-90, le=90),
    admin_levels: str = Query(",".join(DEFAULT_ADMIN_LEVELS)),
    settings_dependency: Settings = Depends(get_settings),
) -> dict[str, object]:
    if west >= east or south >= north:
        raise HTTPException(status_code=422, detail="west/east or south/north bounds are invalid")
    if east - west > 5 or north - south > 5:
        raise HTTPException(status_code=422, detail="administrative boundary bbox is too large")
    levels = tuple(
        level.strip()
        for level in admin_levels.split(",")
        if level.strip().isdigit() and 2 <= int(level.strip()) <= 10
    )
    try:
        return await fetch_admin_boundaries(
            west=west,
            south=south,
            east=east,
            north=north,
            admin_levels=levels or DEFAULT_ADMIN_LEVELS,
            settings=settings_dependency,
        )
    except AppError as exc:
        raise _http_error(exc) from exc


@app.get("/v1/efas/layers")
async def efas_layers(
    settings_dependency: Settings = Depends(get_settings),
) -> dict[str, object]:
    try:
        return await get_efas_layers(settings_dependency)
    except AppError as exc:
        raise _http_error(exc) from exc


@app.get("/v1/efas/location")
async def efas_location(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    radius_meters: float = Query(50_000, gt=1_000, le=250_000),
    settings_dependency: Settings = Depends(get_settings),
) -> dict[str, object]:
    try:
        return await get_location_warnings(
            latitude=latitude,
            longitude=longitude,
            radius_meters=radius_meters,
            settings=settings_dependency,
        )
    except AppError as exc:
        raise _http_error(exc) from exc


@app.get("/v1/efas/map.png")
async def efas_map_png(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    radius_meters: float = Query(50_000, gt=1_000, le=250_000),
    layer: str = Query("mapserver:MIC2"),
    width: int = Query(768, ge=64, le=2048),
    height: int = Query(768, ge=64, le=2048),
    time: str | None = Query(None),
    settings_dependency: Settings = Depends(get_settings),
) -> Response:
    try:
        image = await get_map_png(
            EfasMapRequest(
                latitude=latitude,
                longitude=longitude,
                radius_meters=radius_meters,
                layer=layer,
                width=width,
                height=height,
                time=time,
            ),
            settings_dependency,
        )
    except AppError as exc:
        raise _http_error(exc) from exc
    return Response(
        content=image,
        media_type="image/png",
        headers={"Cache-Control": "no-store", "X-EFAS-Layer": layer},
    )


def _http_error(exc: AppError) -> HTTPException:
    return HTTPException(
        status_code=exc.status_code,
        detail={
            "error": exc.error_code,
            "message": exc.message,
            "details": exc.details,
        },
    )
