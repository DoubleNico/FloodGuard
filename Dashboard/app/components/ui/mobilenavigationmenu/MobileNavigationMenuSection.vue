<template>
  <div :class="sectionClasses" v-bind="$attrs">
    <h3
      v-if="title"
      class="px-4 py-2 text-sm font-semibold text-(--hint-text) uppercase tracking-wide"
    >
      {{ title }}
    </h3>
    <div class="space-y-1">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { MobileNavigationMenuSectionProps } from "~/types/MobileNavigationMenuProps";

defineProps<MobileNavigationMenuSectionProps>();

defineOptions({
  inheritAttrs: false,
});

const sectionClasses = ["mb-6"].join(" ");
</script>
