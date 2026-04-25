export interface Factory {
  id: string;
  name: string;
  location: string;
  lat: number;
  lng: number;
  status: "operational" | "warning" | "critical" | "offline";
  sensorCount: number;
  riskLevel: "low" | "moderate" | "high" | "critical";
  waterProximity: number;
  lastInspection: Date;
  employees: number;
}

export interface SensorReading {
  id: string;
  factoryId: string;
  name: string;
  type: "water-level" | "pressure" | "humidity" | "temperature" | "structural";
  value: number;
  unit: string;
  threshold: number;
  status: "online" | "warning" | "critical" | "offline";
  lastUpdate: Date;
}

export const useIndustrial = () => {
  const factories = useState<Factory[]>("factories", () => [
    { id: "F-001", name: "ArcelorMittal Galați", location: "Siderurgiștilor", lat: 45.4315, lng: 28.0098, status: "warning", sensorCount: 24, riskLevel: "high", waterProximity: 120, lastInspection: new Date(Date.now() - 86400000 * 7), employees: 4200 },
    { id: "F-002", name: "Vard Tulcea Shipyard", location: "Port Industrial", lat: 45.4278, lng: 28.0534, status: "operational", sensorCount: 12, riskLevel: "moderate", waterProximity: 45, lastInspection: new Date(Date.now() - 86400000 * 3), employees: 860 },
    { id: "F-003", name: "Damen Shipyards Galați", location: "Port", lat: 45.4301, lng: 28.0612, status: "critical", sensorCount: 18, riskLevel: "critical", waterProximity: 30, lastInspection: new Date(Date.now() - 86400000 * 1), employees: 1200 },
    { id: "F-004", name: "COMPA Industrial Park", location: "Bariera Traian", lat: 45.4487, lng: 28.0156, status: "operational", sensorCount: 8, riskLevel: "low", waterProximity: 890, lastInspection: new Date(Date.now() - 86400000 * 14), employees: 340 },
  ]);

  const sensors = useState<SensorReading[]>("sensor-readings", () => [
    { id: "S-001", factoryId: "F-001", name: "Danube Proximity Gauge", type: "water-level", value: 142, unit: "cm", threshold: 150, status: "warning", lastUpdate: new Date() },
    { id: "S-002", factoryId: "F-001", name: "Basement Humidity A1", type: "humidity", value: 89, unit: "%", threshold: 85, status: "critical", lastUpdate: new Date() },
    { id: "S-003", factoryId: "F-001", name: "Foundation Pressure P3", type: "pressure", value: 2.8, unit: "bar", threshold: 3.5, status: "online", lastUpdate: new Date() },
    { id: "S-004", factoryId: "F-001", name: "Structural Monitor B2", type: "structural", value: 0.12, unit: "mm", threshold: 0.5, status: "online", lastUpdate: new Date() },
    { id: "S-005", factoryId: "F-002", name: "Dock Water Level", type: "water-level", value: 78, unit: "cm", threshold: 100, status: "online", lastUpdate: new Date() },
    { id: "S-006", factoryId: "F-002", name: "Hull Bay Humidity", type: "humidity", value: 72, unit: "%", threshold: 80, status: "online", lastUpdate: new Date() },
    { id: "S-007", factoryId: "F-003", name: "Dry Dock Sensor", type: "water-level", value: 96, unit: "cm", threshold: 90, status: "critical", lastUpdate: new Date() },
    { id: "S-008", factoryId: "F-003", name: "Crane Foundation", type: "structural", value: 0.45, unit: "mm", threshold: 0.5, status: "warning", lastUpdate: new Date() },
    { id: "S-009", factoryId: "F-003", name: "Engine Room Temp", type: "temperature", value: 38, unit: "°C", threshold: 45, status: "online", lastUpdate: new Date() },
    { id: "S-010", factoryId: "F-004", name: "Perimeter Water", type: "water-level", value: 12, unit: "cm", threshold: 50, status: "online", lastUpdate: new Date() },
  ]);

  const criticalFactories = computed(() => factories.value.filter((f) => f.status === "critical" || f.status === "warning"));
  const criticalSensors = computed(() => sensors.value.filter((s) => s.status === "critical" || s.status === "warning"));
  const totalEmployeesAtRisk = computed(() => criticalFactories.value.reduce((sum, f) => sum + f.employees, 0));

  const factoryStatusColor = (status: Factory["status"]) => {
    const map = { operational: "#22C55E", warning: "#F59E0B", critical: "#EF4444", offline: "#6B7280" };
    return map[status];
  };

  const sensorStatusColor = (status: SensorReading["status"]) => {
    const map = { online: "#22C55E", warning: "#F59E0B", critical: "#EF4444", offline: "#6B7280" };
    return map[status];
  };

  return { factories, sensors, criticalFactories, criticalSensors, totalEmployeesAtRisk, factoryStatusColor, sensorStatusColor };
};
