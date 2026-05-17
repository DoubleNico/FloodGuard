# Operations and Troubleshooting

## Runtime Configuration

Backend environment variables:

| Variable | Default | Purpose |
| --- | --- | --- |
| `ENVIRONMENT` | `local` | Runtime label |
| `DATABASE_PATH` | `floodguard.db` | SQLite database file |
| `JWT_SECRET` | `change-this-dev-secret` | Token signing secret |
| `CORS_ORIGINS` | `*` | Comma-separated allowed origins |
| `CDSE_CLIENT_ID` | unset | Copernicus Data Space OAuth client |
| `CDSE_CLIENT_SECRET` | unset | Copernicus Data Space OAuth secret |
| `SENTINEL_HUB_BASE_URL` | `https://sh.dataspace.copernicus.eu` | Sentinel Hub API base |
| `SENTINEL_HUB_TOKEN_URL` | CDSE token URL | OAuth token endpoint |
| `EFAS_WMS_URL` | EFAS public WMS URL | EFAS WMS endpoint |
| `EFAS_WMS_TOKEN` | unset | Optional EFAS access token |
| `OPEN_METEO_BASE_URL` | `https://api.open-meteo.com/v1` | Open-Meteo API base |
| `OPEN_METEO_FLOOD_BASE_URL` | `https://flood-api.open-meteo.com/v1` | Open-Meteo Flood API base (GloFAS proxy) |
| `OVERPASS_URL` | Overpass public API | Admin boundary source |
| `REQUEST_TIMEOUT_SECONDS` | `45` | Backend external request timeout |
| `FORECAST_INTERVAL_SECONDS` | `1800` | Period between scheduler forecast cycles |
| `FORECAST_SCHEDULER_ENABLED` | `1` | Disable in-process scheduler with `0` (multi-worker, tests, separate worker) |

Mobile URLs are currently constants in `Flutter/lib/services/backend_service.dart`.

## Health Checks

Backend:

```bash
curl http://127.0.0.1:8000/health
```

Configuration:

```bash
curl http://127.0.0.1:8000/v1/config
```

Alerts:

```bash
curl http://127.0.0.1:8000/api/v1/alerts
```

Forecast for a site:

```bash
curl http://127.0.0.1:8000/api/sites/1/forecast
```

## Database Lifecycle

The backend creates and seeds the SQLite database on startup. It also applies lightweight schema backfills for mobile SOS metadata columns and forecast tables.

To reset local state:

```bash
cd floodguard-backend
rm -f floodguard.db
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Troubleshooting

### Mobile app cannot reach backend

Symptoms:

- Site list does not load.
- Push tokens fail to register.
- Authentication error appears in Flutter logs.

Checks:

- Android emulator should use `10.0.2.2`.
- Physical device should use the host LAN IP.
- Backend must bind to an address reachable by the device, for example `0.0.0.0`.

Example:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Copernicus integration returns errors

Checks:

```bash
curl http://127.0.0.1:8000/v1/config
```

If `credentials_configured` is false:

- Set `CDSE_CLIENT_ID`.
- Set `CDSE_CLIENT_SECRET`.
- Restart backend.

Also check:

- Area radius is not too large.
- Sentinel Hub credentials are valid.
- Network access to CDSE/Sentinel Hub is available.

### Forecast snapshot is missing or stale

Symptoms:

- Mobile app shows "No forecast available" for a site.
- Latest snapshot timestamp is more than one hour old.

Checks:

- Confirm Open-Meteo, Open-Meteo Flood, and EFAS endpoints are reachable from the backend host.
- Inspect backend logs for `[scheduler]` errors.
- Confirm `FORECAST_SCHEDULER_ENABLED=1` and `FORECAST_INTERVAL_SECONDS` is set sanely.
- Force a cycle for debugging: `curl -X POST http://127.0.0.1:8000/api/forecast/run`.

### Push alert not delivered

Symptoms:

- Threshold crossed, but no notification reaches the device.

Checks:

- `FCM_SERVICE_ACCOUNT_JSON` is set and readable.
- Mobile app registered a token via `POST /api/push/register`.
- Token has not been invalidated (FCM returns 404 / `INVALID_ARGUMENT`).

### Man-down alert does not show user name or mobility

Expected alert API fields:

```json
{
  "userName": "Andrei Ionescu",
  "userStatus": "Man Down",
  "mobilityInfo": {
    "level": "High",
    "user_status": "Man Down"
  }
}
```

Checks:

```bash
curl http://127.0.0.1:8000/api/v1/alerts
```

Fixes:

- Restart backend to run metadata backfill.
- Confirm the mobile app and backend are talking to the same instance.

### I'M FINE does not mark alert accidental

Expected behavior:

- Mobile posts `Safe` status.
- Mobile patches the known `alert_id`.
- If the alert ID is missing, mobile calls `/api/alerts/accidental`.
- Backend marks the user's latest active SOS as `accidental`.

### Flutter RenderFlex overflow

The flood warning screen is scrollable and should not overflow on short emulator screens. If another screen overflows, wrap the main content in a `SingleChildScrollView` or use flexible constraints instead of fixed height plus `Spacer`.

## Deployment Checklist

- Use HTTPS for the backend.
- Set strict `CORS_ORIGINS`.
- Replace demo users and passwords.
- Replace `JWT_SECRET`.
- Move from SQLite to Postgres + PostGIS for inundation polygons and concurrent usage.
- Configure persistent logs.
- Configure backup and recovery for alert and forecast history.
- Add monitoring for backend health, WebSocket connection counts, and external API failures.
- Validate site-level flood thresholds with local hydrology data.
- Configure FCM service-account credentials for production push.
- Review mobile GPS/privacy handling.
