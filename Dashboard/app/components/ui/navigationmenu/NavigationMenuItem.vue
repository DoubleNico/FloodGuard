<template>
  <li class="relative list-none" :value="value">
    <LazyPopover
      v-if="isMounted"
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
      <slot name="trigger" />
    </div>
  </li>
</template>

<script setup lang="ts">
defineProps<{
  value?: string;
}>();

const isMounted = ref(false);

onMounted(() => {
  isMounted.value = true;
});
</script>
