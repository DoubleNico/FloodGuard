from __future__ import annotations

import asyncio
from dataclasses import dataclass
from html import unescape
from typing import Any
from urllib.parse import urlencode
import json
import re
import xml.etree.ElementTree as ET

import httpx

from app.config import Settings
from app.exceptions import ExternalServiceError
from app.external_response_logging import log_external_response
from app.geo import bbox_from_center

EFAS_FORECAST_LAYERS = [
    {
        "id": "threshold_ongoing",
        "layer": "mapserver:MIC1",
        "title": "Threshold level exceedance ongoing",
        "category": "river_threshold_exceedance",
    },
    {
        "id": "threshold_1_2_days",
        "layer": "mapserver:MIC2",
        "title": "Threshold level exceedance 1-2 days",
        "category": "river_threshold_exceedance",
    },
    {
        "id": "threshold_3_5_days",
        "layer": "mapserver:MIC3",
        "title": "Threshold level exceedance 3-5 days",
        "category": "river_threshold_exceedance",
    },
    {
        "id": "threshold_gt_5_days",
        "layer": "mapserver:MIC4",
        "title": "Threshold level exceedance > 5 days",
        "category": "river_threshold_exceedance",
    },
    {
        "id": "flood_probability",
        "layer": "mapserver:persistence",
        "title": "Flood probability",
        "category": "flood_probability",
    },
    {
        "id": "rapid_flood_mapping",
        "layer": "mapserver:RapidFloodMapping",
        "title": "Rapid Flood Mapping",
        "category": "impact_extent",
    },
    {
        "id": "flash_flood_0_5h",
        "layer": "mapserver:impact1_max0-6_catchSummary",
        "title": "Radar-based River Flash Flood Impact 0-5h",
        "category": "flash_flood_impact",
    },
    {
        "id": "flash_flood_6_24h",
        "layer": "mapserver:impact1_max7-24_catchSummary",
        "title": "Radar-based River Flash Flood Impact 6-24h",
        "category": "flash_flood_impact",
    },
    {
        "id": "flash_flood_25_48h",
        "layer": "mapserver:impact1_max25-48_catchSummary",
        "title": "Radar-based River Flash Flood Impact 25-48h",
        "category": "flash_flood_impact",
    },
]


@dataclass(frozen=True)
class EfasMapRequest:
    latitude: float
    longitude: float
    radius_meters: float
    layer: str
    width: int
    height: int
    time: str | None = None


async def get_efas_layers(settings: Settings) -> dict[str, Any]:
    capabilities = await _wms_get(
        settings,
        {
            "SERVICE": "WMS",
            "REQUEST": "GetCapabilities",
            "VERSION": "1.3.0",
        },
        accept="text/xml",
    )
    parsed_layers = parse_wms_layers(capabilities.text)
    useful_layers = [
        {
            **layer,
            "available": any(parsed["name"] == layer["layer"] for parsed in parsed_layers),
        }
        for layer in EFAS_FORECAST_LAYERS
    ]
    return {
        "service": "EFAS WMS",
        "realtime_access": "restricted_to_authorised_efas_partners",
        "public_access_note": (
            "Public EFAS WMS exposes limited and non-real-time layers. Configure EFAS_WMS_TOKEN "
            "for authorised partner access to real-time forecasts."
        ),
        "token_configured": bool(settings.efas_wms_token),
        "layers": useful_layers,
    }


async def get_location_warnings(
    *,
    latitude: float,
    longitude: float,
    radius_meters: float,
    settings: Settings,
) -> dict[str, Any]:
    bbox = bbox_from_center(latitude, longitude, radius_meters)

    async def fetch_layer(layer: dict[str, Any]) -> dict[str, Any]:
        info = await get_feature_info(
            request=EfasMapRequest(
                latitude=latitude,
                longitude=longitude,
                radius_meters=radius_meters,
                layer=layer["layer"],
                width=101,
                height=101,
            ),
            settings=settings,
        )
        return {
            **layer,
            "feature_info": info,
            "has_signal": bool(info.get("items")),
        }

    layer_results = await asyncio.gather(
        *[fetch_layer(layer) for layer in EFAS_FORECAST_LAYERS],
        return_exceptions=False,
    )
    return {
        "location": {"latitude": latitude, "longitude": longitude, "radius_meters": radius_meters},
        "bbox": bbox.as_list(),
        "source": "EFAS WMS",
        "access_note": (
            "EFAS real-time forecasts and formal early warnings are restricted to authorised EFAS partners. "
            "Without EFAS_WMS_TOKEN this endpoint uses public limited/non-real-time WMS access."
        ),
        "token_configured": bool(settings.efas_wms_token),
        "layers": list(layer_results),
    }


async def get_map_png(request: EfasMapRequest, settings: Settings) -> bytes:
    response = await _wms_get(
        settings,
        build_get_map_params(request),
        accept="image/png",
    )
    content_type = response.headers.get("content-type", "")
    if "image" not in content_type:
        raise ExternalServiceError(
            "EFAS WMS did not return an image",
            details={"content_type": content_type, "body": response.text[:1000]},
        )
    return response.content


async def get_feature_info(request: EfasMapRequest, settings: Settings) -> dict[str, Any]:
    params = build_get_map_params(request)
    params.update(
        {
            "REQUEST": "GetFeatureInfo",
            "QUERY_LAYERS": request.layer,
            "INFO_FORMAT": "text/html",
            "X": str(request.width // 2),
            "Y": str(request.height // 2),
        }
    )
    response = await _wms_get(settings, params, accept="text/html")
    return parse_feature_info(response.text)


def build_get_map_params(request: EfasMapRequest) -> dict[str, str]:
    bbox = bbox_from_center(request.latitude, request.longitude, request.radius_meters)
    params = {
        "SERVICE": "WMS",
        "VERSION": "1.1.1",
        "REQUEST": "GetMap",
        "LAYERS": request.layer,
        "STYLES": "",
        "SRS": "EPSG:4326",
        "BBOX": ",".join(str(value) for value in bbox.as_list()),
        "WIDTH": str(request.width),
        "HEIGHT": str(request.height),
        "FORMAT": "image/png",
        "TRANSPARENT": "TRUE",
    }
    if request.time:
        params["TIME"] = request.time
    return params


def parse_wms_layers(xml_text: str) -> list[dict[str, str | None]]:
    root = ET.fromstring(xml_text)
    namespace = {"wms": "http://www.opengis.net/wms"}
    layers = []
    for layer in root.findall(".//wms:Layer", namespace):
        name = layer.findtext("wms:Name", namespaces=namespace)
        if not name:
            continue
        time_dimension = None
        for dimension in layer.findall("wms:Dimension", namespace):
            if dimension.attrib.get("name") == "time":
                time_dimension = dimension.text
                break
        layers.append(
            {
                "name": name,
                "title": layer.findtext("wms:Title", namespaces=namespace),
                "time_dimension": time_dimension,
            }
        )
    return layers


def parse_feature_info(body: str) -> dict[str, Any]:
    stripped = body.strip()
    if not stripped or stripped == "[]":
        return {"items": [], "errors": [], "raw": stripped}
    try:
        decoded = json.loads(stripped)
        if isinstance(decoded, list):
            items: list[str] = []
            errors: list[str] = []
            for item in decoded:
                text = str(item).strip()
                if not text:
                    continue
                exception = parse_wms_exception(text)
                if exception:
                    errors.append(exception)
                    continue
                cleaned = clean_feature_info_text(text)
                if cleaned:
                    items.append(cleaned)
            return {"items": items, "errors": errors, "raw": stripped}
    except json.JSONDecodeError:
        pass
    exception = parse_wms_exception(stripped)
    if exception:
        return {"items": [], "errors": [exception], "raw": stripped[:4000]}
    text = clean_feature_info_text(stripped)
    return {"items": [text] if text else [], "errors": [], "raw": stripped[:4000]}


def parse_wms_exception(value: str) -> str | None:
    if "ServiceException" not in value and "ExceptionReport" not in value:
        return None
    cdata_match = re.search(r"<!\[CDATA\[(.*?)\]\]>", value, flags=re.DOTALL)
    if cdata_match:
        return re.sub(r"\s+", " ", cdata_match.group(1)).strip()
    try:
        root = ET.fromstring(value)
        texts = [text.strip() for text in root.itertext() if text and text.strip()]
        return " ".join(texts) if texts else "WMS service exception"
    except ET.ParseError:
        cleaned = clean_feature_info_text(value)
        return cleaned or "WMS service exception"


def clean_feature_info_text(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", value)
    text = unescape(text)
    return re.sub(r"\s+", " ", text).strip()


async def _wms_get(settings: Settings, params: dict[str, str], *, accept: str) -> httpx.Response:
    request_params = dict(params)
    if settings.efas_wms_token:
        request_params["token"] = settings.efas_wms_token
    try:
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await client.get(
                settings.efas_wms_url,
                params=request_params,
                headers={
                    "Accept": accept,
                    "User-Agent": "copernicus-flood-backend/0.1",
                },
            )
    except httpx.TimeoutException as exc:
        raise ExternalServiceError("EFAS WMS request timed out") from exc
    except httpx.HTTPError as exc:
        raise ExternalServiceError("EFAS WMS request failed", details={"error": str(exc)}) from exc
    log_external_response(
        source="EFAS WMS",
        method="GET",
        url=str(response.request.url),
        response=response,
    )
    if response.status_code >= 400:
        raise ExternalServiceError(
            "EFAS WMS returned an error",
            details={"status_code": response.status_code, "body": response.text[:1000]},
        )
    return response


def build_efas_wms_url(settings: Settings, params: dict[str, str]) -> str:
    request_params = dict(params)
    if settings.efas_wms_token:
        request_params["token"] = settings.efas_wms_token
    separator = "&" if "?" in settings.efas_wms_url else "?"
    return f"{settings.efas_wms_url}{separator}{urlencode(request_params)}"
