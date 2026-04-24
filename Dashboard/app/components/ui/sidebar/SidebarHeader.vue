<template>
  <div
    class="flex h-16 items-center border-b border-(--border-color) px-4"
    :class="isCollapsed ? 'justify-center' : 'justify-between'"
  >
    <div
      v-if="!isCollapsed"
      class="flex items-center gap-2 overflow-hidden whitespace-nowrap transition-all"
    >
      <slot>
        <span class="text-lg font-bold text-(--label-text)">Brand</span>
      </slot>
    </div>

    <div v-else>
      <slot name="icon">
        <div class="h-8 w-8 rounded-lg bg-primary" />
      </slot>
    </div>

    <button
      v-if="!isCollapsed"
      class="hidden md:flex h-6 w-6 items-center justify-center rounded-md text-(--icon-color) hover:bg-(--surface-secondary) transition-colors"
      @click="toggleCollapse"
    >
      <Icon name="mdi:chevron-left" class="h-4 w-4" />
    </button>
  </div>
</template>

<script setup lang="ts">
import { useSidebar } from "~/composables/useSidebar";
const { isCollapsed, toggleCollapse } = useSidebar();
</script>
