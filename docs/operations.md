# Operations and Troubleshooting

## Runtime Configuration

Backend environment variables:

| Variable | Default | Purpose |
| --- | --- | --- |
| `ENVIRONMENT` | `local` | Runtime label |
| `DATABASE_PATH` | `hydralis.db` | SQLite database file |
| `JWT_SECRET` | `change-this-dev-secret` | Token signing secret |
| `CORS_ORIGINS` | `*` | Comma-separated allowed origins |
| `CDSE_CLIENT_ID` | unset | Copernicus Data Space OAuth client |
| `CDSE_CLIENT_SECRET` | unset | Copernicus Data Space OAuth secret |
| `SENTINEL_HUB_BASE_URL` | `https://sh.dataspace.copernicus.eu` | Sentinel Hub API base |
| `SENTINEL_HUB_TOKEN_URL` | CDSE token URL | OAuth token endpoint |
| `EFAS_WMS_URL` | EFAS public WMS URL | EFAS WMS endpoint |
| `EFAS_WMS_TOKEN` | unset | Optional EFAS access token |
| `OVERPASS_URL` | Overpass public API | Admin boundary source |
| `REQUEST_TIMEOUT_SECONDS` | `45` | Backend external request timeout |

Dashboard environment variables:

| Variable | Default | Purpose |
| --- | --- | --- |
| `NUXT_PUBLIC_API_BASE` | `http://localhost:8000` | Backend base URL |

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

## Database Lifecycle

The backend creates and seeds the SQLite database on startup. It also applies lightweight schema backfills for mobile SOS metadata columns.

If the dashboard shows old alert rows without mobile user metadata:

1. Restart the backend so schema/backfill code runs.
2. Refresh the dashboard.
3. Query `/api/v1/alerts` and confirm the alert includes `userName`, `userStatus`, and `mobilityInfo`.

To reset local state:

```bash
cd copernicus-flood-backend
rm -f hydralis.db
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Troubleshooting

### Dashboard cannot reach backend

Symptoms:

- Login fails.
- Alerts page remains empty.
- WebSocket reconnects repeatedly.

Checks:

```bash
curl http://127.0.0.1:8000/health
echo $NUXT_PUBLIC_API_BASE
```

Fix:

- Start backend first.
- Set `NUXT_PUBLIC_API_BASE=http://127.0.0.1:8000`.
- If accessing from another device, use the backend host LAN IP.

### Mobile app cannot reach backend

Symptoms:

- Map data does not update.
- SOS alerts do not appear on the dashboard.
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
- Hard-refresh dashboard.
- Confirm the dashboard is connected to the same backend instance as the mobile app.

### I'M FINE does not mark alert accidental

Expected behavior:

- Mobile posts `Safe` status.
- Mobile patches the known `alert_id`.
- If the alert ID is missing, mobile calls `/api/alerts/accidental`.
- Backend marks the user's latest active SOS as `accidental`.
- Dashboard receives `alert:updated`.

Checks:

```bash
curl http://127.0.0.1:8000/api/v1/alerts
```

The alert status should be `accidental`.

### Flutter RenderFlex overflow

The flood warning screen is scrollable and should not overflow on short emulator screens. If another screen overflows, wrap the main content in a `SingleChildScrollView` or use flexible constraints instead of fixed height plus `Spacer`.

## Deployment Checklist

- Use HTTPS for backend and dashboard.
- Set strict `CORS_ORIGINS`.
- Replace demo users and passwords.
- Replace `JWT_SECRET`.
- Move from SQLite to a managed database for concurrent usage.
- Configure persistent logs.
- Configure backup and recovery for alert history.
- Add monitoring for backend health, WebSocket connection counts, and external API failures.
- Validate flood classification thresholds with domain experts.
- Review mobile GPS/privacy handling.
