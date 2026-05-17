# FloodGuard

FloodGuard is a standalone mobile application for real-time flood prediction and alerting in industrial environments. It integrates hydrological models with localized precipitation and water-level thresholds to generate site-specific flood risk forecasts up to **48 hours** in advance. When a risk threshold is crossed, FloodGuard pushes actionable alerts to workers and safety managers, including predicted inundation zones.

Unlike generic weather apps, FloodGuard operates independently of external sensor networks, using only public meteorological data and pre-configured site parameters.

## Components

- **`floodguard-backend/`** — FastAPI backend. Hydrological forecast aggregation, site configuration, alerting, and mobile APIs.
- **`Flutter/`** — FloodGuard mobile app for industrial workers and safety managers.
- **`Flood_monitoring_Arduino_circuit/`** — Optional hardware concept (water-level sensor) that can extend public-data forecasts with local readings.

## Data Sources (free, EU-focused)

| Source | Use |
| --- | --- |
| **Copernicus Data Space / Sentinel Hub** | Sentinel-1 SAR backscatter for observed flood extent |
| **CEMS / EFAS** (European Flood Awareness System) | Gridded flood probability forecasts, up to 10 days |
| **GloFAS** | Global flood awareness forecasts, up to 30 days |
| **ECMWF Open Data** | Open precipitation/temperature forecast fields |
| **Open-Meteo** | Free hourly precipitation forecast API, EU-hosted, no API key |
| **EEA Floods Directive** | Static flood-risk vector zones |

## System Overview

```text
                Open-Meteo  ECMWF  EFAS / GloFAS  Sentinel-1 / Copernicus
                     \        |        |              /
                      \_______|________|_____________/
                                      |
                                      v
                            FastAPI Backend
                       (forecast pipeline + sites
                        + alert engine + push)
                                      |
                              REST  +  Push (FCM)
                                      |
                                      v
                          FloodGuard Mobile App
                  (site list, 48h forecast, inundation map,
                       evacuation, man-down SOS)
```

The backend is the source of truth for industrial sites, thresholds, forecast snapshots, alerts, and mobile registrations. The mobile app pulls forecasts and inundation overlays via REST and receives push alerts when thresholds are crossed.

## Repository Layout

```text
.
├── floodguard-backend/             FastAPI backend and tests
├── Flutter/                        FloodGuard mobile app
├── Flood_monitoring_Arduino_circuit/
│   └── circuit_image.png           Hardware concept image
├── docs/                           Project-level documentation
└── backend_spec.md                 Backend integration spec
```

## Quick Start

Backend:

```bash
cd floodguard-backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Mobile app:

```bash
cd Flutter
flutter pub get
flutter run
```

For the Android emulator the mobile app defaults to `http://10.0.2.2:8000`, which maps to the host machine. For a physical device, update `Flutter/lib/services/backend_service.dart` to use the host machine LAN IP.

## Demo Credentials

The mobile app authenticates a demo user automatically:

- Email: `andrei.ionescu@floodguard.com`
- Password: `secure_password`

## Important Workflows

### 48-hour Site Forecast

1. Backend pulls Open-Meteo precipitation forecast + EFAS/GloFAS gridded probabilities for each configured industrial site.
2. Aggregator computes a per-site risk score using site-specific thresholds (precipitation accumulation, water-level proxy, terrain factor).
3. Backend persists a forecast snapshot and exposes it through `GET /api/sites/{id}/forecast`.
4. When a snapshot crosses a threshold, the alert engine creates an alert and pushes to all registered mobile tokens for that site.

### Predicted Inundation Zones

1. Backend overlays EFAS/GloFAS flood probability rasters with the site's terrain footprint.
2. Output is a vector inundation polygon plus probability classes (low / medium / high / extreme).
3. Mobile app renders the overlay on the site map.

### Mobile Man-Down SOS

1. Mobile evacuation flow detects zero movement.
2. Mobile calls `POST /api/alerts/trigger`.
3. Backend records a published SOS alert with reporter, status (`Man Down`), location.
4. If the user taps **I'M FINE**, mobile reports `Safe` and the SOS is marked `accidental`.

### Observed Flood Screening (Sentinel-1)

1. Client requests flood data for a location or area.
2. Backend queries Copernicus Data Space / Sentinel Hub for recent Sentinel-1 scenes.
3. Backend classifies flood likelihood using VV backscatter water fraction and optional baseline comparison.
4. Backend returns JSON results or PNG heatmap overlays.

## Documentation

- [Architecture](docs/architecture.md)
- [Development Setup](docs/development.md)
- [API Reference](docs/api-reference.md)
- [Operations and Troubleshooting](docs/operations.md)
- [Backend README](floodguard-backend/README.md)
- [Mobile README](Flutter/README.md)
- [Arduino Circuit README](Flood_monitoring_Arduino_circuit/README.md)

## Verification

Backend:

```bash
cd floodguard-backend
PYTHONPATH=. ./.venv/bin/pytest -q
```

Mobile:

```bash
cd Flutter
flutter test
flutter analyze
```

## Production Notes

- Replace demo credentials and JWT secret before deployment.
- Store Copernicus, EFAS, GloFAS, ECMWF, and JWT secrets in environment variables or a secret manager.
- Replace SQLite with Postgres + PostGIS before scaling — inundation polygon queries require spatial indexes.
- Put the backend behind TLS and configure strict CORS origins.
- Validate per-site flood thresholds with local hydrology data before operational use.
- Configure FCM credentials for push delivery.
