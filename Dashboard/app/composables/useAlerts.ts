export type AlertSeverity = 1 | 2 | 3 | 4 | 5;
export type AlertType = "flood" | "flash-flood" | "storm" | "evacuation";
export type AlertStatus =
  | "draft"
  | "review"
  | "approved"
  | "published"
  | "updated"
  | "closed"
  | "accidental";

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
  userName?: string;
  userStatus?: string;
  mobilityInfo?: any;
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
  affected_areas?: string[] | string;
  createdAt: string;
  created_at?: string;
  updatedAt: string;
  updated_at?: string;
  publishedAt: string | null;
  published_at?: string | null;
  closedAt: string | null;
  closed_at?: string | null;
  createdBy: string;
  created_by?: string;
  broadcastSent: boolean;
  broadcast_sent?: boolean | number;
  recipientCount: number;
  recipient_count?: number;
  user_name?: string;
  userName?: string;
  user_status?: string;
  userStatus?: string;
  mobility_info?: any;
  mobilityInfo?: any;
}

const parseAlert = (raw: AlertApiRow): FloodAlert => {
  let mobility = raw.mobility_info ?? raw.mobilityInfo;
  if (typeof mobility === "string") {
    try {
      mobility = JSON.parse(mobility);
    } catch {
      mobility = null;
    }
  }
  const createdAt = raw.createdAt ?? raw.created_at ?? new Date().toISOString();
  const updatedAt = raw.updatedAt ?? raw.updated_at ?? createdAt;
  const affectedAreas =
    raw.affectedAreas ??
    parseAffectedAreas(raw.affected_areas) ??
    [];

  return {
    ...raw,
    id: raw.id,
    type: raw.type,
    severity: raw.severity,
    status: raw.status,
    title: raw.title,
    message: raw.message,
    affectedAreas,
    createdAt: new Date(createdAt),
    updatedAt: new Date(updatedAt),
    publishedAt: raw.publishedAt || raw.published_at ? new Date((raw.publishedAt ?? raw.published_at)!) : undefined,
    closedAt: raw.closedAt || raw.closed_at ? new Date((raw.closedAt ?? raw.closed_at)!) : undefined,
    createdBy: raw.createdBy ?? raw.created_by ?? "Mobile",
    broadcastSent: raw.broadcastSent ?? Boolean(raw.broadcast_sent),
    recipientCount: raw.recipientCount ?? raw.recipient_count ?? 0,
    userName: raw.user_name ?? raw.userName,
    userStatus:
      raw.user_status ??
      raw.userStatus ??
      (typeof mobility === "object" && mobility ? mobility.user_status : undefined),
    mobilityInfo: mobility,
  };
};

const parseAffectedAreas = (value: string[] | string | undefined) => {
  if (Array.isArray(value)) return value;
  if (typeof value !== "string") return undefined;
  try {
    return JSON.parse(value);
  } catch {
    return [value];
  }
};

const normalizeAlertPayload = (payload: any): AlertApiRow | null => {
  const source = payload?.broadcast ?? payload?.alert ?? payload;
  if (!source) return null;

  return {
    ...source,
    id: source.id ?? payload?.alert_id,
    user_name: source.user_name ?? source.userName ?? payload?.user_name ?? payload?.userName,
    userName: source.userName ?? source.user_name ?? payload?.userName ?? payload?.user_name,
    user_status: source.user_status ?? source.userStatus ?? payload?.user_status ?? payload?.userStatus,
    userStatus: source.userStatus ?? source.user_status ?? payload?.userStatus ?? payload?.user_status,
    mobility_info: source.mobility_info ?? source.mobilityInfo ?? payload?.mobility_info ?? payload?.mobilityInfo,
    mobilityInfo: source.mobilityInfo ?? source.mobility_info ?? payload?.mobilityInfo ?? payload?.mobility_info,
  } as AlertApiRow;
};

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
      globalAlarmActive.value = hasPublished;
    } catch {
      // keep existing data on error
    } finally {
      loading.value = false;
    }
  };

  const upsertAlertFromPayload = (payload: any) => {
    const raw = normalizeAlertPayload(payload);
    if (!raw?.id) return;

    const alert = parseAlert(raw);
    const index = alerts.value.findIndex((existing) => existing.id === alert.id);
    if (index === -1) {
      alerts.value = [alert, ...alerts.value];
    } else {
      alerts.value[index] = { ...alerts.value[index], ...alert };
    }
    globalAlarmActive.value = alerts.value.some((a) => a.status === "published");
  };

  const activeAlerts = computed(() =>
    alerts.value.filter(
      (a) =>
        a.status !== "closed" &&
        a.status !== "draft" &&
        a.status !== "accidental"
    )
  );

  const publishedAlerts = computed(() =>
    alerts.value.filter((a) => a.status === "published")
  );

  const pendingReview = computed(() =>
    alerts.value.filter((a) => a.status === "review")
  );

  const accidentalAlerts = computed(() =>
    alerts.value.filter((a) => a.status === "accidental")
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
    accidentalAlerts,
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
    upsertAlertFromPayload,
  };
};
