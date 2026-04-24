<template>
  <div :style="itemStyles">
    <slot />
  </div>
</template>

<script setup lang="ts">
import type { GridItemProps } from "~/types/GridItemProps";

const props = defineProps<GridItemProps>();

const itemStyles = computed(() => {
  const styles: Record<string, string> = {};

  if (props.span) {
    const val = String(props.span);
    styles.gridColumn = val === "full" ? "1 / -1" : `span ${val} / span ${val}`;
  } else if (props.start || props.end) {
    styles.gridColumnStart = props.start?.toString() ?? "auto";
    styles.gridColumnEnd = props.end?.toString() ?? "auto";
  }

  if (props.rowSpan) {
    const val = String(props.rowSpan);
    styles.gridRow = val === "full" ? "1 / -1" : `span ${val} / span ${val}`;
  } else if (props.rowStart || props.rowEnd) {
    styles.gridRowStart = props.rowStart?.toString() ?? "auto";
    styles.gridRowEnd = props.rowEnd?.toString() ?? "auto";
  }

  return styles;
});
</script>
