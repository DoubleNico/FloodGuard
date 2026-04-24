<template>
  <Popover trigger="click" placement="bottom-start" :offset="8" class="w-full">
    <template #default>
      <div class="relative w-full">
        <Input
          :model-value="displayValue"
          :readonly="isMobile"
          type="text"
          :label="label"
          :placeholder="placeholder"
          :icon-left="icon"
          :inputmode="isMobile ? 'none' : undefined"
          class="cursor-pointer"
          :class="$attrs.class"
        />

        <div
          v-if="isMobile"
          class="absolute inset-0 z-20 bg-transparent cursor-pointer"
          aria-hidden="true"
        />
      </div>
    </template>

    <template #content="{ close }">
      <div
        class="rounded-2xl border border-(--border-color) bg-(--surface-primary) shadow-(--shadow-apple) overflow-hidden"
      >
        <Calendar
          :model-value="modelValue"
          :enable-time="enableTime"
          @update:model-value="(val) => onSelect(val, close)"
        />
      </div>
    </template>
  </Popover>
</template>

<script setup lang="ts">
import { useBreakpoints, breakpointsTailwind } from "@vueuse/core";

const props = withDefaults(
  defineProps<{
    modelValue?: Date | string | null;
    label?: string;
    placeholder?: string;
    icon?: string;
    enableTime?: boolean;
  }>(),
  {
    placeholder: "Pick a date",
    icon: "mdi:calendar",
    enableTime: false,
  }
);

const emit = defineEmits(["update:modelValue"]);

const breakpoints = useBreakpoints(breakpointsTailwind);
const isMobile = breakpoints.smaller("md");

const isMounted = ref(false);
onMounted(() => {
  isMounted.value = true;
});

const formattedDate = computed(() => {
  if (!props.modelValue) return "";
  const d = new Date(props.modelValue);
  if (isNaN(d.getTime())) return "";

  const options: Intl.DateTimeFormatOptions = {
    month: "long",
    day: "numeric",
    year: "numeric",
  };

  if (props.enableTime) {
    options.hour = "2-digit";
    options.minute = "2-digit";
  }

  return d.toLocaleString("en-US", options);
});

const displayValue = computed(() => {
  if (!isMounted.value) return "";
  return formattedDate.value;
});

const onSelect = (date: Date, close: () => void) => {
  emit("update:modelValue", date);
  if (!props.enableTime) {
    close();
  }
};
</script>
