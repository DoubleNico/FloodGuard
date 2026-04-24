<template>
  <div :class="contentClasses" v-bind="$attrs">
    <slot />
  </div>
</template>

<script setup lang="ts">
import type { NavigationMenuContentProps } from "~/types/NavigationMenuProps";

defineProps<NavigationMenuContentProps>();

defineOptions({ inheritAttrs: false });

const contentClasses = computed(() => {
  return [
    "origin-top",
    "rounded-2xl",
    "border border-(--nav-content-border)",
    "bg-(--nav-content-bg)",
    "backdrop-blur-2xl saturate-150",
    "shadow-(--nav-content-shadow)",
    "p-2",
    "z-50",
    "w-auto",
  ].join(" ");
});
</script>
