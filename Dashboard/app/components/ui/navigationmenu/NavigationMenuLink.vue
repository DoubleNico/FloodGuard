<template>
  <component
    :is="asChild ? 'div' : 'a'"
    :href="!asChild ? href : undefined"
    :target="!asChild ? target : undefined"
    :class="linkClasses"
    v-bind="$attrs"
  >
    <slot />
  </component>
</template>

<script setup lang="ts">
import type { NavigationMenuLinkProps } from "~/types/NavigationMenuProps";

const props = withDefaults(defineProps<NavigationMenuLinkProps>(), {
  active: false,
  asChild: false,
});

defineOptions({ inheritAttrs: false });

const linkClasses = computed(() => {
  const classes = [
    "block select-none rounded-xl p-3 no-underline outline-none transition-all duration-200",
    "hover:bg-[color-mix(in_srgb,var(--color-primary)_10%,transparent)]", // some hover tint, todo: make it more fine
    "focus:bg-[color-mix(in_srgb,var(--color-primary)_15%,transparent)]",
  ];

  if (props.active) {
    classes.push(
      "bg-[color-mix(in_srgb,var(--color-primary)_15%,transparent)]"
    );
  }

  return classes.join(" ");
});
</script>
