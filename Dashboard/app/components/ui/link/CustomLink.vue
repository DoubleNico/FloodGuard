<template>
  <NuxtLink :to="to" :target="target" :class="linkClasses" v-bind="$attrs">
    <slot />
  </NuxtLink>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { LinkProps } from "~/types/LinkProps";

defineOptions({
  inheritAttrs: false,
});

const props = withDefaults(defineProps<LinkProps>(), {
  variant: "primary",
  underline: true,
  weight: "medium",
  size: "base",
});

const linkClasses = computed(() => {
  const classes = [
    "inline-flex items-center gap-1 cursor-pointer transition-colors duration-200",
    "focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:rounded-sm",
  ];

  const colorMap = {
    primary:
      "text-(--btn-primary-bg) hover:text-(--btn-primary-hover) focus-visible:ring-(--btn-primary-bg)",
    secondary:
      "text-(--btn-secondary-bg) hover:text-(--btn-secondary-hover) focus-visible:ring-(--btn-secondary-bg)",
    accent:
      "text-(--btn-accent-bg) hover:text-(--btn-accent-hover) focus-visible:ring-(--btn-accent-bg)",
    success:
      "text-(--btn-success-bg) hover:text-(--btn-success-hover) focus-visible:ring-(--btn-success-bg)",
    danger:
      "text-(--btn-danger-bg) hover:text-(--btn-danger-hover) focus-visible:ring-(--btn-danger-bg)",
    default:
      "text-(--label-text) hover:text-(--label-text)/80 focus-visible:ring-(--label-text)",
    muted:
      "text-(--hint-text) hover:text-(--label-text) focus-visible:ring-(--hint-text)",
  };

  classes.push(colorMap[props.variant] || colorMap.primary);

  const weightMap = {
    normal: "font-normal",
    medium: "font-medium",
    semibold: "font-semibold",
    bold: "font-bold",
  };

  classes.push(weightMap[props.weight]);

  const sizeMap = {
    xs: "text-xs",
    sm: "text-sm",
    md: "text-md",
    lg: "text-lg",
    base: "text-base",
    xl: "text-xl",
  };
  classes.push(sizeMap[props.size]);

  if (props.underline) {
    classes.push("hover:underline underline-offset-4");
  }

  return classes.join(" ");
});
</script>
