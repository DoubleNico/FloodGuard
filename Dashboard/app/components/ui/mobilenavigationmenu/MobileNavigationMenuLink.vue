<template>
  <a :href="href" :class="linkClasses" v-bind="$attrs">
    <slot />
  </a>
</template>

<script setup lang="ts">
import type { MobileNavigationMenuLinkProps } from "~/types/MobileNavigationMenuProps";

const props = withDefaults(defineProps<MobileNavigationMenuLinkProps>(), {
  inDropdown: false,
});

defineOptions({
  inheritAttrs: false,
});

const linkClasses = computed(() => {
  const classes = [
    "flex items-center w-full rounded-xl",
    "text-base transition-colors duration-200",
    "hover:bg-(--nav-trigger-hover)",
    "focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500",
  ];

  if (props.inDropdown) {
    classes.push(
      "px-4 pl-8 py-2",
      "text-sm font-normal text-(--label-text)/80 hover:text-(--label-text)"
    );
  } else {
    classes.push("px-4 py-3", "font-medium text-(--label-text)");
  }

  return classes.join(" ");
});
</script>
