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

    <div class="relative">
      <div
        v-if="iconLeft || $slots.iconLeft"
        class="pointer-events-none absolute left-0 top-0 flex h-full items-center pl-3 text-(--icon-color)"
      >
        <slot name="iconLeft">
          <Icon v-if="iconLeft" :name="iconLeft" :class="iconClasses" />
        </slot>
      </div>

      <select
        :id="selectId"
        ref="selectRef"
        v-bind="$attrs"
        :value="modelValue"
        :disabled="disabled || loading"
        :required="required"
        :class="selectClasses"
        @change="onChange"
        @blur="onBlur"
        @focus="onFocus"
      >
        <option v-if="placeholder" value="" disabled selected>
          {{ placeholder }}
        </option>

        <template v-for="(option, index) in normalizedOptions" :key="index">
          <option :value="option.value" :disabled="option.disabled">
            {{ option.label }}
          </option>
        </template>
      </select>

      <div
        class="pointer-events-none absolute right-0 top-0 flex h-full items-center pr-3 text-(--icon-color)"
      >
        <Icon
          v-if="loading"
          name="mdi:loading"
          :class="[iconClasses, 'animate-spin']"
        />
        <svg
          v-else
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 20 20"
          fill="currentColor"
          aria-hidden="true"
          :class="iconClasses"
        >
          <path
            fill-rule="evenodd"
            d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z"
            clip-rule="evenodd"
          />
        </svg>
      </div>
    </div>

    <p v-if="error" class="text-[0.8125rem] text-(--input-error-text)">
      {{ error }}
    </p>
    <p v-else-if="hint" class="text-[0.8125rem] text-(--hint-text)">
      {{ hint }}
    </p>
  </div>
</template>

<script setup lang="ts">
import type { SelectProps, SelectOption } from "~/types/SelectProps";

const props = withDefaults(defineProps<SelectProps>(), {
  size: "md",
  color: "primary",
  disabled: false,
  required: false,
  loading: false,
  block: false,
  options: () => [],
});

defineOptions({
  inheritAttrs: false,
});

const emit = defineEmits<{
  "update:modelValue": [value: string | number];
  change: [event: Event];
  blur: [event: FocusEvent];
  focus: [event: FocusEvent];
}>();

const selectRef = ref<HTMLSelectElement | null>(null);
const selectId = computed(() => props.id || useId());

defineExpose({
  ref: selectRef,
  focus: () => selectRef.value?.focus(),
  blur: () => selectRef.value?.blur(),
});

const normalizedOptions = computed<SelectOption[]>(() => {
  return props.options.map((opt) => {
    if (typeof opt === "string" || typeof opt === "number") {
      return { label: String(opt), value: opt };
    }
    return opt;
  });
});

const onChange = (event: Event) => {
  const target = event.target as HTMLSelectElement;
  emit("update:modelValue", target.value);
  emit("change", event);
};

const onBlur = (event: FocusEvent) => {
  emit("blur", event);
};

const onFocus = (event: FocusEvent) => {
  emit("focus", event);
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

const selectClasses = computed(() => {
  const classes = [
    "w-full appearance-none rounded-[0.625rem] border-[0.5px] outline-none transition-all duration-200 ease-[cubic-bezier(0.4,0,0.2,1)] cursor-pointer",

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

const iconClasses = computed(() => {
  const sizeClasses = {
    sm: "w-4 h-4",
    md: "w-5 h-5",
    lg: "w-6 h-6",
  };
  return sizeClasses[props.size];
});
</script>
