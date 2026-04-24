<template>
  <button
    type="button"
    role="tab"
    :aria-selected="isActive"
    :tabindex="tabIndex"
    :disabled="disabled"
    :class="triggerClasses"
    @click="handleClick"
  >
    <span class="relative z-10 flex items-center gap-2">
      <slot />
    </span>

    <span
      v-if="isActive"
      class="absolute inset-0 z-0 rounded-[0.5rem] bg-(--surface-primary) shadow-sm transition-all duration-200 ease-[cubic-bezier(0.4,0,0.2,1)]"
      layout-id="active-tab-bg"
    />
  </button>
</template>

<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    value: string | number;
    disabled?: boolean;
  }>(),
  {
    disabled: false,
  }
);

const context = inject<{
  activeValue: Ref<string | number>;
  setValue: (val: string | number) => void;
}>("tabs-context");

const isActive = computed(() => context?.activeValue.value === props.value);

const tabIndex = computed(() => (isActive.value ? 0 : -1));

const handleClick = () => {
  if (!props.disabled && context) {
    context.setValue(props.value);
  }
};

const triggerClasses = computed(() => [
  "relative inline-flex items-center justify-center whitespace-nowrap rounded-[0.5rem] px-3 py-1.5 text-sm font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-(--color-primary) ring-offset-2",
  "disabled:pointer-events-none disabled:opacity-50",
  isActive.value
    ? "text-(--label-text)"
    : "text-(--hint-text) hover:text-(--label-text) hover:bg-black/5 dark:hover:bg-white/5",
]);
</script>
