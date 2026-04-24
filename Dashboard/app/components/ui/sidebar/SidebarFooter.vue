<template>
  <div class="border-t border-(--border-color) p-3">
    <slot :is-collapsed="isCollapsed" />
  </div>
</template>

<script setup lang="ts">
const { isCollapsed } = useSidebar();
</script>
