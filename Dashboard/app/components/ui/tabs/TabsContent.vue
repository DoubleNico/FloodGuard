<template>
  <div
    v-if="shouldRender"
    v-show="shouldShow"
    :id="panelId"
    role="tabpanel"
    :tabindex="tabIndex"
    :aria-labelledby="ariaLabelledBy"
    :class="contentClasses"
  >
    <slot />
  </div>
</template>

<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    value: string | number;
    unmount?: boolean;
    forceMount?: boolean;
  }>(),
  {
    unmount: false,
    forceMount: false,
  }
);

const context = inject<{ activeValue: Ref<string | number> }>("tabs-context");

const isActive = computed(() => context?.activeValue.value === props.value);

const shouldRender = computed(() => {
  if (props.forceMount) return true;
  return props.unmount ? isActive.value : true;
});

const shouldShow = computed(() => {
  if (props.forceMount) return true;
  return props.unmount ? true : isActive.value;
});

const panelId = computed(() => `tab-panel-${props.value}`);
const ariaLabelledBy = computed(() => `tab-trigger-${props.value}`);

const tabIndex = computed(() => (isActive.value ? 0 : -1));

const contentClasses = computed(() => [
  "mt-2 w-full",
  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-(--color-primary) focus-visible:ring-offset-2",
  "transition-opacity duration-150",
  isActive.value ? "opacity-100" : "opacity-0",
]);
</script>
