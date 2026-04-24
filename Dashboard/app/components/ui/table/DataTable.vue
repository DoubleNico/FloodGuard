<template>
  <div class="w-full space-y-4">
    <div v-if="$slots.toolbar" class="flex items-center justify-between">
      <slot name="toolbar" />
    </div>

    <Table>
      <TableHeader>
        <TableRow>
          <TableHead v-if="enableRowReorder" class="w-[40px] px-0" />
          <TableHead
            v-for="(col, index) in tableColumns"
            :key="col.key"
            :class="[
              col.width,
              'cursor-move transition-opacity duration-200 select-none group',
              draggedColIndex === index
                ? 'opacity-40 border-dashed border-(--border-color)'
                : '',
            ]"
            :align="col.align"
            :sortable="col.sortable"
            :sort-direction="
              currentSort.key === col.key ? currentSort.dir : null
            "
            :label-asc="col.sortLabels?.asc"
            :label-desc="col.sortLabels?.desc"
            draggable="true"
            @dragstart="onColDragStart($event, index)"
            @dragover.prevent
            @drop="onColDrop(index)"
            @sort="(dir) => handleSort(col.key, dir)"
          >
            <div class="flex items-center gap-1.5">
              <Icon
                name="mdi:drag-vertical"
                class="w-4 h-4 text-(--hint-text) opacity-40 group-hover:opacity-100 transition-opacity cursor-grab"
              />
              <span>{{ col.label }}</span>
            </div>
          </TableHead>
        </TableRow>
      </TableHeader>

      <TableBody>
        <TableRow
          v-for="(row, rowIndex) in sortedData"
          :key="row[rowKey] || rowIndex"
          :draggable="enableRowReorder"
          :class="[
            enableRowReorder ? 'cursor-move' : '',
            draggedRowIndex === rowIndex
              ? 'opacity-40 bg-(--surface-secondary)'
              : '',

            dragOverRowIndex === rowIndex ? 'border-b-2 border-primary' : '',
          ]"
          @dragstart="onRowDragStart($event, rowIndex)"
          @dragover.prevent="onRowDragOver($event, rowIndex)"
          @drop="onRowDrop(rowIndex)"
          @dragend="resetDragState"
        >
          <TableCell v-if="enableRowReorder" class="w-[40px] px-0 text-center">
            <Icon
              name="mdi:drag"
              class="w-5 h-5 text-(--hint-text) opacity-50 hover:opacity-100 cursor-grab"
            />
          </TableCell>

          <TableCell
            v-for="col in tableColumns"
            :key="col.key"
            :align="col.align"
          >
            <slot :name="col.key" :row="row" :value="row[col.key]">
              {{ row[col.key] }}
            </slot>
          </TableCell>
        </TableRow>

        <TableRow v-if="sortedData.length === 0">
          <TableCell
            :colspan="tableColumns.length + (enableRowReorder ? 1 : 0)"
            class="h-24 text-center text-(--hint-text)"
          >
            <slot name="empty">No results found.</slot>
          </TableCell>
        </TableRow>
      </TableBody>
    </Table>

    <div v-if="$slots.footer" class="border-t border-(--border-color) pt-4">
      <slot name="footer" :data="sortedData" />
    </div>
  </div>
</template>

<script setup lang="ts" generic="T extends Record<string, any>">
import type { Column } from "~/types/Column";

const props = withDefaults(
  defineProps<{
    columns: Column[];
    data: T[];
    enableRowReorder?: boolean;
    rowKey?: string;
  }>(),
  {
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
const currentSort = ref<{ key: string | null; dir: "asc" | "desc" | null }>({
  key: null,
  dir: null,
});

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

const handleSort = (key: string, dir: "asc" | "desc" | null) => {
  currentSort.value = { key, dir };
};

const sortedData = computed(() => {
  const { key, dir } = currentSort.value;

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
    emit("update:columns", [...tableColumns.value]);
    draggedColIndex.value = null;
  }
};

const onRowDragStart = (e: DragEvent, i: number) => {
  if (!props.enableRowReorder) return;
  draggedRowIndex.value = i;

  if (currentSort.value.key) {
    currentSort.value = { key: null, dir: null };
  }
  if (e.dataTransfer) {
    e.dataTransfer.effectAllowed = "move";
  }
};

const onRowDragOver = (e: DragEvent, i: number) => {
  if (props.enableRowReorder) {
    dragOverRowIndex.value = i;
  }
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
</script>
