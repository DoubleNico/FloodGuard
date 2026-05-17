from __future__ import annotations

from app.config import Settings
from app.sentinel_hub import SentinelHubClient


def test_catalog_filter_uses_documented_cql_text() -> None:
    client = SentinelHubClient(Settings())

    assert (
        client._catalog_filter("IW", "DV", "ASCENDING")
        == "sar:instrument_mode='IW' AND s1:polarization='DV' AND sat:orbit_state='ascending'"
    )
