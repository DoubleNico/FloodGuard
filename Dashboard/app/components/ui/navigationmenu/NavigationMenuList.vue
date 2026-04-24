<template>
  <ul :class="listClasses" v-bind="$attrs">
    <slot />
  </ul>
</template>

<script setup lang="ts">
import type { NavigationMenuListProps } from "~/types/NavigationMenuProps";

const props = withDefaults(defineProps<NavigationMenuListProps>(), {
  align: "center",
});

defineOptions({
  inheritAttrs: false,
});

const navigationMenu = inject<{
  orientation: string;
}>("navigationMenu", { orientation: "horizontal" });

const listClasses = computed(() => {
  const classes = ["group flex list-none items-center"];

  if (navigationMenu.orientation === "horizontal") {
    classes.push("flex-row space-x-1");
  } else {
    classes.push("flex-col space-y-1");
  }

  if (props.align === "left") {
    classes.push("justify-start");
  } else if (props.align === "right") {
    classes.push("justify-end");
  } else {
    classes.push("justify-center");
  }

  return classes.join(" ");
});
</script>
