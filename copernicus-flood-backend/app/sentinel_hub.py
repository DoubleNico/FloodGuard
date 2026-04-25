from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import httpx

from app.config import Settings
from app.exceptions import ExternalServiceError, MissingCredentialsError, NoSceneFoundError
from app.geo import bbox_from_area
from app.models import LatestSceneRequest, SatelliteScene
from app.time_utils import iso_z, parse_datetime, utcnow


class SentinelHubClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._client: httpx.AsyncClient | None = None
        self._token: str | None = None
        self._token_expires_at: datetime | None = None

    async def __aenter__(self) -> "SentinelHubClient":
        self._client = httpx.AsyncClient(timeout=self.settings.request_timeout_seconds)
        return self

    async def __aexit__(self, *_: object) -> None:
        if self._client is not None:
            await self._client.aclose()

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.settings.request_timeout_seconds)
        return self._client

    async def get_access_token(self) -> str:
        if (
            self._token
            and self._token_expires_at is not None
            and self._token_expires_at > utcnow() + timedelta(seconds=60)
        ):
            return self._token

        if not self.settings.cdse_client_id or not self.settings.cdse_client_secret:
            raise MissingCredentialsError(
                "Set CDSE_CLIENT_ID and CDSE_CLIENT_SECRET to call Copernicus Sentinel Hub APIs."
            )

        response = await self._send(
            "POST",
            self.settings.sentinel_hub_token_url,
            data={
                "grant_type": "client_credentials",
                "client_id": self.settings.cdse_client_id,
                "client_secret": self.settings.cdse_client_secret,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            authenticate=False,
        )
        payload = response.json()
        token = payload.get("access_token")
        if not token:
            raise ExternalServiceError("Token response did not include access_token")
        expires_in = int(payload.get("expires_in", 300))
        self._token = token
        self._token_expires_at = utcnow() + timedelta(seconds=expires_in)
        return token

    async def catalog_latest(self, request: LatestSceneRequest) -> list[SatelliteScene]:
        bbox = bbox_from_area(request.area)
        end = utcnow()
        start = end - timedelta(days=request.lookback_days)
        payload: dict[str, Any] = {
            "bbox": bbox.as_list(),
            "datetime": f"{iso_z(start)}/{iso_z(end)}",
            "collections": ["sentinel-1-grd"],
            "limit": min(max(request.limit, 1), 100),
            "filter": self._catalog_filter(
                request.acquisition_mode,
                request.polarization,
                request.orbit_direction,
            ),
        }
        data = await self.post_json("/catalog/v1/search", payload)
        scenes = [scene_from_stac_item(item) for item in data.get("features", [])]
        scenes = [scene for scene in scenes if scene.datetime is not None]
        scenes.sort(key=lambda scene: scene.datetime, reverse=True)
        if not scenes:
            raise NoSceneFoundError(
                "No Sentinel-1 GRD scenes found for the requested area and lookback window.",
                details={"lookback_days": request.lookback_days, "bbox": bbox.as_list()},
            )
        return scenes

    async def statistics(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self.post_json("/statistics/v1", payload)

    async def process_image(self, payload: dict[str, Any]) -> bytes:
        token = await self.get_access_token()
        response = await self._send(
            "POST",
            f"{self.settings.sentinel_hub_base_url}/process/v1",
            json=payload,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "image/png",
            },
        )
        return response.content

    async def post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        token = await self.get_access_token()
        response = await self._send(
            "POST",
            f"{self.settings.sentinel_hub_base_url}{path}",
            json=payload,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        )
        return response.json()

    async def _send(
        self,
        method: str,
        url: str,
        *,
        authenticate: bool = True,
        **kwargs: Any,
    ) -> httpx.Response:
        try:
            response = await self.client.request(method, url, **kwargs)
        except httpx.TimeoutException as exc:
            raise ExternalServiceError("Copernicus request timed out") from exc
        except httpx.HTTPError as exc:
            raise ExternalServiceError("Copernicus request failed", details={"error": str(exc)}) from exc

        if response.status_code >= 400:
            details: dict[str, Any] = {"status_code": response.status_code}
            try:
                details["body"] = response.json()
            except ValueError:
                details["body"] = response.text[:1000]
            if authenticate and response.status_code == 401:
                self._token = None
            raise ExternalServiceError("Copernicus API returned an error", details=details)
        return response

    @staticmethod
    def _catalog_filter(
        acquisition_mode: str,
        polarization: str,
        orbit_direction: str | None,
    ) -> str:
        filters = [
            f"sar:instrument_mode='{acquisition_mode}'",
            f"s1:polarization='{polarization}'",
        ]
        if orbit_direction:
            filters.append(f"sat:orbit_state='{orbit_direction.lower()}'")
        return " AND ".join(filters)


def scene_from_stac_item(item: dict[str, Any]) -> SatelliteScene:
    properties = item.get("properties", {})
    scene_datetime = (
        parse_datetime(properties.get("datetime"))
        or parse_datetime(properties.get("start_datetime"))
        or utcnow()
    )
    orbit = properties.get("sat:orbit_state")
    return SatelliteScene(
        id=item.get("id", ""),
        datetime=scene_datetime,
        start_datetime=parse_datetime(properties.get("start_datetime")),
        end_datetime=parse_datetime(properties.get("end_datetime")),
        platform=properties.get("platform"),
        acquisition_mode=properties.get("sar:instrument_mode"),
        polarization=properties.get("s1:polarization"),
        orbit_direction=orbit.upper() if isinstance(orbit, str) else orbit,
        bbox=item.get("bbox"),
    )
