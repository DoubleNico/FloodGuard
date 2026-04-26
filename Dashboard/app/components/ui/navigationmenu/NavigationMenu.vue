<template>
  <nav ref="navRef" :class="navClasses" v-bind="$attrs">
    <div
      class="absolute inset-0 bg-(--nav-bg) backdrop-blur-xl border-b border-(--nav-border) -z-10"
    ></div>

    <div v-if="$slots.left" class="flex shrink-0 items-center relative z-10">
      <slot name="left" />
    </div>
    <div :class="centerClasses">
      <slot />
    </div>
    <div v-if="$slots.right" class="flex shrink-0 items-center relative z-10">
      <slot name="right" />
    </div>
  </nav>
</template>

<script setup lang="ts">
import type { NavigationMenuProps } from "~/types/NavigationMenuProps";

const props = withDefaults(defineProps<NavigationMenuProps>(), {
  viewport: true,
  orientation: "horizontal",
});

defineOptions({
  inheritAttrs: false,
});

const slots = useSlots();
const navRef = ref<HTMLElement | null>(null);
const activeValue = ref(props.defaultValue || "");

const updateActiveValue = (value: string) => {
  activeValue.value = value;
};

provide("navigationMenu", {
  activeValue,
  updateActiveValue,
  orientation: props.orientation,
  viewport: props.viewport,
});

const hasLeftOrRight = computed(() => slots.left || slots.right);

const navClasses = computed(() => {
  const classes = [
    "sticky top-0 z-50 flex items-center w-full gap-4 transition-all duration-300",
  ];

  if (props.orientation === "horizontal") {
    classes.push("flex-row");
    if (hasLeftOrRight.value) {
      classes.push("justify-between");
    } else {
      classes.push("justify-center");
    }
  } else {
    classes.push("flex-col");
  }

  return classes.join(" ");
});

const centerClasses = computed(() => {
  const classes = ["flex items-center relative z-10"];
  if (props.orientation === "horizontal") {
    classes.push("flex-1 min-w-0 justify-center");
  } else {
    classes.push("w-full");
  }
  if (!hasLeftOrRight.value && props.orientation === "horizontal") {
    classes.push("justify-center");
  }
  return classes.join(" ");
});
</script>
