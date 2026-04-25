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

const generateMockAlerts = (): FloodAlert[] => {
  const now = new Date();
  return [
    {
      id: "ALR-001",
      type: "flood",
      severity: 4,
      status: "published",
      title: "Danube River Level Critical — Galați Sector",
      message:
        "Water levels at Galați monitoring station have exceeded 650cm. Immediate evacuation advisory for Port and Faleza Dunării zones. Citizens should proceed to designated safe locations.",
      affectedAreas: ["Port", "Faleza Dunării", "Centru"],
      createdAt: new Date(now.getTime() - 3600000 * 2),
      updatedAt: new Date(now.getTime() - 3600000),
      publishedAt: new Date(now.getTime() - 3600000),
      createdBy: "Dispatcher Ionescu",
      broadcastSent: true,
      recipientCount: 12847,
    },
    {
      id: "ALR-002",
      type: "flash-flood",
      severity: 3,
      status: "approved",
      title: "Flash Flood Warning — Micro 17-19",
      message:
        "Heavy rainfall forecast combined with saturated ground conditions. Moderate risk of localized flooding in low-lying residential areas.",
      affectedAreas: ["Micro 17", "Micro 18", "Micro 19"],
      createdAt: new Date(now.getTime() - 3600000 * 4),
      updatedAt: new Date(now.getTime() - 3600000 * 3),
      createdBy: "Dispatcher Popescu",
      broadcastSent: false,
      recipientCount: 0,
    },
    {
      id: "ALR-003",
      type: "storm",
      severity: 2,
      status: "review",
      title: "Severe Weather Advisory — Greater Galați",
      message:
        "Meteorological services forecast sustained winds exceeding 70km/h with heavy precipitation over the next 12 hours.",
      affectedAreas: ["Țiglina I", "Țiglina II", "Micro 38", "Micro 39"],
      createdAt: new Date(now.getTime() - 3600000 * 6),
      updatedAt: new Date(now.getTime() - 3600000 * 5),
      createdBy: "System (Auto-detected)",
      broadcastSent: false,
      recipientCount: 0,
    },
    {
      id: "ALR-004",
      type: "flood",
      severity: 5,
      status: "closed",
      title: "Danube Overflow — Siderurgiștilor Industrial Zone",
      message:
        "Critical flooding event resolved. All-clear issued for industrial sector. Post-incident damage assessment in progress.",
      affectedAreas: ["Siderurgiștilor", "Port"],
      createdAt: new Date(now.getTime() - 86400000 * 2),
      updatedAt: new Date(now.getTime() - 86400000),
      publishedAt: new Date(now.getTime() - 86400000 * 2),
      closedAt: new Date(now.getTime() - 86400000),
      createdBy: "Dispatcher Ionescu",
      broadcastSent: true,
      recipientCount: 8234,
    },
  ];
};

export const useAlerts = () => {
  const alerts = useState<FloodAlert[]>("flood-alerts", () =>
    generateMockAlerts()
  );
  const globalAlarmActive = useState<boolean>(
    "global-alarm-active",
    () => true
  );
  const lastBroadcastTime = useState<Date | null>(
    "last-broadcast-time",
    () => new Date(Date.now() - 3600000)
  );

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

  const createAlert = (
    data: Omit<
      FloodAlert,
      | "id"
      | "createdAt"
      | "updatedAt"
      | "broadcastSent"
      | "recipientCount"
      | "status"
    >
  ) => {
    const id = `ALR-${String(alerts.value.length + 1).padStart(3, "0")}`;
    const now = new Date();
    alerts.value.unshift({
      ...data,
      id,
      status: "draft",
      createdAt: now,
      updatedAt: now,
      broadcastSent: false,
      recipientCount: 0,
    });
    return id;
  };

  const updateAlertStatus = (id: string, status: AlertStatus) => {
    const alert = alerts.value.find((a) => a.id === id);
    if (alert) {
      alert.status = status;
      alert.updatedAt = new Date();
      if (status === "published") {
        alert.publishedAt = new Date();
      }
      if (status === "closed") {
        alert.closedAt = new Date();
      }
    }
  };

  const broadcastGlobalAlarm = (alertId: string) => {
    const alert = alerts.value.find((a) => a.id === alertId);
    if (alert) {
      alert.broadcastSent = true;
      alert.recipientCount = Math.floor(Math.random() * 15000) + 5000;
      alert.status = "published";
      alert.publishedAt = new Date();
      alert.updatedAt = new Date();
      globalAlarmActive.value = true;
      lastBroadcastTime.value = new Date();
    }
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

  return {
    alerts,
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
  };
};
