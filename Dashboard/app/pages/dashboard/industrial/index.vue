<template>
  <div class="space-y-6 max-w-[1400px] mx-auto">
    <div>
      <h1 class="text-2xl font-bold text-(--label-text) tracking-tight">Industrial Hub</h1>
      <p class="text-sm text-(--hint-text) mt-1">Facility monitoring and flood risk assessment — Galați Industrial Zone</p>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard icon="mdi:factory" label="Total Facilities" :value="factories.length" glow-color="primary" icon-bg="#0066CC" class="animate-fade-up stagger-1" />
      <StatCard icon="mdi:alert-octagon" label="At-Risk Facilities" :value="criticalFactories.length" glow-color="danger" icon-bg="#EF4444" class="animate-fade-up stagger-2" />
      <StatCard icon="mdi:account-hard-hat" label="Employees at Risk" :value="totalEmployeesAtRisk" glow-color="warning" icon-bg="#F59E0B" class="animate-fade-up stagger-3" />
      <StatCard icon="mdi:access-point" label="Critical Sensors" :value="criticalSensors.length" glow-color="info" icon-bg="#3B82F6" class="animate-fade-up stagger-4" />
    </div>

    <Card class="p-5">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h2 class="text-lg font-semibold text-(--label-text)">Factory Locations & Flood Risk</h2>
          <p class="text-xs text-(--hint-text) flex items-center gap-1 mt-0.5">
            <Icon name="mdi:satellite-variant" class="h-3 w-3" /> Copernicus Flood Risk Overlay
          </p>
        </div>
      </div>
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-2 h-[400px] map-container">
          <ClientOnly>
            <LMap :zoom="12" :center="[45.4353, 28.0350]" :use-global-leaflet="false" :options="{ zoomControl: true, attributionControl: false }">
              <LTileLayer url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" layer-type="base" name="CartoDB Dark" />
              <LMarker v-for="hz in floodHeatmap" :key="hz.id" :lat-lng="[hz.lat, hz.lng]">
                <LIcon :icon-size="[hz.radius / 6, hz.radius / 6]" :icon-anchor="[hz.radius / 12, hz.radius / 12]" class-name="">
                  <div class="rounded-full" :style="{
                    width: `${hz.radius / 6}px`,
                    height: `${hz.radius / 6}px`,
                    background: `radial-gradient(circle, ${heatmapIntensityColor(hz.intensity)}50, ${heatmapIntensityColor(hz.intensity)}10, transparent)`,
                  }" />
                </LIcon>
              </LMarker>
              <LMarker v-for="factory in factories" :key="factory.id" :lat-lng="[factory.lat, factory.lng]">
                <LIcon :icon-size="[44, 44]" :icon-anchor="[22, 22]" class-name="">
                  <div class="flex flex-col items-center">
                    <div class="h-11 w-11 rounded-xl flex flex-col items-center justify-center shadow-lg border-2" :style="{ background: factory.status === 'critical' ? '#7F1D1D' : factory.status === 'warning' ? '#92400E' : '#14532D', borderColor: factoryStatusColor(factory.status) }">
                      <Icon name="mdi:factory" class="h-5 w-5 text-white" />
                    </div>
                  </div>
                </LIcon>
                <LPopup>
                  <div class="p-2 min-w-[200px]">
                    <h3 class="font-bold text-sm text-gray-900 mb-1">{{ factory.name }}</h3>
                    <p class="text-xs text-gray-600 mb-2">{{ factory.location }}</p>
                    <div class="space-y-1 text-xs">
                      <div class="flex justify-between"><span class="text-gray-500">Status:</span><span class="font-medium capitalize" :style="{ color: factoryStatusColor(factory.status) }">{{ factory.status }}</span></div>
                      <div class="flex justify-between"><span class="text-gray-500">Risk:</span><span class="font-medium capitalize">{{ factory.riskLevel }}</span></div>
                      <div class="flex justify-between"><span class="text-gray-500">Employees:</span><span class="font-medium">{{ factory.employees }}</span></div>
                      <div class="flex justify-between"><span class="text-gray-500">Water Distance:</span><span class="font-medium">{{ factory.waterProximity }}m</span></div>
                      <div class="flex justify-between"><span class="text-gray-500">Sensors:</span><span class="font-medium">{{ factory.sensorCount }}</span></div>
                    </div>
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
        <div class="space-y-3">
          <div v-for="factory in factories" :key="factory.id" class="p-3 rounded-xl border border-(--border-color) bg-(--surface-secondary)/30 hover:bg-(--surface-secondary)/50 transition-colors cursor-pointer" @click="navigateTo('/dashboard/industrial/factories')">
            <div class="flex items-center gap-2 mb-2">
              <div class="h-8 w-8 rounded-lg flex items-center justify-center shrink-0" :style="{ background: `${factoryStatusColor(factory.status)}15` }">
                <Icon name="mdi:factory" class="h-4 w-4" :style="{ color: factoryStatusColor(factory.status) }" />
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-(--label-text) truncate">{{ factory.name }}</p>
                <p class="text-[10px] text-(--hint-text)">{{ factory.location }}</p>
              </div>
              <Badge :variant="factory.status === 'operational' ? 'success' : factory.status === 'critical' ? 'danger' : 'secondary'" class="shrink-0">
                {{ factory.status }}
              </Badge>
            </div>
            <div class="grid grid-cols-3 gap-2 text-center">
              <div class="p-1.5 rounded-lg bg-(--surface-secondary)/50">
                <p class="text-sm font-bold text-(--label-text)">{{ factory.sensorCount }}</p>
                <p class="text-[9px] text-(--hint-text)">Sensors</p>
              </div>
              <div class="p-1.5 rounded-lg bg-(--surface-secondary)/50">
                <p class="text-sm font-bold text-(--label-text)">{{ factory.employees }}</p>
                <p class="text-[9px] text-(--hint-text)">People</p>
              </div>
              <div class="p-1.5 rounded-lg bg-(--surface-secondary)/50">
                <p class="text-sm font-bold" :class="factory.waterProximity < 100 ? 'text-red-500' : factory.waterProximity < 300 ? 'text-amber-500' : 'text-green-500'">{{ factory.waterProximity }}m</p>
                <p class="text-[9px] text-(--hint-text)">Water</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Card>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: "dashboard", middleware: "auth" });
const { factories, criticalFactories, criticalSensors, totalEmployeesAtRisk, factoryStatusColor } = useIndustrial();
const { floodHeatmap, heatmapIntensityColor } = useSatelliteData();
</script>
