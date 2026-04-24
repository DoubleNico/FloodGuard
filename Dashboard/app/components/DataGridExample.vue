<template>
  <div class="h-[700px] p-6 space-y-4 flex flex-col">
    <div class="flex justify-between items-center shrink-0">
      <div class="flex flex-col gap-1">
        <h2 class="text-xl font-bold text-(--label-text)">
          Advanced Grid System
        </h2>
        <p class="text-sm text-(--hint-text)">
          Infinite Scroll • Drag Columns • Drag Rows • Flash Updates
        </p>
      </div>
      <div class="flex gap-2">
        <Button size="sm" variant="outline" @click="isLive = !isLive">
          {{ isLive ? "Pause Updates" : "Resume Updates" }}
        </Button>
        <div
          class="text-sm font-mono bg-(--surface-secondary) px-2 py-1 rounded"
        >
          {{ isMounted ? rowData.length : 0 }} records
        </div>
      </div>
    </div>

    <ClientOnly>
      <DataGrid
        v-if="isMounted"
        :columns="colDefs"
        :data="rowData"
        :page-size="50"
        enable-row-reorder
        row-key="id"
        @update:data="rowData = $event"
      >
        <template #status="{ value }">
          <FlashCell :value="value">
            <Badge :variant="getStatusVariant(value)">{{ value }}</Badge>
          </FlashCell>
        </template>

        <template #amount="{ value }">
          <FlashCell :value="value">
            <span class="font-mono text-right w-full">
              {{
                new Intl.NumberFormat("en-US", {
                  style: "currency",
                  currency: "USD",
                }).format(value)
              }}
            </span>
          </FlashCell>
        </template>

        <template #marketPrice="{ value }">
          <FlashCell :value="value">
            <span
              class="font-mono transition-colors duration-300"
              :class="value > 1.0545 ? 'text-green-500' : 'text-red-500'"
            >
              {{ value.toFixed(5) }}
            </span>
          </FlashCell>
        </template>

        <template #footer="{ total, showing }">
          <div class="flex justify-between w-full">
            <span>Showing top {{ showing }} rows</span>
            <span>Database Total: {{ total }}</span>
          </div>
        </template>
      </DataGrid>

      <template #fallback>
        <div
          class="h-full w-full flex items-center justify-center border border-dashed rounded-xl"
        >
          Loading Grid...
        </div>
      </template>
    </ClientOnly>
  </div>
</template>

<script setup lang="ts">
import type { Column } from "~/types/Column";

interface Row {
  id: string;
  account: string;
  amount: number;
  status: string;
  marketPrice: number;
}

const isMounted = ref(false);
const isLive = ref(false);

const rowData = ref<Row[]>([]);
const statuses = ["Filled", "Pending", "Cancelled", "Working"];

onMounted(() => {
  rowData.value = generateData(1000);
  isMounted.value = true;
});

const colDefs = ref<Column[]>([
  { key: "id", label: "ID", width: "100px" },
  { key: "account", label: "Account", width: "150px" },
  {
    key: "amount",
    label: "Amount",
    width: "1fr",
    align: "right",
    sortLabels: { asc: "Low to High", desc: "High to Low" },
  },
  {
    key: "marketPrice",
    label: "Live Price",
    width: "1fr",
    align: "right",
  },
  { key: "status", label: "Status", width: "140px", align: "center" },
]);

function generateData(count: number): Row[] {
  const accounts = ["VIP_Trader", "Retail_Fund", "Algo_Bot_01", "Hedge_A"];

  return Array.from({ length: count }).map((_, i) => ({
    id: `ORD-${String(i + 1).padStart(4, "0")}`,
    account: accounts[Math.floor(Math.random() * accounts.length)],
    amount: Math.floor(Math.random() * 10000),
    status: statuses[Math.floor(Math.random() * statuses.length)],
    marketPrice: 1.054 + Math.random() * 0.001,
  })) as Row[];
}

let interval: number;
onMounted(() => {
  interval = setInterval(() => {
    if (!isLive.value || !isMounted.value) return;

    for (let i = 0; i < rowData.value.length / 2; i++) {
      const idx = Math.floor(Math.random() * rowData.value.length);
      const row = rowData.value[idx];
      if (row) {
        row.marketPrice = 1.054 + Math.random() * 0.002;
        if (Math.random() > 0.8)
          row.status =
            statuses[Math.floor(Math.random() * statuses.length)] || row.status;
      }
    }
  }, 500);
});

onUnmounted(() => clearInterval(interval));

const getStatusVariant = (status: string) => {
  switch (status) {
    case "Filled":
      return "success";
    case "Cancelled":
      return "danger";
    case "Working":
      return "secondary";
    default:
      return "outline";
  }
};
</script>
