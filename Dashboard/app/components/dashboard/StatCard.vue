<template>
  <div
    class="stat-card-glow rounded-[20px] border border-(--border-color) bg-(--surface-primary) shadow-(--shadow-apple) p-5 transition-all duration-300 hover:shadow-md"
    :class="[`glow-${glowColor}`]"
  >
    <div class="flex items-start justify-between mb-3">
      <div class="h-10 w-10 rounded-xl flex items-center justify-center" :style="{ background: `${iconBg}15` }">
        <Icon :name="icon" class="h-5 w-5" :style="{ color: iconBg }" />
      </div>
      <div v-if="trend" class="flex items-center gap-1 text-xs font-semibold" :class="trend > 0 ? 'text-red-500' : 'text-green-500'">
        <Icon :name="trend > 0 ? 'mdi:trending-up' : 'mdi:trending-down'" class="h-3.5 w-3.5" />
        <span>{{ Math.abs(trend) }}%</span>
      </div>
    </div>
    <p class="text-2xl font-bold text-(--label-text) tracking-tight">{{ formattedValue }}</p>
    <p class="text-sm text-(--hint-text) mt-1">{{ label }}</p>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  icon: string;
  label: string;
  value: number | string;
  trend?: number;
  glowColor?: "danger" | "warning" | "success" | "info" | "primary";
  iconBg?: string;
}>();

const formattedValue = computed(() => {
  if (typeof props.value === "string") return props.value;
  return props.value.toLocaleString();
});
</script>
