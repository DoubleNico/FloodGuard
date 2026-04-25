<template>
  <div class="space-y-6 max-w-[1400px] mx-auto">
    <div>
      <h1 class="text-2xl font-bold text-(--label-text) tracking-tight">Sensor Monitoring</h1>
      <p class="text-sm text-(--hint-text) mt-1">Real-time telemetry from all connected devices</p>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <StatCard icon="mdi:access-point" label="Total Sensors" :value="sensors.length" glow-color="primary" icon-bg="#0066CC" />
      <StatCard icon="mdi:alert-circle" label="Critical / Warning" :value="criticalSensors.length" glow-color="danger" icon-bg="#EF4444" />
      <StatCard icon="mdi:check-circle" label="Online" :value="sensors.filter(s => s.status === 'online').length" glow-color="success" icon-bg="#22C55E" />
    </div>

    <DataTable :columns="columns" :data="sensors" row-key="id">
      <template #name="{ row }">
        <div class="flex items-center gap-2">
          <span class="h-2 w-2 rounded-full shrink-0" :style="{ background: sensorStatusColor(row.status) }" />
          <div>
            <p class="text-sm font-medium text-(--label-text)">{{ row.name }}</p>
            <p class="text-[10px] text-(--hint-text)">{{ factoryName(row.factoryId) }}</p>
          </div>
        </div>
      </template>
      <template #type="{ value }">
        <span class="text-xs capitalize">{{ value.replace('-', ' ') }}</span>
      </template>
      <template #value="{ row }">
        <span class="font-mono text-sm font-bold" :class="row.value >= row.threshold ? 'text-red-500' : 'text-(--label-text)'">
          {{ row.value }} <span class="text-xs font-normal text-(--hint-text)">{{ row.unit }}</span>
        </span>
      </template>
      <template #threshold="{ row }">
        <span class="text-xs text-(--hint-text)">{{ row.threshold }} {{ row.unit }}</span>
      </template>
      <template #status="{ value }">
        <Badge :variant="value === 'online' ? 'success' : value === 'critical' ? 'danger' : value === 'warning' ? 'secondary' : 'outline'">
          {{ value }}
        </Badge>
      </template>
      <template #lastUpdate="{ value }">
        <span class="text-xs text-(--hint-text)">{{ new Date(value).toLocaleTimeString() }}</span>
      </template>
    </DataTable>
  </div>
</template>

<script setup lang="ts">
import type { Column } from "~/types/Column";

definePageMeta({ layout: "dashboard", middleware: "auth" });
const { sensors, factories, criticalSensors, sensorStatusColor } = useIndustrial();

const factoryName = (id: string) => factories.value.find((f) => f.id === id)?.name || id;

const columns: Column[] = [
  { key: "name", label: "Sensor", width: "w-[240px]", sortable: true },
  { key: "type", label: "Type", width: "w-[120px]", sortable: true },
  { key: "value", label: "Reading", width: "w-[120px]", sortable: true },
  { key: "threshold", label: "Threshold", width: "w-[100px]" },
  { key: "status", label: "Status", width: "w-[100px]", sortable: true },
  { key: "lastUpdate", label: "Last Update", width: "w-[120px]", sortable: true },
];
</script>
