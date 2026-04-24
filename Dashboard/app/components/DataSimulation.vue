<template>
  <div class="p-6">
    <DataTable
      :columns="columns"
      :data="marketData"
      enable-row-reorder
      row-key="symbol"
      @update:data="marketData = $event"
    >
      <template #toolbar>
        <div class="flex flex-col gap-1">
          <h2 class="text-lg font-semibold text-(--label-text)">Live Market</h2>
          <p class="text-xs text-(--hint-text)">
            Drag rows or columns to reorder
          </p>
        </div>

        <div class="flex gap-2">
          <Button
            size="sm"
            color="secondary"
            icon-left="mdi:table-row-plus-after"
            @click="addRandomRow"
          >
            Add Row
          </Button>

          <Button
            size="sm"
            color="secondary"
            icon-left="mdi:plus"
            @click="addDynamicColumn"
          >
            Add Column
          </Button>
          <Button size="sm" variant="outline" @click="isLive = !isLive">
            {{ isLive ? "Pause" : "Resume" }}
          </Button>
        </div>
      </template>

      <template #marketPrice="{ value }">
        <FlashCell :value="value">
          <span :class="getPriceColor(value)">{{ formatNumber(value) }}</span>
        </FlashCell>
      </template>

      <template #price="{ value }">
        <FlashCell :value="value">
          <span :class="getPriceColor(value)">{{ formatNumber(value) }}</span>
        </FlashCell>
      </template>

      <template v-for="col in dynamicColumnKeys" :key="col" #[col]="{ value }">
        <FlashCell :value="value">
          <span class="font-mono text-xs text-(--label-text)">{{
            value?.toFixed(0)
          }}</span>
        </FlashCell>
      </template>

      <template #orderStatus="{ value }">
        <Badge
          :variant="
            value === 'Filled'
              ? 'success'
              : value === 'Cancelled'
              ? 'danger'
              : 'secondary'
          "
        >
          {{ value }}
        </Badge>
      </template>

      <template #footer="{ data }">
        <div
          class="flex items-center justify-between text-xs text-(--hint-text)"
        >
          <span>Total Rows: {{ data.length }}</span>
          <span>Columns: {{ columns.length }}</span>
        </div>
      </template>
    </DataTable>
  </div>
</template>

<script setup lang="ts">
import type { Column } from "~/types/Column";

interface MarketRow {
  symbol: string;
  account: string;
  marketPrice: number;
  price: number;
  orderStatus: string;
  [key: string]: number | string;
}

const isLive = ref(false);
const dynamicCount = ref(0);
const rowCounter = ref(1);

const columns = ref<Column[]>([
  { key: "symbol", label: "Symbol", width: "w-[100px]", sortable: true },
  { key: "account", label: "Account", sortable: true },
  { key: "marketPrice", label: "Market Price", align: "right", sortable: true },
  { key: "price", label: "Price", align: "right", sortable: true },
  { key: "orderStatus", label: "Status", width: "w-[120px]" },
]);

const dynamicColumnKeys = computed(() =>
  columns.value.filter((c) => c.key.startsWith("dyn_")).map((c) => c.key)
);

const marketData = ref<MarketRow[]>([
  {
    symbol: "AAPL",
    account: "ACC-001",
    marketPrice: 150.22,
    price: 149.0,
    orderStatus: "Filled",
  },
  {
    symbol: "GOOGL",
    account: "ACC-002",
    marketPrice: 2800.5,
    price: 2805.0,
    orderStatus: "Working",
  },
  {
    symbol: "TSLA",
    account: "ACC-001",
    marketPrice: 750.1,
    price: 740.0,
    orderStatus: "Cancelled",
  },
  {
    symbol: "MSFT",
    account: "ACC-003",
    marketPrice: 299.99,
    price: 301.0,
    orderStatus: "Filled",
  },
]);

const addRandomRow = () => {
  const symbols = ["NVDA", "AMZN", "NFLX", "META", "AMD", "INTC", "IBM"];
  const accounts = ["ACC-001", "ACC-002", "ACC-003", "ACC-004", "ACC-005"];
  const statuses = ["Filled", "Working", "Cancelled"];

  const randomSymbol =
    symbols[Math.floor(Math.random() * symbols.length)] +
    "-" +
    rowCounter.value++;
  const randomAccount =
    accounts[Math.floor(Math.random() * accounts.length)] || "ACC-000";
  const randomStatus =
    statuses[Math.floor(Math.random() * statuses.length)] || "Working";
  const basePrice = Math.random() * 1000 + 50;

  const newRow: MarketRow = {
    symbol: randomSymbol,
    account: randomAccount,
    marketPrice: basePrice,
    price: basePrice - Math.random() * 5,
    orderStatus: randomStatus,
  };

  dynamicColumnKeys.value.forEach((key) => {
    newRow[key] = Math.floor(Math.random() * 100);
  });

  marketData.value.push(newRow);
};

const addDynamicColumn = () => {
  dynamicCount.value++;
  const newKey = `dyn_${dynamicCount.value}`;

  columns.value.push({
    key: newKey,
    label: `Extra ${dynamicCount.value}`,
    align: "right",
    sortable: true,
  });

  marketData.value.forEach((row: MarketRow) => {
    row[newKey] = Math.floor(Math.random() * 100);
  });
};

let interval: number;

onMounted(() => {
  interval = setInterval(() => {
    if (!isLive.value) return;

    const newData = marketData.value.map((item: MarketRow) => {
      const newItem = { ...item };

      if (Math.random() > 0.5) {
        const change = (Math.random() - 0.5) * 2;
        newItem.marketPrice += change;
        newItem.price += change;
      }

      dynamicColumnKeys.value.forEach((key) => {
        if (Math.random() > 0.8) {
          newItem[key] =
            (Number(newItem[key]) || 0) + Math.floor(Math.random() * 5);
        }
      });
      return newItem;
    });

    marketData.value = newData;
  }, 800);
});

onUnmounted(() => clearInterval(interval));

const getPriceColor = (val: number) => {
  if (val > 1000) return "text-(--input-error-text)";
  if (val > 0) return "text-green-500";
  return "text-(--hint-text)";
};
const formatNumber = (val: number) => val.toFixed(2);
</script>
