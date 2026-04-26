# Hydralis Dispatch Dashboard

Nuxt dashboard for flood monitoring, emergency dispatch, satellite intelligence, safe locations, industrial telemetry, and subscription usage.

## Features

- Role-aware dashboard shell for dispatcher, industrial, and admin views.
- Alert workflow: draft, review, approved, published, closed, accidental.
- Mobile SOS alert display with reporter name, man-down status, and mobility information.
- Real-time updates from backend WebSocket `/api/v1/stream`.
- Safe location map and CRUD views.
- Satellite intelligence: water levels, NDWI, precipitation, Galileo status.
- Industrial factory and sensor monitoring.
- Subscription and usage screens.
- Light/dark theme support and English/Romanian locale files.

## Tech Stack

- Nuxt 4
- Vue 3
- Tailwind CSS 4
- Nuxt Icon
- Leaflet
- Chart.js

## Setup

```bash
npm install
```

Run local development server:

```bash
NUXT_PUBLIC_API_BASE=http://127.0.0.1:8000 npm run dev
```

Open:

```text
http://localhost:3000
```

Build:

```bash
npm run build
```

Preview:

```bash
npm run preview
```

## Runtime Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `NUXT_PUBLIC_API_BASE` | `http://localhost:8000` | FastAPI backend base URL |

## Demo Login

Use a seeded backend account:

| Username | Password | Role |
| --- | --- | --- |
| `dispatcher_ion` | `password123` | Dispatcher |
| `dispatcher_ana` | `password123` | Dispatcher |

## Important Files

| Path | Purpose |
| --- | --- |
| `app/pages/auth.vue` | Login page |
| `app/layouts/dashboard.vue` | Dashboard shell, sidebar, WebSocket lifecycle |
| `app/pages/dashboard/index.vue` | Overview |
| `app/pages/dashboard/alerts.vue` | Alerts and broadcast workflow |
| `app/pages/dashboard/map.vue` | Safe location map |
| `app/pages/dashboard/satellite.vue` | Satellite intelligence |
| `app/pages/dashboard/industrial/*` | Factory and sensor pages |
| `app/composables/useApi.ts` | REST client |
| `app/composables/useStream.ts` | WebSocket event handling |
| `app/composables/useAlerts.ts` | Alert state and normalization |
| `app/components/dashboard/AlertRow.vue` | Alert row rendering |

## Real-Time Alert Flow

The dashboard connects to:

```text
ws://<backend>/api/v1/stream
```

For `alert:mobile_emergency`, it upserts the alert immediately from the WebSocket payload so mobile SOS metadata appears without waiting for a full refresh.

Expected mobile SOS display fields:

- `userName`
- `userStatus`
- `mobilityInfo.level`

## Related Documentation

- [Project README](../README.md)
- [Architecture](../docs/architecture.md)
- [Development Setup](../docs/development.md)
- [API Reference](../docs/api-reference.md)
