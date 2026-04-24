<template>
  <div :class="wrapperClasses">
    <label
      v-if="label"
      :for="inputId"
      class="block text-sm font-medium tracking-tight text-(--label-text)"
    >
      {{ label }}
      <span v-if="required" class="ml-1 text-(--input-error-text)">*</span>
    </label>

    <LazyPopover
      v-if="isCustomDate && isMounted"
      placement="bottom-start"
      :offset="8"
      trigger="click"
      :model-value="isCalendarOpen"
      block
      @update:model-value="toggleCalendar"
    >
      <template #default>
        <div class="relative w-full">
          <div
            class="absolute left-0 top-0 flex h-full items-center pl-3 text-(--icon-color) cursor-pointer hover:text-(--label-text) transition-colors z-10"
            @click.stop="toggleCalendar(!isCalendarOpen)"
            @mousedown.prevent
          >
            <Icon :name="iconLeft || 'mdi:calendar'" :class="iconClasses" />
          </div>

          <input
            :id="inputId"
            ref="inputRef"
            v-bind="$attrs"
            v-model="localInputValue"
            type="text"
            :disabled="disabled"
            :readonly="readonly || isMobile"
            :inputmode="isMobile ? 'none' : undefined"
            :required="required"
            :placeholder="placeholder || 'MM/DD/YYYY'"
            :name="name"
            :autocomplete="autocomplete || computedAutocomplete"
            :class="inputClasses"
            @focus="onFocus"
            @blur="onBlur"
            @keydown.enter="parseAndSetDate"
          />

          <div
            v-if="isMobile"
            class="absolute inset-0 z-20 bg-transparent"
            aria-hidden="true"
          />
        </div>
      </template>
      <template #content>
        <div
          class="rounded-2xl border border-(--border-color) bg-(--surface-primary) shadow-(--shadow-apple) overflow-hidden"
        >
          <Calendar
            :model-value="modelValue instanceof Date ? modelValue : null"
            :enable-time="enableTime"
            @update:model-value="onCalendarSelect"
          />
        </div>
      </template>
    </LazyPopover>

    <LazyPopover
      v-else-if="isCustomColor && isMounted"
      placement="bottom-start"
      :offset="8"
      trigger="click"
      :disabled="disabled || readonly"
      block
    >
      <template #default>
        <div class="relative w-full">
          <div
            class="absolute left-0 top-0 flex h-full items-center pl-3 text-(--icon-color) pointer-events-none z-10"
          >
            <div
              class="h-4 w-4 rounded-full border border-(--border-color) shadow-sm bg-[url('/checkboard.png')]"
            >
              <div
                class="h-full w-full rounded-full"
                :style="{ backgroundColor: modelValue as string }"
              />
            </div>
          </div>

          <input
            :id="inputId"
            ref="inputRef"
            v-bind="$attrs"
            type="text"
            :value="modelValue"
            readonly
            :class="inputClasses"
            :disabled="disabled"
            :placeholder="placeholder"
          />

          <div
            v-if="isMobile"
            class="absolute inset-0 z-20 bg-transparent"
            aria-hidden="true"
          />
        </div>
      </template>
      <template #content>
        <ColorPicker
          :model-value="modelValue instanceof String ? (modelValue as string) : '#ffffff'"
          @update:model-value="(val) => emit('update:modelValue', val)"
        />
      </template>
    </LazyPopover>

    <div v-else class="relative isolate">
      <div
        v-if="hasPrefix"
        class="absolute left-0 top-0 z-20 h-full flex items-center pl-1"
        style="
          --input-border: transparent;
          --input-bg: transparent;
          --shadow-inset: none;
        "
      >
        <CustomSelect
          :model-value="prefixValue"
          :options="prefixOptions"
          :searchable="prefixSearchable"
          :disabled="disabled"
          hide-scrollbar
          size="sm"
          class="w-[100px]"
          :name="name ? `${name}-prefix` : undefined"
          autocomplete="tel-country-code"
          @update:model-value="$emit('update:prefixValue', $event)"
        />
      </div>

      <div
        v-else-if="shouldShowLeftSection"
        class="absolute left-0 top-0 flex h-full items-center pl-3 text-(--icon-color) z-10"
      >
        <slot name="iconLeft">
          <Icon
            v-if="iconLeft"
            :name="iconLeft"
            :class="[iconClasses, 'pointer-events-none']"
          />
          <Icon
            v-else-if="
              !loading && ['date', 'month', 'datetime-local'].includes(type)
            "
            name="mdi:calendar"
            :class="[
              iconClasses,
              'cursor-pointer pointer-events-auto hover:opacity-75',
            ]"
            @click="openNativePicker"
          />
          <Icon
            v-else-if="!loading && type === 'time'"
            name="mdi:clock-outline"
            :class="[
              iconClasses,
              'cursor-pointer pointer-events-auto hover:opacity-75',
            ]"
            @click="openNativePicker"
          />
        </slot>
      </div>

      <input
        :id="inputId"
        ref="inputRef"
        v-bind="$attrs"
        :type="computedType"
        :value="modelValue"
        :disabled="disabled"
        :readonly="readonly"
        :required="required"
        :placeholder="placeholder"
        :name="name"
        :autocomplete="autocomplete || computedAutocomplete"
        :autofocus="autofocus"
        :min="min"
        :max="max"
        :step="step"
        :pattern="pattern"
        :maxlength="maxlength"
        :minlength="minlength"
        :class="inputClasses"
        @input="onInput"
        @change="onChange"
        @blur="onBlur"
        @focus="onFocus"
        @keydown="onKeydown"
      />

      <div
        v-if="showRightSection"
        class="absolute right-0 top-0 flex h-full items-center gap-2 pr-3 text-(--icon-color) z-10"
      >
        <button
          v-if="
            clearable &&
            modelValue &&
            !disabled &&
            !readonly &&
            type !== 'password'
          "
          type="button"
          class="flex cursor-pointer items-center border-none bg-transparent p-0 text-(--icon-color) hover:opacity-70"
          tabindex="-1"
          @click="clear"
        >
          <Icon name="mdi:close-circle" :class="iconClasses" />
        </button>
        <div v-if="type === 'password'" class="flex items-center">
          <button
            type="button"
            class="flex cursor-pointer items-center border-none bg-transparent p-0 text-(--icon-color) hover:opacity-75"
            tabindex="-1"
            @click="togglePasswordVisibility"
          >
            <Icon
              :name="isPasswordVisible ? 'mdi:eye-off' : 'mdi:eye'"
              :class="iconClasses"
            />
          </button>
        </div>
        <Icon
          v-if="loading"
          name="mdi:loading"
          :class="[iconClasses, 'animate-spin']"
        />
        <slot name="iconRight">
          <Icon
            v-if="iconRight && !loading && type !== 'password'"
            :name="iconRight"
            :class="[iconClasses, 'cursor-pointer']"
          />
        </slot>
      </div>
    </div>

    <p v-if="error" class="text-[0.8125rem] text-(--input-error-text) mt-1">
      {{ error }}
    </p>
    <p v-else-if="hint" class="text-[0.8125rem] text-(--hint-text) mt-1">
      {{ hint }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { useFocus, useBreakpoints, breakpointsTailwind } from "@vueuse/core";
import type { InputProps } from "~/types/InputProps";

const props = withDefaults(defineProps<InputProps>(), {
  type: "text",
  size: "md",
  color: "primary",
  disabled: false,
  readonly: false,
  required: false,
  loading: false,
  clearable: false,
  block: false,
  autofocus: false,
  enableTime: false,
});

defineOptions({ inheritAttrs: false });

const emit = defineEmits<{
  "update:modelValue": [value: string | number | Date | null];
  "update:prefixValue": [value: string | number];
  change: [event: Event];
  blur: [event: FocusEvent];
  focus: [event: FocusEvent];
  clear: [];
}>();

const breakpoints = useBreakpoints(breakpointsTailwind);
const isMobile = breakpoints.smaller("md");

const inputRef = ref<HTMLInputElement | null>(null);
const inputId = computed(() => props.id || useId());
const isPasswordVisible = ref(false);
const isMounted = ref(false);
const isCalendarOpen = ref(false);
const localInputValue = ref("");

useFocus(inputRef, { initialValue: props.autofocus });

onMounted(() => {
  isMounted.value = true;
  if (props.modelValue instanceof Date) {
    localInputValue.value = formatDate(props.modelValue);
  }
});

watch(
  () => props.modelValue,
  (val) => {
    if (val instanceof Date) {
      localInputValue.value = formatDate(val);
    } else if (!val) {
      localInputValue.value = "";
    }
  }
);

const isCustomColor = computed(() => props.type === "custom-color");
const isCustomDate = computed(() => props.type === "custom-date");
const hasPrefix = computed(
  () =>
    props.type === "tel" &&
    props.prefixOptions &&
    props.prefixOptions.length > 0
);

function formatDate(date: Date) {
  if (isNaN(date.getTime())) return "";
  const options: Intl.DateTimeFormatOptions = {
    year: "numeric",
    month: "numeric",
    day: "numeric",
  };
  if (props.enableTime) {
    options.hour = "2-digit";
    options.minute = "2-digit";
  }
  return date.toLocaleString(undefined, options);
}

function parseAndSetDate() {
  if (!localInputValue.value) {
    emit("update:modelValue", null);
    return;
  }
  const d = new Date(localInputValue.value);
  if (!isNaN(d.getTime())) {
    emit("update:modelValue", d);
  }
}

function onCalendarSelect(date: Date) {
  emit("update:modelValue", date);
  if (!props.enableTime) {
    toggleCalendar(false);
  }
}

function toggleCalendar(val: boolean) {
  if (props.disabled || props.readonly) return;
  if (val) parseAndSetDate();
  isCalendarOpen.value = val;
}

const computedType = computed(() => {
  if (props.type === "password")
    return isPasswordVisible.value ? "text" : "password";
  if (props.type === "custom-color" || props.type === "custom-date")
    return "text";
  return props.type;
});

const computedAutocomplete = computed(() => {
  if (props.autocomplete) return props.autocomplete;
  const map: Record<string, string> = {
    email: "email",
    tel: "tel",
    url: "url",
    search: "off",
    password: props.name?.includes("new") ? "new-password" : "current-password",
    text: props.name?.includes("name")
      ? "name"
      : props.name?.includes("username")
      ? "username"
      : "off",
  };
  return map[props.type] || "off";
});

const togglePasswordVisibility = () =>
  (isPasswordVisible.value = !isPasswordVisible.value);
const isDateOrTimeType = computed(() =>
  ["date", "month", "time", "datetime-local"].includes(props.type)
);

const shouldShowLeftSection = computed(
  () =>
    !hasPrefix.value &&
    (isCustomColor.value ||
      isCustomDate.value ||
      props.iconLeft ||
      !!useSlots().iconLeft ||
      (isDateOrTimeType.value && !props.loading))
);

const showRightSection = computed(
  () =>
    props.loading ||
    props.iconRight ||
    props.type === "password" ||
    (props.clearable && props.modelValue && !props.disabled && !props.readonly)
);

const onKeydown = (e: KeyboardEvent) => {
  if (props.type === "number" && ["e", "E", "+", "-"].includes(e.key))
    e.preventDefault();
};

const onInput = (event: Event) => {
  const target = event.target as HTMLInputElement;
  let val: string | number | null = target.value;
  if (props.type === "number") {
    if (props.max !== undefined && Number(val) > Number(props.max)) {
      val = String(props.max);
      target.value = val;
    }
    val = val === "" ? null : Number(val);
  }
  emit("update:modelValue", val);
};

const onBlur = (event: FocusEvent) => {
  if (props.type === "number") {
    const val = Number(props.modelValue);
    if (props.min !== undefined && val < Number(props.min))
      emit("update:modelValue", Number(props.min));
    if (props.max !== undefined && val > Number(props.max))
      emit("update:modelValue", Number(props.max));
  }
  if (isCustomDate.value) parseAndSetDate();
  emit("blur", event);
};

const onChange = (event: Event) => emit("change", event);
const onFocus = (event: FocusEvent) => emit("focus", event);
const clear = () => {
  emit("update:modelValue", "");
  localInputValue.value = "";
  emit("clear");
  inputRef.value?.focus();
};

const openNativePicker = () => {
  if (inputRef.value && "showPicker" in HTMLInputElement.prototype) {
    try {
      inputRef.value.showPicker();
    } catch (e) {
      console.error(e);
      inputRef.value.focus();
    }
  } else {
    inputRef.value?.focus();
  }
};

const wrapperClasses = computed(() => [
  "flex flex-col gap-1.5",
  props.block && "w-full",
]);

const inputClasses = computed(() => {
  const c = [
    "[&::-webkit-search-cancel-button]:hidden [&::-webkit-search-decoration]:hidden [&::-webkit-calendar-picker-indicator]:hidden",
    "[&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none [&::-moz-range-thumb]:appearance-none",
    "w-full appearance-none rounded-[0.625rem] border-[0.5px] outline-none transition-all duration-200 ease-[cubic-bezier(0.4,0,0.2,1)]",
    "bg-(--input-bg) text-(--input-text) border-(--input-border) placeholder:text-(--input-placeholder)",
    "shadow-[inset_0_1px_2px_rgba(0,0,0,0.03),0_1px_1px_rgba(0,0,0,0.02)]",
    "hover:border-(--input-border-hover) hover:shadow-[inset_0_1px_2px_rgba(0,0,0,0.04),0_1px_2px_rgba(0,0,0,0.03)]",
    "[&:-webkit-autofill]:!shadow-[inset_0_0_0px_1000px_var(--input-bg)]",
    "[&:-webkit-autofill]:[-webkit-text-fill-color:var(--input-text)]",
    "[&:-webkit-autofill]:transition-[background-color_5000s_ease-in-out_0s]",
    "[&:-webkit-autofill:hover]:!shadow-[inset_0_0_0px_1000px_var(--input-bg)]",
    "[&:-webkit-autofill:focus]:!shadow-[inset_0_0_0px_1000px_var(--input-bg)]",
    "[&:-webkit-autofill:active]:!shadow-[inset_0_0_0px_1000px_var(--input-bg)]",
  ];

  const sizeClasses = {
    xs: "px-2 py-1.5 text-xs min-h-7",
    sm: "px-3 py-1.5 text-sm min-h-8",
    base: "px-3.5 py-2 text-base min-h-9",
    md: "px-4 py-2.5 text-base min-h-[2.75rem]",
    lg: "px-5 py-3.5 text-lg min-h-[3.25rem]",
    xl: "px-6 py-4 text-xl min-h-14",
  };
  c.push(sizeClasses[props.size]);

  if (hasPrefix.value) {
    c.push("pl-[130px]");
  } else if (shouldShowLeftSection.value) {
    c.push(
      props.size === "sm" ? "pl-9" : props.size === "lg" ? "pl-13" : "pl-11"
    );
  }

  if (showRightSection.value) {
    c.push(
      props.size === "sm" ? "pr-9" : props.size === "lg" ? "pr-16" : "pr-14"
    );
  }

  if (props.error)
    c.push(
      "border-(--input-error-border) focus:border-(--input-error-border) focus:ring-[3.5px] focus:ring-[rgba(255,59,48,0.12)]"
    );
  else if (props.readonly)
    c.push("cursor-default bg-(--input-disabled-bg) opacity-75");
  else if (props.disabled)
    c.push(
      "cursor-not-allowed bg-(--input-disabled-bg) text-(--input-disabled-text) opacity-50"
    );
  else {
    c.push("focus:border-1 focus:ring-[3.5px]");
    c.push(
      focusColorClasses[props.color as keyof typeof focusColorClasses] ||
        focusColorClasses.primary
    );
  }
  return c.join(" ");
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
const iconClasses = computed(
  () =>
    ({
      xs: "w-3 h-3",
      sm: "w-4 h-4",
      base: "w-5 h-5",
      md: "w-5 h-5",
      lg: "w-6 h-6",
      xl: "w-7 h-7",
    }[props.size])
);
</script>
