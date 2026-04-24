<template>
  <div :class="classes">
    <slot />
  </div>
</template>

<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    modelValue?: string | number;
    defaultValue?: string | number;
    orientation?: "horizontal" | "vertical";
  }>(),
  {
    orientation: "horizontal",
  }
);

const emit = defineEmits(["update:modelValue"]);

const innerValue = ref(props.defaultValue ?? "");

const activeValue = computed({
  get: () => props.modelValue ?? innerValue.value,
  set: (val) => {
    innerValue.value = val;
    emit("update:modelValue", val);
  },
});

const registeredTabs = ref<
  Array<{ value: string | number; element?: HTMLElement }>
>([]);

const registerTab = (value: string | number) => {
  if (!registeredTabs.value.find((t) => t.value === value)) {
    registeredTabs.value.push({ value });
  }
};

const unregisterTab = (value: string | number) => {
  registeredTabs.value = registeredTabs.value.filter((t) => t.value !== value);
};

provide("tabs-context", {
  activeValue,
  orientation: props.orientation,
  setValue: (val: string | number) => {
    activeValue.value = val;
  },
  registerTab,
  unregisterTab,
  registeredTabs: computed(() => registeredTabs.value),
});

const classes = computed(() => {
  return props.orientation === "vertical" ? "flex gap-4" : "w-full";
});
</script>
