<template>
  <div :class="dropdownClasses">
    <button
      type="button"
      :class="triggerClasses"
      :aria-expanded="isOpen"
      @click="toggleDropdown"
    >
      <span class="flex-1 text-left">{{ title }}</span>
      <Icon
        name="mdi:chevron-down"
        :class="[
          'w-5 h-5 transition-transform duration-200',
          isOpen && 'rotate-180',
        ]"
      />
    </button>

    <Transition
      enter-active-class="transition-all duration-200 ease-out"
      enter-from-class="opacity-0 max-h-0"
      enter-to-class="opacity-100 max-h-[500px]"
      leave-active-class="transition-all duration-200 ease-in"
      leave-from-class="opacity-100 max-h-[500px]"
      leave-to-class="opacity-0 max-h-0"
    >
      <div v-if="isOpen" class="overflow-hidden">
        <div class="py-2 space-y-1">
          <slot />
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import type { MobileNavigationMenuDropdownProps } from "~/types/MobileNavigationMenuProps";

const props = withDefaults(defineProps<MobileNavigationMenuDropdownProps>(), {
  defaultOpen: false,
});

const isOpen = ref(props.defaultOpen);

provide("inDropdown", true);

const toggleDropdown = () => {
  isOpen.value = !isOpen.value;
};

const dropdownClasses = ["w-full mb-2"];

const triggerClasses = [
  "flex items-center w-full px-4 py-3 rounded-xl",
  "text-base font-semibold text-(--label-text)",
  "transition-colors duration-200",
  "hover:bg-(--nav-trigger-hover)",
  "focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500",
].join(" ");
</script>
