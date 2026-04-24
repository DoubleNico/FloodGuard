<template>
  <nav :class="listClasses" v-bind="$attrs">
    <slot />
  </nav>
</template>

<script setup lang="ts">
defineOptions({
  inheritAttrs: false,
});

const listClasses = ["flex flex-col space-y-1"].join(" ");
</script>
