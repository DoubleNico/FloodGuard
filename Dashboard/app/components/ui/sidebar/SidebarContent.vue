<template>
  <div
    class="flex-1 overflow-y-auto overflow-x-hidden p-3 space-y-1 scrollbar-hide"
  >
    <slot />
  </div>
</template>

<style scoped>
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
