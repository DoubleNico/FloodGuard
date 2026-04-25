from __future__ import annotations

from app.admin_boundaries import build_overpass_query, overpass_to_geojson


def test_build_overpass_query_requests_admin_relations_with_geometry() -> None:
    query = build_overpass_query(
        west=28.0,
        south=45.4,
        east=28.1,
        north=45.5,
        admin_levels=("2", "4"),
    )

    assert '[out:json][timeout:25]' in query
    assert 'relation["boundary"="administrative"]["admin_level"~"^(2|4)$"]' in query
    assert "(45.4,28.0,45.5,28.1)" in query
    assert "is_in(45.45,28.05)" in query
    assert "out geom;" in query


def test_overpass_to_geojson_converts_relation_way_members() -> None:
    payload = {
        "elements": [
            {
                "type": "relation",
                "id": 100,
                "tags": {"name": "Example County", "admin_level": "6", "boundary": "administrative"},
                "members": [
                    {
                        "type": "way",
                        "ref": 200,
                        "geometry": [
                            {"lat": 45.4, "lon": 28.0},
                            {"lat": 45.5, "lon": 28.1},
                        ],
                    }
                ],
            }
        ]
    }

    geojson = overpass_to_geojson(payload, label_lon=28.05, label_lat=45.45)

    assert geojson["type"] == "FeatureCollection"
    assert geojson["features"][0]["properties"]["name"] == "Example County"
    assert geojson["features"][0]["geometry"]["coordinates"] == [[28.0, 45.4], [28.1, 45.5]]


def test_overpass_to_geojson_adds_visible_region_label() -> None:
    payload = {
        "elements": [
            {
                "type": "relation",
                "id": 1,
                "center": {"lat": 45.9, "lon": 25.1},
                "tags": {"name": "Romania", "admin_level": "2", "boundary": "administrative"},
            },
            {
                "type": "relation",
                "id": 2,
                "center": {"lat": 45.8, "lon": 27.7},
                "tags": {"name": "Galati", "admin_level": "4", "boundary": "administrative"},
            },
        ]
    }

    geojson = overpass_to_geojson(payload, label_lon=28.05, label_lat=45.45)

    assert geojson["features"][0]["properties"]["kind"] == "admin_label"
    assert geojson["features"][0]["properties"]["name"] == "Romania / Galati"
    assert geojson["features"][0]["geometry"]["coordinates"] == [28.05, 45.45]
