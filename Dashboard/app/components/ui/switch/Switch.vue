<template>
  <div :class="wrapperClasses">
    <label
      v-if="label && labelPosition === 'left'"
      :for="switchId"
      class="cursor-pointer select-none text-sm font-medium tracking-tight text-(--label-text)"
    >
      {{ label }}
      <span v-if="required" class="ml-1 text-(--input-error-text)">*</span>
    </label>

    <button
      :id="switchId"
      ref="switchRef"
      type="button"
      role="switch"
      :aria-checked="modelValue"
      :aria-label="label || 'Toggle switch'"
      :disabled="disabled"
      :class="switchClasses"
      @click="toggle"
      @keydown.space.prevent="toggle"
      @keydown.enter.prevent="toggle"
    >
      <span :class="thumbClasses" aria-hidden="true" />

      <input
        v-if="name"
        v-bind="$attrs"
        type="checkbox"
        :name="name"
        :checked="modelValue"
        class="sr-only"
        tabindex="-1"
      />
    </button>

    <label
      v-if="label && labelPosition === 'right'"
      :for="switchId"
      class="cursor-pointer select-none text-sm font-medium tracking-tight text-(--label-text)"
    >
      {{ label }}
      <span v-if="required" class="ml-1 text-(--input-error-text)">*</span>
    </label>
  </div>
</template>

<script setup lang="ts">
import type { SwitchProps } from "~/types/SwitchProps";

const props = withDefaults(defineProps<SwitchProps>(), {
  modelValue: false,
  size: "md",
  disabled: false,
  labelPosition: "right",
  required: false,
});

defineOptions({
  inheritAttrs: false,
});

const emit = defineEmits<{
  "update:modelValue": [value: boolean];
  change: [value: boolean];
}>();

const switchRef = ref<HTMLButtonElement | null>(null);
const switchId = computed(() => props.id || useId());

defineExpose({
  ref: switchRef,
});

const toggle = () => {
  if (props.disabled) return;
  const newValue = !props.modelValue;
  emit("update:modelValue", newValue);
  emit("change", newValue);
};

const wrapperClasses = computed(() => {
  const classes = ["inline-flex items-center gap-3"];
  if (props.disabled) {
    classes.push("opacity-50 cursor-not-allowed");
  }
  return classes.join(" ");
});

const switchClasses = computed(() => {
  const classes = [
    "relative inline-flex flex-shrink-0 cursor-pointer rounded-full border-none outline-none transition-colors duration-200 ease-[cubic-bezier(0.4,0,0.2,1)]",
    "focus-visible:ring-4 focus-visible:ring-[color-mix(in_srgb,var(--btn-primary-bg)_20%,transparent)]",
  ];

  const sizeClasses = {
    sm: "h-5 w-9",
    md: "h-6 w-11",
    lg: "h-7 w-14",
  };
  classes.push(sizeClasses[props.size]);

  if (props.modelValue) {
    const activeColorClasses = {
      primary: "bg-(--btn-primary-bg)",
      secondary: "bg-(--btn-secondary-bg)",
      accent: "bg-(--btn-accent-bg)",
      success: "bg-(--btn-success-bg)",
      danger: "bg-(--btn-danger-bg)",
    };

    if (props.color && activeColorClasses[props.color]) {
      classes.push(activeColorClasses[props.color]);
    } else {
      classes.push(activeColorClasses.primary);
    }
  } else {
    classes.push("bg-(--switch-bg-off)");
  }

  if (props.class) {
    classes.push(props.class);
  }

  if (props.disabled) {
    classes.push("cursor-not-allowed");
  }

  return classes.join(" ");
});

const thumbClasses = computed(() => {
  const classes = [
    "pointer-events-none inline-block rounded-full bg-white shadow ring-0 transition-transform duration-200 ease-[cubic-bezier(0.4,0,0.2,1)]",
    "shadow-[0_1px_3px_rgba(0,0,0,0.1),0_1px_2px_rgba(0,0,0,0.06)]",
  ];

  const sizeConfig = {
    sm: {
      size: "h-4 w-4 m-0.5",
      translate: "translate-x-4",
    },
    md: {
      size: "h-5 w-5 m-0.5",
      translate: "translate-x-5",
    },
    lg: {
      size: "h-6 w-6 m-0.5",
      translate: "translate-x-7",
    },
  };

  const config = sizeConfig[props.size];

  classes.push(config.size);

  if (props.modelValue) {
    classes.push(config.translate);
  } else {
    classes.push("translate-x-0");
  }

  return classes.join(" ");
});
</script>
