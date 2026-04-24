<template>
  <button
    ref="buttonRef"
    v-bind="$attrs"
    :type="type"
    :disabled="disabled || loading"
    :class="buttonClasses"
  >
    <Icon v-if="loading" name="mdi:loading" class="animate-spin" />
    <Icon v-else-if="iconLeft" :name="iconLeft" />
    <span v-if="$slots.default"><slot /></span>
    <Icon v-if="iconRight && !loading" :name="iconRight" />
  </button>
</template>

<script setup lang="ts">
import type { ButtonProps } from "~/types/ButtonProps";

// Define that the component does not inherit attributes automatically
defineOptions({
  inheritAttrs: false,
});

const buttonRef = ref<HTMLButtonElement | null>(null);

// allow parent to access if needed
defineExpose({
  ref: buttonRef,
});

const props = withDefaults(defineProps<ButtonProps>(), {
  variant: "solid",
  size: "md",
  type: "button",
  disabled: false,
  loading: false,
  block: false,
  rounded: "md",
  iconLeft: undefined,
  iconRight: undefined,
});

const buttonClasses = computed(() => {
  const classes = [
    "btn",
    "inline-flex items-center justify-center gap-2 cursor-pointer",
    "font-medium transition-all duration-200",
    "focus:outline-none focus:ring-2 focus:ring-offset-2",
    "disabled:opacity-40 disabled:cursor-not-allowed",
    "active:scale-[0.98]",
  ];

  const sizeClasses = {
    xs: "px-3 py-1.5 text-xs min-h-[28px]",
    sm: "px-4 py-2 text-sm min-h-[32px]",
    md: "px-5 py-2.5 text-base min-h-[36px]",
    lg: "px-6 py-3 text-lg min-h-[44px]",
    xl: "px-7 py-3.5 text-xl min-h-[52px]",
  };
  classes.push(sizeClasses[props.size]);

  const roundedClasses = {
    none: "rounded-none",
    sm: "rounded-md",
    md: "rounded-lg",
    lg: "rounded-xl",
    full: "rounded-full",
  };
  classes.push(roundedClasses[props.rounded]);

  classes.push(`btn-${props.variant}`);

  if (props.color) {
    classes.push(`btn-${props.variant}-${props.color}`);
  }

  if (props.block) {
    classes.push("w-full");
  }

  return classes.join(" ");
});
</script>
