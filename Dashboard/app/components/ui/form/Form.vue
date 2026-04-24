<template>
  <form
    :class="['flex flex-col gap-6', $attrs.class]"
    @submit.prevent="handleSubmit"
  >
    <slot />
  </form>
</template>

<script setup lang="ts">
defineOptions({
  inheritAttrs: false,
});

const emit = defineEmits<{
  submit: [event: Event];
}>();

const handleSubmit = (event: Event) => {
  emit("submit", event);
};
</script>
