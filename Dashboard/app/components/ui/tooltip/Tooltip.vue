<template>
  <Popover
    ref="popoverRef"
    :trigger="trigger"
    :placement="side"
    :offset="sideOffset"
    :hover-delay="delay"
    class="inline-flex"
    @update:model-value="handleStateChange"
  >
    <slot />

    <template #content>
      <div
        class="z-50 overflow-hidden rounded-lg px-3 py-1.5 text-xs font-medium shadow-(--shadow-apple) transition-all animate-in fade-in-0 zoom-in-95 bg-(--surface-secondary) border border-(--border-color) text-(--label-text)"
      >
        <slot name="content">
          {{ text }}
        </slot>
      </div>
    </template>
  </Popover>
</template>

<script setup lang="ts">
import type Popover from "../popover/Popover.vue";

const props = withDefaults(
  defineProps<{
    text?: string;
    side?: "top" | "bottom" | "left" | "right";
    sideOffset?: number;
    delay?: number;
    trigger?: "hover" | "click";
    closeDelay?: number;
  }>(),
  {
    text: "",
    side: "top",
    sideOffset: 6,
    delay: 300,
    trigger: "hover",
    closeDelay: 0,
  }
);

const popoverRef = ref<InstanceType<typeof Popover> | null>(null);
let autoCloseTimer: ReturnType<typeof setTimeout> | null = null;

const handleStateChange = (isOpen: boolean) => {
  if (autoCloseTimer) {
    clearTimeout(autoCloseTimer);
    autoCloseTimer = null;
  }

  if (isOpen && props.trigger === "click" && props.closeDelay > 0) {
    autoCloseTimer = setTimeout(() => {
      popoverRef.value?.close();
    }, props.closeDelay);
  }
};
</script>
