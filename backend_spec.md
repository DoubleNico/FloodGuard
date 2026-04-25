# Backend Integration Specification

To transition the app from the Mock state to the Real backend, the backend must provide the following data structures. 

Since this is a real-time tracking and alerting application, we recommend a mix of **REST API** (for static/initial data like the 10-day forecast) and **WebSockets** (for real-time Galileo positioning and Sensor alerts).

---

## 1. Copernicus 10-Day Forecast (Passive Readiness)
Provides the macro-level risk assessment for the industrial site.

**Protocol:** REST API (GET) or WebSocket  
**Endpoint Example:** `GET /api/v1/copernicus/forecast?siteId=123`  

**Expected JSON Response:**
```json
{
  "site_id": "123",
  "timestamp": "2026-04-25T12:00:00Z",
  "forecast": {
    "risk_level": "LOW",           // "LOW", "MEDIUM", "HIGH", "CRITICAL"
    "forecast_days": 10,           // Standard 10-day window
    "confidence_score": 0.92,      // 0.0 to 1.0 probability
    "primary_threat": "Heavy Rain", // Human-readable threat
    "water_level_prediction_m": 0.2 // Predicted max water level in meters
  }
}
```

---

## 2. Galileo + EGNOS Telemetry (Worker Positioning)
Provides sub-meter precision tracking of the worker.

**Protocol:** WebSocket or MQTT (Push from App to Backend, and Backend to Dashboard)  
**Topic/Event Example:** `worker.telemetry.update`  

**Expected JSON Payload:**
```json
{
  "worker_id": "USR-8892",
  "timestamp": "2026-04-25T12:45:01Z",
  "location": {
    "latitude": 45.435312,
    "longitude": 28.008034,
    "altitude_m": 12.5,
    "accuracy_m": 0.8           // Important: EGNOS high precision (< 1m)
  },
  "geofence": {
    "is_inside": true,          // Boolean: is worker inside the "Industrial Geofence"
    "zone_name": "Sector 4G"
  },
  "movement": {
    "speed_mps": 1.2,           // Meters per second
    "heading_deg": 45.0,        // 0-360 degrees
    "is_stationary": false      // Becomes true if speed == 0 for 60 seconds (Man-Down trigger)
  }
}
```

---

## 3. Industrial Sensor Network (Critical Siren Trigger)
Real-time water level and structural sensors on the site.

**Protocol:** WebSocket (Push from Backend to App)  
**Topic/Event Example:** `sensor.alert.critical`  

**Expected JSON Payload:**
```json
{
  "event_id": "EVT-9921",
  "timestamp": "2026-04-25T12:48:22Z",
  "sensor": {
    "id": "SNS-GATE-01",
    "type": "WATER_LEVEL",
    "location_name": "Main Gate",
    "coordinates": {
      "latitude": 45.4360,
      "longitude": 28.0060
    }
  },
  "reading": {
    "value": 0.55,              // Current reading (e.g. 0.55 meters)
    "unit": "meters",
    "threshold": 0.50,          // The limit that was breached
    "trend": "RISING"           // "RISING", "STABLE", "FALLING"
  },
  "severity": "CRITICAL",       // Triggers the "Critical Siren" override
  "action_required": "EVACUATE" // Instructions for the app routing engine
}
```

---

## 4. Dispatcher / Auto-SOS (Man-Down Alert)
The payload the mobile app sends to the backend when the 60-second zero-movement watchdog triggers during an evacuation.

**Protocol:** REST API (POST) or WebSocket  
**Endpoint Example:** `POST /api/v1/emergency/sos`  

**Expected JSON Payload:**
```json
{
  "alert_type": "MAN_DOWN",
  "worker_id": "USR-8892",
  "triggered_at": "2026-04-25T12:51:00Z",
  "last_known_location": {
    "latitude": 45.4380,
    "longitude": 28.0120,
    "accuracy_m": 0.8
  },
  "context": {
    "active_evacuation_id": "EVAC-2026",
    "stationary_duration_sec": 60
  }
}
```

---

## Summary for the Backend Team
To make the Mobile App fully functional, the backend needs to expose:
1. **A static endpoint** for the Copernicus 10-day risk gauge.
2. **A WebSocket channel** where the app can stream Galileo GPS coordinates and receive sensor alerts.
3. **An SOS endpoint** to receive "Man-Down" emergency dispatches.
