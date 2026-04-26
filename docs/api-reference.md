# API Reference

Base backend URL for local development:

```text
http://127.0.0.1:8000
```

OpenAPI documentation is available at:

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

Example:

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

Returns a PNG flood-risk overlay.

```bash
curl -o heatmap.png \
  "http://127.0.0.1:8000/v1/flood/heatmap.png?latitude=45.45&longitude=28.05&radius_meters=1000"
```

## EFAS and Boundaries

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/v1/admin/boundaries` | Administrative boundary GeoJSON |
| `GET` | `/v1/efas/layers` | Available EFAS WMS layers |
| `GET` | `/v1/efas/location` | EFAS location warning summary |
| `GET` | `/v1/efas/map.png` | EFAS WMS PNG overlay |

Example:

```bash
curl \
  "http://127.0.0.1:8000/v1/efas/location?latitude=45.45&longitude=28.05&radius_meters=50000"
```

## Dashboard API

All dashboard endpoints are under `/api/v1`.

### Authentication

`POST /api/v1/auth/login`

Request:

```json
{
  "username": "dispatcher_ion",
  "password": "password123"
}
```

Response:

```json
{
  "token": "...",
  "user": {
    "id": "usr_001",
    "username": "dispatcher_ion",
    "role": "dispatcher"
  }
}
```

### Alerts

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/v1/alerts` | List alerts |
| `POST` | `/api/v1/alerts` | Create draft alert |
| `PATCH` | `/api/v1/alerts/{alert_id}/status` | Update workflow state |
| `PATCH` | `/api/v1/alerts/{alert_id}/message` | Update alert message |
| `POST` | `/api/v1/alerts/{alert_id}/broadcast` | Publish/broadcast alert |

Alert statuses:

```text
draft, review, approved, published, updated, closed, accidental
```

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

### Safe Locations

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/v1/locations` | List safe locations |
| `POST` | `/api/v1/locations` | Create safe location |
| `PATCH` | `/api/v1/locations/{location_id}` | Update safe location |
| `DELETE` | `/api/v1/locations/{location_id}` | Delete safe location |

### Satellite Intelligence

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/v1/satellite/water-levels` | Water level stations |
| `GET` | `/api/v1/satellite/ndwi` | NDWI readings |
| `GET` | `/api/v1/satellite/precipitation` | Precipitation forecast |
| `GET` | `/api/v1/satellite/galileo` | Galileo satellite status |
| `GET` | `/api/v1/satellite/heatmap` | Flood heatmap demo data |

### Industrial Monitoring

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/v1/industrial/factories` | List factories |
| `POST` | `/api/v1/industrial/factories` | Create factory |
| `GET` | `/api/v1/industrial/sensors` | List sensors |
| `POST` | `/api/v1/industrial/sensors` | Create sensor |

### Subscription

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/v1/subscription/status` | Current tier and usage |

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

### Status Update

`POST /api/user/status`

Request:

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

Request:

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

Response includes `alert_id`, `trigger_id`, and the created dispatch alert.

### Accidental Alert Fallback

`POST /api/alerts/accidental`

Requires mobile bearer token. Marks the latest active SOS for the authenticated mobile user as accidental. This is used when the mobile app did not retain the original `alert_id`.

## WebSocket

`WS /api/v1/stream`

Event shape:

```json
{
  "event": "alert:mobile_emergency",
  "payload": {}
}
```

Important events:

| Event | Payload |
| --- | --- |
| `alert:new` | Alert row |
| `alert:updated` | Alert row |
| `alert:mobile_emergency` | SOS payload with nested created alert |
| `user:status_update` | Mobile status update |
| `user:status_emergency` | Mobile emergency/help status |
| `location:occupancy_update` | Safe location update |
