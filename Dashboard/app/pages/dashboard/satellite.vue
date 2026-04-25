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

    <Card class="p-5">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h2 class="text-lg font-semibold text-(--label-text)">Water Level Stations & Flood Forecast</h2>
          <p class="text-xs text-(--hint-text) flex items-center gap-1 mt-0.5">
            <Icon name="mdi:satellite-variant" class="h-3 w-3" /> Copernicus Sentinel-1 SAR — Galați Monitoring Network
          </p>
        </div>
        <Badge variant="outline" class="alarm-pulse">Live Feed</Badge>
      </div>
      <div class="grid grid-cols-1 lg:grid-cols-5 gap-6">
        <div class="lg:col-span-3 h-[400px] map-container">
          <ClientOnly>
            <LMap :zoom="12" :center="[45.4353, 28.0397]" :use-global-leaflet="false" :options="{ zoomControl: true, attributionControl: false }">
              <LTileLayer url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" layer-type="base" name="CartoDB Dark" />
              <LMarker v-for="wl in waterLevels" :key="wl.station" :lat-lng="[wl.lat, wl.lng]">
                <LIcon :icon-size="[48, 48]" :icon-anchor="[24, 24]" class-name="">
                  <div class="flex flex-col items-center">
                    <div class="h-12 w-12 rounded-xl flex flex-col items-center justify-center shadow-lg border-2" :style="{ background: wl.level >= wl.criticalLevel ? '#7F1D1D' : wl.level >= wl.warningLevel ? '#92400E' : '#14532D', borderColor: wl.level >= wl.criticalLevel ? '#EF4444' : wl.level >= wl.warningLevel ? '#F59E0B' : '#22C55E' }">
                      <span class="text-white text-xs font-bold leading-none">{{ Math.round(wl.level) }}</span>
                      <span class="text-white/60 text-[8px]">cm</span>
                    </div>
                  </div>
                </LIcon>
                <LPopup>
                  <div class="p-2 min-w-[180px]">
                    <h3 class="font-bold text-sm text-gray-900 mb-1">{{ wl.station }}</h3>
                    <div class="space-y-1 text-xs">
                      <div class="flex justify-between"><span class="text-gray-500">Level:</span><span class="font-bold" :style="{ color: wl.level >= wl.criticalLevel ? '#EF4444' : wl.level >= wl.warningLevel ? '#F59E0B' : '#22C55E' }">{{ Math.round(wl.level) }}cm</span></div>
                      <div class="flex justify-between"><span class="text-gray-500">Warning:</span><span>{{ wl.warningLevel }}cm</span></div>
                      <div class="flex justify-between"><span class="text-gray-500">Critical:</span><span>{{ wl.criticalLevel }}cm</span></div>
                      <div class="flex justify-between"><span class="text-gray-500">Trend:</span><span class="capitalize font-medium">{{ wl.trend }}</span></div>
                    </div>
                  </div>
                </LPopup>
              </LMarker>
              <LMarker v-for="hz in floodHeatmap" :key="hz.id" :lat-lng="[hz.lat, hz.lng]">
                <LIcon :icon-size="[hz.radius / 5, hz.radius / 5]" :icon-anchor="[hz.radius / 10, hz.radius / 10]" class-name="">
                  <div class="rounded-full" :style="{
                    width: `${hz.radius / 5}px`,
                    height: `${hz.radius / 5}px`,
                    background: `radial-gradient(circle, ${heatmapIntensityColor(hz.intensity)}60, ${heatmapIntensityColor(hz.intensity)}10, transparent)`,
                  }" />
                </LIcon>
              </LMarker>
            </LMap>
            <template #fallback>
              <div class="h-full flex items-center justify-center bg-(--surface-secondary) rounded-[20px]">
                <Icon name="mdi:map" class="h-8 w-8 text-(--hint-text)" />
              </div>
            </template>
          </ClientOnly>
        </div>
        <div class="lg:col-span-2 space-y-4">
          <div v-for="wl in waterLevels" :key="wl.station" class="space-y-2 p-3 rounded-xl border border-(--border-color) bg-(--surface-secondary)/30">
            <div class="flex items-center justify-between">
              <span class="text-sm font-medium text-(--label-text)">{{ wl.station.replace('Galați — ', '') }}</span>
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
      </div>
    </Card>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
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

    <Card class="p-5">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h2 class="text-lg font-semibold text-(--label-text)">NDWI Analysis & Risk Map</h2>
          <p class="text-xs text-(--hint-text) flex items-center gap-1 mt-0.5">
            <Icon name="mdi:satellite-variant" class="h-3 w-3" /> Copernicus Sentinel-2 MSI
          </p>
        </div>
      </div>
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="grid grid-cols-2 gap-3 lg:col-span-1 h-fit">
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
        <div class="lg:col-span-2 h-[400px] map-container">
          <ClientOnly>
            <LMap :zoom="13" :center="[45.4353, 28.0397]" :use-global-leaflet="false" :options="{ zoomControl: true, attributionControl: false }">
              <LTileLayer url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" layer-type="base" name="CartoDB Dark" />
              <LMarker v-for="nr in ndwiReadings" :key="nr.zone" :lat-lng="[nr.lat, nr.lng]">
                <LIcon :icon-size="[32, 32]" :icon-anchor="[16, 32]" class-name="">
                  <div class="flex flex-col items-center">
                    <div class="h-8 w-8 rounded-full flex items-center justify-center shadow-lg border-2 border-white" :style="{ background: ndwiRiskColor(nr.risk) }">
                      <span class="text-white text-xs font-bold">{{ Math.round(nr.value * 100) }}</span>
                    </div>
                  </div>
                </LIcon>
                <LPopup>
                  <div class="p-2 min-w-[150px]">
                    <h3 class="font-bold text-sm text-gray-900 mb-1">{{ nr.zone }}</h3>
                    <p class="text-xs text-gray-600 mb-1">NDWI Value: <strong :style="{ color: ndwiRiskColor(nr.risk) }">{{ nr.value.toFixed(2) }}</strong></p>
                    <p class="text-xs text-gray-500 uppercase font-semibold">{{ nr.risk }} RISK</p>
                  </div>
                </LPopup>
              </LMarker>
            </LMap>
            <template #fallback>
              <div class="h-full flex items-center justify-center bg-(--surface-secondary) rounded-[20px]">
                <Icon name="mdi:map" class="h-8 w-8 text-(--hint-text)" />
              </div>
            </template>
          </ClientOnly>
        </div>
      </div>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { Bar } from "vue-chartjs";
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Tooltip, Legend } from "chart.js";

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

definePageMeta({ layout: "dashboard", middleware: "auth" });

const { waterLevels, precipitation, galileoSatellites, ndwiReadings, floodHeatmap, operationalSatellites, averageSignal, ndwiRiskColor, heatmapIntensityColor, startSimulation, stopSimulation } = useSatelliteData();

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
