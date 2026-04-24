<template>
  <th
    :class="[
      'h-12 px-4 align-middle font-medium text-(--hint-text) transition-colors [&:has([role=checkbox])]:pr-0',
      alignClass,
      $attrs.class,
    ]"
    :aria-sort="ariaSortValue"
  >
    <div :class="['flex items-center w-full h-full', contentAlignClass]">
      <div
        v-if="!sortable"
        class="flex items-center gap-2"
        :class="{ 'flex-row-reverse': align === 'right' }"
      >
        <slot />
      </div>

      <Popover
        v-else
        class="h-full"
        :placement="align === 'right' ? 'bottom-end' : 'bottom-start'"
        :offset="4"
      >
        <template #default>
          <div
            class="flex items-center gap-2 cursor-pointer select-none hover:text-(--label-text) group h-full"
            :class="{ 'flex-row-reverse': align === 'right' }"
          >
            <span class="truncate"><slot /></span>

            <span
              class="flex items-center justify-center rounded p-0.5 transition-opacity duration-200"
              :class="[
                sortDirection
                  ? 'opacity-100 text-(--label-text)'
                  : 'opacity-0 group-hover:opacity-50',
                sortDirection ? 'bg-(--surface-secondary)' : '',
              ]"
            >
              <Icon
                v-if="sortDirection === 'asc'"
                name="mdi:arrow-up"
                class="h-3.5 w-3.5"
              />
              <Icon
                v-else-if="sortDirection === 'desc'"
                name="mdi:arrow-down"
                class="h-3.5 w-3.5"
              />
              <Icon
                v-else
                name="mdi:unfold-more-horizontal"
                class="h-3.5 w-3.5"
              />
            </span>
          </div>
        </template>

        <template #content="{ close }">
          <div
            class="min-w-[160px] p-1 rounded-lg border border-(--border-color) bg-(--surface-primary) shadow-lg flex flex-col gap-0.5"
          >
            <span
              class="px-2 py-1.5 text-xs font-semibold text-(--hint-text) uppercase tracking-wider"
            >
              Sort By
            </span>

            <button
              class="flex items-center justify-between px-2 py-1.5 text-sm rounded-md hover:bg-(--surface-secondary) text-(--label-text) transition-colors"
              @click="handleSort('asc', close)"
            >
              <div class="flex items-center gap-2">
                <Icon
                  name="mdi:sort-ascending"
                  class="h-4 w-4 text-(--icon-color)"
                />
                <span>{{ labelAsc }}</span>
              </div>
              <Icon
                v-if="sortDirection === 'asc'"
                name="mdi:check"
                class="h-3.5 w-3.5 text-primary"
              />
            </button>

            <button
              class="flex items-center justify-between px-2 py-1.5 text-sm rounded-md hover:bg-(--surface-secondary) text-(--label-text) transition-colors"
              @click="handleSort('desc', close)"
            >
              <div class="flex items-center gap-2">
                <Icon
                  name="mdi:sort-descending"
                  class="h-4 w-4 text-(--icon-color)"
                />
                <span>{{ labelDesc }}</span>
              </div>
              <Icon
                v-if="sortDirection === 'desc'"
                name="mdi:check"
                class="h-3.5 w-3.5 text-primary"
              />
            </button>

            <div class="my-1 h-px bg-(--border-color)" />

            <button
              class="flex items-center gap-2 px-2 py-1.5 text-sm rounded-md hover:bg-(--surface-secondary) text-(--input-error-text) transition-colors disabled:opacity-50"
              :disabled="!sortDirection"
              @click="handleSort(null, close)"
            >
              <Icon name="mdi:close" class="h-4 w-4" />
              <span>Clear Sort</span>
            </button>
          </div>
        </template>
      </Popover>
    </div>
  </th>
</template>

<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    align?: "left" | "center" | "right";
    sortable?: boolean;
    sortDirection?: "asc" | "desc" | null;
    labelAsc?: string;
    labelDesc?: string;
  }>(),
  {
    align: "left",
    sortable: false,
    sortDirection: null,
    labelAsc: "Ascending",
    labelDesc: "Descending",
  }
);

const emit = defineEmits<{
  (e: "update:sortDirection" | "sort", value: "asc" | "desc" | null): void;
}>();

const alignClass = computed(() => {
  if (props.align === "center") return "text-center";
  if (props.align === "right") return "text-right";
  return "text-left";
});

const contentAlignClass = computed(() => {
  if (props.align === "center") return "justify-center";
  if (props.align === "right") return "justify-end";
  return "justify-start";
});

const ariaSortValue = computed(() => {
  if (!props.sortable) return undefined;
  if (props.sortDirection === "asc") return "ascending";
  if (props.sortDirection === "desc") return "descending";
  return "none";
});

const handleSort = (dir: "asc" | "desc" | null, closeFn: () => void) => {
  emit("update:sortDirection", dir);
  emit("sort", dir);
  closeFn();
};
</script>
