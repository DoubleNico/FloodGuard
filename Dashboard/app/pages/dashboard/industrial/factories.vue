<template>
  <div class="space-y-6 max-w-[1400px] mx-auto">
    <div>
      <h1 class="text-2xl font-bold text-(--label-text) tracking-tight">Factory Monitoring</h1>
      <p class="text-sm text-(--hint-text) mt-1">Detailed view of all monitored industrial facilities</p>
    </div>

    <DataTable :columns="columns" :data="factories" row-key="id">
      <template #name="{ row }">
        <div class="flex items-center gap-2">
          <div class="h-8 w-8 rounded-lg flex items-center justify-center shrink-0" :style="{ background: `${factoryStatusColor(row.status)}15` }">
            <Icon name="mdi:factory" class="h-4 w-4" :style="{ color: factoryStatusColor(row.status) }" />
          </div>
          <div>
            <p class="text-sm font-medium text-(--label-text)">{{ row.name }}</p>
            <p class="text-[10px] text-(--hint-text)">{{ row.location }}</p>
          </div>
        </div>
      </template>
      <template #status="{ value }">
        <Badge :variant="value === 'operational' ? 'success' : value === 'critical' ? 'danger' : value === 'warning' ? 'secondary' : 'outline'">
          {{ value }}
        </Badge>
      </template>
      <template #riskLevel="{ value }">
        <span class="text-xs font-semibold capitalize" :style="{ color: value === 'critical' ? '#EF4444' : value === 'high' ? '#F97316' : value === 'moderate' ? '#F59E0B' : '#22C55E' }">{{ value }}</span>
      </template>
      <template #waterProximity="{ value }">
        <span class="font-medium" :class="value < 100 ? 'text-red-500' : value < 300 ? 'text-amber-500' : 'text-green-500'">{{ value }}m</span>
      </template>
      <template #lastInspection="{ value }">
        <span class="text-xs text-(--hint-text)">{{ new Date(value).toLocaleDateString() }}</span>
      </template>
    </DataTable>
  </div>
</template>

<script setup lang="ts">
import type { Column } from "~/types/Column";

definePageMeta({ layout: "dashboard", middleware: "auth" });
const { factories, factoryStatusColor } = useIndustrial();

const columns: Column[] = [
  { key: "name", label: "Factory", width: "w-[280px]", sortable: true },
  { key: "status", label: "Status", width: "w-[120px]", sortable: true },
  { key: "riskLevel", label: "Risk", width: "w-[100px]", sortable: true },
  { key: "sensorCount", label: "Sensors", width: "w-[90px]", sortable: true },
  { key: "employees", label: "Employees", width: "w-[100px]", sortable: true },
  { key: "waterProximity", label: "Water Dist.", width: "w-[110px]", sortable: true },
  { key: "lastInspection", label: "Last Inspection", width: "w-[130px]", sortable: true },
];
</script>
