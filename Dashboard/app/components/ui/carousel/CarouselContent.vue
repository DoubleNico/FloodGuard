<template>
  <div class="overflow-hidden">
    <div
      ref="carouselRef"
      :class="[
        'flex',
        orientation === 'horizontal' ? '-ml-4' : '-mt-4 flex-col',
        'overflow-x-auto snap-x snap-mandatory scroll-smooth no-scrollbar',
      ]"
    >
      <template v-if="loop && isMounted">
        <slot v-for="i in 3" :key="i" />
      </template>

      <slot v-else />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useEventListener } from "@vueuse/core";

const {
  carouselRef,
  orientation,
  checkScrollability,
  loop,
  initInfiniteScroll,
} = useCarousel();
const isMounted = ref(false);

onMounted(async () => {
  isMounted.value = true;

  await nextTick();

  checkScrollability();
  if (loop) initInfiniteScroll();
});

useEventListener(carouselRef, "scroll", checkScrollability, { passive: true });
useEventListener(window, "resize", checkScrollability);
</script>

<style scoped>
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
