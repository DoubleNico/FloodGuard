<template>
  <div class="space-y-8 max-w-[1400px] mx-auto">
    <div>
      <h1 class="text-2xl font-bold text-(--label-text) tracking-tight">Dashboard Overview</h1>
      <p class="text-sm text-(--hint-text) mt-1">{{ isDispatcher ? 'Flood monitoring and emergency dispatch' : isIndustrial ? 'Industrial facility monitoring' : 'System administration' }} — Galați, Romania</p>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard icon="mdi:bell-alert" label="Active Alerts" :value="activeAlerts.length" :trend="12" glow-color="danger" icon-bg="#EF4444" class="animate-fade-up stagger-1" />
      <StatCard icon="mdi:account-group" label="Citizens Notified" :value="totalRecipients" :trend="-5" glow-color="info" icon-bg="#3B82F6" class="animate-fade-up stagger-2" />
      <StatCard icon="mdi:map-marker-check" label="Safe Locations Open" :value="openLocations.length" glow-color="success" icon-bg="#22C55E" class="animate-fade-up stagger-3" />
      <StatCard icon="mdi:satellite-variant" label="Galileo Satellites" :value="`${operationalSatellites}/8`" glow-color="primary" icon-bg="#0066CC" class="animate-fade-up stagger-4" />
    </div>

    <div v-if="isDispatcher || isAdmin" class="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <Card class="lg:col-span-2 p-5">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold text-(--label-text)">Recent Alerts</h2>
          <CustomLink to="/dashboard/alerts">
            <Button variant="ghost" color="primary" size="sm">View All</Button>
          </CustomLink>
        </div>
        <div class="space-y-3">
          <div v-for="alert in recentAlerts" :key="alert.id" class="flex items-center gap-3 p-3 rounded-xl bg-(--surface-secondary)/50 hover:bg-(--surface-secondary) transition-colors">
            <div class="h-10 w-10 rounded-xl flex items-center justify-center shrink-0" :style="{ background: `${severityColor(alert.severity)}15` }">
              <Icon name="mdi:alert-circle" class="h-5 w-5" :style="{ color: severityColor(alert.severity) }" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-(--label-text) truncate">{{ alert.title }}</p>
              <p class="text-xs text-(--hint-text)">{{ alert.affectedAreas.join(', ') }}</p>
            </div>
            <div class="flex items-center gap-2 shrink-0">
              <Badge :variant="alert.status === 'published' ? 'success' : alert.status === 'review' ? 'secondary' : 'outline'">
                {{ alert.status }}
              </Badge>
              <Badge :variant="alert.severity >= 4 ? 'danger' : alert.severity >= 3 ? 'default' : 'outline'">
                {{ severityLabel(alert.severity) }}
              </Badge>
            </div>
          </div>
        </div>
      </Card>

      <Card class="p-5">
        <h2 class="text-lg font-semibold text-(--label-text) mb-4">Water Levels</h2>
        <div class="space-y-4">
          <div v-for="wl in waterLevels" :key="wl.station" class="space-y-1.5">
            <div class="flex items-center justify-between">
              <span class="text-sm font-medium text-(--label-text) truncate">{{ wl.station.replace('Galați — ', '') }}</span>
              <div class="flex items-center gap-1.5">
                <Icon :name="wl.trend === 'rising' ? 'mdi:arrow-up' : wl.trend === 'falling' ? 'mdi:arrow-down' : 'mdi:minus'" class="h-3.5 w-3.5" :class="wl.trend === 'rising' ? 'text-red-500' : wl.trend === 'falling' ? 'text-green-500' : 'text-(--hint-text)'" />
                <span class="text-sm font-bold" :class="wl.level >= wl.criticalLevel ? 'text-red-500' : wl.level >= wl.warningLevel ? 'text-amber-500' : 'text-(--label-text)'">
                  {{ Math.round(wl.level) }}cm
                </span>
              </div>
            </div>
            <div class="water-gauge">
              <div class="water-gauge-fill" :style="{ width: `${Math.min(100, (wl.level / wl.criticalLevel) * 100)}%`, background: wl.level >= wl.criticalLevel ? '#EF4444' : wl.level >= wl.warningLevel ? '#F59E0B' : '#22C55E' }" />
            </div>
            <div class="flex justify-between text-[10px] text-(--hint-text)">
              <span>0</span>
              <span>Warning: {{ wl.warningLevel }}</span>
              <span>Critical: {{ wl.criticalLevel }}</span>
            </div>
          </div>
        </div>
        <div class="mt-4 pt-3 border-t border-(--border-color)">
          <p class="text-[10px] text-(--hint-text) flex items-center gap-1">
            <Icon name="mdi:satellite-variant" class="h-3 w-3" />
            Source: Copernicus Data Space Ecosystem
          </p>
        </div>
      </Card>
    </div>

    <div v-if="isIndustrial || isAdmin" class="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <Card class="lg:col-span-2 p-5">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold text-(--label-text)">Factory Status</h2>
          <CustomLink to="/dashboard/industrial/factories">
            <Button variant="ghost" color="primary" size="sm">View All</Button>
          </CustomLink>
        </div>
        <div class="space-y-3">
          <div v-for="f in factories" :key="f.id" class="flex items-center gap-3 p-3 rounded-xl bg-(--surface-secondary)/50 hover:bg-(--surface-secondary) transition-colors">
            <div class="h-10 w-10 rounded-xl flex items-center justify-center shrink-0" :style="{ background: `${factoryStatusColor(f.status)}15` }">
              <Icon name="mdi:factory" class="h-5 w-5" :style="{ color: factoryStatusColor(f.status) }" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-(--label-text) truncate">{{ f.name }}</p>
              <p class="text-xs text-(--hint-text)">{{ f.employees }} employees • {{ f.sensorCount }} sensors</p>
            </div>
            <Badge :variant="f.status === 'operational' ? 'success' : f.status === 'critical' ? 'danger' : 'secondary'">
              {{ f.status }}
            </Badge>
          </div>
        </div>
      </Card>

      <Card class="p-5">
        <h2 class="text-lg font-semibold text-(--label-text) mb-4">Risk Summary</h2>
        <div class="space-y-4">
          <StatCard icon="mdi:alert-octagon" label="Critical Factories" :value="criticalFactories.length" glow-color="danger" icon-bg="#EF4444" />
          <StatCard icon="mdi:account-hard-hat" label="Employees at Risk" :value="totalEmployeesAtRisk" glow-color="warning" icon-bg="#F59E0B" />
          <StatCard icon="mdi:access-point-off" label="Critical Sensors" :value="criticalSensors.length" glow-color="info" icon-bg="#3B82F6" />
        </div>
      </Card>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <Card class="p-5">
        <h2 class="text-lg font-semibold text-(--label-text) mb-4">Shelter Occupancy</h2>
        <div class="space-y-3">
          <div v-for="loc in locations.slice(0, 5)" :key="loc.id" class="space-y-1.5">
            <div class="flex items-center justify-between">
              <span class="text-sm font-medium text-(--label-text) truncate">{{ loc.name }}</span>
              <span class="text-xs font-semibold" :style="{ color: statusColor(loc.status) }">{{ loc.currentOccupancy }}/{{ loc.capacity }}</span>
            </div>
            <div class="water-gauge">
              <div class="water-gauge-fill" :style="{ width: `${(loc.currentOccupancy / loc.capacity) * 100}%`, background: statusColor(loc.status) }" />
            </div>
          </div>
        </div>
      </Card>

      <Card class="p-5">
        <h2 class="text-lg font-semibold text-(--label-text) mb-4">NDWI Risk Map</h2>
        <div class="grid grid-cols-2 gap-2">
          <div v-for="nr in ndwiReadings" :key="nr.zone" class="p-3 rounded-xl bg-(--surface-secondary)/50 border border-(--border-color)">
            <div class="flex items-center justify-between mb-1">
              <span class="text-xs font-medium text-(--label-text) truncate">{{ nr.zone }}</span>
              <span class="h-2 w-2 rounded-full" :style="{ background: ndwiRiskColor(nr.risk) }" />
            </div>
            <p class="text-lg font-bold" :style="{ color: ndwiRiskColor(nr.risk) }">{{ nr.value.toFixed(2) }}</p>
            <p class="text-[10px] text-(--hint-text) uppercase font-semibold">{{ nr.risk }}</p>
          </div>
        </div>
        <div class="mt-3 pt-3 border-t border-(--border-color)">
          <p class="text-[10px] text-(--hint-text) flex items-center gap-1">
            <Icon name="mdi:satellite-variant" class="h-3 w-3" />
            Normalized Difference Water Index — Copernicus Sentinel-2
          </p>
        </div>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: "dashboard", middleware: "auth" });

const { isDispatcher, isIndustrial, isAdmin } = useRole();
const { activeAlerts, totalRecipients, severityColor, severityLabel } = useAlerts();
const { openLocations, locations, statusColor } = useSafeLocations();
const { waterLevels, ndwiReadings, ndwiRiskColor, operationalSatellites, startSimulation, stopSimulation } = useSatelliteData();
const { factories, criticalFactories, criticalSensors, totalEmployeesAtRisk, factoryStatusColor } = useIndustrial();

const recentAlerts = computed(() => activeAlerts.value.slice(0, 4));

onMounted(() => startSimulation());
onBeforeUnmount(() => stopSimulation());
</script>
