<template>
  <div
    ref="listRef"
    role="tablist"
    :aria-orientation="orientation === 'vertical' ? 'vertical' : 'horizontal'"
    :class="[
      'inline-flex items-center justify-center rounded-[0.625rem] bg-(--surface-secondary) p-1 text-(--hint-text)',
      orientation === 'vertical' ? 'flex-col h-fit' : 'h-10',
    ]"
    @keydown="handleKeyDown"
  >
    <slot />
  </div>
</template>

<script setup lang="ts">
const context = inject<{ orientation: string }>("tabs-context");
const orientation = context?.orientation || "horizontal";
const listRef = ref<HTMLElement | null>(null);

const handleKeyDown = (e: KeyboardEvent) => {
  if (!listRef.value) return;

  const tabs = Array.from(
    listRef.value.querySelectorAll('[role="tab"]:not([disabled])')
  ) as HTMLElement[];
  const index = tabs.indexOf(document.activeElement as HTMLElement);

  if (index === -1) return;

  let nextIndex = index;
  const isHorizontal = orientation === "horizontal";

  switch (e.key) {
    case isHorizontal ? "ArrowRight" : "ArrowDown":
      nextIndex = (index + 1) % tabs.length;
      e.preventDefault();
      break;
    case isHorizontal ? "ArrowLeft" : "ArrowUp":
      nextIndex = (index - 1 + tabs.length) % tabs.length;
      e.preventDefault();
      break;
    case "Home":
      nextIndex = 0;
      e.preventDefault();
      break;
    case "End":
      nextIndex = tabs.length - 1;
      e.preventDefault();
      break;
  }

  if (nextIndex !== index) {
    tabs[nextIndex]?.focus();
    tabs[nextIndex]?.click();
  }
};
</script>
