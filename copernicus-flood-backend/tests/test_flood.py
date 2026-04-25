from __future__ import annotations

from datetime import datetime, timezone

from app.flood import (
    build_statistics_payload,
    classify_status,
    extract_water_stats,
    water_evalscript,
    weighted_water_fraction,
)
from app.models import AreaInput, CenterRadius, FloodDetectionRequest, SatelliteScene, WaterStats


def test_water_evalscript_embeds_threshold() -> None:
    script = water_evalscript(-16.5)

    assert "sentinel-1" not in script.lower()
    assert "vvDb <= -16.500000" in script
    assert 'bands: ["VV", "dataMask"]' in script


def test_extract_water_stats_parses_sentinel_hub_response() -> None:
    response = {
        "data": [
            {
                "interval": {
                    "from": "2026-04-20T00:00:00Z",
                    "to": "2026-04-21T00:00:00Z",
                },
                "outputs": {
                    "water": {
                        "bands": {
                            "water": {
                                "stats": {
                                    "mean": 0.25,
                                    "sampleCount": 100,
                                    "noDataCount": 20,
                                }
                            }
                        }
                    },
                    "vv_db": {
                        "bands": {
                            "vv_db": {
                                "stats": {
                                    "mean": -18.0,
                                    "percentiles": {
                                        "10.0": -24.0,
                                        "50.0": -17.5,
                                        "90.0": -12.0,
                                    },
                                }
                            }
                        }
                    },
                },
            }
        ]
    }

    stats = extract_water_stats(response, resolution_meters=20)

    assert len(stats) == 1
    assert stats[0].water_fraction == 0.25
    assert stats[0].valid_pixel_count == 80
    assert stats[0].estimated_water_area_m2 == 8_000
    assert stats[0].vv_db_p50 == -17.5


def test_statistics_payload_uses_float_histogram_bins() -> None:
    request = FloodDetectionRequest(
        area=AreaInput(center=CenterRadius(latitude=45, longitude=26, radius_meters=500)),
        baseline={"enabled": False},
    )
    dt = datetime(2026, 4, 20, tzinfo=timezone.utc)

    payload = build_statistics_payload(
        request=request,
        time_from=dt,
        time_to=dt,
        aggregation_interval_days=1,
    )

    assert payload["calculations"]["water"]["histograms"]["water"]["bins"] == [0.0, 0.5, 1.5]


def test_weighted_water_fraction() -> None:
    dt = datetime(2026, 4, 20, tzinfo=timezone.utc)
    stats = [
        WaterStats(
            interval_from=dt,
            interval_to=dt,
            water_fraction=0.10,
            valid_pixel_count=100,
            no_data_count=0,
            estimated_water_area_m2=4_000,
        ),
        WaterStats(
            interval_from=dt,
            interval_to=dt,
            water_fraction=0.30,
            valid_pixel_count=300,
            no_data_count=0,
            estimated_water_area_m2=36_000,
        ),
    ]

    assert weighted_water_fraction(stats) == 0.25


def test_classify_likely_flooding_with_baseline_increase() -> None:
    dt = datetime(2026, 4, 20, tzinfo=timezone.utc)
    current = WaterStats(
        interval_from=dt,
        interval_to=dt,
        water_fraction=0.18,
        valid_pixel_count=1_000,
        no_data_count=0,
        estimated_water_area_m2=72_000,
    )

    assert (
        classify_status(
            current=current,
            min_valid_pixels=100,
            min_water_fraction=0.10,
            min_increase_fraction=0.05,
            baseline_water_fraction=0.08,
            water_fraction_change=0.10,
        )
        == "likely_flooding"
    )


def test_classify_insufficient_data() -> None:
    dt = datetime(2026, 4, 20, tzinfo=timezone.utc)
    current = WaterStats(
        interval_from=dt,
        interval_to=dt,
        water_fraction=0.90,
        valid_pixel_count=10,
        no_data_count=0,
        estimated_water_area_m2=3_600,
    )

    assert (
        classify_status(
            current=current,
            min_valid_pixels=100,
            min_water_fraction=0.10,
            min_increase_fraction=0.05,
            baseline_water_fraction=None,
            water_fraction_change=None,
        )
        == "insufficient_data"
    )
