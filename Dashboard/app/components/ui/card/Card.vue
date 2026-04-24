<template>
  <div
    :class="[
      'rounded-[20px] border border-(--border-color) bg-(--surface-primary) shadow-(--shadow-apple) transition-all duration-200',
      hover ? 'hover:shadow-md hover:border-(--border-hover)' : '',
    ]"
  >
    <slot />
  </div>
</template>

<script setup lang="ts">
defineProps<{
  hover?: boolean;
}>();
</script>
