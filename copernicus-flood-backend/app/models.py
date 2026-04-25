from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator


OrbitDirection = Literal["ASCENDING", "DESCENDING"]
AcquisitionMode = Literal["IW", "EW", "SM"]
Polarization = Literal["DV", "SV", "VV"]


class BBox(BaseModel):
    west: float = Field(..., ge=-180, le=180)
    south: float = Field(..., ge=-90, le=90)
    east: float = Field(..., ge=-180, le=180)
    north: float = Field(..., ge=-90, le=90)

    @model_validator(mode="after")
    def validate_order(self) -> "BBox":
        if self.west >= self.east:
            raise ValueError("west must be smaller than east")
        if self.south >= self.north:
            raise ValueError("south must be smaller than north")
        return self

    def as_list(self) -> list[float]:
        return [self.west, self.south, self.east, self.north]


class CenterRadius(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    radius_meters: float = Field(..., gt=0, le=100_000)


class AreaInput(BaseModel):
    bbox: BBox | None = None
    center: CenterRadius | None = None
    geometry: dict[str, Any] | None = Field(
        default=None,
        description="GeoJSON Polygon or MultiPolygon in WGS84 longitude/latitude.",
    )

    @model_validator(mode="after")
    def exactly_one_area_type(self) -> "AreaInput":
        provided = [self.bbox is not None, self.center is not None, self.geometry is not None]
        if sum(provided) != 1:
            raise ValueError("provide exactly one of bbox, center, or geometry")
        return self


class BaselineConfig(BaseModel):
    enabled: bool = True
    days: int = Field(90, ge=12, le=730)
    gap_days: int = Field(
        7,
        ge=0,
        le=60,
        description="Days before the latest scene to exclude from baseline.",
    )
    interval_days: int = Field(
        12,
        ge=1,
        le=60,
        description="Temporal aggregation interval used for baseline statistics.",
    )


class FloodDetectionRequest(BaseModel):
    area: AreaInput
    lookback_days: int = Field(30, ge=1, le=180)
    resolution_meters: float = Field(20, ge=10, le=250)
    water_threshold_db: float = Field(
        -17.0,
        ge=-30,
        le=-5,
        description="VV backscatter threshold. Lower values are darker and more water-like.",
    )
    min_water_fraction: float = Field(
        0.10,
        ge=0,
        le=1,
        description="Minimum latest water fraction required before reporting flooding.",
    )
    min_increase_fraction: float = Field(
        0.05,
        ge=0,
        le=1,
        description="Minimum increase over baseline water fraction.",
    )
    min_valid_pixels: int = Field(100, ge=1)
    acquisition_mode: AcquisitionMode = "IW"
    polarization: Polarization = "DV"
    orbit_direction: OrbitDirection | None = None
    baseline: BaselineConfig = Field(default_factory=BaselineConfig)

    @field_validator("polarization")
    @classmethod
    def prefer_vv_capable_polarization(cls, value: Polarization) -> Polarization:
        if value not in {"DV", "SV", "VV"}:
            raise ValueError("polarization must include VV")
        return value


class LatestSceneRequest(BaseModel):
    area: AreaInput
    lookback_days: int = Field(30, ge=1, le=180)
    limit: int = Field(10, ge=1, le=100)
    acquisition_mode: AcquisitionMode = "IW"
    polarization: Polarization = "DV"
    orbit_direction: OrbitDirection | None = None


class FloodHeatmapRequest(BaseModel):
    area: AreaInput
    lookback_days: int = Field(30, ge=1, le=180)
    width: int = Field(768, ge=64, le=2048)
    height: int = Field(768, ge=64, le=2048)
    water_threshold_db: float = Field(-17.0, ge=-30, le=-5)
    acquisition_mode: AcquisitionMode = "IW"
    polarization: Polarization = "DV"
    orbit_direction: OrbitDirection | None = None


class SatelliteScene(BaseModel):
    id: str
    collection: str = "sentinel-1-grd"
    datetime: datetime
    start_datetime: datetime | None = None
    end_datetime: datetime | None = None
    platform: str | None = None
    acquisition_mode: str | None = None
    polarization: str | None = None
    orbit_direction: str | None = None
    bbox: list[float] | None = None


class WaterStats(BaseModel):
    interval_from: datetime
    interval_to: datetime
    water_fraction: float
    valid_pixel_count: int
    no_data_count: int
    estimated_water_area_m2: float
    vv_db_mean: float | None = None
    vv_db_p10: float | None = None
    vv_db_p50: float | None = None
    vv_db_p90: float | None = None


class FloodDetectionResponse(BaseModel):
    status: Literal[
        "likely_flooding",
        "possible_flooding",
        "no_flood_signal",
        "insufficient_data",
    ]
    confidence: Literal["low", "medium", "high"]
    flooded: bool
    latest_scene: SatelliteScene
    current: WaterStats
    baseline_water_fraction: float | None = None
    baseline_intervals_used: int = 0
    water_fraction_change: float | None = None
    method: str
    warnings: list[str] = Field(default_factory=list)
