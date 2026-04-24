<template>
  <button
    ref="triggerRef"
    type="button"
    :disabled="disabled"
    :class="triggerClasses"
    v-bind="$attrs"
  >
    <slot />
  </button>
</template>

<script setup lang="ts">
import type { NavigationMenuTriggerProps } from "~/types/NavigationMenuProps";

defineProps<NavigationMenuTriggerProps>();

defineOptions({ inheritAttrs: false });

const triggerRef = ref<HTMLButtonElement | null>(null);

const triggerClasses = computed(() => {
  return [
    "group relative inline-flex h-8 items-center justify-center rounded-full",
    "px-3 text-[13px] font-medium leading-none tracking-tight transition-all duration-200 ease-out",
    "text-(--label-text)/80",
    "hover:bg-(--nav-trigger-hover) hover:text-(--label-text)",
    "focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500",
    "disabled:pointer-events-none disabled:opacity-50",
  ].join(" ");
});
</script>
