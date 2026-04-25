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

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <Card v-for="factory in factories" :key="factory.id" class="p-5 hover:shadow-lg transition-shadow cursor-pointer" hover @click="navigateTo('/dashboard/industrial/factories')">
        <div class="flex items-start justify-between mb-4">
          <div class="flex items-center gap-3">
            <div class="h-12 w-12 rounded-xl flex items-center justify-center" :style="{ background: `${factoryStatusColor(factory.status)}15` }">
              <Icon name="mdi:factory" class="h-6 w-6" :style="{ color: factoryStatusColor(factory.status) }" />
            </div>
            <div>
              <h3 class="text-base font-semibold text-(--label-text)">{{ factory.name }}</h3>
              <p class="text-xs text-(--hint-text)">{{ factory.location }}</p>
            </div>
          </div>
          <Badge :variant="factory.status === 'operational' ? 'success' : factory.status === 'critical' ? 'danger' : 'secondary'">
            {{ factory.status }}
          </Badge>
        </div>

        <div class="grid grid-cols-3 gap-3">
          <div class="p-2.5 rounded-lg bg-(--surface-secondary)/50 text-center">
            <p class="text-lg font-bold text-(--label-text)">{{ factory.sensorCount }}</p>
            <p class="text-[10px] text-(--hint-text)">Sensors</p>
          </div>
          <div class="p-2.5 rounded-lg bg-(--surface-secondary)/50 text-center">
            <p class="text-lg font-bold text-(--label-text)">{{ factory.employees }}</p>
            <p class="text-[10px] text-(--hint-text)">Employees</p>
          </div>
          <div class="p-2.5 rounded-lg bg-(--surface-secondary)/50 text-center">
            <p class="text-lg font-bold" :class="factory.waterProximity < 100 ? 'text-red-500' : factory.waterProximity < 300 ? 'text-amber-500' : 'text-green-500'">{{ factory.waterProximity }}m</p>
            <p class="text-[10px] text-(--hint-text)">Water Dist.</p>
          </div>
        </div>

        <div class="mt-3 flex items-center justify-between text-xs text-(--hint-text)">
          <span>Risk: <span class="font-semibold capitalize" :style="{ color: factory.riskLevel === 'critical' ? '#EF4444' : factory.riskLevel === 'high' ? '#F97316' : factory.riskLevel === 'moderate' ? '#F59E0B' : '#22C55E' }">{{ factory.riskLevel }}</span></span>
          <span>Last inspection: {{ new Date(factory.lastInspection).toLocaleDateString() }}</span>
        </div>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: "dashboard", middleware: "auth" });
const { factories, criticalFactories, criticalSensors, totalEmployeesAtRisk, factoryStatusColor } = useIndustrial();
</script>
