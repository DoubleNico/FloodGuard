<template>
  <div
    v-if="isMobileOpen"
    class="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm md:hidden transition-opacity"
    @click="closeMobile"
  />

  <aside
    class="fixed inset-y-0 left-0 z-50 flex flex-col border-r border-(--border-color) bg-(--surface-primary) transition-all duration-300 ease-in-out md:static"
    :class="[
      isMobileOpen
        ? 'translate-x-0 shadow-xl'
        : '-translate-x-full md:translate-x-0',
      isCollapsed ? 'w-[70px]' : 'w-64',
    ]"
  >
    <slot />
  </aside>
</template>

<script setup lang="ts">
const { isMobileOpen, closeMobile, isCollapsed } = useSidebar();
</script>
