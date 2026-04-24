<template>
  <div :class="wrapperClasses">
    <label
      v-if="label"
      :for="selectId"
      class="block text-sm font-medium tracking-tight text-(--label-text)"
    >
      {{ label }}
      <span v-if="required" class="ml-1 text-(--input-error-text)">*</span>
    </label>

    <LazyPopover
      v-if="isMounted"
      v-model="isOpen"
      block
      placement="bottom"
      :offset="4"
      :disabled="disabled || loading"
    >
      <template #default>
        <div ref="containerRef" class="relative" :class="wrapperClasses">
          <div
            v-if="iconLeft || $slots.iconLeft"
            class="pointer-events-none absolute left-0 top-0 z-20 flex h-full items-center pl-3 text-(--icon-color)"
          >
            <slot name="iconLeft">
              <Icon v-if="iconLeft" :name="iconLeft" :class="iconClasses" />
            </slot>
          </div>

          <button
            :id="selectId"
            ref="triggerRef"
            type="button"
            :disabled="disabled || loading"
            :class="triggerClasses"
            :aria-expanded="isOpen"
            aria-haspopup="listbox"
            @keydown="onKeydown"
          >
            <span v-if="selectedOption" class="flex items-center">
              <Icon
                v-if="selectedOption.icon"
                :name="selectedOption.icon"
                :class="['mr-2', iconClasses]"
              />
              <span class="truncate">{{ selectedOption.label }}</span>
            </span>
            <span v-else class="block truncate text-(--input-placeholder)">
              {{ placeholder || "Select an option" }}
            </span>

            <span
              class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3"
            >
              <Icon
                v-if="loading"
                name="mdi:loading"
                :class="[iconClasses, 'animate-spin']"
              />
              <Icon
                v-else-if="clearable && modelValue && !disabled"
                name="mdi:close-circle"
                :class="[
                  iconClasses,
                  'pointer-events-auto cursor-pointer hover:text-(--input-error-text) transition-colors',
                ]"
                @click.stop="clearSelection"
              />
              <svg
                v-else
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 20 20"
                fill="currentColor"
                aria-hidden="true"
                :class="[
                  iconClasses,
                  'transition-transform duration-200',
                  isOpen && 'rotate-180',
                ]"
              >
                <path
                  fill-rule="evenodd"
                  d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z"
                  clip-rule="evenodd"
                />
              </svg>
            </span>
          </button>
        </div>
      </template>

      <template #content>
        <div
          :class="dropdownClasses"
          role="listbox"
          :aria-labelledby="selectId"
          :style="{ width: `${triggerRef?.offsetWidth}px` }"
        >
          <div v-if="searchable" class="p-2">
            <input
              ref="searchRef"
              v-model="searchQuery"
              type="text"
              placeholder="Search..."
              class="w-full rounded-[0.5rem] border border-(--input-border) bg-(--input-bg) px-3 py-1.5 text-sm text-(--input-text) placeholder:text-(--input-placeholder) outline-none focus:border-(--btn-primary-bg) focus:ring-2 focus:ring-[color-mix(in_srgb,var(--btn-primary-bg)_12%,transparent)]"
              @keydown.stop="onSearchKeydown"
            />
          </div>

          <ul
            ref="optionsRef"
            class="max-h-60 overflow-auto py-1"
            :class="{ 'scrollbar-hide': hideScrollbar }"
            :style="
              hideScrollbar
                ? 'scrollbar-width: none; -ms-overflow-style: none;'
                : ''
            "
          >
            <li
              v-for="(option, index) in filteredOptions"
              :key="option.value"
              :class="optionClasses(option, index)"
              :aria-selected="option.value === modelValue"
              :aria-disabled="option.disabled"
              role="option"
              @click.stop="selectOption(option)"
              @mouseenter="highlightedIndex = index"
            >
              <Icon
                v-if="option.icon"
                :name="option.icon"
                :class="['mr-2', iconClasses]"
              />
              <span class="block truncate">{{ option.label }}</span>
              <Icon
                v-if="option.value === modelValue"
                name="mdi:check"
                :class="['ml-auto', iconClasses]"
              />
            </li>
            <li
              v-if="filteredOptions.length === 0"
              class="px-3 py-2 text-sm text-(--input-placeholder)"
            >
              No options found
            </li>
          </ul>
        </div>
      </template>
    </LazyPopover>

    <p v-if="error" class="text-[0.8125rem] text-(--input-error-text)">
      {{ error }}
    </p>
    <p v-else-if="hint" class="text-[0.8125rem] text-(--hint-text)">
      {{ hint }}
    </p>
  </div>
</template>

<script setup lang="ts">
import type {
  CustomSelectProps,
  CustomSelectOption,
} from "~/types/CustomSelectProps";

const props = withDefaults(defineProps<CustomSelectProps>(), {
  size: "md",
  color: "primary",
  disabled: false,
  required: false,
  loading: false,
  block: false,
  searchable: false,
  clearable: false,
  hideScrollbar: false,
  options: () => [],
});

defineOptions({
  inheritAttrs: false,
});

const emit = defineEmits<{
  "update:modelValue": [value: string | number];
  change: [value: string | number];
}>();

const containerRef = ref<HTMLDivElement | null>(null);
const triggerRef = ref<HTMLButtonElement | null>(null);
const searchRef = ref<HTMLInputElement | null>(null);
const optionsRef = ref<HTMLUListElement | null>(null);
const selectId = computed(() => props.id || useId());

const isOpen = ref(false);
const searchQuery = ref("");
const highlightedIndex = ref(0);

defineExpose({
  ref: triggerRef,
  focus: () => triggerRef.value?.focus(),
  blur: () => triggerRef.value?.blur(),
  open: () => (isOpen.value = true),
  close: () => (isOpen.value = false),
});

const selectedOption = computed(() => {
  return props.options?.find((opt) => opt.value === props.modelValue);
});

const filteredOptions = computed(() => {
  if (!props.searchable || !searchQuery.value) {
    return props.options || [];
  }
  const query = searchQuery.value.toLowerCase();
  return (props.options || []).filter((opt) =>
    opt.label.toLowerCase().includes(query)
  );
});

watch(isOpen, (value) => {
  if (value) {
    highlightedIndex.value = Math.max(
      0,
      filteredOptions.value.findIndex((opt) => opt.value === props.modelValue)
    );
    nextTick(() => {
      if (props.searchable && searchRef.value) {
        searchRef.value.focus();
      }
      scrollToHighlighted();
    });
  } else {
    searchQuery.value = "";
  }
});

const selectOption = (option: CustomSelectOption) => {
  if (option.disabled) return;
  emit("update:modelValue", option.value);
  emit("change", option.value);
  isOpen.value = false;
};

const clearSelection = () => {
  emit("update:modelValue", "");
  emit("change", "");
  isOpen.value = false;
};

const onKeydown = (event: KeyboardEvent) => {
  switch (event.key) {
    case "ArrowDown":
      event.preventDefault();
      if (!isOpen.value) {
        isOpen.value = true;
      } else {
        highlightedIndex.value = Math.min(
          highlightedIndex.value + 1,
          filteredOptions.value.length - 1
        );
        scrollToHighlighted();
      }
      break;
    case "ArrowUp":
      event.preventDefault();
      if (isOpen.value) {
        highlightedIndex.value = Math.max(highlightedIndex.value - 1, 0);
        scrollToHighlighted();
      }
      break;
    case "Enter":
    case " ":
      event.preventDefault();
      if (isOpen.value) {
        const option = filteredOptions.value[highlightedIndex.value];
        if (option) {
          selectOption(option);
        }
      } else {
        isOpen.value = true;
      }
      break;
    case "Escape":
      event.preventDefault();
      if (isOpen.value) {
        isOpen.value = false;
      }
      break;
    case "Tab":
      if (isOpen.value) {
        isOpen.value = false;
      }
      break;
  }
};

const onSearchKeydown = (event: KeyboardEvent) => {
  if (event.key === "ArrowDown" || event.key === "ArrowUp") {
    event.preventDefault();
    onKeydown(event);
  } else if (event.key === "Enter") {
    event.preventDefault();
    const option = filteredOptions.value[highlightedIndex.value];
    if (option) {
      selectOption(option);
    }
  } else if (event.key === "Escape") {
    event.preventDefault();
    isOpen.value = false;
  }
};

const scrollToHighlighted = () => {
  nextTick(() => {
    const optionsList = optionsRef.value;
    const highlightedOption = optionsList?.children[
      highlightedIndex.value
    ] as HTMLElement;
    if (highlightedOption) {
      highlightedOption.scrollIntoView({ block: "nearest" });
    }
  });
};

const wrapperClasses = computed(() => {
  const classes = ["flex flex-col gap-1.5"];
  if (props.block) {
    classes.push("w-full");
  }
  return classes.join(" ");
});

const sizeClasses = {
  sm: "pl-3 pr-8 py-1.5 text-sm min-h-8",
  md: "pl-4 pr-10 py-2.5 text-base min-h-[2.75rem]",
  lg: "pl-5 pr-12 py-3.5 text-lg min-h-[3.25rem]",
};

const paddingLeftWithIcon = {
  sm: "pl-9",
  md: "pl-11",
  lg: "pl-13",
};

const focusColorClasses = {
  primary:
    "focus:border-(--btn-primary-bg) focus:ring-[color-mix(in_srgb,var(--btn-primary-bg)_12%,transparent)]",
  secondary:
    "focus:border-(--btn-secondary-bg) focus:ring-[color-mix(in_srgb,var(--btn-secondary-bg)_12%,transparent)]",
  accent:
    "focus:border-(--btn-accent-bg) focus:ring-[color-mix(in_srgb,var(--btn-accent-bg)_12%,transparent)]",
  success:
    "focus:border-(--btn-success-bg) focus:ring-[color-mix(in_srgb,var(--btn-success-bg)_12%,transparent)]",
  danger:
    "focus:border-(--btn-danger-bg) focus:ring-[color-mix(in_srgb,var(--btn-danger-bg)_12%,transparent)]",
};

const triggerClasses = computed(() => {
  const classes = [
    "w-full text-left appearance-none rounded-[0.625rem] border-[0.5px] outline-none transition-all duration-200 ease-[cubic-bezier(0.4,0,0.2,1)] cursor-pointer",

    "bg-(--input-bg) text-(--input-text) border-(--input-border)",

    "shadow-[inset_0_1px_2px_rgba(0,0,0,0.03),0_1px_1px_rgba(0,0,0,0.02)]",

    "hover:border-(--input-border-hover) hover:shadow-[inset_0_1px_2px_rgba(0,0,0,0.04),0_1px_2px_rgba(0,0,0,0.03)]",
  ];

  classes.push(sizeClasses[props.size]);

  if (props.iconLeft) {
    classes.push(paddingLeftWithIcon[props.size]);
  }

  if (props.error) {
    classes.push(
      "border-(--input-error-border) focus:border-(--input-error-border) focus:ring-[3.5px] focus:ring-[rgba(255,59,48,0.12)]"
    );
  } else if (props.disabled) {
    classes.push(
      "cursor-not-allowed bg-(--input-disabled-bg) text-(--input-disabled-text) opacity-50"
    );
  } else {
    classes.push("focus:border-1 focus:ring-[3.5px]");
    classes.push(
      focusColorClasses[props.color as keyof typeof focusColorClasses] ||
        focusColorClasses.primary
    );
  }

  return classes.join(" ");
});

const dropdownClasses = computed(() => {
  return [
    "z-10 w-full rounded-[0.625rem] border border-(--input-border)",
    "bg-(--input-bg) shadow-[0_4px_12px_rgba(0,0,0,0.1),0_2px_4px_rgba(0,0,0,0.06)]",
    "backdrop-blur-sm overflow-hidden",
  ].join(" ");
});

const optionClasses = (option: CustomSelectOption, index: number) => {
  const classes = [
    "flex items-center px-3 py-2 text-sm cursor-pointer transition-colors duration-150",
    "text-(--input-text)",
  ];

  if (option.disabled) {
    classes.push("opacity-50 cursor-not-allowed bg-(--input-disabled-bg)");
  } else if (index === highlightedIndex.value) {
    classes.push(
      "bg-[color-mix(in_srgb,var(--btn-primary-bg)_8%,transparent)]"
    );
  } else {
    classes.push(
      "hover:bg-[color-mix(in_srgb,var(--btn-primary-bg)_5%,transparent)]"
    );
  }

  if (option.value === props.modelValue) {
    classes.push("font-medium");
  }

  return classes.join(" ");
};

const iconClasses = computed(() => {
  const sizeClasses = {
    sm: "w-4 h-4",
    md: "w-5 h-5",
    lg: "w-6 h-6",
  };
  return sizeClasses[props.size];
});

const isMounted = ref(false);

onMounted(() => {
  isMounted.value = true;
});
</script>

<style scoped>
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
</style>
