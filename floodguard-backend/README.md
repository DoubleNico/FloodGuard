# FloodGuard Backend

FastAPI service that powers the FloodGuard mobile app. It aggregates public meteorological data and Copernicus Earth observation products into per-site 48-hour flood-risk forecasts, delivers push alerts when site thresholds are crossed, and exposes the Sentinel-1 / EFAS / GloFAS toolset under the `/v1` prefix.

Project-level documentation:

- [Architecture](../docs/architecture.md)
- [Development Setup](../docs/development.md)
- [API Reference](../docs/api-reference.md)
- [Operations and Troubleshooting](../docs/operations.md)

## What it does

- Aggregates Open-Meteo precipitation forecasts, EFAS gridded flood probability, GloFAS forecasts, and ECMWF Open Data into a per-site 48h risk score.
- Produces predicted inundation polygons by overlaying flood-probability rasters with site terrain footprints.
- Pushes threshold-triggered alerts to mobile devices through FCM (configurable).
- Searches the Sentinel Hub Catalog API for the newest `sentinel-1-grd` scene intersecting a bbox, point radius, or GeoJSON polygon.
- Runs Sentinel Hub Statistical API over that area and scene date.
- Classifies flood signal from Sentinel-1 VV backscatter water fraction, with optional pre-event baseline comparison.
- Serves a browser map at `/map` with a Sentinel-1 PNG heatmap overlay.
- Shows administrative boundaries from OpenStreetMap.
- Provides EFAS WMS flood forecast and early-warning layer access.
- Provides FloodGuard mobile endpoints for sign-up, login, map aggregation, status updates, and emergency triggers.
- Returns JSON and PNG overlays without downloading full satellite products.

This is an automated screening signal, not an official emergency-management flood map.

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

Or:

```bash
python run.py
```

OpenAPI docs at `http://127.0.0.1:8000/docs`. Browser map at `http://127.0.0.1:8000/map`.

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

## API summary

- `GET /health` — service health.
- `GET /map` — browser map with a Sentinel-1 flood-risk heatmap overlay.
- `GET /v1/config` — non-secret runtime configuration.
- `POST /v1/catalog/latest` — latest Sentinel-1 GRD scenes for an area.
- `POST /v1/flood/detect` — flood screening result.
- `GET /v1/flood/heatmap.png` — PNG overlay for a point/radius area.
- `GET /v1/admin/boundaries` — administrative boundary GeoJSON.
- `GET /v1/efas/layers` — EFAS WMS layers.
- `GET /v1/efas/location` — EFAS feature-info summary around a location.
- `GET /v1/efas/map.png` — EFAS WMS map overlay.
- `GET /api/sites` and `GET /api/sites/{id}/forecast` — sites and 48h forecast snapshots (planned).
- `POST /api/push/register` — FCM token registration scoped by site (planned).
- `POST /api/v1/auth/login` — operator login.
- `GET|POST /api/v1/alerts` — list and create alerts.
- `PATCH /api/v1/alerts/{id}/status` — update alert state.
- `POST /api/v1/alerts/{id}/broadcast` — publish an alert.
- `GET|POST|PATCH|DELETE /api/v1/locations` — safe locations.
- `GET /api/v1/satellite/*` — water level, NDWI, precipitation, Galileo demo feeds.
- `WS /api/v1/stream` — real-time updates.
- `POST /api/auth/signup` — mobile sign-up.
- `POST /api/auth/login` — mobile login.
- `GET /api/map/data` — mobile map payload.
- `POST /api/user/status` — mobile status update.
- `POST /api/alerts/trigger` — mobile man-down trigger.
- `POST /api/alerts/accidental` — mark latest active SOS as accidental.

Heatmap overlay:

```bash
curl -o heatmap.png \
  "http://127.0.0.1:8000/v1/flood/heatmap.png?latitude=45.45&longitude=28.05&radius_meters=1000&lookback_days=30"
```

EFAS location forecast/warning:

```bash
curl \
  "http://127.0.0.1:8000/v1/efas/location?latitude=45.45&longitude=28.05&radius_meters=50000"
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
- GloFAS access depends on Copernicus Climate Data Store credentials when used as a CDS dataset.
- Open-Meteo is public and key-less; suitable for development without external credentials.
