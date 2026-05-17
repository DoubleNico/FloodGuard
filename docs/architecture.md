# Architecture

How the FloodGuard backend, mobile app, and hardware concept fit together.

## Components

### FloodGuard Backend

Location: `floodguard-backend/`

Technology:

- FastAPI
- SQLite (Postgres + PostGIS recommended for production)
- Pydantic
- httpx
- Uvicorn

Responsibilities:

- Aggregate public meteorological data into per-site 48h flood-risk forecasts.
- Serve flood screening endpoints using Copernicus Data Space / Sentinel Hub.
- Serve EFAS / GloFAS forecast overlays.
- Serve OSM administrative boundary overlays.
- Persist industrial site configuration, thresholds, mobile users, alerts, and forecast snapshots.
- Authenticate mobile clients with lightweight JWT tokens.
- Push alerts to registered mobile devices when site thresholds are crossed.
- Broadcast real-time events over `/api/v1/stream` (mobile clients).
- Seed demo data for local development.

Important backend modules:

| Module | Responsibility |
| --- | --- |
| `app/main.py` | FastAPI app, Copernicus/EFAS/map endpoints, router registration |
| `app/floodguard.py` | Auth, alerts, mobile registrations, satellite, industrial, WebSocket |
| `app/mobile.py` | Mobile auth, map aggregation, status updates, SOS trigger, accidental alert handling |
| `app/database.py` | SQLite schema, seed data, migration/backfill helpers |
| `app/flood.py` | Sentinel-1 flood classification logic |
| `app/sentinel_hub.py` | Copernicus Data Space / Sentinel Hub client |
| `app/efas.py` | EFAS WMS integration |
| `app/admin_boundaries.py` | OSM / Overpass administrative boundaries |
| `app/forecast.py` | Forecast pipeline (Open-Meteo + EFAS/GloFAS aggregation, threshold engine) — *to be added* |
| `app/sites.py` | Industrial site configuration, thresholds — *to be added* |

### FloodGuard Mobile App

Location: `Flutter/`

Technology:

- Flutter
- flutter_map
- latlong2
- http
- web_socket_channel
- shared_preferences
- flutter_tts
- audioplayers

Responsibilities:

- Show site list with current and forecast risk levels.
- Render predicted inundation polygons on the site map.
- Receive push alerts when a site crosses a threshold.
- Display 48h forecast detail per site.
- Walk workers through evacuation flow.
- Trigger man-down SOS after zero-movement detection.
- Confirm **I'M FINE** to mark a SOS as accidental.
- Store mobility/accessibility preferences locally.

Important mobile files:

| Path | Responsibility |
| --- | --- |
| `lib/main.dart` | App entry point |
| `lib/services/backend_service.dart` | Backend REST/WebSocket client |
| `lib/screens/dashboard_screen.dart` | Site map, status, evacuation, man-down flow |
| `lib/screens/alert_screen.dart` | Flood warning and evacuation prompt |
| `lib/screens/profile_screen.dart` | Mobility/accessibility preferences |
| `lib/screens/login_screen.dart` | Demo login screen |
| `lib/screens/signup_screen.dart` | Demo sign-up screen |

### Hardware Concept

Location: `Flood_monitoring_Arduino_circuit/`

Optional Arduino water-level sensor concept. Not currently wired into ingestion. A production integration would add a sensor ingestion endpoint or MQTT bridge that writes readings into the backend `sensors` table and feeds the forecast aggregator alongside public-data sources.

See [Flood Monitoring Arduino Circuit](../Flood_monitoring_Arduino_circuit/README.md).

## Data Sources

| Source | Use | Cost / Region |
| --- | --- | --- |
| Copernicus Data Space / Sentinel Hub | Sentinel-1 SAR backscatter, observed flood extent | Free with registration, EU |
| CEMS / EFAS | Gridded flood probability forecasts up to 10 days | Free with registration, EU |
| GloFAS (via Open-Meteo Flood API) | River-discharge forecasts up to 210 days | Free, no key, EU-hosted |
| ECMWF Open Data | Open precipitation and temperature fields | Free, global |
| Open-Meteo | Hourly precipitation forecast API | Free, no key, EU-hosted |
| EEA Floods Directive | Flood-risk vector zones | Free, EU |
| OpenStreetMap / Overpass | Administrative boundaries, basemap tiles | Free, global |

## Data Stores

The backend uses SQLite by default. `DATABASE_PATH` controls the location and defaults to `floodguard.db`.

Major tables:

| Table | Purpose |
| --- | --- |
| `users` | Operator accounts (single role: admin) |
| `mobile_users` | FloodGuard mobile accounts |
| `sites` | Industrial site geometry, contact list, thresholds |
| `forecast_snapshots` | Per-site forecast outputs (risk score, precipitation, inundation polygon) |
| `alerts` | Threshold-triggered alerts and mobile SOS alerts |
| `user_status_updates` | Mobile status events |
| `emergency_triggers` | Mobile emergency trigger history |
| `safe_locations` | Shelters, assembly points, medical, supplies |
| `water_levels`, `ndwi_readings`, `precipitation_forecast`, `galileo_satellites` | Satellite/intelligence demo data |
| `factories`, `sensors` | Industrial monitoring (legacy / optional) |
| `push_tokens` | Registered mobile FCM/APNs tokens, scoped by site |

> Postgres + PostGIS is recommended before scaling; inundation polygon queries need spatial indexes.

## Real-Time Events

The backend WebSocket endpoint is:

```text
WS /api/v1/stream
```

Event envelope:

```json
{
  "event": "alert:updated",
  "payload": {}
}
```

Key events:

| Event | Producer | Consumer | Purpose |
| --- | --- | --- | --- |
| `alert:new` | Backend | Mobile | New threshold alert created |
| `alert:updated` | Backend | Mobile | Alert status changed |
| `forecast:updated` | Backend | Mobile | New forecast snapshot for a site |
| `user:status_update` | Backend | Mobile | Mobile user status changed |

## Forecast Pipeline

In-process asyncio scheduler (`app/scheduler.py`) launched in the FastAPI lifespan. Disable with `FORECAST_SCHEDULER_ENABLED=0` for multi-worker deployments or tests.

```text
forecast_loop (every FORECAST_INTERVAL_SECONDS, default 1800s)
  -> for each site in sites table:
       -> if latest snapshot is fresh (< interval/2): skip
       -> fetch Open-Meteo precipitation forecast (next 48h)
       -> fetch EFAS feature-info probability over site
       -> fetch GloFAS river-discharge forecast (Open-Meteo Flood API)
       -> normalize discharge against baseline → glofas_probability
       -> compute aggregate risk score
       -> compute inundation polygon (probability >= medium)
       -> insert forecast_snapshots row
       -> if risk_class in {high, extreme}:
            -> dispatch FCM push to push_tokens for site
```

Manual trigger for ops: `POST /api/forecast/run` runs one full cycle synchronously and returns a counters dict.

## Man-Down SOS Sequence

```text
Mobile dashboard
  -> detects zero movement
  -> POST /api/alerts/trigger
Backend
  -> validates mobile JWT
  -> loads mobile user profile
  -> stores emergency_triggers row
  -> stores published alerts row with user name, user_status, mobility_info
  -> broadcasts alert:mobile_emergency
Mobile user taps I'M FINE
  -> POST /api/user/status with Safe
  -> PATCH /api/v1/alerts/{id}/status accidental
Backend
  -> broadcasts alert:updated
```

## Security Model

Current implementation is demo-oriented:

- Passwords are hashed with a demo SHA-256 helper.
- JWT tokens are generated locally with `JWT_SECRET`.
- Mobile endpoints require a mobile token for SOS actions.

For production:

- Replace password hashing with Argon2 or bcrypt.
- Rotate and protect `JWT_SECRET`.
- Use HTTPS everywhere.
- Use a managed database.
- Add role-based authorization checks to all write endpoints.
- Audit SOS/alert lifecycle events.
- Store FCM service-account credentials in a secret manager.

## External Services

| Service | Used For | Configuration |
| --- | --- | --- |
| Copernicus Data Space / Sentinel Hub | Sentinel-1 catalog, statistical API, heatmap PNG | `CDSE_CLIENT_ID`, `CDSE_CLIENT_SECRET` |
| EFAS WMS | Flood forecast/warning overlays | `EFAS_WMS_URL`, optional `EFAS_WMS_TOKEN` |
| Open-Meteo Flood API (GloFAS proxy) | River-discharge forecast | `OPEN_METEO_FLOOD_BASE_URL` |
| Open-Meteo | Precipitation forecast | No credentials, public endpoint |
| ECMWF Open Data | Public forecast fields | No credentials |
| Overpass API | Administrative boundaries | `OVERPASS_URL` |
| OpenStreetMap tiles | Mobile map display | Flutter `flutter_map` tile layer |
| FCM | Push notification delivery | `FCM_SERVICE_ACCOUNT_JSON` |
