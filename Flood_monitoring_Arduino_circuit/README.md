# Flood Monitoring Arduino Circuit

This folder contains the hardware concept asset for the Hydralis flood monitoring circuit.

## Asset

| File | Purpose |
| --- | --- |
| `circuit_image.png` | Circuit diagram image for the Arduino-based flood monitoring concept |

## Intended Role

The circuit represents the field sensor side of the platform. In a production deployment, an Arduino or compatible microcontroller would collect local flood or water-level readings and publish them to the backend through one of these integration paths:

- HTTP sensor ingestion endpoint.
- MQTT broker with a backend bridge.
- Gateway service running near the field device.

The current repository does not include firmware or a live ingestion service for this circuit. The backend already contains industrial sensor data models and dashboard views, so the recommended next step is to add a dedicated ingestion API that validates device identity, records readings, and broadcasts updates to the dispatch dashboard.

## Integration Notes

- Use stable hardware identifiers for each deployed device.
- Authenticate device traffic before accepting telemetry.
- Store raw measurements and derived alert states separately.
- Include timestamp, device location, water level, battery state, and connectivity state in every reading.
- Keep emergency dispatch alerts separate from routine telemetry unless a reading crosses an operational threshold.

## Related Documentation

- [Project README](../README.md)
- [Architecture](../docs/architecture.md)
- [API Reference](../docs/api-reference.md)
