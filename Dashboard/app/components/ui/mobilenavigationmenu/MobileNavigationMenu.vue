<template>
  <div>
    <button
      type="button"
      :class="buttonClasses"
      :aria-expanded="isOpen"
      aria-label="Toggle mobile menu"
      @click="toggleMenu"
    >
      <span
        :class="['hamburger-line', isOpen && 'rotate-45 translate-y-1.5']"
      />
      <span :class="['hamburger-line', isOpen && 'opacity-0']" />
      <span
        :class="['hamburger-line', isOpen && '-rotate-45 -translate-y-1.5']"
      />
    </button>

    <Teleport v-if="isMounted" to="body">
      <Transition
        enter-active-class="transition-opacity duration-300 ease-out"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition-opacity duration-200 ease-in"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div v-if="isOpen" :class="overlayClasses" @click="closeMenu">
          <Transition
            enter-active-class="transition-transform duration-300 ease-out"
            enter-from-class="translate-y-full"
            enter-to-class="translate-y-0"
            leave-active-class="transition-transform duration-200 ease-in"
            leave-from-class="translate-y-0"
            leave-to-class="translate-y-full"
          >
            <div v-if="isOpen" :class="menuClasses" @click.stop>
              <div
                class="flex items-center justify-between px-6 h-14 border-b border-(--nav-border)"
              >
                <span
                  class="font-semibold text-lg tracking-tight text-(--label-text)"
                  >Menu</span
                >
                <button
                  type="button"
                  :class="closeButtonClasses"
                  aria-label="Close menu"
                  @click="closeMenu"
                >
                  <Icon name="mdi:close" class="w-6 h-6" />
                </button>
              </div>

              <div class="flex-1 overflow-y-auto px-6 py-6">
                <slot />
              </div>
            </div>
          </Transition>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import type { MobileNavigationMenuProps } from "~/types/MobileNavigationMenuProps";

const props = withDefaults(defineProps<MobileNavigationMenuProps>(), {
  modelValue: false,
  buttonPosition: "right",
});

const emit = defineEmits<{
  "update:modelValue": [value: boolean];
}>();

const isOpen = computed({
  get: () => props.modelValue,
  set: (value) => emit("update:modelValue", value),
});

const toggleMenu = () => {
  isOpen.value = !isOpen.value;
};

const closeMenu = () => {
  isOpen.value = false;
};

const isMounted = ref(false);

onMounted(() => {
  isMounted.value = true;
});

watch(isOpen, (open) => {
  if (typeof window !== "undefined") {
    if (open) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
  }
});

onBeforeUnmount(() => {
  if (typeof window !== "undefined") {
    document.body.style.overflow = "";
  }
});

const buttonClasses = computed(() => {
  const classes = [
    "flex flex-col justify-center items-center gap-1 w-10 h-10",
    "rounded-full transition-colors",
    "hover:bg-(--nav-trigger-hover) focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500",
  ];

  if (props.buttonPosition === "left") {
    classes.push("order-first");
  }

  return classes.join(" ");
});

const overlayClasses = [
  "fixed inset-0 z-[100] bg-black/50 backdrop-blur-sm",
].join(" ");

const menuClasses = [
  "fixed inset-0 z-[101]",
  "flex flex-col",
  "bg-(--nav-bg) backdrop-blur-xl",
  "shadow-(--nav-content-shadow)",
].join(" ");

const closeButtonClasses = [
  "w-10 h-10 rounded-full flex items-center justify-center",
  "text-(--label-text) transition-colors",
  "hover:bg-(--nav-trigger-hover) focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500",
].join(" ");
</script>

<style scoped>
@reference 'tailwindcss';
.hamburger-line {
  @apply block w-5 h-0.5 bg-(--label-text) transition-all duration-300 ease-out;
}
</style>
