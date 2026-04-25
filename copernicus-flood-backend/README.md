# Copernicus Flood Backend

Python HTTP API for flood screening in a GPS area using recent Copernicus Sentinel-1 GRD SAR data through the Copernicus Data Space Ecosystem Sentinel Hub APIs.
It also exposes the Hydralis dispatch/mobile API under `/api/v1` with persistent SQLite storage.

## What it does

- Searches the Sentinel Hub Catalog API for the newest `sentinel-1-grd` scene intersecting a bbox, point radius, or GeoJSON polygon.
- Runs Sentinel Hub Statistical API over that area and scene date.
- Classifies likely/possible flood signal from Sentinel-1 VV backscatter water fraction and, when available, a pre-event baseline window.
- Serves a browser map at `/map` with a Sentinel-1 PNG heatmap overlay from Sentinel Hub Process API.
- Shows country and subdivision boundaries above the heatmap from OpenStreetMap administrative boundary data.
- Provides EFAS WMS flood forecast and early-warning layer access for a location.
- Provides Hydralis dispatch/mobile endpoints for authentication, alerts, safe locations, industrial telemetry, subscriptions, and WebSocket updates.
- Returns JSON and PNG overlays without downloading full satellite products.

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

The browser map is available at `http://127.0.0.1:8000/map`.

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
- `GET /map` - browser map with a Sentinel-1 flood-risk heatmap overlay.
- `GET /v1/config` - non-secret runtime configuration.
- `POST /v1/catalog/latest` - latest Sentinel-1 GRD scenes for an area.
- `POST /v1/flood/detect` - flood screening result.
- `GET /v1/flood/heatmap.png` - PNG overlay for a point/radius area.
- `GET /v1/admin/boundaries` - administrative boundary GeoJSON for the visible heatmap area.
- `GET /v1/efas/layers` - EFAS forecast/warning layers available through WMS.
- `GET /v1/efas/location` - EFAS feature-info summary for forecast/warning layers around a location.
- `GET /v1/efas/map.png` - EFAS WMS map overlay for a selected forecast/warning layer.
- `POST /api/v1/auth/login` - Hydralis dashboard/mobile login.
- `GET|POST /api/v1/alerts` - list and create alerts.
- `PATCH /api/v1/alerts/{id}/status` - update alert workflow state.
- `POST /api/v1/alerts/{id}/broadcast` - publish an alert and increment sent usage.
- `GET|POST|PATCH|DELETE /api/v1/locations` - safe locations CRUD.
- `GET /api/v1/satellite/*` - water level, NDWI, precipitation, and Galileo data.
- `GET /api/v1/industrial/factories` and `/api/v1/industrial/sensors` - industrial monitoring.
- `GET /api/v1/subscription/status` - SaaS plan and usage.
- `WS /api/v1/stream` - frontend update stream.

Example heatmap overlay:

```bash
curl -o heatmap.png \
  "http://127.0.0.1:8000/v1/flood/heatmap.png?latitude=45.45&longitude=28.05&radius_meters=1000&lookback_days=30"
```

Example EFAS location forecast/warning request:

```bash
curl \
  "http://127.0.0.1:8000/v1/efas/location?latitude=45.45&longitude=28.05&radius_meters=50000"
```

Example EFAS threshold-exceedance map:

```bash
curl -o efas-threshold-1-2-days.png \
  "http://127.0.0.1:8000/v1/efas/map.png?latitude=45.45&longitude=28.05&radius_meters=50000&layer=mapserver:MIC2"
```

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
- EFAS real-time forecasts and formal early warnings are restricted to authorised EFAS partners. Without `EFAS_WMS_TOKEN`, EFAS endpoints use public limited/non-real-time WMS access.
