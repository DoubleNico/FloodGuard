from __future__ import annotations

import pytest

from app.geo import bbox_from_center, bbox_from_geometry, resolution_degrees_for_area
from app.models import AreaInput, CenterRadius


def test_bbox_from_center_contains_point() -> None:
    bbox = bbox_from_center(latitude=45.0, longitude=26.0, radius_meters=1_000)

    assert bbox.west < 26.0 < bbox.east
    assert bbox.south < 45.0 < bbox.north


def test_bbox_from_geometry_polygon() -> None:
    geometry = {
        "type": "Polygon",
        "coordinates": [
            [
                [26.0, 45.0],
                [26.1, 45.0],
                [26.1, 45.1],
                [26.0, 45.1],
                [26.0, 45.0],
            ]
        ],
    }

    bbox = bbox_from_geometry(geometry)

    assert bbox.as_list() == [26.0, 45.0, 26.1, 45.1]


def test_invalid_geometry_type_rejected() -> None:
    with pytest.raises(ValueError, match="Polygon or MultiPolygon"):
        bbox_from_geometry({"type": "Point", "coordinates": [26.0, 45.0]})


def test_resolution_degrees_are_positive() -> None:
    area = AreaInput(center=CenterRadius(latitude=45, longitude=26, radius_meters=1_000))

    resx, resy = resolution_degrees_for_area(area, 20)

    assert resx > 0
    assert resy > 0

