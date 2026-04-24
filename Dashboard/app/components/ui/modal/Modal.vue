<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition duration-300 ease-out"
      leave-active-class="transition duration-200 ease-in"
      enter-from-class="opacity-0"
      leave-to-class="opacity-0"
    >
      <div
        v-if="modelValue"
        class="fixed inset-0 z-100 flex items-center justify-center p-4 sm:p-6 bg-black/40 backdrop-blur-md"
        @click="onOverlayClick"
      >
        <Transition
          enter-active-class="transition duration-400 ease-[cubic-bezier(0.32,0.72,0,1)]"
          leave-active-class="transition duration-200 ease-in"
          enter-from-class="opacity-0 scale-95 translate-y-4"
          leave-to-class="opacity-0 scale-95 translate-y-4"
        >
          <div
            v-if="modelValue"
            ref="panelRef"
            :class="panelClasses"
            role="dialog"
            aria-modal="true"
            :aria-labelledby="title ? 'modal-title' : undefined"
            @click.stop
          >
            <header
              v-if="!hideHeader"
              class="flex items-center justify-between px-6 py-4 border-b border-(--border-color) shrink-0"
            >
              <slot name="header" :close="close">
                <h2
                  v-if="title"
                  id="modal-title"
                  class="text-[17px] font-semibold leading-6 text-(--label-text) tracking-tight"
                >
                  {{ title }}
                </h2>
              </slot>

              <button
                v-if="!hideClose"
                type="button"
                class="ml-auto group relative inline-flex h-7 w-7 items-center justify-center rounded-full text-(--icon-color) transition-colors hover:bg-(--btn-ghost-bg) hover:text-(--label-text) focus:outline-none focus-visible:ring-2 focus-visible:ring-primary cursor-pointer"
                aria-label="Close modal"
                @click="close"
              >
                <Icon name="mdi:close" class="h-4.5 w-4.5" />
              </button>
            </header>

            <main class="flex-1 overflow-y-auto p-6 text-(--label-text)">
              <slot :close="close" />
            </main>

            <footer
              v-if="$slots.footer"
              class="flex items-center justify-end gap-3 px-6 py-4 border-t border-(--border-color) bg-(--surface-secondary)/30 shrink-0"
            >
              <slot name="footer" :close="close" />
            </footer>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { useEventListener } from "@vueuse/core";
import type { ModalProps } from "~/types/ModalProps";

const props = withDefaults(defineProps<ModalProps>(), {
  modelValue: false,
  persistent: false,
  hideClose: false,
  size: "md",
});

const emit = defineEmits<{
  "update:modelValue": [value: boolean];
}>();

const panelRef = ref<HTMLElement | null>(null);

const hideHeader = computed(
  () => !props.title && !props.hideClose && !useSlots().header
);

const panelClasses = computed(() => [
  "relative flex flex-col rounded-[20px] max-h-[90vh] w-full overflow-hidden",

  "bg-(--surface-primary) shadow-(--shadow-apple)",

  "border border-(--border-color) ring-1 ring-black/5",
  "modal-panel",

  {
    "max-w-[400px]": props.size === "sm",
    "max-w-[550px]": props.size === "md",
    "max-w-[750px]": props.size === "lg",
    "max-w-[960px]": props.size === "xl",
    "max-w-full h-[90vh] mx-4": props.size === "full",
  },
  props.panelClass,
]);

const close = () => {
  emit("update:modelValue", false);
};

const onOverlayClick = () => {
  if (!props.persistent) {
    close();
  }
};

onMounted(() => {
  useEventListener(document, "keydown", (e: KeyboardEvent) => {
    if (!props.persistent && e.key === "Escape" && props.modelValue) {
      close();
    }
  });

  watch(
    () => props.modelValue,
    (isOpen) => {
      if (typeof document !== "undefined") {
        if (isOpen) {
          document.body.style.overflow = "hidden";
          document.body.style.paddingRight = "var(--scrollbar-width, 0px)";
        } else {
          document.body.style.overflow = "";
          document.body.style.paddingRight = "";
        }
      }
    },
    { immediate: true }
  );

  const handleFocus = (e: KeyboardEvent) => {
    if (e.key !== "Tab" || !panelRef.value) return;

    const focusable = panelRef.value.querySelectorAll<HTMLElement>(
      'a[href], button:not([disabled]), input:not([disabled]), textarea:not([disabled]), select:not([disabled]), details, [tabindex]:not([tabindex="-1"])'
    );

    if (focusable.length === 0) return;

    const first = focusable[0];
    const last = focusable[focusable.length - 1];

    if (e.shiftKey) {
      if (document.activeElement === first) {
        if (last) last.focus();
        e.preventDefault();
      }
    } else {
      if (document.activeElement === last) {
        if (first) first.focus();
        e.preventDefault();
      }
    }
  };

  watch(
    () => props.modelValue,
    (isOpen) => {
      if (isOpen) {
        document.addEventListener("keydown", handleFocus);

        nextTick(() => {
          setTimeout(() => {
            const focusable = panelRef.value?.querySelector<HTMLElement>(
              'input:not([disabled]), button:not([disabled]), [tabindex]:not([tabindex="-1"])'
            );
            focusable?.focus();
          }, 50);
        });
      } else {
        document.removeEventListener("keydown", handleFocus);
      }
    }
  );
});

onBeforeUnmount(() => {
  if (typeof document !== "undefined") {
    document.body.style.overflow = "";
    document.body.style.paddingRight = "";
  }
});
</script>
