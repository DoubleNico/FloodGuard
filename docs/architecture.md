# Architecture

This document describes how the Hydralis backend, dispatch dashboard, mobile app, and hardware concept fit together.

## Components

### Copernicus Flood Backend

Location: `copernicus-flood-backend/`

Technology:

- FastAPI
- SQLite
- Pydantic
- httpx
- Uvicorn

Responsibilities:

- Serve flood screening endpoints using Copernicus Data Space/Sentinel Hub.
- Serve EFAS WMS forecast and warning overlays.
- Serve OSM administrative boundary overlays.
- Persist dashboard/mobile domain data in SQLite.
- Authenticate dashboard and mobile clients with lightweight JWT tokens.
- Broadcast real-time events over `/api/v1/stream`.
- Seed demo data for local development.

Important backend modules:

| Module | Responsibility |
| --- | --- |
| `app/main.py` | FastAPI app, Copernicus/EFAS/map endpoints, router registration |
| `app/hydralis.py` | Dashboard auth, alerts, safe locations, satellite, industrial, subscription, WebSocket |
| `app/mobile.py` | Mobile auth, map aggregation, status updates, SOS trigger, accidental alert handling |
| `app/database.py` | SQLite schema, seed data, migration/backfill helpers |
| `app/flood.py` | Flood classification logic |
| `app/sentinel_hub.py` | Copernicus Data Space/Sentinel Hub client |
| `app/efas.py` | EFAS WMS integration |
| `app/admin_boundaries.py` | OSM/Overpass administrative boundaries |

### Dispatch Dashboard

Location: `Dashboard/`

Technology:

- Nuxt 4
- Vue 3
- Tailwind CSS 4
- Nuxt Icon
- Leaflet
- Chart.js

Responsibilities:

- Dispatcher and admin overview.
- Alert creation, review, broadcast, closure, accidental alert tracking.
- Real-time alert updates through WebSocket.
- Safe location management and map view.
- Satellite intelligence view: water levels, precipitation, NDWI, Galileo.
- Industrial facility and sensor monitoring.
- Subscription and plan usage view.

Important dashboard areas:

| Path | Responsibility |
| --- | --- |
| `app/pages/auth.vue` | Dashboard login |
| `app/layouts/dashboard.vue` | Dashboard shell, sidebar, stream connection |
| `app/pages/dashboard/alerts.vue` | Alert workflow and broadcast UI |
| `app/pages/dashboard/map.vue` | Safe location and flood map view |
| `app/pages/dashboard/satellite.vue` | Satellite and forecast intelligence |
| `app/pages/dashboard/industrial/*` | Industrial facility and sensor views |
| `app/composables/useAlerts.ts` | Alert state, API calls, WebSocket payload normalization |
| `app/composables/useStream.ts` | WebSocket connection and event routing |
| `app/composables/useApi.ts` | Runtime API client |

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

- Show map and nearby safe locations.
- Fetch backend map/flood warning payloads.
- Simulate evacuation state transitions.
- Track worker/user status.
- Trigger man-down SOS after zero movement.
- Let the user confirm **I'M FINE**, which marks the dispatch alert as accidental.
- Store mobility/accessibility preferences locally.

Important mobile files:

| Path | Responsibility |
| --- | --- |
| `lib/main.dart` | App entry point |
| `lib/services/backend_service.dart` | Backend REST/WebSocket client |
| `lib/screens/dashboard_screen.dart` | Main map, status, evacuation, man-down flow |
| `lib/screens/alert_screen.dart` | Flood warning and evacuation prompt |
| `lib/screens/profile_screen.dart` | Mobility/accessibility preferences |
| `lib/screens/login_screen.dart` | Demo login screen |
| `lib/screens/signup_screen.dart` | Demo sign-up screen |

### Hardware Concept

Location: `Flood_monitoring_Arduino_circuit/`

The repository includes a circuit image representing a flood monitoring Arduino concept. It is not currently wired into the backend data ingestion path. A production integration would usually add a sensor ingestion endpoint or MQTT bridge that writes readings into the backend `sensors` table and broadcasts dashboard updates.

See [Flood Monitoring Arduino Circuit](../Flood_monitoring_Arduino_circuit/README.md) for the component-level notes.

## Data Stores

The backend uses SQLite by default. `DATABASE_PATH` controls the location and defaults to `hydralis.db`.

Major tables:

| Table | Purpose |
| --- | --- |
| `users` | Dashboard users and roles |
| `alerts` | Alert lifecycle, mobile SOS alerts, broadcast metadata |
| `mobile_users` | FloodGuard mobile accounts |
| `user_status_updates` | Mobile status events |
| `emergency_triggers` | Mobile emergency trigger history |
| `safe_locations` | Shelters, assembly points, medical, supplies |
| `water_levels`, `ndwi_readings`, `precipitation_forecast`, `galileo_satellites` | Satellite/intelligence demo data |
| `factories`, `sensors` | Industrial monitoring |
| `subscription_status` | SaaS plan and usage counters |

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
| `alert:new` | Backend | Dashboard/Mobile | New dashboard alert created |
| `alert:updated` | Backend | Dashboard/Mobile | Alert status/message changed |
| `alert:mobile_emergency` | Backend | Dashboard | Mobile man-down SOS created |
| `user:status_update` | Backend | Dashboard/Mobile | Mobile user status changed |
| `user:status_emergency` | Backend | Dashboard | Mobile user needs help/emergency |
| `location:occupancy_update` | Backend | Dashboard | Safe location occupancy changed |

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
Dispatch dashboard
  -> upserts alert immediately from WebSocket payload
  -> refreshes alert list from REST for normal alert events
  -> displays reporter and mobility details
Mobile user taps I'M FINE
  -> POST /api/user/status with Safe
  -> PATCH /api/v1/alerts/{id}/status accidental, or fallback POST /api/alerts/accidental
Backend
  -> broadcasts alert:updated
Dispatch dashboard
  -> moves alert into Accidental tab
```

## Security Model

Current implementation is demo-oriented:

- Passwords are hashed with a demo SHA-256 helper.
- JWT tokens are generated locally with `JWT_SECRET`.
- Dashboard roles are dispatcher, industrial, and admin.
- Mobile endpoints require a mobile token for SOS actions.

For production:

- Replace password hashing with Argon2/bcrypt.
- Rotate and protect `JWT_SECRET`.
- Use HTTPS everywhere.
- Use a managed database.
- Add role-based authorization checks to all write endpoints.
- Audit SOS/alert lifecycle events.

## External Services

| Service | Used For | Configuration |
| --- | --- | --- |
| Copernicus Data Space / Sentinel Hub | Sentinel-1 catalog, statistical API, heatmap PNG | `CDSE_CLIENT_ID`, `CDSE_CLIENT_SECRET` |
| EFAS WMS | Flood forecast/warning overlays | `EFAS_WMS_URL`, optional `EFAS_WMS_TOKEN` |
| Overpass API | Administrative boundaries | `OVERPASS_URL` |
| OpenStreetMap tiles | Mobile map display | Flutter `flutter_map` tile layer |
