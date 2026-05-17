from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv


load_dotenv()


def _split_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in value.split(",") if part.strip()]


@dataclass(frozen=True)
class Settings:
    app_name: str = "FloodGuard API"
    environment: str = os.getenv("ENVIRONMENT", "local")

    cdse_client_id: str | None = os.getenv("CDSE_CLIENT_ID")
    cdse_client_secret: str | None = os.getenv("CDSE_CLIENT_SECRET")

    sentinel_hub_base_url: str = os.getenv(
        "SENTINEL_HUB_BASE_URL", "https://sh.dataspace.copernicus.eu"
    ).rstrip("/")
    sentinel_hub_token_url: str = os.getenv(
        "SENTINEL_HUB_TOKEN_URL",
        "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token",
    )
    overpass_url: str = os.getenv(
        "OVERPASS_URL",
        "https://overpass-api.de/api/interpreter",
    )
    efas_wms_url: str = os.getenv(
        "EFAS_WMS_URL",
        "https://european-flood.emergency.copernicus.eu/api/wms/",
    )
    efas_wms_token: str | None = os.getenv("EFAS_WMS_TOKEN")
    glofas_api_key: str | None = os.getenv("GLOFAS_API_KEY")
    open_meteo_base_url: str = os.getenv(
        "OPEN_METEO_BASE_URL",
        "https://api.open-meteo.com/v1",
    ).rstrip("/")
    open_meteo_flood_base_url: str = os.getenv(
        "OPEN_METEO_FLOOD_BASE_URL",
        "https://flood-api.open-meteo.com/v1",
    ).rstrip("/")
    forecast_interval_seconds: int = int(os.getenv("FORECAST_INTERVAL_SECONDS", "1800"))
    forecast_scheduler_enabled: bool = os.getenv("FORECAST_SCHEDULER_ENABLED", "1") not in {"0", "false", "False"}

    request_timeout_seconds: float = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "45"))
    cors_origins: tuple[str, ...] = tuple(_split_csv(os.getenv("CORS_ORIGINS")) or ["*"])
    database_path: str = os.getenv("DATABASE_PATH", "floodguard.db")
    jwt_secret: str = os.getenv("JWT_SECRET", "change-this-dev-secret")


@lru_cache
def get_settings() -> Settings:
    return Settings()
