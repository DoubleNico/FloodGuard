<template>
  <span class="transition-colors duration-500 rounded px-1" :class="flashClass">
    <slot />
  </span>
</template>

<script setup lang="ts">
const props = defineProps<{ value: number | string }>();

const flashClass = ref("");
let timeout: ReturnType<typeof setTimeout>;
watch(
  () => props.value,
  (newVal, oldVal) => {
    if (newVal === oldVal) return;

    flashClass.value = "bg-(--surface-secondary) text-(--label-text)";

    clearTimeout(timeout);
    timeout = setTimeout(() => {
      flashClass.value = "";
    }, 300);
  }
);
</script>
