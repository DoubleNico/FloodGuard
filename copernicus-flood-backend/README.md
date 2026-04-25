# Copernicus Flood Backend

Python HTTP API for flood screening in a GPS area using recent Copernicus Sentinel-1 GRD SAR data through the Copernicus Data Space Ecosystem Sentinel Hub APIs.

## What it does

- Searches the Sentinel Hub Catalog API for the newest `sentinel-1-grd` scene intersecting a bbox, point radius, or GeoJSON polygon.
- Runs Sentinel Hub Statistical API over that area and scene date.
- Classifies likely/possible flood signal from Sentinel-1 VV backscatter water fraction and, when available, a pre-event baseline window.
- Returns JSON for a future frontend; it does not download full satellite products.

This is an automated screening signal, not an official emergency management flood map.

## Setup

Create a Copernicus Data Space Ecosystem account and OAuth client, then set:

```bash
export CDSE_CLIENT_ID="..."
export CDSE_CLIENT_SECRET="..."
```

Install and run:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

OpenAPI docs are available at `http://127.0.0.1:8000/docs`.

## Example request

```bash
curl -X POST http://127.0.0.1:8000/v1/flood/detect \
  -H "Content-Type: application/json" \
  -d '{
    "area": {
      "center": {
        "latitude": 45.05,
        "longitude": 26.05,
        "radius_meters": 2500
      }
    },
    "lookback_days": 30,
    "resolution_meters": 20,
    "water_threshold_db": -17,
    "min_water_fraction": 0.10,
    "min_increase_fraction": 0.05
  }'
```

## API

- `GET /health` - service health.
- `GET /v1/config` - non-secret runtime configuration.
- `POST /v1/catalog/latest` - latest Sentinel-1 GRD scenes for an area.
- `POST /v1/flood/detect` - flood screening result.

## Area formats

Provide exactly one of:

```json
{"bbox": {"west": 26.0, "south": 45.0, "east": 26.1, "north": 45.1}}
```

```json
{"center": {"latitude": 45.05, "longitude": 26.05, "radius_meters": 2500}}
```

```json
{"geometry": {"type": "Polygon", "coordinates": [[[26.0,45.0],[26.1,45.0],[26.1,45.1],[26.0,45.1],[26.0,45.0]]]}}
```

## Notes

- Sentinel-1 SAR works through cloud cover and at night, which makes it suitable for flood screening.
- The default flood signal uses a VV backscatter threshold and compares the latest water fraction to a 90-day baseline with a 7-day gap.
- Thresholds are area-dependent. Tune `water_threshold_db`, `min_water_fraction`, and `min_increase_fraction` with local validation data before production use.
