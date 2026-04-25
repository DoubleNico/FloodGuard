from __future__ import annotations

from collections.abc import AsyncIterator

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import Settings, get_settings
from app.exceptions import AppError
from app.flood import detect_flood
from app.models import FloodDetectionRequest, FloodDetectionResponse, LatestSceneRequest, SatelliteScene
from app.sentinel_hub import SentinelHubClient

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="HTTP API for Sentinel-1 flood screening using Copernicus Data Space Ecosystem.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials="*" not in settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def copernicus_client(
    settings_dependency: Settings = Depends(get_settings),
) -> AsyncIterator[SentinelHubClient]:
    async with SentinelHubClient(settings_dependency) as client:
        yield client


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


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


def _http_error(exc: AppError) -> HTTPException:
    return HTTPException(
        status_code=exc.status_code,
        detail={
            "error": exc.error_code,
            "message": exc.message,
            "details": exc.details,
        },
    )
