<template>
  <span
    class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 border"
    :class="variantClasses"
  >
    <slot />
  </span>
</template>

<script setup lang="ts">
import type { BadgeVariant } from "~/types/BadgeVariant";

const props = withDefaults(
  defineProps<{
    variant?: BadgeVariant;
  }>(),
  {
    variant: "default",
  }
);

const variantClasses = computed(() => {
  switch (props.variant) {
    case "success":
      return "border-transparent bg-(--btn-success-bg) text-(--btn-success-text) shadow-sm hover:opacity-80";
    case "danger":
      return "border-transparent bg-(--btn-danger-bg) text-(--btn-danger-text) shadow-sm hover:opacity-80";
    case "secondary":
      return "border-transparent bg-(--btn-secondary-bg) text-(--btn-secondary-text) hover:opacity-80";
    case "outline":
      return "text-(--label-text) border-(--border-color)";
    default:
      return "border-transparent bg-(--btn-primary-bg) text-(--btn-primary-text) shadow-sm hover:opacity-80";
  }
});
</script>
