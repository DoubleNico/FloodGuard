<template>
  <Button
    :disabled="!canScrollNext"
    variant="outline"
    size="sm"
    rounded="full"
    class="absolute h-8 w-8 rounded-full p-0 z-10 opacity-70 hover:opacity-100 disabled:opacity-0 transition-opacity bg-(--surface-primary) shadow-sm"
    :class="
      orientation === 'horizontal'
        ? '-right-4 top-1/2 -translate-y-1/2'
        : '-bottom-4 left-1/2 -translate-x-1/2 rotate-90'
    "
    @click="scrollNext"
  >
    <Icon name="mdi:chevron-right" class="h-4 w-4 text-(--icon-color)" />
    <span class="sr-only">Next slide</span>
  </Button>
</template>

<script setup lang="ts">
const { orientation, scrollNext, canScrollNext } = useCarousel();
</script>
