<template>
  <li class="relative list-none" :value="value">
    <LazyPopover
      v-if="isMounted && hasPopoverSlots"
      trigger="hover"
      :hover-delay="200"
      placement="bottom"
    >
      <template #default>
        <slot name="trigger" />
      </template>
      <template #content>
        <slot name="content" />
      </template>
    </LazyPopover>
    <div v-else>
      <slot name="trigger">
        <slot />
      </slot>
    </div>
  </li>
</template>

<script setup lang="ts">
defineProps<{
  value?: string;
}>();

const slots = useSlots();
const isMounted = ref(false);
const hasPopoverSlots = computed(() => Boolean(slots.trigger || slots.content));

onMounted(() => {
  isMounted.value = true;
});
</script>
