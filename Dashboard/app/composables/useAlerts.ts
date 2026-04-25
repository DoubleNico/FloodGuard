export type AlertSeverity = 1 | 2 | 3 | 4 | 5;
export type AlertType = "flood" | "flash-flood" | "storm" | "evacuation";
export type AlertStatus =
  | "draft"
  | "review"
  | "approved"
  | "published"
  | "updated"
  | "closed";

export interface FloodAlert {
  id: string;
  type: AlertType;
  severity: AlertSeverity;
  status: AlertStatus;
  title: string;
  message: string;
  affectedAreas: string[];
  createdAt: Date;
  updatedAt: Date;
  publishedAt?: Date;
  closedAt?: Date;
  createdBy: string;
  broadcastSent: boolean;
  recipientCount: number;
}

const GALATI_ZONES = [
  "Centru",
  "Micro 13",
  "Micro 14",
  "Micro 16",
  "Micro 17",
  "Micro 18",
  "Micro 19",
  "Micro 20",
  "Micro 21",
  "Micro 38",
  "Micro 39",
  "Micro 40",
  "Țiglina I",
  "Țiglina II",
  "Țiglina III",
  "Mazepa I",
  "Mazepa II",
  "Siderurgiștilor",
  "Port",
  "Faleza Dunării",
  "Bariera Traian",
  "Dimitrie Cantemir",
];

interface AlertApiRow {
  id: string;
  type: AlertType;
  severity: AlertSeverity;
  status: AlertStatus;
  title: string;
  message: string;
  affectedAreas: string[];
  createdAt: string;
  updatedAt: string;
  publishedAt: string | null;
  closedAt: string | null;
  createdBy: string;
  broadcastSent: boolean;
  recipientCount: number;
}

const parseAlert = (raw: AlertApiRow): FloodAlert => ({
  ...raw,
  createdAt: new Date(raw.createdAt),
  updatedAt: new Date(raw.updatedAt),
  publishedAt: raw.publishedAt ? new Date(raw.publishedAt) : undefined,
  closedAt: raw.closedAt ? new Date(raw.closedAt) : undefined,
});

export const useAlerts = () => {
  const { get, post, patch } = useApi();

  const alerts = useState<FloodAlert[]>("flood-alerts", () => []);
  const loading = useState("alerts-loading", () => false);
  const globalAlarmActive = useState<boolean>(
    "global-alarm-active",
    () => false
  );
  const lastBroadcastTime = useState<Date | null>(
    "last-broadcast-time",
    () => null
  );

  const refreshAlerts = async () => {
    loading.value = true;
    try {
      const data = await get<{ alerts: AlertApiRow[] }>("/api/v1/alerts");
      alerts.value = data.alerts.map(parseAlert);
      const hasPublished = alerts.value.some((a) => a.status === "published");
      if (hasPublished && !globalAlarmActive.value) {
        globalAlarmActive.value = true;
      }
    } catch {
      // keep existing data on error
    } finally {
      loading.value = false;
    }
  };

  const activeAlerts = computed(() =>
    alerts.value.filter(
      (a) => a.status !== "closed" && a.status !== "draft"
    )
  );

  const publishedAlerts = computed(() =>
    alerts.value.filter((a) => a.status === "published")
  );

  const pendingReview = computed(() =>
    alerts.value.filter((a) => a.status === "review")
  );

  const totalRecipients = computed(() =>
    alerts.value.reduce((sum, a) => sum + a.recipientCount, 0)
  );

  const highestSeverity = computed(() => {
    const active = activeAlerts.value;
    if (active.length === 0) return 0;
    return Math.max(...active.map((a) => a.severity));
  });

  const createAlert = async (
    data: {
      type: AlertType;
      severity: AlertSeverity;
      title: string;
      message: string;
      affectedAreas: string[];
      createdBy: string;
    }
  ) => {
    await post("/api/v1/alerts", {
      type: data.type,
      severity: data.severity,
      title: data.title,
      message: data.message,
      affectedAreas: data.affectedAreas,
    });
    await refreshAlerts();
  };

  const updateAlertStatus = async (id: string, status: AlertStatus) => {
    await patch(`/api/v1/alerts/${id}/status`, { status });
    await refreshAlerts();
  };

  const broadcastGlobalAlarm = async (alertId: string) => {
    await post(`/api/v1/alerts/${alertId}/broadcast`);
    globalAlarmActive.value = true;
    lastBroadcastTime.value = new Date();
    await refreshAlerts();
  };

  const dismissGlobalAlarm = () => {
    globalAlarmActive.value = false;
  };

  const severityLabel = (severity: AlertSeverity) => {
    switch (severity) {
      case 1:
        return "Advisory";
      case 2:
        return "Watch";
      case 3:
        return "Warning";
      case 4:
        return "Critical";
      case 5:
        return "Extreme";
    }
  };

  const severityColor = (severity: AlertSeverity) => {
    switch (severity) {
      case 1:
        return "#3B82F6";
      case 2:
        return "#F59E0B";
      case 3:
        return "#F97316";
      case 4:
        return "#EF4444";
      case 5:
        return "#7F1D1D";
    }
  };

  if (import.meta.client && alerts.value.length === 0) {
    refreshAlerts();
  }

  return {
    alerts,
    loading,
    activeAlerts,
    publishedAlerts,
    pendingReview,
    totalRecipients,
    highestSeverity,
    globalAlarmActive,
    lastBroadcastTime,
    galatiZones: GALATI_ZONES,
    createAlert,
    updateAlertStatus,
    broadcastGlobalAlarm,
    dismissGlobalAlarm,
    severityLabel,
    severityColor,
    refreshAlerts,
  };
};
