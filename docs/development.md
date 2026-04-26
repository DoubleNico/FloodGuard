# Development Setup

This guide describes local setup for all Hydralis components.

## Prerequisites

- Python 3.11 or newer
- Node.js 20 or newer
- npm
- Flutter SDK matching `Flutter/pubspec.yaml` (`sdk: ^3.11.5`)
- Android Studio or Xcode for mobile emulator/device development
- Optional: Copernicus Data Space credentials
- Optional: EFAS WMS token

## Backend Setup

```bash
cd copernicus-flood-backend
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
DATABASE_PATH=hydralis.db
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

## Dashboard Setup

```bash
cd Dashboard
npm install
NUXT_PUBLIC_API_BASE=http://127.0.0.1:8000 npm run dev
```

Default dashboard URL:

```text
http://localhost:3000
```

Build:

```bash
npm run build
```

Preview production build:

```bash
npm run preview
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

Use `10.0.2.2` for Android emulator because it points to the host machine. For a physical phone, replace it with the backend host LAN IP, for example:

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
2. Dashboard on port `3000`.
3. Flutter emulator/app.

This order prevents mobile/dashboard startup requests from hitting a missing backend.

## Seed Data

The backend initializes the SQLite schema and demo data during FastAPI startup. Re-running the backend keeps existing rows and applies lightweight schema backfills.

To reset all local demo data:

```bash
cd copernicus-flood-backend
rm -f hydralis.db
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Only delete the database when you intentionally want to lose local alert and status history.

## Common Development Tasks

### Verify SOS alert metadata

1. Start backend and dashboard.
2. Trigger the mobile man-down demo.
3. Open dashboard Alerts page.
4. Confirm the alert shows:
   - reporter name
   - user status
   - mobility level
5. Tap **I'M FINE** on mobile.
6. Confirm the alert moves to Accidental.

### Query alerts directly

```bash
curl http://127.0.0.1:8000/api/v1/alerts
```

### Check Copernicus configuration

```bash
curl http://127.0.0.1:8000/v1/config
```

`credentials_configured` must be `true` for live Sentinel Hub calls.

## Code Style Notes

- Backend tests use pytest and direct endpoint function calls for fast verification.
- Dashboard state lives in composables and should avoid page-local API duplication.
- Mobile API access should remain centralized in `BackendService`.
- Keep demo constants clearly separated from production configuration.
