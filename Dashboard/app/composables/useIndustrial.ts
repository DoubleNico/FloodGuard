export interface Factory {
  id: string; name: string; location: string; lat: number; lng: number;
  status: "operational" | "warning" | "critical" | "offline";
  sensorCount: number; riskLevel: "low" | "moderate" | "high" | "critical";
  waterProximity: number; lastInspection: Date; employees: number;
}

export interface SensorReading {
  id: string; factoryId: string; name: string;
  type: "water-level" | "pressure" | "humidity" | "temperature" | "structural";
  value: number; unit: string; threshold: number;
  status: "online" | "warning" | "critical" | "offline"; lastUpdate: Date;
}

export const useIndustrial = () => {
  const { get } = useApi();
  const factories = useState<Factory[]>("factories", () => []);
  const sensors = useState<SensorReading[]>("sensor-readings", () => []);
  const loading = useState("industrial-loading", () => false);

  const refreshIndustrial = async () => {
    loading.value = true;
    try {
      const [fData, sData] = await Promise.all([
        get<{ factories: any[] }>("/api/v1/industrial/factories"),
        get<{ sensors: any[] }>("/api/v1/industrial/sensors"),
      ]);
      factories.value = fData.factories.map((f) => ({
        ...f,
        lastInspection: new Date(f.lastInspection),
      }));
      sensors.value = sData.sensors.map((s) => ({
        ...s,
        lastUpdate: new Date(s.lastUpdate),
      }));
    } catch { /* keep existing */ } finally { loading.value = false; }
  };

  const createFactory = async (data: Omit<Factory, "id" | "sensorCount" | "lastInspection">) => {
    const { post } = useApi();
    await post("/api/v1/industrial/factories", data);
    await refreshIndustrial();
  };

  const createSensor = async (data: Omit<SensorReading, "id" | "lastUpdate">) => {
    const { post } = useApi();
    await post("/api/v1/industrial/sensors", data);
    await refreshIndustrial();
  };

  const criticalFactories = computed(() => factories.value.filter((f) => f.status === "critical" || f.status === "warning"));
  const criticalSensors = computed(() => sensors.value.filter((s) => s.status === "critical" || s.status === "warning"));
  const totalEmployeesAtRisk = computed(() => criticalFactories.value.reduce((sum, f) => sum + f.employees, 0));

  const factoryStatusColor = (status: Factory["status"]) =>
    ({ operational: "#22C55E", warning: "#F59E0B", critical: "#EF4444", offline: "#6B7280" })[status];
  const sensorStatusColor = (status: SensorReading["status"]) =>
    ({ online: "#22C55E", warning: "#F59E0B", critical: "#EF4444", offline: "#6B7280" })[status];

  if (import.meta.client && factories.value.length === 0) { refreshIndustrial(); }

  return { factories, sensors, criticalFactories, criticalSensors, totalEmployeesAtRisk, factoryStatusColor, sensorStatusColor, refreshIndustrial, loading, createFactory, createSensor };
};
