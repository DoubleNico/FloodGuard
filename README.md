# Hydralis Flood Disaster Management System

Hydralis is an integrated flood disaster management platform with three primary software components:

- **Copernicus Flood Backend** (`copernicus-flood-backend/`): FastAPI service for flood screening, Sentinel Hub/Copernicus integration, EFAS overlays, persistent dispatch data, mobile APIs, and WebSocket events.
- **Dispatch Dashboard** (`Dashboard/`): Nuxt web application used by dispatchers, industrial operators, and administrators to monitor alerts, satellite intelligence, safe locations, industrial telemetry, and subscriptions.
- **Hydralis Mobile App** (`Flutter/`): Flutter mobile application for citizen/worker guidance, map awareness, evacuation flow, status updates, and man-down SOS alerts.

There is also an Arduino circuit asset under `Flood_monitoring_Arduino_circuit/` for the flood monitoring hardware concept.

## System Overview

```text
                         Copernicus Data Space / Sentinel Hub
                                      |
                                      v
Flutter Mobile App  <---- REST ---->  FastAPI Backend  <---- REST ---->  Nuxt Dispatch Dashboard
       |                              SQLite storage                         |
       |                                  |                                  |
       +---------- WebSocket events ------+---------- WebSocket events ------+
                                      |
                                      v
                              EFAS / OSM boundary data
```

The backend is the source of truth for alerts, mobile users, safe locations, industrial facilities, satellite data, and WebSocket updates. The dashboard and mobile app communicate with it through REST and WebSocket endpoints.

## Repository Layout

```text
.
├── copernicus-flood-backend/      FastAPI backend and tests
├── Dashboard/                     Nuxt dispatch dashboard
├── Flutter/                       Flutter mobile app
├── Flood_monitoring_Arduino_circuit/
│   └── circuit_image.png          Hardware concept image
├── docs/                          Project-level documentation
└── backend_spec.md                Earlier backend integration specification
```

## Quick Start

Start the backend first:

```bash
cd copernicus-flood-backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Start the dashboard:

```bash
cd Dashboard
npm install
NUXT_PUBLIC_API_BASE=http://127.0.0.1:8000 npm run dev
```

Start the mobile app:

```bash
cd Flutter
flutter pub get
flutter run
```

For the Android emulator, the mobile app defaults to `http://10.0.2.2:8000`, which maps to the host machine. For a physical device, update `Flutter/lib/services/backend_service.dart` to use the host machine LAN IP.

## Demo Credentials

The backend seeds demo dashboard users into SQLite during startup.

| Username | Password | Role |
| --- | --- | --- |
| `dispatcher_ion` | `password123` | Dispatcher |
| `dispatcher_ana` | `password123` | Dispatcher |

The mobile app authenticates a demo user automatically:

- Email: `andrei.ionescu@hydralis.com`
- Password: `secure_password`

## Important Workflows

### Mobile Man-Down SOS

1. Mobile evacuation flow detects zero movement.
2. Mobile calls `POST /api/alerts/trigger`.
3. Backend creates a published dispatch alert with:
   - user name
   - user status (`Man Down`)
   - mobility/safety level
   - precise location
4. Backend broadcasts `alert:mobile_emergency` over WebSocket.
5. Dashboard displays the SOS alert and reporter metadata.
6. If the user taps **I'M FINE**, mobile reports `Safe` and marks the latest SOS as `accidental`.

### Copernicus Flood Screening

1. A client requests flood data for a location or area.
2. Backend queries Copernicus Data Space/Sentinel Hub for recent Sentinel-1 scenes.
3. Backend classifies flood likelihood using VV backscatter water fraction and optional baseline comparison.
4. Backend returns JSON results or PNG heatmap overlays.

### Dispatch Alert Lifecycle

Alerts support these states:

```text
draft -> review -> approved -> published -> updated/closed
published -> accidental
```

Mobile SOS alerts are created as `published`; user confirmation through **I'M FINE** changes them to `accidental`.

## Documentation Index

- [Architecture](docs/architecture.md)
- [Development Setup](docs/development.md)
- [API Reference](docs/api-reference.md)
- [Operations and Troubleshooting](docs/operations.md)
- [Backend README](copernicus-flood-backend/README.md)
- [Dashboard README](Dashboard/README.md)
- [Mobile README](Flutter/README.md)
- [Arduino Circuit README](Flood_monitoring_Arduino_circuit/README.md)

## Verification

Backend:

```bash
cd copernicus-flood-backend
PYTHONPATH=. ./.venv/bin/pytest -q
```

Dashboard:

```bash
cd Dashboard
npm run build
```

Mobile:

```bash
cd Flutter
flutter test
flutter analyze
```

## Production Notes

- Replace demo credentials and JWT secret before deployment.
- Store Copernicus, EFAS, and JWT secrets in environment variables or a secret manager.
- Use a production database instead of SQLite for concurrent multi-user deployment.
- Put the backend behind TLS and configure strict CORS origins.
- Validate flood thresholds with local hydrology data before operational use.
