<template>
  <div :class="itemClasses" v-bind="$attrs">
    <slot :in-dropdown="inDropdown" />
  </div>
</template>

<script setup lang="ts">
defineOptions({
  inheritAttrs: false,
});

const inDropdown = inject("inDropdown", false);

const itemClasses = ["w-full"].join(" ");
</script>
