# Hydralis Mobile App

Flutter mobile app for flood readiness, evacuation guidance, user status updates, and man-down SOS alerts.

## Features

- Map view with worker/user position and safe location marker.
- Backend map payload fetch from `/api/map/data`.
- WebSocket connection to dispatch events.
- Demo evacuation state machine.
- Flood warning screen and evacuation start action.
- Mobility/accessibility profile settings.
- Periodic mobile status updates.
- Automatic man-down SOS trigger.
- **I'M FINE** confirmation that marks the dispatch SOS alert as accidental.

## Tech Stack

- Flutter
- `flutter_map`
- `latlong2`
- `http`
- `web_socket_channel`
- `shared_preferences`
- `flutter_tts`
- `audioplayers`

## Setup

```bash
flutter pub get
flutter run
```

Run tests:

```bash
flutter test
flutter analyze
```

## Backend Configuration

Backend URLs are in:

```text
lib/services/backend_service.dart
```

Defaults:

```dart
final String baseUrl = 'http://10.0.2.2:8000/api';
final String apiV1Url = 'http://10.0.2.2:8000/api/v1';
final String wsUrl = 'ws://10.0.2.2:8000/api/v1/stream';
```

Use `10.0.2.2` for Android emulator. For a physical device, replace this with the backend host LAN IP and run the backend with:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Demo User

The app tries to login this demo user, then signs it up if missing:

| Field | Value |
| --- | --- |
| Email | `andrei.ionescu@hydralis.com` |
| Password | `secure_password` |
| Name | `Andrei Ionescu` |

## Important Files

| Path | Purpose |
| --- | --- |
| `lib/main.dart` | App entry point |
| `lib/services/backend_service.dart` | Backend REST and WebSocket client |
| `lib/screens/dashboard_screen.dart` | Main map, status, evacuation, man-down flow |
| `lib/screens/alert_screen.dart` | Flood warning and evacuation prompt |
| `lib/screens/profile_screen.dart` | Mobility/accessibility profile |
| `lib/screens/login_screen.dart` | Demo login screen |
| `lib/screens/signup_screen.dart` | Demo sign-up screen |

## Man-Down SOS Flow

1. Evacuation state starts.
2. Simulated movement stops and triggers man-down.
3. Mobile sends `POST /api/alerts/trigger` with:
   - user id
   - user name
   - `user_status: "Man Down"`
   - mobility profile
   - current location
4. Backend creates a published dispatch alert.
5. User can tap **I'M FINE**.
6. Mobile posts `Safe` status and marks the alert accidental.

## Troubleshooting

### Backend requests fail on emulator

Confirm backend is running on the host:

```bash
curl http://127.0.0.1:8000/health
```

Android emulator should use `10.0.2.2`, not `127.0.0.1`.

### SOS does not appear on dashboard

- Confirm mobile and dashboard point to the same backend.
- Confirm mobile logs show successful authentication.
- Check backend alerts:

```bash
curl http://127.0.0.1:8000/api/v1/alerts
```

### Alert screen overflows

`alert_screen.dart` uses a scrollable layout to support short emulator screens. If another screen overflows, avoid fixed-height `Column` layouts with `Spacer` and wrap content in `SingleChildScrollView`.

## Related Documentation

- [Project README](../README.md)
- [Architecture](../docs/architecture.md)
- [Development Setup](../docs/development.md)
- [API Reference](../docs/api-reference.md)
