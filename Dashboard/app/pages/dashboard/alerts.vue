<template>
  <div class="space-y-6 max-w-[1400px] mx-auto">
    <div
      class="flex flex-col sm:flex-row sm:items-center justify-between gap-4"
    >
      <div>
        <h1 class="text-2xl font-bold text-(--label-text) tracking-tight">
          Alerts & Broadcast
        </h1>
        <p class="text-sm text-(--hint-text) mt-1">
          Manage flood alerts and send emergency broadcasts
        </p>
      </div>
      <div class="flex items-center gap-3">
        <Button
          variant="outline"
          color="primary"
          icon-left="mdi:plus"
          @click="showCreateModal = true"
          >New Alert</Button
        >
        <Button
          v-if="activeAlerts.length > 0"
          variant="solid"
          color="danger"
          icon-left="mdi:broadcast"
          class="alarm-ring"
          @click="openGlobalBroadcastModal"
        >
          Broadcast Global Alarm
        </Button>
      </div>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard
        icon="mdi:bell-ring"
        label="Active Alerts"
        :value="activeAlerts.length"
        glow-color="danger"
        icon-bg="#EF4444"
      />
      <StatCard
        icon="mdi:clock-check"
        label="Pending Review"
        :value="pendingReview.length"
        glow-color="warning"
        icon-bg="#F59E0B"
      />
      <StatCard
        icon="mdi:shield-check"
        label="Accidental"
        :value="accidentalAlerts.length"
        glow-color="success"
        icon-bg="#22C55E"
      />
      <StatCard
        icon="mdi:broadcast"
        label="Broadcasts Sent"
        :value="publishedAlerts.length"
        glow-color="success"
        icon-bg="#22C55E"
      />
      <StatCard
        icon="mdi:account-group"
        label="Total Notified"
        :value="totalRecipients"
        glow-color="info"
        icon-bg="#3B82F6"
      />
    </div>

    <Tabs v-model="activeTab" default-value="all">
      <TabsList>
        <TabsTrigger value="all">All Alerts</TabsTrigger>
        <TabsTrigger value="published">Published</TabsTrigger>
        <TabsTrigger value="review">Pending Review</TabsTrigger>
        <TabsTrigger value="accidental">Accidental</TabsTrigger>
        <TabsTrigger value="closed">Closed</TabsTrigger>
      </TabsList>

      <TabsContent value="all">
        <div class="space-y-3 mt-4">
          <AlertRow
            v-for="alert in alerts"
            :key="alert.id"
            :alert="alert"
            @broadcast="onBroadcast"
            @update-status="onUpdateStatus"
          />
        </div>
      </TabsContent>
      <TabsContent value="published">
        <div class="space-y-3 mt-4">
          <AlertRow
            v-for="alert in publishedAlerts"
            :key="alert.id"
            :alert="alert"
            @broadcast="onBroadcast"
            @update-status="onUpdateStatus"
          />
        </div>
      </TabsContent>
      <TabsContent value="review">
        <div class="space-y-3 mt-4">
          <AlertRow
            v-for="alert in pendingReview"
            :key="alert.id"
            :alert="alert"
            @broadcast="onBroadcast"
            @update-status="onUpdateStatus"
          />
        </div>
      </TabsContent>
      <TabsContent value="accidental">
        <div class="space-y-3 mt-4">
          <AlertRow
            v-for="alert in accidentalAlerts"
            :key="alert.id"
            :alert="alert"
            @broadcast="onBroadcast"
            @update-status="onUpdateStatus"
          />
        </div>
      </TabsContent>
      <TabsContent value="closed">
        <div class="space-y-3 mt-4">
          <AlertRow
            v-for="alert in closedAlerts"
            :key="alert.id"
            :alert="alert"
            @broadcast="onBroadcast"
            @update-status="onUpdateStatus"
          />
        </div>
      </TabsContent>
    </Tabs>

    <Modal v-model="showCreateModal" title="Create New Alert" size="lg">
      <Form class="space-y-4" @submit="handleCreateAlert">
        <CustomSelect
          v-model="newAlert.type"
          label="Alert Type"
          :options="alertTypeOptions"
          :required="true"
        />
        <CustomSelect
          v-model="newAlert.severity"
          label="Severity"
          :options="severityOptions"
          :required="true"
        />
        <Input
          v-model="newAlert.title"
          label="Alert Title"
          placeholder="e.g. Danube flood warning for Port area"
          :required="true"
        />
        <Textarea
          v-model="newAlert.message"
          label="Message"
          placeholder="Detailed alert message for citizens..."
          :rows="4"
          :required="true"
        />
        <CustomSelect
          v-model="newAlert.affectedAreas"
          label="Affected Areas"
          :options="galatiZones.map((z) => ({ label: z, value: z }))"
          :required="true"
        />
      </Form>
      <template #footer="{ close }">
        <Button variant="outline" color="secondary" @click="close"
          >Cancel</Button
        >
        <Button variant="solid" color="primary" @click="handleCreateAlert"
          >Create Alert</Button
        >
      </template>
    </Modal>

    <Modal
      v-model="showBroadcastModal"
      title="Broadcast Global Alarm"
      size="md"
    >
      <div class="text-center space-y-4">
        <div
          class="h-20 w-20 mx-auto rounded-full bg-red-500/10 flex items-center justify-center alarm-ring"
        >
          <Icon name="mdi:broadcast" class="h-10 w-10 text-red-500" />
        </div>
        <h3 class="text-xl font-bold text-(--label-text)">
          Send Emergency Broadcast?
        </h3>
        <p class="text-sm text-(--hint-text)">
          This will send a high-priority push notification to all registered
          citizens in the affected zones. This action cannot be undone.
        </p>

        <div
          v-if="!isGlobalBroadcast"
          class="p-3 rounded-xl bg-(--surface-secondary) text-left"
        >
          <p class="text-xs text-(--hint-text) mb-1">Alert to broadcast:</p>
          <p class="text-sm font-medium text-(--label-text)">
            {{ broadcastTarget?.title || "Select an alert" }}
          </p>
        </div>
        <div v-else class="text-left mt-4">
          <CustomSelect
            v-model="selectedBroadcastAlertId"
            label="Select Alert to Broadcast"
            :options="
              broadcastableAlerts.map((a) => ({ label: a.title, value: a.id }))
            "
          />
        </div>
      </div>
      <template #footer="{ close }">
        <Button variant="outline" color="secondary" @click="close"
          >Cancel</Button
        >
        <Button
          variant="solid"
          color="danger"
          icon-left="mdi:broadcast"
          :disabled="isGlobalBroadcast && !selectedBroadcastAlertId"
          @click="confirmBroadcast(close)"
        >
          Confirm Broadcast
        </Button>
      </template>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import type { AlertStatus, FloodAlert } from "~/composables/useAlerts";

definePageMeta({ layout: "dashboard", middleware: "auth" });

const {
  alerts,
  activeAlerts,
  publishedAlerts,
  pendingReview,
  accidentalAlerts,
  totalRecipients,
  galatiZones,
  createAlert,
  updateAlertStatus,
  broadcastGlobalAlarm,
  severityLabel,
} = useAlerts();

const activeTab = ref("all");
const showCreateModal = ref(false);
const showBroadcastModal = ref(false);
const broadcastTarget = ref<FloodAlert | null>(null);
const isGlobalBroadcast = ref(false);
const selectedBroadcastAlertId = ref("");

const closedAlerts = computed(() =>
  alerts.value.filter((a) => a.status === "closed"),
);
const broadcastableAlerts = computed(() =>
  alerts.value.filter(
    (a) => a.status === "approved" || a.status === "published",
  ),
);

const newAlert = reactive({
  type: "",
  severity: "",
  title: "",
  message: "",
  affectedAreas: "",
});

const alertTypeOptions = [
  { label: "Flood", value: "flood" },
  { label: "Flash Flood", value: "flash-flood" },
  { label: "Storm", value: "storm" },
  { label: "Evacuation", value: "evacuation" },
];

const severityOptions = [
  { label: "1 — Advisory", value: "1" },
  { label: "2 — Watch", value: "2" },
  { label: "3 — Warning", value: "3" },
  { label: "4 — Critical", value: "4" },
  { label: "5 — Extreme", value: "5" },
];

const handleCreateAlert = () => {
  if (!newAlert.title || !newAlert.type) return;
  createAlert({
    type: newAlert.type as any,
    severity: (parseInt(newAlert.severity) || 3) as any,
    title: newAlert.title,
    message: newAlert.message,
    affectedAreas: newAlert.affectedAreas
      ? [newAlert.affectedAreas]
      : ["Centru"],
    createdBy: "Current Dispatcher",
  });
  showCreateModal.value = false;
  Object.assign(newAlert, {
    type: "",
    severity: "",
    title: "",
    message: "",
    affectedAreas: "",
  });
};

const openGlobalBroadcastModal = () => {
  isGlobalBroadcast.value = true;
  broadcastTarget.value = null;
  selectedBroadcastAlertId.value = "";
  showBroadcastModal.value = true;
};

const onBroadcast = (alert: FloodAlert) => {
  isGlobalBroadcast.value = false;
  broadcastTarget.value = alert;
  showBroadcastModal.value = true;
};

const confirmBroadcast = (close: () => void) => {
  if (isGlobalBroadcast.value && selectedBroadcastAlertId.value) {
    broadcastGlobalAlarm(selectedBroadcastAlertId.value);
  } else if (broadcastTarget.value) {
    broadcastGlobalAlarm(broadcastTarget.value.id);
  }
  close();
};

const onUpdateStatus = (id: string, status: AlertStatus) => {
  updateAlertStatus(id, status);
};
</script>
