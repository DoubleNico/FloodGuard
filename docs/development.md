# Development Setup

Local setup for the FloodGuard backend and mobile app.

## Prerequisites

- Python 3.11 or newer
- Flutter SDK matching `Flutter/pubspec.yaml` (`sdk: ^3.11.5`)
- Android Studio or Xcode for mobile emulator/device development
- Optional: Copernicus Data Space credentials (for live Sentinel-1 calls)
- Optional: EFAS WMS token (for live EFAS overlays)

## Backend Setup

```bash
cd floodguard-backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
```

Edit `.env` as needed:

```bash
CDSE_CLIENT_ID=...
CDSE_CLIENT_SECRET=...
EFAS_WMS_TOKEN=...
JWT_SECRET=replace-this-for-any-shared-environment
DATABASE_PATH=floodguard.db
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

Run the backend:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Useful URLs:

- Health: `http://127.0.0.1:8000/health`
- OpenAPI: `http://127.0.0.1:8000/docs`
- Browser map: `http://127.0.0.1:8000/map`

Run tests:

```bash
PYTHONPATH=. ./.venv/bin/pytest -q
```

Run a single test:

```bash
PYTHONPATH=. ./.venv/bin/pytest tests/test_mobile.py::test_login -q
```

## Mobile Setup

```bash
cd Flutter
flutter pub get
flutter run
```

The mobile backend client is configured in:

```text
Flutter/lib/services/backend_service.dart
```

Defaults:

```dart
final String baseUrl = 'http://10.0.2.2:8000/api';
final String apiV1Url = 'http://10.0.2.2:8000/api/v1';
final String wsUrl = 'ws://10.0.2.2:8000/api/v1/stream';
```

Use `10.0.2.2` for Android emulator because it points to the host machine. For a physical phone, replace it with the backend host LAN IP:

```dart
final String baseUrl = 'http://192.168.1.20:8000/api';
```

Run checks:

```bash
flutter analyze
flutter test
```

## Recommended Local Startup Order

1. Backend on port `8000`.
2. Flutter emulator/app.

## Seed Data

The backend initializes the SQLite schema and demo data during FastAPI startup. Re-running the backend keeps existing rows and applies lightweight schema backfills.

To reset all local demo data:

```bash
cd floodguard-backend
rm -f floodguard.db
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Only delete the database when you intentionally want to lose local site, alert, and status history.

## Common Development Tasks

### Trigger a mobile SOS

1. Start backend.
2. Trigger the mobile man-down demo from the Flutter app.
3. Inspect alerts via REST.
4. Tap **I'M FINE** on mobile.
5. Confirm the alert flips to `accidental`.

### Query alerts directly

```bash
curl http://127.0.0.1:8000/api/v1/alerts
```

### Check Copernicus configuration

```bash
curl http://127.0.0.1:8000/v1/config
```

`credentials_configured` must be `true` for live Sentinel Hub calls.

### Inspect a site's 48h forecast

```bash
curl http://127.0.0.1:8000/api/sites/1/forecast
```

## Code Style Notes

- Backend tests use pytest and direct endpoint function calls for fast verification.
- Mobile API access should remain centralized in `BackendService`.
- Keep demo constants clearly separated from production configuration.
- Forecast aggregation logic should stay in `app/forecast.py`; do not inline data-source HTTP calls in route handlers.
