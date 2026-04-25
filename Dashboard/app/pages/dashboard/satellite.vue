<template>
  <div class="space-y-6 max-w-[1400px] mx-auto">
    <div>
      <h1 class="text-2xl font-bold text-(--label-text) tracking-tight">Satellite Intelligence</h1>
      <p class="text-sm text-(--hint-text) mt-1">Copernicus Earth Observation & Galileo GNSS data feeds</p>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard icon="mdi:satellite-variant" label="Galileo Satellites" :value="`${operationalSatellites}/8`" glow-color="primary" icon-bg="#0066CC" class="animate-fade-up stagger-1" />
      <StatCard icon="mdi:signal" label="Avg Signal Strength" :value="`${averageSignal}%`" glow-color="success" icon-bg="#22C55E" class="animate-fade-up stagger-2" />
      <StatCard icon="mdi:water" label="Highest Water Level" :value="`${Math.round(Math.max(...waterLevels.map(w => w.level)))}cm`" glow-color="danger" icon-bg="#EF4444" class="animate-fade-up stagger-3" />
      <StatCard icon="mdi:earth" label="NDWI Zones Monitored" :value="ndwiReadings.length" glow-color="info" icon-bg="#3B82F6" class="animate-fade-up stagger-4" />
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <Card class="p-5">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h2 class="text-lg font-semibold text-(--label-text)">Water Level Monitoring</h2>
            <p class="text-xs text-(--hint-text) flex items-center gap-1 mt-0.5">
              <Icon name="mdi:satellite-variant" class="h-3 w-3" /> Copernicus Sentinel-1 SAR
            </p>
          </div>
          <Badge variant="outline">Live</Badge>
        </div>
        <div class="space-y-5">
          <div v-for="wl in waterLevels" :key="wl.station" class="space-y-2">
            <div class="flex items-center justify-between">
              <span class="text-sm font-medium text-(--label-text)">{{ wl.station }}</span>
              <div class="flex items-center gap-2">
                <Icon :name="wl.trend === 'rising' ? 'mdi:trending-up' : wl.trend === 'falling' ? 'mdi:trending-down' : 'mdi:trending-neutral'" class="h-4 w-4" :class="wl.trend === 'rising' ? 'text-red-500' : wl.trend === 'falling' ? 'text-green-500' : 'text-(--hint-text)'" />
                <span class="text-xl font-bold" :class="wl.level >= wl.criticalLevel ? 'text-red-500' : wl.level >= wl.warningLevel ? 'text-amber-500' : 'text-green-500'">
                  {{ Math.round(wl.level) }}<span class="text-sm font-normal text-(--hint-text)">cm</span>
                </span>
              </div>
            </div>
            <div class="relative">
              <div class="water-gauge h-3 rounded-lg">
                <div class="water-gauge-fill rounded-lg" :style="{ width: `${Math.min(100, (wl.level / wl.criticalLevel) * 100)}%`, background: wl.level >= wl.criticalLevel ? 'linear-gradient(90deg, #EF4444, #DC2626)' : wl.level >= wl.warningLevel ? 'linear-gradient(90deg, #F59E0B, #D97706)' : 'linear-gradient(90deg, #22C55E, #16A34A)' }" />
              </div>
              <div class="absolute top-0 h-3 w-0.5 bg-(--label-text)/30" :style="{ left: `${(wl.warningLevel / wl.criticalLevel) * 100}%` }" />
            </div>
            <div class="flex justify-between text-[10px] text-(--hint-text)">
              <span>Normal</span>
              <span>Warning ({{ wl.warningLevel }}cm)</span>
              <span>Critical ({{ wl.criticalLevel }}cm)</span>
            </div>
          </div>
        </div>
      </Card>

      <Card class="p-5">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h2 class="text-lg font-semibold text-(--label-text)">Precipitation Forecast</h2>
            <p class="text-xs text-(--hint-text) flex items-center gap-1 mt-0.5">
              <Icon name="mdi:satellite-variant" class="h-3 w-3" /> Copernicus ERA5 Reanalysis
            </p>
          </div>
        </div>
        <div class="h-[280px]">
          <ClientOnly>
            <Bar v-if="chartData" :data="chartData" :options="chartOptions" />
            <template #fallback>
              <div class="h-full flex items-center justify-center">
                <p class="text-sm text-(--hint-text)">Loading chart...</p>
              </div>
            </template>
          </ClientOnly>
        </div>
      </Card>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <Card class="p-5">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h2 class="text-lg font-semibold text-(--label-text)">NDWI Analysis</h2>
            <p class="text-xs text-(--hint-text) flex items-center gap-1 mt-0.5">
              <Icon name="mdi:satellite-variant" class="h-3 w-3" /> Copernicus Sentinel-2 MSI
            </p>
          </div>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div v-for="nr in ndwiReadings" :key="nr.zone" class="p-3 rounded-xl border border-(--border-color) bg-(--surface-secondary)/30 hover:bg-(--surface-secondary)/60 transition-colors">
            <div class="flex items-center justify-between mb-2">
              <span class="text-xs font-medium text-(--label-text) truncate">{{ nr.zone }}</span>
              <span class="text-[10px] font-bold uppercase px-1.5 py-0.5 rounded-full" :style="{ background: `${ndwiRiskColor(nr.risk)}20`, color: ndwiRiskColor(nr.risk) }">{{ nr.risk }}</span>
            </div>
            <p class="text-2xl font-bold tracking-tight" :style="{ color: ndwiRiskColor(nr.risk) }">{{ nr.value.toFixed(2) }}</p>
            <div class="water-gauge mt-2">
              <div class="water-gauge-fill" :style="{ width: `${nr.value * 100}%`, background: ndwiRiskColor(nr.risk) }" />
            </div>
          </div>
        </div>
      </Card>

      <Card class="p-5">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h2 class="text-lg font-semibold text-(--label-text)">Galileo Constellation Status</h2>
            <p class="text-xs text-(--hint-text) flex items-center gap-1 mt-0.5">
              <Icon name="mdi:satellite-uplink" class="h-3 w-3" /> EU Galileo GNSS
            </p>
          </div>
          <Badge variant="success">{{ operationalSatellites }}/{{ galileoSatellites.length }} Active</Badge>
        </div>
        <div class="space-y-3">
          <div v-for="sat in galileoSatellites" :key="sat.id" class="flex items-center gap-3 p-3 rounded-xl bg-(--surface-secondary)/30">
            <div class="h-9 w-9 rounded-lg flex items-center justify-center" :style="{ background: sat.status === 'operational' ? '#22C55E15' : sat.status === 'testing' ? '#F59E0B15' : '#EF444415' }">
              <Icon name="mdi:satellite-variant" class="h-4.5 w-4.5" :style="{ color: sat.status === 'operational' ? '#22C55E' : sat.status === 'testing' ? '#F59E0B' : '#EF4444' }" />
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2">
                <span class="text-sm font-medium text-(--label-text)">{{ sat.id }}</span>
                <span class="text-xs text-(--hint-text)">{{ sat.name }}</span>
              </div>
              <div v-if="sat.status === 'operational'" class="water-gauge mt-1.5">
                <div class="water-gauge-fill" :style="{ width: `${sat.signal}%`, background: sat.signal > 85 ? '#22C55E' : sat.signal > 70 ? '#F59E0B' : '#EF4444' }" />
              </div>
            </div>
            <div class="flex items-center gap-2 shrink-0">
              <span v-if="sat.status === 'operational'" class="text-sm font-bold text-(--label-text)">{{ Math.round(sat.signal) }}%</span>
              <Badge :variant="sat.status === 'operational' ? 'success' : sat.status === 'testing' ? 'secondary' : 'danger'">
                {{ sat.status }}
              </Badge>
            </div>
          </div>
        </div>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Bar } from "vue-chartjs";
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Tooltip, Legend } from "chart.js";

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

definePageMeta({ layout: "dashboard", middleware: "auth" });

const { waterLevels, precipitation, galileoSatellites, ndwiReadings, operationalSatellites, averageSignal, ndwiRiskColor, startSimulation, stopSimulation } = useSatelliteData();

const chartData = computed(() => ({
  labels: precipitation.value.map((p) => p.date),
  datasets: [
    {
      label: "Actual (mm)",
      data: precipitation.value.map((p) => p.actual),
      backgroundColor: "rgba(34, 197, 94, 0.7)",
      borderRadius: 6,
      barThickness: 16,
    },
    {
      label: "Forecast (mm)",
      data: precipitation.value.map((p) => p.forecast),
      backgroundColor: "rgba(59, 130, 246, 0.5)",
      borderRadius: 6,
      barThickness: 16,
    },
  ],
}));

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: "top" as const, labels: { boxWidth: 12, usePointStyle: true, padding: 16, font: { size: 11 } } },
  },
  scales: {
    x: { grid: { display: false }, ticks: { font: { size: 10 } } },
    y: { grid: { color: "rgba(128,128,128,0.1)" }, ticks: { font: { size: 10 } }, title: { display: true, text: "mm", font: { size: 10 } } },
  },
};

onMounted(() => startSimulation());
onBeforeUnmount(() => stopSimulation());
</script>
