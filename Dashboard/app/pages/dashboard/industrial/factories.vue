<template>
  <div class="space-y-6 max-w-[1400px] mx-auto">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-(--label-text) tracking-tight">Factory Monitoring</h1>
        <p class="text-sm text-(--hint-text) mt-1">Detailed view of all monitored industrial facilities</p>
      </div>
      <div>
        <Button variant="solid" color="primary" icon-left="mdi:plus" @click="showAddModal = true">Add Factory</Button>
      </div>
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

    <Modal v-model="showAddModal" title="Add New Factory" size="lg">
      <Form class="space-y-4" @submit="handleAddFactory">
        <Input v-model="newFactory.name" label="Factory Name" placeholder="e.g. Liberty Steel Galați" :required="true" />
        <Input v-model="newFactory.location" label="Location" placeholder="e.g. Smârdan Industrial Area" :required="true" />
        <div class="grid grid-cols-2 gap-4">
          <Input v-model="newFactory.lat" label="Latitude" type="number" placeholder="45.4268" :required="true" />
          <Input v-model="newFactory.lng" label="Longitude" type="number" placeholder="28.0551" :required="true" />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <CustomSelect v-model="newFactory.status" label="Status" :options="statusOptions" :required="true" />
          <CustomSelect v-model="newFactory.riskLevel" label="Risk Level" :options="riskOptions" :required="true" />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <Input v-model="newFactory.waterProximity" label="Water Proximity (meters)" type="number" placeholder="500" :required="true" />
          <Input v-model="newFactory.employees" label="Employees" type="number" placeholder="2500" :required="true" />
        </div>
      </Form>
      <template #footer="{ close }">
        <Button variant="outline" color="secondary" @click="close">Cancel</Button>
        <Button variant="solid" color="primary" @click="handleAddFactory">Add Factory</Button>
      </template>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import type { Column } from "~/types/Column";

definePageMeta({ layout: "dashboard", middleware: "auth" });
const { factories, factoryStatusColor, createFactory } = useIndustrial();

const showAddModal = ref(false);

const newFactory = reactive({
  name: "", location: "", lat: "", lng: "", status: "operational", riskLevel: "low", waterProximity: "", employees: "",
});

const statusOptions = [
  { label: "Operational", value: "operational" },
  { label: "Warning", value: "warning" },
  { label: "Critical", value: "critical" },
  { label: "Offline", value: "offline" },
];

const riskOptions = [
  { label: "Low", value: "low" },
  { label: "Moderate", value: "moderate" },
  { label: "High", value: "high" },
  { label: "Critical", value: "critical" },
];

const handleAddFactory = async () => {
  if (!newFactory.name || !newFactory.location) return;
  await createFactory({
    name: newFactory.name,
    location: newFactory.location,
    lat: parseFloat(newFactory.lat),
    lng: parseFloat(newFactory.lng),
    status: newFactory.status as any,
    riskLevel: newFactory.riskLevel as any,
    waterProximity: parseInt(newFactory.waterProximity) || 0,
    employees: parseInt(newFactory.employees) || 0,
  });
  showAddModal.value = false;
  Object.assign(newFactory, { name: "", location: "", lat: "", lng: "", status: "operational", riskLevel: "low", waterProximity: "", employees: "" });
};

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
