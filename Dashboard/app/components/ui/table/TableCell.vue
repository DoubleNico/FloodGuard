<template>
  <td
    :class="[
      'p-4 align-middle text-(--label-text) [&:has([role=checkbox])]:pr-0',
      alignClass,
      $attrs.class,
    ]"
  >
    <div :class="['flex items-center w-full gap-2', contentAlignClass]">
      <slot />
    </div>
  </td>
</template>

<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    align?: "left" | "center" | "right";
  }>(),
  {
    align: "left",
  }
);

const alignClass = computed(() => {
  if (props.align === "center") return "text-center";
  if (props.align === "right") return "text-right";
  return "text-left";
});

const contentAlignClass = computed(() => {
  if (props.align === "center") return "justify-center";
  if (props.align === "right") return "justify-end";
  return "justify-start";
});
</script>
