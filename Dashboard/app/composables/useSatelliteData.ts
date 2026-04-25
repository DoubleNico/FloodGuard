export interface WaterLevelReading {
  station: string;
  level: number;
  warningLevel: number;
  criticalLevel: number;
  trend: "rising" | "stable" | "falling";
  timestamp: Date;
}

export interface PrecipitationData {
  date: string;
  actual: number | null;
  forecast: number | null;
}

export interface GalileoSatellite {
  id: string;
  name: string;
  status: "operational" | "testing" | "unavailable";
  signal: number;
}

export interface NDWIReading {
  zone: string;
  value: number;
  risk: "low" | "moderate" | "high" | "critical";
}

export const useSatelliteData = () => {
  const waterLevels = useState<WaterLevelReading[]>("water-levels", () => [
    { station: "Galați — Danube Main", level: 658, warningLevel: 600, criticalLevel: 700, trend: "rising", timestamp: new Date() },
    { station: "Galați — Siret Confluence", level: 423, warningLevel: 450, criticalLevel: 520, trend: "stable", timestamp: new Date() },
    { station: "Galați — Prut Downstream", level: 387, warningLevel: 400, criticalLevel: 480, trend: "falling", timestamp: new Date() },
  ]);

  const precipitation = useState<PrecipitationData[]>("precipitation-data", () => {
    const data: PrecipitationData[] = [];
    const today = new Date();
    for (let i = 6; i >= 0; i--) {
      const d = new Date(today);
      d.setDate(d.getDate() - i);
      data.push({ date: d.toLocaleDateString("en-US", { month: "short", day: "numeric" }), actual: Math.round(Math.random() * 35 + 5), forecast: null });
    }
    for (let i = 1; i <= 3; i++) {
      const d = new Date(today);
      d.setDate(d.getDate() + i);
      data.push({ date: d.toLocaleDateString("en-US", { month: "short", day: "numeric" }), actual: null, forecast: Math.round(Math.random() * 40 + 10) });
    }
    return data;
  });

  const galileoSatellites = useState<GalileoSatellite[]>("galileo-satellites", () => [
    { id: "E01", name: "GSAT0101", status: "operational", signal: 92 },
    { id: "E02", name: "GSAT0102", status: "operational", signal: 87 },
    { id: "E03", name: "GSAT0103", status: "operational", signal: 95 },
    { id: "E04", name: "GSAT0104", status: "testing", signal: 64 },
    { id: "E05", name: "GSAT0201", status: "operational", signal: 89 },
    { id: "E06", name: "GSAT0202", status: "operational", signal: 91 },
    { id: "E07", name: "GSAT0203", status: "unavailable", signal: 0 },
    { id: "E08", name: "GSAT0204", status: "operational", signal: 83 },
  ]);

  const ndwiReadings = useState<NDWIReading[]>("ndwi-readings", () => [
    { zone: "Port Industrial", value: 0.72, risk: "critical" },
    { zone: "Faleza Dunării", value: 0.61, risk: "high" },
    { zone: "Centru", value: 0.38, risk: "moderate" },
    { zone: "Micro 17-19", value: 0.45, risk: "moderate" },
    { zone: "Țiglina", value: 0.22, risk: "low" },
    { zone: "Siderurgiștilor", value: 0.55, risk: "high" },
    { zone: "Bariera Traian", value: 0.18, risk: "low" },
    { zone: "Mazepa", value: 0.31, risk: "moderate" },
  ]);

  const operationalSatellites = computed(() => galileoSatellites.value.filter((s) => s.status === "operational").length);

  const averageSignal = computed(() => {
    const op = galileoSatellites.value.filter((s) => s.status === "operational");
    if (op.length === 0) return 0;
    return Math.round(op.reduce((sum, s) => sum + s.signal, 0) / op.length);
  });

  const ndwiRiskColor = (risk: NDWIReading["risk"]) => {
    const map = { low: "#22C55E", moderate: "#F59E0B", high: "#F97316", critical: "#EF4444" };
    return map[risk];
  };

  let refreshInterval: ReturnType<typeof setInterval> | null = null;

  const startSimulation = () => {
    if (refreshInterval) return;
    refreshInterval = setInterval(() => {
      waterLevels.value = waterLevels.value.map((wl) => ({
        ...wl,
        level: wl.level + (Math.random() > 0.5 ? 1 : -1) * Math.random() * 3,
        timestamp: new Date(),
      }));
      galileoSatellites.value = galileoSatellites.value.map((s) => ({
        ...s,
        signal: s.status === "operational" ? Math.min(100, Math.max(70, s.signal + (Math.random() - 0.5) * 6)) : s.signal,
      }));
    }, 5000);
  };

  const stopSimulation = () => {
    if (refreshInterval) { clearInterval(refreshInterval); refreshInterval = null; }
  };

  return { waterLevels, precipitation, galileoSatellites, ndwiReadings, operationalSatellites, averageSignal, ndwiRiskColor, startSimulation, stopSimulation };
};
