# API Reference

Base backend URL for local development:

```text
http://127.0.0.1:8000
```

OpenAPI documentation:

```text
http://127.0.0.1:8000/docs
```

## Health and Configuration

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Service health check |
| `GET` | `/v1/config` | Non-secret runtime configuration |
| `GET` | `/map` | Browser flood map page |

## Copernicus Flood Screening

### `POST /v1/catalog/latest`

Returns recent Sentinel-1 scenes for a requested area.

### `POST /v1/flood/detect`

Runs flood screening over a bbox, center/radius, or GeoJSON polygon.

```bash
curl -X POST http://127.0.0.1:8000/v1/flood/detect \
  -H "Content-Type: application/json" \
  -d '{
    "area": {
      "center": {
        "latitude": 45.45,
        "longitude": 28.05,
        "radius_meters": 2500
      }
    },
    "lookback_days": 30,
    "water_threshold_db": -17,
    "min_water_fraction": 0.10
  }'
```

### `GET /v1/flood/heatmap.png`

PNG flood-risk overlay.

```bash
curl -o heatmap.png \
  "http://127.0.0.1:8000/v1/flood/heatmap.png?latitude=45.45&longitude=28.05&radius_meters=1000"
```

## EFAS, GloFAS, and Boundaries

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/v1/admin/boundaries` | Administrative boundary GeoJSON |
| `GET` | `/v1/efas/layers` | Available EFAS WMS layers |
| `GET` | `/v1/efas/location` | EFAS location warning summary |
| `GET` | `/v1/efas/map.png` | EFAS WMS PNG overlay |
| `GET` | `/v1/glofas/location` | GloFAS location forecast (planned) |

## Sites and Forecasts (FloodGuard core, phase 2)

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/sites` | List industrial sites visible to the caller |
| `POST` | `/api/sites` | Create a new site (admin only) |
| `PATCH` | `/api/sites/{site_id}` | Update a site (admin only) |
| `DELETE` | `/api/sites/{site_id}` | Delete a site (admin only) |
| `GET` | `/api/sites/{site_id}/forecast` | Latest 48h forecast snapshot for a site |
| `GET` | `/api/sites/{site_id}/inundation.geojson` | Predicted inundation polygons (probability classes) |

Site payload (planned shape):

```json
{
  "id": 1,
  "name": "Galați Refinery North",
  "country": "RO",
  "location": { "lat": 45.45, "lng": 28.05 },
  "footprint_geojson": { "type": "Polygon", "coordinates": [...] },
  "thresholds": {
    "precip_mm_24h": 60,
    "precip_mm_48h": 90,
    "efas_probability": 0.4
  },
  "contacts": ["andrei.ionescu@floodguard.com"]
}
```

Forecast snapshot (planned shape):

```json
{
  "site_id": 1,
  "generated_at": "2026-05-08T08:30:00Z",
  "horizon_hours": 48,
  "risk_score": 0.72,
  "risk_class": "high",
  "drivers": {
    "precip_mm_24h": 78,
    "precip_mm_48h": 112,
    "efas_probability": 0.55,
    "glofas_probability": 0.41
  },
  "inundation_geojson": { "type": "FeatureCollection", "features": [...] }
}
```

## Push Registration (planned)

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/api/push/register` | Register an FCM token, scoped by site list |
| `DELETE` | `/api/push/register/{token}` | Unregister a token |

Request:

```json
{
  "token": "fcm-device-token",
  "site_ids": [1, 2, 5],
  "platform": "android"
}
```

## Alerts

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/v1/alerts` | List alerts |
| `POST` | `/api/v1/alerts` | Create alert (admin) |
| `PATCH` | `/api/v1/alerts/{alert_id}/status` | Update alert status |
| `PATCH` | `/api/v1/alerts/{alert_id}/message` | Update alert message |
| `POST` | `/api/v1/alerts/{alert_id}/broadcast` | Publish/broadcast alert |

Alert statuses:

```text
draft, review, approved, published, updated, closed, accidental
```

> The `draft → review → approved` lifecycle is being simplified for FloodGuard. Threshold-triggered alerts are created as `published` directly. Manual review is optional.

Mobile SOS alerts are created as published alerts and include:

```json
{
  "userName": "Andrei Ionescu",
  "userStatus": "Man Down",
  "mobilityInfo": {
    "has_issues": true,
    "level": "High",
    "user_status": "Man Down"
  }
}
```

## Mobile API

Mobile endpoints are under `/api`.

### Authentication

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/api/auth/signup` | Create mobile user |
| `POST` | `/api/auth/login` | Login mobile user |

### Map Data

`GET /api/map/data`

Query:

```text
lat=45.4353&lng=28.0080&radius=10km
```

Returns:

- nearby safe locations
- active alerts
- Copernicus flood warning summary
- EFAS summary
- forecast snapshots for sites within radius (planned)

### Status Update

`POST /api/user/status`

```json
{
  "user_id": "mob_001",
  "status": "Safe",
  "current_location": {
    "lat": 45.4353,
    "lng": 28.0080
  }
}
```

If status is `Safe`, the backend also attempts to mark the user's latest active SOS as `accidental`.

### Man-Down SOS

`POST /api/alerts/trigger`

Requires mobile bearer token.

```json
{
  "user_id": "mob_001",
  "user_name": "Andrei Ionescu",
  "user_status": "Man Down",
  "mobility_info": {
    "has_issues": true,
    "level": "High",
    "gravity": "High"
  },
  "current_location": {
    "lat": 45.4385,
    "lng": 28.0112
  },
  "message": "MAN-DOWN DETECTED: Zero movement for 60 seconds."
}
```

Response includes `alert_id`, `trigger_id`, and the created alert.

### Accidental Alert Fallback

`POST /api/alerts/accidental`

Requires mobile bearer token. Marks the latest active SOS for the authenticated mobile user as accidental, when the original `alert_id` is unknown.

## Operator Authentication

`POST /api/v1/auth/login`

```json
{
  "username": "operator",
  "password": "password123"
}
```

Response:

```json
{
  "token": "...",
  "user": {
    "id": "usr_001",
    "username": "operator",
    "role": "admin"
  }
}
```

> Operator login is retained for site management and alert review. Dispatcher-style multi-role workflow has been removed for FloodGuard.

## WebSocket

`WS /api/v1/stream`

Event shape:

```json
{
  "event": "alert:new",
  "payload": {}
}
```

Important events:

| Event | Payload |
| --- | --- |
| `alert:new` | New alert row |
| `alert:updated` | Updated alert row |
| `alert:mobile_emergency` | SOS payload with nested alert |
| `forecast:updated` | New forecast snapshot for a site (planned) |
| `user:status_update` | Mobile status update |
