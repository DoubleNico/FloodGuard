<template>
  <div :class="baseClasses" :style="computedStyles">
    <slot />
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { GridProps } from "~/types/GridProps";

const props = withDefaults(defineProps<GridProps>(), {
  cols: 1,
  gap: 4,
  flow: "row",
  as: "div",
});

const baseClasses = computed(() => {
  const classes = [
    "grid",
    props.content ? `content-${props.content}` : "",
    props.items ? `items-${props.items}` : "",
    props.justify ? `justify-items-${props.justify}` : "",
  ];

  if (props.flow) {
    classes.push(`grid-flow-${props.flow}`);
  }

  if (typeof props.cols === "number" && props.cols > 0 && props.cols <= 12) {
    classes.push(`grid-cols-${props.cols}`);
  }

  if (typeof props.rows === "number" && props.rows > 0 && props.rows <= 6) {
    classes.push(`grid-rows-${props.rows}`);
  }

  if (props.gap) classes.push(`gap-${props.gap}`);
  if (props.gapX) classes.push(`gap-x-${props.gapX}`);
  if (props.gapY) classes.push(`gap-y-${props.gapY}`);

  return classes.filter(Boolean);
});

const computedStyles = computed(() => {
  const styles: Record<string, string> = {};

  if (typeof props.cols !== "number" || props.cols > 12) {
    styles.gridTemplateColumns =
      typeof props.cols === "number"
        ? `repeat(${props.cols}, minmax(0, 1fr))`
        : props.cols;
  }

  if (props.rows) {
    if (typeof props.rows !== "number" || props.rows > 6) {
      styles.gridTemplateRows =
        typeof props.rows === "number"
          ? `repeat(${props.rows}, minmax(0, 1fr))`
          : props.rows;
    }
  }

  return styles;
});
</script>
