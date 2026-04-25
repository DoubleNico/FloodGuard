from __future__ import annotations

from app.map_page import MAP_HTML


def test_map_page_includes_heatmap_endpoint() -> None:
    assert "Copernicus Flood Risk Map" in MAP_HTML
    assert "/v1/flood/heatmap.png" in MAP_HTML
    assert "/v1/admin/boundaries" in MAP_HTML
    assert "light_only_labels" in MAP_HTML
    assert "admin-region-label" in MAP_HTML


def test_efas_routes_are_registered() -> None:
    from app.main import app

    paths = {route.path for route in app.routes}

    assert "/v1/efas/layers" in paths
    assert "/v1/efas/location" in paths
    assert "/v1/efas/map.png" in paths
    assert "/api/v1/auth/login" in paths
    assert "/api/v1/alerts" in paths
    assert "/api/v1/stream" in paths
