<template>
  <div class="space-y-6 max-w-[1000px] mx-auto">
    <div>
      <h1 class="text-2xl font-bold text-(--label-text) tracking-tight">Subscription & Pricing</h1>
      <p class="text-sm text-(--hint-text) mt-1">Manage your Hydralis plan</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <Card v-for="plan in plans" :key="plan.tier" class="p-6 relative transition-all duration-300" :class="plan.tier === currentTier ? 'ring-2 ring-blue-500 shadow-lg shadow-blue-500/10' : 'hover:shadow-md'" hover>
        <div v-if="plan.tier === currentTier" class="absolute top-4 right-4">
          <Badge variant="success">Current Plan</Badge>
        </div>

        <div class="mb-4">
          <h3 class="text-lg font-bold text-(--label-text)">{{ plan.name }}</h3>
          <div class="flex items-baseline gap-1 mt-2">
            <span class="text-3xl font-bold text-(--label-text)">€{{ plan.price }}</span>
            <span class="text-sm text-(--hint-text)">/month</span>
          </div>
        </div>

        <ul class="space-y-2 mb-6">
          <li v-for="feature in plan.features" :key="feature" class="flex items-center gap-2 text-sm text-(--label-text)">
            <Icon name="mdi:check-circle" class="h-4 w-4 text-green-500 shrink-0" />
            <span>{{ feature }}</span>
          </li>
        </ul>

        <div class="mt-auto">
          <Button v-if="plan.tier !== currentTier" variant="outline" color="primary" block @click="changeTier(plan.tier)">
            {{ plans.indexOf(plan) > plans.findIndex(p => p.tier === currentTier) ? 'Upgrade' : 'Downgrade' }}
          </Button>
          <Button v-else variant="solid" color="primary" block :disabled="true">Active</Button>
        </div>
      </Card>
    </div>

    <Card class="p-6">
      <h2 class="text-lg font-semibold text-(--label-text) mb-4">Current Usage</h2>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="p-4 rounded-xl bg-(--surface-secondary)/50">
          <p class="text-2xl font-bold text-(--label-text)">{{ usage.alertsSent }}</p>
          <p class="text-xs text-(--hint-text)">Alerts Sent</p>
          <div v-if="currentPlan.limits.alerts > 0" class="water-gauge mt-2">
            <div class="water-gauge-fill" :style="{ width: `${(usage.alertsSent / currentPlan.limits.alerts) * 100}%`, background: (usage.alertsSent / currentPlan.limits.alerts) > 0.8 ? '#EF4444' : '#22C55E' }" />
          </div>
          <p v-if="currentPlan.limits.alerts > 0" class="text-[10px] text-(--hint-text) mt-1">{{ usage.alertsSent }}/{{ currentPlan.limits.alerts }}</p>
          <p v-else class="text-[10px] text-green-500 mt-1">Unlimited</p>
        </div>
        <div class="p-4 rounded-xl bg-(--surface-secondary)/50">
          <p class="text-2xl font-bold text-(--label-text)">{{ usage.locationsConfigured }}</p>
          <p class="text-xs text-(--hint-text)">Locations</p>
          <div v-if="currentPlan.limits.locations > 0" class="water-gauge mt-2">
            <div class="water-gauge-fill" :style="{ width: `${(usage.locationsConfigured / currentPlan.limits.locations) * 100}%`, background: '#3B82F6' }" />
          </div>
        </div>
        <div class="p-4 rounded-xl bg-(--surface-secondary)/50">
          <p class="text-2xl font-bold text-(--label-text)">{{ usage.sensorsConnected }}</p>
          <p class="text-xs text-(--hint-text)">Sensors</p>
        </div>
        <div class="p-4 rounded-xl bg-(--surface-secondary)/50">
          <p class="text-2xl font-bold text-(--label-text)">{{ usage.activeUsers }}</p>
          <p class="text-xs text-(--hint-text)">Active Users</p>
        </div>
      </div>
    </Card>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: "dashboard", middleware: "auth" });
const { currentTier, plans, currentPlan, usage, changeTier } = useSubscription();
</script>
