from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from statistics import fmean
from typing import Any, Protocol

from app.exceptions import NoStatisticsError
from app.geo import bounds_payload_from_area, resolution_degrees_for_area
from app.models import (
    FloodHeatmapRequest,
    FloodDetectionRequest,
    FloodDetectionResponse,
    LatestSceneRequest,
    SatelliteScene,
    WaterStats,
)
from app.time_utils import iso_z

METHOD = (
    "Sentinel-1 GRD VV backscatter water proxy using terrain-corrected gamma0, "
    "Lee speckle filtering, and Sentinel Hub Statistical API. This is a screening "
    "signal, not an official emergency flood map."
)


class FloodDataClient(Protocol):
    async def catalog_latest(self, request: LatestSceneRequest) -> list[SatelliteScene]:
        ...

    async def statistics(self, payload: dict[str, Any]) -> dict[str, Any]:
        ...

    async def process_image(self, payload: dict[str, Any]) -> bytes:
        ...


async def detect_flood(
    request: FloodDetectionRequest,
    client: FloodDataClient,
) -> FloodDetectionResponse:
    latest_scene = (
        await client.catalog_latest(
            LatestSceneRequest(
                area=request.area,
                lookback_days=request.lookback_days,
                limit=25,
                acquisition_mode=request.acquisition_mode,
                polarization=request.polarization,
                orbit_direction=request.orbit_direction,
            )
        )
    )[0]

    current_from, current_to = day_bounds(latest_scene.datetime)
    current_payload = build_statistics_payload(
        request=request,
        time_from=current_from,
        time_to=current_to,
        aggregation_interval_days=1,
    )

    # Build baseline payload ahead of time so we can fire both requests concurrently.
    baseline_payload: dict[str, Any] | None = None
    if request.baseline.enabled:
        baseline_to = latest_scene.datetime - timedelta(days=request.baseline.gap_days)
        baseline_from = baseline_to - timedelta(days=request.baseline.days)
        if baseline_from < baseline_to:
            baseline_payload = build_statistics_payload(
                request=request,
                time_from=baseline_from,
                time_to=baseline_to,
                aggregation_interval_days=request.baseline.interval_days,
            )

    # Fetch current stats and (optional) baseline stats concurrently.
    if baseline_payload is not None:
        current_response, baseline_response = await asyncio.gather(
            client.statistics(current_payload),
            client.statistics(baseline_payload),
        )
    else:
        current_response = await client.statistics(current_payload)
        baseline_response = None

    current_stats = extract_water_stats(current_response, resolution_meters=request.resolution_meters)
    if not current_stats:
        raise NoStatisticsError(
            "No valid Sentinel-1 statistics were returned for the latest scene.",
            details={"scene_id": latest_scene.id, "scene_datetime": latest_scene.datetime.isoformat()},
        )
    current = current_stats[-1]

    warnings: list[str] = []
    baseline_fraction: float | None = None
    baseline_intervals_used = 0

    if baseline_response is not None:
        baseline_stats = extract_water_stats(baseline_response, resolution_meters=request.resolution_meters)
        usable = [stat for stat in baseline_stats if stat.valid_pixel_count >= request.min_valid_pixels]
        baseline_intervals_used = len(usable)
        baseline_fraction = weighted_water_fraction(usable)

    if request.baseline.enabled and baseline_fraction is None:
        warnings.append("No usable baseline statistics were available; using latest water fraction only.")

    water_fraction_change = (
        current.water_fraction - baseline_fraction if baseline_fraction is not None else None
    )
    status = classify_status(
        current=current,
        min_valid_pixels=request.min_valid_pixels,
        min_water_fraction=request.min_water_fraction,
        min_increase_fraction=request.min_increase_fraction,
        baseline_water_fraction=baseline_fraction,
        water_fraction_change=water_fraction_change,
    )
    confidence = confidence_level(
        current=current,
        latest_scene=latest_scene,
        baseline_intervals_used=baseline_intervals_used,
    )

    return FloodDetectionResponse(
        status=status,
        confidence=confidence,
        flooded=status in {"likely_flooding", "possible_flooding"},
        latest_scene=latest_scene,
        current=current,
        baseline_water_fraction=baseline_fraction,
        baseline_intervals_used=baseline_intervals_used,
        water_fraction_change=water_fraction_change,
        method=METHOD,
        warnings=warnings,
    )


def build_statistics_payload(
    *,
    request: FloodDetectionRequest,
    time_from: datetime,
    time_to: datetime,
    aggregation_interval_days: int,
) -> dict[str, Any]:
    resx, resy = resolution_degrees_for_area(request.area, request.resolution_meters)
    data_filter: dict[str, Any] = {
        "acquisitionMode": request.acquisition_mode,
        "polarization": request.polarization,
        "resolution": "HIGH",
        "mosaickingOrder": "mostRecent",
    }
    if request.orbit_direction:
        data_filter["orbitDirection"] = request.orbit_direction

    return {
        "input": {
            "bounds": bounds_payload_from_area(request.area),
            "data": [
                {
                    "type": "sentinel-1-grd",
                    "dataFilter": data_filter,
                    "processing": {
                        "orthorectify": "true",
                        "backCoeff": "GAMMA0_TERRAIN",
                        "demInstance": "COPERNICUS_30",
                        "speckleFilter": {
                            "type": "LEE",
                            "windowSizeX": 5,
                            "windowSizeY": 5,
                        },
                    },
                }
            ],
        },
        "aggregation": {
            "timeRange": {"from": iso_z(time_from), "to": iso_z(time_to)},
            "aggregationInterval": {"of": f"P{aggregation_interval_days}D"},
            "lastIntervalBehavior": "SHORTEN",
            "evalscript": water_evalscript(request.water_threshold_db),
            "resx": resx,
            "resy": resy,
        },
        "calculations": {
            "water": {
                "histograms": {"water": {"bins": [0.0, 0.5, 1.5]}},
                "statistics": {"water": {"percentiles": {"k": [50]}}},
            },
            "vv_db": {
                "statistics": {"vv_db": {"percentiles": {"k": [10, 50, 90]}}},
            },
        },
    }


async def build_heatmap_png(
    request: FloodHeatmapRequest,
    client: FloodDataClient,
) -> tuple[bytes, SatelliteScene]:
    latest_scene = (
        await client.catalog_latest(
            LatestSceneRequest(
                area=request.area,
                lookback_days=request.lookback_days,
                limit=25,
                acquisition_mode=request.acquisition_mode,
                polarization=request.polarization,
                orbit_direction=request.orbit_direction,
            )
        )
    )[0]
    time_from, time_to = day_bounds(latest_scene.datetime)
    payload = build_heatmap_payload(
        request=request,
        time_from=time_from,
        time_to=time_to,
    )
    return await client.process_image(payload), latest_scene


def build_heatmap_payload(
    *,
    request: FloodHeatmapRequest,
    time_from: datetime,
    time_to: datetime,
) -> dict[str, Any]:
    data_filter: dict[str, Any] = {
        "timeRange": {"from": iso_z(time_from), "to": iso_z(time_to)},
        "acquisitionMode": request.acquisition_mode,
        "polarization": request.polarization,
        "resolution": "HIGH",
        "mosaickingOrder": "mostRecent",
    }
    if request.orbit_direction:
        data_filter["orbitDirection"] = request.orbit_direction

    return {
        "input": {
            "bounds": bounds_payload_from_area(request.area),
            "data": [
                {
                    "type": "sentinel-1-grd",
                    "dataFilter": data_filter,
                    "processing": {
                        "orthorectify": "true",
                        "backCoeff": "GAMMA0_TERRAIN",
                        "demInstance": "COPERNICUS_30",
                        "speckleFilter": {
                            "type": "LEE",
                            "windowSizeX": 5,
                            "windowSizeY": 5,
                        },
                    },
                }
            ],
        },
        "output": {
            "width": request.width,
            "height": request.height,
            "responses": [
                {
                    "identifier": "default",
                    "format": {"type": "image/png"},
                }
            ],
        },
        "evalscript": heatmap_evalscript(request.water_threshold_db),
    }


def water_evalscript(water_threshold_db: float) -> str:
    return f"""
//VERSION=3
function setup() {{
  return {{
    input: [{{
      bands: ["VV", "dataMask"],
      units: "LINEAR_POWER"
    }}],
    output: [
      {{ id: "water", bands: ["water"], sampleType: "FLOAT32" }},
      {{ id: "vv_db", bands: ["vv_db"], sampleType: "FLOAT32" }},
      {{ id: "dataMask", bands: ["water", "vv_db"] }}
    ]
  }};
}}

function evaluatePixel(samples) {{
  var valid = samples.dataMask === 1 && samples.VV > 0;
  var vvDb = valid ? 10.0 * Math.log(samples.VV) / Math.LN10 : -9999.0;
  var water = valid && vvDb <= {water_threshold_db:.6f} ? 1.0 : 0.0;
  return {{
    water: [water],
    vv_db: [vvDb],
    dataMask: [valid ? 1 : 0, valid ? 1 : 0]
  }};
}}
""".strip()


def heatmap_evalscript(water_threshold_db: float) -> str:
    medium_threshold = water_threshold_db + 2.0
    low_threshold = water_threshold_db + 4.0
    return f"""
//VERSION=3
function setup() {{
  return {{
    input: [{{
      bands: ["VV", "dataMask"],
      units: "LINEAR_POWER"
    }}],
    output: {{ id: "default", bands: 4 }}
  }};
}}

function evaluatePixel(samples) {{
  if (samples.dataMask !== 1 || samples.VV <= 0) {{
    return [0, 0, 0, 0];
  }}

  var vvDb = 10.0 * Math.log(samples.VV) / Math.LN10;
  if (vvDb <= {water_threshold_db:.6f}) {{
    return [0.92, 0.12, 0.12, 0.82];
  }}
  if (vvDb <= {medium_threshold:.6f}) {{
    return [1.00, 0.62, 0.10, 0.68];
  }}
  if (vvDb <= {low_threshold:.6f}) {{
    return [0.10, 0.48, 0.96, 0.42];
  }}
  return [0, 0, 0, 0];
}}
""".strip()


def extract_water_stats(response: dict[str, Any], *, resolution_meters: float) -> list[WaterStats]:
    stats: list[WaterStats] = []
    for entry in response.get("data", []):
        if entry.get("status") and entry.get("status") != "OK":
            continue
        interval = entry.get("interval", {})
        outputs = entry.get("outputs", {})
        water_band = _first_band(outputs.get("water", {}), preferred="water")
        if not water_band:
            continue
        water_raw_stats = water_band.get("stats", {})
        mean = water_raw_stats.get("mean")
        sample_count = int(water_raw_stats.get("sampleCount") or 0)
        no_data_count = int(water_raw_stats.get("noDataCount") or 0)
        valid_count = max(sample_count - no_data_count, 0)
        if mean is None or valid_count <= 0:
            continue

        vv_band = _first_band(outputs.get("vv_db", {}), preferred="vv_db") or {}
        vv_raw_stats = vv_band.get("stats", {})
        percentiles = vv_raw_stats.get("percentiles", {})

        water_fraction = max(0.0, min(float(mean), 1.0))
        stats.append(
            WaterStats(
                interval_from=_parse_response_datetime(interval.get("from")),
                interval_to=_parse_response_datetime(interval.get("to")),
                water_fraction=water_fraction,
                valid_pixel_count=valid_count,
                no_data_count=no_data_count,
                estimated_water_area_m2=water_fraction * valid_count * resolution_meters**2,
                vv_db_mean=_optional_float(vv_raw_stats.get("mean")),
                vv_db_p10=_optional_float(percentiles.get("10.0")),
                vv_db_p50=_optional_float(percentiles.get("50.0")),
                vv_db_p90=_optional_float(percentiles.get("90.0")),
            )
        )
    return stats


def weighted_water_fraction(stats: list[WaterStats]) -> float | None:
    weighted_values = [
        (stat.water_fraction, stat.valid_pixel_count)
        for stat in stats
        if stat.valid_pixel_count > 0
    ]
    total_weight = sum(weight for _, weight in weighted_values)
    if total_weight == 0:
        return None
    return sum(value * weight for value, weight in weighted_values) / total_weight


def classify_status(
    *,
    current: WaterStats,
    min_valid_pixels: int,
    min_water_fraction: float,
    min_increase_fraction: float,
    baseline_water_fraction: float | None,
    water_fraction_change: float | None,
) -> str:
    if current.valid_pixel_count < min_valid_pixels:
        return "insufficient_data"
    if baseline_water_fraction is None or water_fraction_change is None:
        if current.water_fraction >= min_water_fraction:
            return "possible_flooding"
        return "no_flood_signal"
    if (
        current.water_fraction >= min_water_fraction
        and water_fraction_change >= min_increase_fraction
    ):
        return "likely_flooding"
    if (
        current.water_fraction >= min_water_fraction
        and water_fraction_change >= min_increase_fraction / 2
    ):
        return "possible_flooding"
    return "no_flood_signal"


def confidence_level(
    *,
    current: WaterStats,
    latest_scene: SatelliteScene,
    baseline_intervals_used: int,
) -> str:
    scene_age_days = (datetime.now(timezone.utc) - latest_scene.datetime).total_seconds() / 86_400
    if current.valid_pixel_count >= 1_000 and scene_age_days <= 7 and baseline_intervals_used >= 3:
        return "high"
    if current.valid_pixel_count >= 100 and scene_age_days <= 14:
        return "medium"
    return "low"


def day_bounds(value: datetime) -> tuple[datetime, datetime]:
    value = value.astimezone(timezone.utc)
    start = value.replace(hour=0, minute=0, second=0, microsecond=0)
    return start, start + timedelta(days=1)


def _first_band(output: dict[str, Any], *, preferred: str) -> dict[str, Any] | None:
    bands = output.get("bands") if isinstance(output, dict) else None
    if not isinstance(bands, dict) or not bands:
        return None
    if preferred in bands:
        return bands[preferred]
    return next(iter(bands.values()))


def _parse_response_datetime(value: str | None) -> datetime:
    if value is None:
        raise ValueError("statistics interval is missing datetime")
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _optional_float(value: Any) -> float | None:
    if value is None:
        return None
    return float(value)


def mean_water_fraction(stats: list[WaterStats]) -> float | None:
    if not stats:
        return None
    return fmean(stat.water_fraction for stat in stats)
