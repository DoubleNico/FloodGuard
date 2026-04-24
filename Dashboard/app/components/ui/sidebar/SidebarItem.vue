<template>
  <Tooltip v-if="isCollapsed" side="right" :text="label" :offset="10">
    <NuxtLink
      :to="to"
      class="relative flex h-10 w-10 items-center justify-center rounded-lg text-(--icon-color) transition-colors hover:bg-(--surface-secondary) hover:text-(--label-text)"
      active-class="bg-(--btn-primary-bg) text-white hover:bg-(--btn-primary-bg) hover:text-white"
      @click="onClick"
    >
      <Icon :name="icon" class="h-5 w-5 shrink-0" />
    </NuxtLink>
  </Tooltip>

  <NuxtLink
    v-else
    :to="to"
    class="group flex h-10 w-full items-center gap-3 rounded-lg px-3 text-sm font-medium text-(--label-text) transition-colors hover:bg-(--surface-secondary)"
    active-class="bg-(--surface-secondary) text-(--color-primary) font-semibold"
    @click="onClick"
  >
    <Icon
      :name="icon"
      class="h-5 w-5 shrink-0 text-(--icon-color) transition-colors group-hover:text-(--label-text)"
      :class="{ 'text-primary': isActive }"
    />
    <span class="truncate">{{ label }}</span>

    <div v-if="$slots.suffix" class="ml-auto">
      <slot name="suffix" />
    </div>
  </NuxtLink>
</template>

<script setup lang="ts">
const props = defineProps<{
  to?: string;
  icon: string;
  label: string;
}>();

const { isCollapsed, closeMobile } = useSidebar();
const route = useRoute();

const isActive = computed(() => props.to && route.path.startsWith(props.to));

const onClick = () => {
  if (window.innerWidth < 768) {
    closeMobile();
  }
};
</script>
