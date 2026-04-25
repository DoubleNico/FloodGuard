<template>
  <div class="flex items-center gap-3 p-4 rounded-xl border border-(--border-color) bg-(--surface-primary) hover:bg-(--surface-secondary)/30 transition-all">
    <div class="h-12 w-12 rounded-xl flex items-center justify-center shrink-0" :style="{ background: `${severityColor(alert.severity)}15` }">
      <Icon :name="typeIcon" class="h-6 w-6" :style="{ color: severityColor(alert.severity) }" />
    </div>

    <div class="flex-1 min-w-0">
      <div class="flex items-center gap-2 mb-1">
        <p class="text-sm font-semibold text-(--label-text) truncate">{{ alert.title }}</p>
        <Badge :variant="statusVariant">{{ statusLabel }}</Badge>
        <Badge :variant="alert.severity >= 4 ? 'danger' : alert.severity >= 3 ? 'default' : 'outline'">
          {{ severityLabel(alert.severity) }}
        </Badge>
      </div>
      <p class="text-xs text-(--hint-text) truncate">{{ alert.affectedAreas.join(', ') }} • {{ timeAgo(alert.updatedAt) }}</p>
      <p v-if="alert.broadcastSent" class="text-xs text-green-500 mt-0.5 flex items-center gap-1">
        <Icon name="mdi:check-circle" class="h-3 w-3" />
        Broadcast sent to {{ alert.recipientCount.toLocaleString() }} citizens
      </p>
      <div v-if="alert.userName || userStatusLabel || mobilityLabel" class="mt-2 p-2 rounded-lg border" :class="identityPanelClass">
        <p v-if="alert.userName" class="text-xs font-bold flex items-center gap-1" :class="identityTextClass">
          <Icon name="mdi:account-alert" class="h-3 w-3" />
          Reported by: {{ alert.userName }}
        </p>
        <p v-if="userStatusLabel" class="text-[10px] mt-0.5 flex items-center gap-1" :class="identitySubtextClass">
          <Icon name="mdi:heart-pulse" class="h-3 w-3" />
          User status: {{ userStatusLabel }}
        </p>
        <p v-if="mobilityLabel" class="text-[10px] mt-0.5 flex items-center gap-1" :class="identitySubtextClass">
          <Icon name="mdi:human-walker" class="h-3 w-3" />
          Mobility level: {{ mobilityLabel }}
        </p>
        <p v-if="alert.mobilityInfo?.has_issues" class="text-[10px] mt-0.5" :class="identitySubtextClass">
          Mobility assistance required
        </p>
      </div>
    </div>

    <div class="flex items-center gap-2 shrink-0">
      <Button v-if="alert.status === 'draft'" variant="outline" color="secondary" size="sm" @click="$emit('updateStatus', alert.id, 'review')">Submit for Review</Button>
      <Button v-if="alert.status === 'review'" variant="solid" color="primary" size="sm" @click="$emit('updateStatus', alert.id, 'approved')">Approve</Button>
      <Button v-if="alert.status === 'approved'" variant="solid" color="danger" size="sm" icon-left="mdi:broadcast" @click="$emit('broadcast', alert)">Broadcast</Button>
      <Button v-if="alert.status !== 'closed' && alert.status !== 'accidental'" variant="ghost" color="danger" size="sm" @click="$emit('updateStatus', alert.id, 'closed')">
        <Icon name="mdi:close-circle" class="h-4 w-4" />
      </Button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { AlertStatus, FloodAlert } from "~/composables/useAlerts";

const props = defineProps<{ alert: FloodAlert }>();
defineEmits<{
  broadcast: [alert: FloodAlert];
  updateStatus: [id: string, status: AlertStatus];
}>();

const { severityColor, severityLabel } = useAlerts();

const typeIcon = computed(() => {
  if (props.alert.status === "accidental") return "mdi:shield-check";
  const map: Record<string, string> = { flood: "mdi:water-alert", "flash-flood": "mdi:weather-pouring", storm: "mdi:weather-lightning", evacuation: "mdi:exit-run" };
  return map[props.alert.type] || "mdi:alert";
});

const statusVariant = computed(() => {
  const map: Record<string, string> = { draft: "outline", review: "secondary", approved: "default", published: "success", updated: "default", closed: "outline", accidental: "secondary" };
  return (map[props.alert.status] || "outline") as any;
});

const statusLabel = computed(() => props.alert.status === "accidental" ? "accidental" : props.alert.status);

const userStatusLabel = computed(() => props.alert.userStatus || props.alert.mobilityInfo?.user_status || "");

const mobilityLabel = computed(() => {
  const mobility = props.alert.mobilityInfo;
  if (!mobility) return "";
  return mobility.level || mobility.gravity || safetyLevelLabel(mobility.safety_level);
});

const safetyLevelLabel = (level: unknown) => {
  const labels: Record<number, string> = {
    0: "Safe",
    1: "Moderate",
    2: "At Risk",
    3: "High Risk",
  };
  return typeof level === "number" ? labels[level] || "Unknown" : "";
};

const identityPanelClass = computed(() =>
  props.alert.status === "accidental"
    ? "bg-emerald-500/5 border-emerald-500/10"
    : "bg-red-500/5 border-red-500/10",
);

const identityTextClass = computed(() =>
  props.alert.status === "accidental" ? "text-emerald-500" : "text-red-500",
);

const identitySubtextClass = computed(() =>
  props.alert.status === "accidental" ? "text-emerald-400" : "text-red-400",
);

const timeAgo = (date: Date) => {
  const seconds = Math.floor((Date.now() - date.getTime()) / 1000);
  if (seconds < 60) return "Just now";
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  return `${Math.floor(seconds / 86400)}d ago`;
};
</script>
