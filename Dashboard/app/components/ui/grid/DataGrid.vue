<template>
  <div
    class="flex flex-col w-full h-full border border-(--border-color) rounded-xl overflow-hidden bg-(--surface-primary)"
  >
    <Grid
      :cols="gridTemplateColumns"
      gap="0"
      class="border-b border-(--border-color) bg-(--surface-secondary) text-(--hint-text) text-xs font-bold uppercase tracking-wider select-none sticky top-0 z-20 shadow-sm"
    >
      <GridItem
        v-if="enableRowReorder"
        class="border-r border-(--border-color) flex items-center justify-center bg-(--surface-secondary)"
      >
        <Icon name="mdi:drag" class="opacity-0" />
      </GridItem>

      <GridItem
        v-for="(col, index) in tableColumns"
        :key="col.key"
        class="relative flex items-center px-4 py-3 border-r border-(--border-color) last:border-r-0 hover:bg-[color-mix(in_srgb,var(--surface-secondary)_90%,black)] transition-colors group"
        :class="[
          getAlignClass(col.align),
          draggedColIndex === index
            ? 'opacity-40 border-dashed border-(--border-color)'
            : '',
        ]"
        draggable="true"
        @dragstart="onColDragStart($event, index)"
        @dragover.prevent
        @drop="onColDrop(index)"
      >
        <div
          class="mr-2 cursor-grab text-(--hint-text) opacity-0 group-hover:opacity-100 transition-opacity"
        >
          <Icon name="mdi:drag-vertical" class="w-4 h-4" />
        </div>

        <div
          class="flex items-center gap-2 w-full h-full min-w-0"
          :class="getContentAlignClass(col.align)"
        >
          <div v-if="!col.sortable" class="truncate">
            {{ col.label }}
          </div>

          <Popover
            v-else
            class="h-full min-w-0 flex-1"
            :placement="col.align === 'right' ? 'bottom-end' : 'bottom-start'"
            :offset="4"
          >
            <template #default>
              <div
                class="flex items-center gap-2 cursor-pointer select-none hover:text-(--label-text) group/sort h-full"
                :class="getContentAlignClass(col.align)"
              >
                <span class="truncate">{{ col.label }}</span>

                <span
                  class="flex items-center justify-center rounded p-0.5 transition-opacity duration-200"
                  :class="[
                    sortState.key === col.key
                      ? 'opacity-100 text-(--label-text) bg-(--surface-secondary)'
                      : 'opacity-0 group-hover/sort:opacity-50',
                  ]"
                >
                  <Icon
                    v-if="sortState.key === col.key && sortState.dir === 'asc'"
                    name="mdi:arrow-up"
                    class="w-3.5 h-3.5"
                  />
                  <Icon
                    v-else-if="
                      sortState.key === col.key && sortState.dir === 'desc'
                    "
                    name="mdi:arrow-down"
                    class="w-3.5 h-3.5"
                  />
                  <Icon
                    v-else
                    name="mdi:unfold-more-horizontal"
                    class="w-3.5 h-3.5"
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
                  >Sort By</span
                >

                <button
                  class="flex items-center justify-between px-2 py-1.5 text-sm rounded-md hover:bg-(--surface-secondary) text-(--label-text) transition-colors"
                  @click="
                    handleSort(col.key, 'asc');
                    close();
                  "
                >
                  <div class="flex items-center gap-2">
                    <Icon
                      name="mdi:sort-ascending"
                      class="h-4 w-4 text-(--icon-color)"
                    />
                    <span>{{ col.sortLabels?.asc || "Ascending" }}</span>
                  </div>
                  <Icon
                    v-if="sortState.key === col.key && sortState.dir === 'asc'"
                    name="mdi:check"
                    class="h-3.5 w-3.5 text-primary"
                  />
                </button>

                <button
                  class="flex items-center justify-between px-2 py-1.5 text-sm rounded-md hover:bg-(--surface-secondary) text-(--label-text) transition-colors"
                  @click="
                    handleSort(col.key, 'desc');
                    close();
                  "
                >
                  <div class="flex items-center gap-2">
                    <Icon
                      name="mdi:sort-descending"
                      class="h-4 w-4 text-(--icon-color)"
                    />
                    <span>{{ col.sortLabels?.desc || "Descending" }}</span>
                  </div>
                  <Icon
                    v-if="sortState.key === col.key && sortState.dir === 'desc'"
                    name="mdi:check"
                    class="h-3.5 w-3.5 text-primary"
                  />
                </button>

                <div class="my-1 h-px bg-(--border-color)" />
                <button
                  class="flex items-center gap-2 px-2 py-1.5 text-sm rounded-md hover:bg-(--surface-secondary) text-(--input-error-text) transition-colors disabled:opacity-50"
                  :disabled="sortState.key !== col.key"
                  @click="
                    handleSort(null, null);
                    close();
                  "
                >
                  <Icon name="mdi:close" class="h-4 w-4" />
                  <span>Clear Sort</span>
                </button>
              </div>
            </template>
          </Popover>
        </div>
      </GridItem>
    </Grid>

    <div
      ref="scrollContainer"
      class="overflow-y-auto flex-1 scrollbar-hide relative"
    >
      <template v-if="visibleData.length > 0">
        <Grid
          v-for="(row, rowIndex) in visibleData"
          :key="row[rowKey] || rowIndex"
          :cols="gridTemplateColumns"
          gap="0"
          class="border-b border-(--border-color) last:border-b-0 hover:bg-(--surface-secondary) transition-colors text-sm text-(--label-text) group"
          :class="[
            enableRowReorder ? 'cursor-move' : '',
            draggedRowIndex === rowIndex
              ? 'opacity-40 bg-(--surface-secondary)'
              : '',
            dragOverRowIndex === rowIndex ? 'border-b-2 border-primary' : '',
          ]"
          :draggable="enableRowReorder"
          @dragstart="onRowDragStart($event, rowIndex)"
          @dragover.prevent="onRowDragOver($event, rowIndex)"
          @drop="onRowDrop(rowIndex)"
          @dragend="resetDragState"
        >
          <GridItem
            v-if="enableRowReorder"
            class="w-[40px] border-r border-(--border-color) flex items-center justify-center text-(--hint-text) cursor-grab hover:text-(--label-text)"
          >
            <Icon name="mdi:drag" class="w-5 h-5" />
          </GridItem>

          <GridItem
            v-for="col in tableColumns"
            :key="col.key"
            class="px-4 py-3 border-r border-(--border-color) last:border-r-0 flex items-center truncate h-full"
            :class="getAlignClass(col.align)"
          >
            <slot :name="col.key" :row="row" :value="row[col.key]">
              <span class="truncate">
                {{ row[col.key] }}
              </span>
            </slot>
          </GridItem>
        </Grid>

        <div
          v-if="visibleData.length < sortedData.length"
          class="p-4 text-center text-xs text-(--hint-text) animate-pulse"
        >
          Loading more...
        </div>
      </template>

      <div
        v-else
        class="flex flex-col items-center justify-center h-48 text-(--hint-text)"
      >
        <Icon name="mdi:database-off" class="w-8 h-8 mb-2 opacity-50" />
        <p>No data available</p>
      </div>
    </div>

    <div
      v-if="$slots.footer"
      class="border-t border-(--border-color) bg-(--surface-secondary) p-2 text-xs text-(--hint-text)"
    >
      <slot
        name="footer"
        :total="sortedData.length"
        :showing="visibleData.length"
      />
    </div>
  </div>
</template>

<script setup lang="ts" generic="T extends Record<string, any>">
import { useInfiniteScroll } from "@vueuse/core";
import type { Column } from "~/types/Column";

const props = withDefaults(
  defineProps<{
    columns: Column[];
    data: T[];
    pageSize?: number;
    enableRowReorder?: boolean;
    rowKey?: string;
  }>(),
  {
    pageSize: 50,
    enableRowReorder: false,
    rowKey: "id",
  }
);

const emit = defineEmits<{
  "update:data": [value: T[]];
  "update:columns": [value: Column[]];
}>();

const tableColumns = ref<Column[]>([...props.columns]);
const tableData = ref<T[]>([...props.data]);

watch(
  () => props.columns,
  (v) => (tableColumns.value = [...v]),
  { deep: true }
);

watch(
  () => props.data,
  (v) => (tableData.value = [...v]),
  { deep: true }
);

const gridTemplateColumns = computed(() => {
  const cols = tableColumns.value.map((c) => c.width || "1fr").join(" ");
  return props.enableRowReorder ? `40px ${cols}` : cols;
});

const scrollContainer = ref<HTMLElement | null>(null);
const displayLimit = ref(props.pageSize);

useInfiniteScroll(
  scrollContainer,
  () => {
    if (displayLimit.value < sortedData.value.length) {
      displayLimit.value += props.pageSize;
    }
  },
  { distance: 50 }
);

const sortState = ref<{ key: string | null; dir: "asc" | "desc" | null }>({
  key: null,
  dir: null,
});

const handleSort = (key: string | null, dir: "asc" | "desc" | null) => {
  sortState.value = { key, dir };
  displayLimit.value = props.pageSize;
  if (scrollContainer.value) scrollContainer.value.scrollTop = 0;
};

const sortedData = computed(() => {
  const { key, dir } = sortState.value;
  if (!key || !dir) return tableData.value;

  const data = [...tableData.value];
  const colConfig = tableColumns.value.find((c) => c.key === key);
  const customOrder = colConfig?.sortOrder;

  data.sort((a, b) => {
    const valA = a[key];
    const valB = b[key];
    if (customOrder) {
      const idxA = customOrder.indexOf(valA);
      const idxB = customOrder.indexOf(valB);
      const pA = idxA === -1 ? 9999 : idxA;
      const pB = idxB === -1 ? 9999 : idxB;
      return dir === "asc" ? pA - pB : pB - pA;
    }
    if (valA < valB) return dir === "asc" ? -1 : 1;
    if (valA > valB) return dir === "asc" ? 1 : -1;
    return 0;
  });
  return data;
});

const visibleData = computed(() =>
  sortedData.value.slice(0, displayLimit.value)
);

const draggedColIndex = ref<number | null>(null);
const draggedRowIndex = ref<number | null>(null);
const dragOverRowIndex = ref<number | null>(null);

const onColDragStart = (e: DragEvent, i: number) => {
  draggedColIndex.value = i;
  if (e.dataTransfer) e.dataTransfer.effectAllowed = "move";
};

const onColDrop = (i: number) => {
  if (draggedColIndex.value !== null) {
    const item = tableColumns.value[draggedColIndex.value] as Column;
    tableColumns.value.splice(draggedColIndex.value, 1);
    tableColumns.value.splice(i, 0, item);
    emit("update:columns", tableColumns.value);
    draggedColIndex.value = null;
  }
};

const onRowDragStart = (e: DragEvent, i: number) => {
  if (!props.enableRowReorder) return;

  if (sortState.value.key) sortState.value = { key: null, dir: null };
  draggedRowIndex.value = i;
  if (e.dataTransfer) e.dataTransfer.effectAllowed = "move";
};

const onRowDragOver = (e: DragEvent, i: number) => {
  if (props.enableRowReorder) dragOverRowIndex.value = i;
};

const onRowDrop = (dropIndex: number) => {
  if (draggedRowIndex.value !== null) {
    const item = tableData.value[draggedRowIndex.value];
    if (item === undefined) return;
    tableData.value.splice(draggedRowIndex.value, 1);
    tableData.value.splice(dropIndex, 0, item);
    emit("update:data", [...tableData.value] as T[]);
    resetDragState();
  }
};
const resetDragState = () => {
  draggedRowIndex.value = null;
  dragOverRowIndex.value = null;
  draggedColIndex.value = null;
};

const getAlignClass = (align?: "left" | "center" | "right") => {
  if (align === "right") return "justify-end text-right";
  if (align === "center") return "justify-center text-center";
  return "justify-start text-left";
};

const getContentAlignClass = (align?: "left" | "center" | "right") => {
  if (align === "right") return "flex-row-reverse";
  if (align === "center") return "justify-center";
  return "flex-row";
};
</script>
