<template>
  <div :class="wrapperClasses">
    <label
      v-if="label"
      :for="textareaId"
      class="block text-sm font-medium tracking-tight text-(--label-text)"
    >
      {{ label }}
      <span v-if="required" class="ml-1 text-(--input-error-text)">*</span>
    </label>

    <div class="relative">
      <textarea
        :id="textareaId"
        ref="textareaRef"
        v-bind="$attrs"
        :value="modelValue"
        :rows="rows"
        :disabled="disabled || loading"
        :readonly="readonly"
        :required="required"
        :class="textareaClasses"
        @input="onInput"
        @change="onChange"
        @blur="onBlur"
        @focus="onFocus"
      />

      <div
        v-if="loading"
        class="absolute right-3 top-3 flex items-center justify-center rounded-full bg-(--input-bg) p-1 shadow-sm"
      >
        <Icon
          name="mdi:loading"
          class="h-4 w-4 animate-spin text-(--icon-color)"
        />
      </div>
    </div>

    <div class="flex justify-between gap-4">
      <div class="flex-1">
        <p v-if="error" class="text-[0.8125rem] text-(--input-error-text)">
          {{ error }}
        </p>
        <p v-else-if="hint" class="text-[0.8125rem] text-(--hint-text)">
          {{ hint }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { TextareaProps } from "~/types/Textarea";

const props = withDefaults(defineProps<TextareaProps>(), {
  rows: 3,
  resize: "vertical",
  color: "primary",
  disabled: false,
  readonly: false,
  required: false,
  loading: false,
  block: false,
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

const textareaRef = ref<HTMLTextAreaElement | null>(null);
const textareaId = computed(() => props.id || useId());

defineExpose({
  ref: textareaRef,
  focus: () => textareaRef.value?.focus(),
  blur: () => textareaRef.value?.blur(),
  select: () => textareaRef.value?.select(),
});

const onInput = (event: Event) => {
  const target = event.target as HTMLTextAreaElement;
  emit("update:modelValue", target.value);
};

const onChange = (event: Event) => {
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

const resizeClasses = {
  none: "resize-none",
  both: "resize",
  horizontal: "resize-x",
  vertical: "resize-y",
};

const textareaClasses = computed(() => {
  const classes = [
    "w-full appearance-none rounded-[0.625rem] border-[0.5px] outline-none transition-all duration-200 ease-[cubic-bezier(0.4,0,0.2,1)]",

    "p-3 text-base leading-relaxed",

    "bg-(--input-bg) text-(--input-text) border-(--input-border)",

    "placeholder:font-normal placeholder:text-(--input-placeholder)",

    "shadow-[inset_0_1px_2px_rgba(0,0,0,0.03),0_1px_1px_rgba(0,0,0,0.02)]",

    "hover:border-(--input-border-hover) hover:shadow-[inset_0_1px_2px_rgba(0,0,0,0.04),0_1px_2px_rgba(0,0,0,0.03)]",
  ];

  classes.push(resizeClasses[props.resize]);

  if (props.error) {
    classes.push(
      "border-(--input-error-border) focus:border-(--input-error-border) focus:ring-[3.5px] focus:ring-[rgba(255,59,48,0.12)]"
    );
  } else if (props.readonly) {
    classes.push(
      "cursor-default bg-(--input-disabled-bg) opacity-75 hover:border-(--input-border)"
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
</script>
