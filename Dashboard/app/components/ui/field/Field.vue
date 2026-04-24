<template>
  <div :class="['flex flex-col gap-1.5', $attrs.class]">
    <label
      v-if="label"
      :for="fieldId"
      class="block text-sm font-medium tracking-tight text-(--label-text)"
    >
      {{ label }}
      <span v-if="required" class="ml-1 text-(--input-error-text)">*</span>
    </label>

    <slot
      :id="fieldId"
      :aria-describedby="descriptionId"
      :aria-invalid="!!error"
      :aria-required="required"
    />

    <p
      v-if="error"
      :id="errorId"
      class="text-[0.8125rem] text-(--input-error-text)"
      role="alert"
    >
      {{ error }}
    </p>

    <p
      v-else-if="hint"
      :id="hintId"
      class="text-[0.8125rem] text-(--hint-text)"
    >
      {{ hint }}
    </p>
  </div>
</template>

<script setup lang="ts">
import type { FieldProps } from "~/types/FieldProps";

defineOptions({
  inheritAttrs: false,
});

const props = withDefaults(defineProps<FieldProps>(), {
  required: false,
  id: undefined,
});

const fieldId = computed(() => props.id || useId());
const errorId = computed(() => `${fieldId.value}-error`);
const hintId = computed(() => `${fieldId.value}-hint`);

const descriptionId = computed(() => {
  if (props.error) return errorId.value;
  if (props.hint) return hintId.value;
  return undefined;
});
</script>
