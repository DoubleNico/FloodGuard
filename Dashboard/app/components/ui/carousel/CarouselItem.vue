<template>
  <div
    role="group"
    aria-roledescription="slide"
    v-bind="$attrs"
    :class="[
      'min-w-0 shrink-0 grow-0 snap-start',
      orientation === 'horizontal' ? 'pl-4' : 'pt-4',
      $attrs.class,
    ]"
  >
    <slot />
  </div>
</template>

<script setup lang="ts">
defineOptions({
  inheritAttrs: false,
});

const { orientation } = useCarousel();
</script>
