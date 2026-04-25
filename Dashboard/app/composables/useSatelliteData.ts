export interface WaterLevelReading {
  station: string;
  level: number;
  warningLevel: number;
  criticalLevel: number;
  trend: "rising" | "stable" | "falling";
  timestamp: Date;
  lat: number;
  lng: number;
}
export interface FloodHeatmapZone {
  id: string;
  zone: string;
  lat: number;
  lng: number;
  intensity: number;
  radius: number;
  polygon: [number, number][];
  riskLevel: "low" | "moderate" | "high" | "critical";
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
  lat: number;
  lng: number;
}

const COORDS: Record<string, { lat: number; lng: number }> = {
  "Danube - Galati": { lat: 45.432, lng: 28.052 },
  "Siret - Sendreni": { lat: 45.398, lng: 28.018 },
  "Prut - Oancea": { lat: 45.465, lng: 28.075 },
  Port: { lat: 45.4268, lng: 28.0551 },
  "Faleza Dunarii": { lat: 45.4285, lng: 28.0461 },
  "Micro 17": { lat: 45.4215, lng: 28.0195 },
};

export const useSatelliteData = () => {
  const { get } = useApi();
  const waterLevels = useState<WaterLevelReading[]>("water-levels", () => []);
  const precipitation = useState<PrecipitationData[]>(
    "precipitation-data",
    () => [],
  );
  const galileoSatellites = useState<GalileoSatellite[]>(
    "galileo-satellites",
    () => [],
  );
  const ndwiReadings = useState<NDWIReading[]>("ndwi-readings", () => []);
  const floodHeatmap = useState<FloodHeatmapZone[]>("flood-heatmap", () => []);
  const loading = useState("satellite-loading", () => false);

  const refreshSatelliteData = async () => {
    loading.value = true;
    try {
      const [wl, ndwi, precip, gal, heatmap] = await Promise.all([
        get<any[]>("/api/v1/satellite/water-levels"),
        get<any[]>("/api/v1/satellite/ndwi"),
        get<any[]>("/api/v1/satellite/precipitation"),
        get<any[]>("/api/v1/satellite/galileo"),
        get<any[]>("/api/v1/satellite/heatmap"),
      ]);
      waterLevels.value = wl.map((r) => ({
        station: r.station,
        level: r.level,
        warningLevel: r.warningLevel,
        criticalLevel: r.criticalLevel,
        trend: r.trend,
        timestamp: new Date(),
        ...(COORDS[r.station] || { lat: 45.43, lng: 28.05 }),
      }));
      ndwiReadings.value = ndwi.map((r) => ({
        zone: r.zone,
        value: r.value,
        risk: r.risk,
        ...(COORDS[r.zone] || { lat: 45.43, lng: 28.05 }),
      }));
      galileoSatellites.value = gal.map((r) => ({
        id: r.id,
        name: r.name,
        status: r.status,
        signal: r.signal,
      }));
      floodHeatmap.value = heatmap.map((r) => ({
        ...r,
        radius:
          typeof r.radius === "number"
            ? r.radius
            : Math.max(30, Math.round(r.intensity * 100)),
      }));
    } catch {
      /* keep existing */
    } finally {
      loading.value = false;
    }
  };

  const operationalSatellites = computed(
    () =>
      galileoSatellites.value.filter((s) => s.status === "operational").length,
  );
  const averageSignal = computed(() => {
    const op = galileoSatellites.value.filter(
      (s) => s.status === "operational",
    );
    return op.length === 0
      ? 0
      : Math.round(op.reduce((s, x) => s + x.signal, 0) / op.length);
  });
  const ndwiRiskColor = (risk: NDWIReading["risk"]) =>
    ({
      low: "#22C55E",
      moderate: "#F59E0B",
      high: "#F97316",
      critical: "#EF4444",
    })[risk];

  let iv: ReturnType<typeof setInterval> | null = null;
  const startSimulation = () => {
    if (iv) return;
    iv = setInterval(() => {
      waterLevels.value = waterLevels.value.map((wl) => ({
        ...wl,
        level: wl.level + (Math.random() > 0.5 ? 1 : -1) * Math.random() * 3,
        timestamp: new Date(),
      }));
      galileoSatellites.value = galileoSatellites.value.map((s) => ({
        ...s,
        signal:
          s.status === "operational"
            ? Math.min(100, Math.max(70, s.signal + (Math.random() - 0.5) * 6))
            : s.signal,
      }));
    }, 5000);
  };
  const stopSimulation = () => {
    if (iv) {
      clearInterval(iv);
      iv = null;
    }
  };
  const heatmapIntensityColor = (i: number) =>
    i >= 0.75
      ? "#EF4444"
      : i >= 0.5
        ? "#F97316"
        : i >= 0.25
          ? "#F59E0B"
          : "#22C55E";

  if (import.meta.client && waterLevels.value.length === 0) {
    refreshSatelliteData();
  }

  return {
    waterLevels,
    precipitation,
    galileoSatellites,
    ndwiReadings,
    floodHeatmap,
    operationalSatellites,
    averageSignal,
    ndwiRiskColor,
    heatmapIntensityColor,
    startSimulation,
    stopSimulation,
    refreshSatelliteData,
    loading,
  };
};
