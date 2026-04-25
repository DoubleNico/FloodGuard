from __future__ import annotations

import math
from typing import Any

from app.models import AreaInput, BBox

WGS84_CRS = "http://www.opengis.net/def/crs/EPSG/0/4326"
METERS_PER_DEGREE_LAT = 111_320.0


def bbox_from_center(latitude: float, longitude: float, radius_meters: float) -> BBox:
    lat_delta = radius_meters / METERS_PER_DEGREE_LAT
    cos_lat = max(math.cos(math.radians(latitude)), 0.01)
    lon_delta = radius_meters / (METERS_PER_DEGREE_LAT * cos_lat)

    return BBox(
        west=max(-180.0, longitude - lon_delta),
        south=max(-90.0, latitude - lat_delta),
        east=min(180.0, longitude + lon_delta),
        north=min(90.0, latitude + lat_delta),
    )


def validate_geojson_geometry(geometry: dict[str, Any]) -> None:
    geometry_type = geometry.get("type")
    coordinates = geometry.get("coordinates")
    if geometry_type not in {"Polygon", "MultiPolygon"}:
        raise ValueError("geometry must be a GeoJSON Polygon or MultiPolygon")
    if not isinstance(coordinates, list) or not coordinates:
        raise ValueError("geometry.coordinates must be a non-empty list")
    _walk_positions(coordinates)


def _walk_positions(node: Any) -> None:
    if _is_position(node):
        lon, lat = float(node[0]), float(node[1])
        if not -180 <= lon <= 180 or not -90 <= lat <= 90:
            raise ValueError("geometry coordinates must be WGS84 lon/lat values")
        return
    if not isinstance(node, list) or not node:
        raise ValueError("invalid GeoJSON coordinates")
    for child in node:
        _walk_positions(child)


def _is_position(value: Any) -> bool:
    return (
        isinstance(value, list)
        and len(value) >= 2
        and isinstance(value[0], int | float)
        and isinstance(value[1], int | float)
    )


def bbox_from_geometry(geometry: dict[str, Any]) -> BBox:
    validate_geojson_geometry(geometry)
    longitudes: list[float] = []
    latitudes: list[float] = []

    def collect(node: Any) -> None:
        if _is_position(node):
            longitudes.append(float(node[0]))
            latitudes.append(float(node[1]))
            return
        for child in node:
            collect(child)

    collect(geometry["coordinates"])
    return BBox(
        west=min(longitudes),
        south=min(latitudes),
        east=max(longitudes),
        north=max(latitudes),
    )


def bbox_from_area(area: AreaInput) -> BBox:
    if area.bbox is not None:
        return area.bbox
    if area.center is not None:
        return bbox_from_center(
            area.center.latitude,
            area.center.longitude,
            area.center.radius_meters,
        )
    if area.geometry is not None:
        return bbox_from_geometry(area.geometry)
    raise ValueError("area is missing")


def bounds_payload_from_area(area: AreaInput) -> dict[str, Any]:
    if area.geometry is not None:
        validate_geojson_geometry(area.geometry)
        return {
            "geometry": area.geometry,
            "properties": {"crs": WGS84_CRS},
        }
    return {
        "bbox": bbox_from_area(area).as_list(),
        "properties": {"crs": WGS84_CRS},
    }


def resolution_degrees_for_area(area: AreaInput, resolution_meters: float) -> tuple[float, float]:
    bbox = bbox_from_area(area)
    center_lat = (bbox.south + bbox.north) / 2
    cos_lat = max(math.cos(math.radians(center_lat)), 0.01)
    resy = resolution_meters / METERS_PER_DEGREE_LAT
    resx = resolution_meters / (METERS_PER_DEGREE_LAT * cos_lat)
    return resx, resy

