from __future__ import annotations

from app.config import Settings
from app.efas import (
    EfasMapRequest,
    build_efas_wms_url,
    build_get_map_params,
    clean_feature_info_text,
    parse_feature_info,
    parse_wms_layers,
)


def test_build_get_map_params_uses_point_radius_bbox() -> None:
    params = build_get_map_params(
        EfasMapRequest(
            latitude=45.45,
            longitude=28.05,
            radius_meters=50_000,
            layer="mapserver:MIC2",
            width=512,
            height=256,
        )
    )

    assert params["SERVICE"] == "WMS"
    assert params["VERSION"] == "1.1.1"
    assert params["LAYERS"] == "mapserver:MIC2"
    assert params["SRS"] == "EPSG:4326"
    assert params["WIDTH"] == "512"
    assert params["HEIGHT"] == "256"


def test_parse_wms_layers_extracts_time_dimension() -> None:
    xml = """<?xml version="1.0"?>
<WMS_Capabilities xmlns="http://www.opengis.net/wms">
  <Capability>
    <Layer>
      <Layer>
        <Name>mapserver:MIC2</Name>
        <Title>Threshold level exceedance 1-2 days</Title>
        <Dimension name="time">2026-04-01T00:00:00/2026-04-25T00:00:00/PT12H</Dimension>
      </Layer>
    </Layer>
  </Capability>
</WMS_Capabilities>
"""

    layers = parse_wms_layers(xml)

    assert layers == [
        {
            "name": "mapserver:MIC2",
            "title": "Threshold level exceedance 1-2 days",
            "time_dimension": "2026-04-01T00:00:00/2026-04-25T00:00:00/PT12H",
        }
    ]


def test_parse_feature_info_handles_empty_and_html_payloads() -> None:
    assert parse_feature_info("[]")["items"] == []

    parsed = parse_feature_info('["<table><tr><td>Warning</td><td>High</td></tr></table>"]')

    assert parsed["items"] == ["Warning High"]


def test_parse_feature_info_treats_wms_exception_as_error() -> None:
    payload = (
        '["<?xml version=\\"1.0\\"?><ServiceExceptionReport><ServiceException>'
        '<![CDATA[No data for layer MIC2]]></ServiceException></ServiceExceptionReport>"]'
    )

    parsed = parse_feature_info(payload)

    assert parsed["items"] == []
    assert parsed["errors"] == ["No data for layer MIC2"]


def test_build_efas_wms_url_adds_token_when_configured() -> None:
    settings = Settings(efas_wms_url="https://example.test/wms/", efas_wms_token="secret")

    url = build_efas_wms_url(settings, {"SERVICE": "WMS", "REQUEST": "GetMap"})

    assert url == "https://example.test/wms/?SERVICE=WMS&REQUEST=GetMap&token=secret"


def test_clean_feature_info_text_strips_markup() -> None:
    assert clean_feature_info_text("<b>Flood</b>&nbsp;probability") == "Flood probability"
