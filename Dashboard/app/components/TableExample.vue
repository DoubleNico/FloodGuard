<template>
  <div class="px-4">
    <DataTable
      :columns="columns"
      :data="processedData"
      enable-row-reorder
      @sort="handleSortChange"
    >
      <template #toolbar>
        <h2 class="text-lg font-semibold text-(--label-text)">
          Recent Invoices
        </h2>
        <Input
          v-model="search"
          placeholder="Filter..."
          class="w-64"
          size="sm"
          icon-left="mdi:magnify"
        />
      </template>

      <template #status="{ value }">
        <Badge :variant="statusConfig[value] || 'default'">
          {{ value }}
        </Badge>
      </template>

      <template #method="{ value }">
        <div class="flex items-center gap-2">
          <Icon :name="getMethodIcon(value)" class="text-(--hint-text)" />
          {{ value }}
        </div>
      </template>

      <template #amount="{ value }">
        {{ formatCurrency(value) }}
      </template>
    </DataTable>
  </div>
</template>

<script setup lang="ts">
import type { BadgeVariant } from "~/types/BadgeVariant";
import type { Column } from "~/types/Column";

const columns: Column[] = [
  { key: "invoice", label: "Invoice", width: "w-[100px]", sortable: true },
  {
    key: "status",
    label: "Status",
    sortable: true,
    width: "w-[120px]",

    sortOrder: ["Paid", "Pending", "Unpaid"],

    sortLabels: {
      asc: "Paid First",
      desc: "Unpaid First",
    },
  },
  {
    key: "method",
    label: "Method",
    sortable: true,
    width: "w-[180px]",

    sortOrder: ["PayPal", "Credit Card", "Bank Transfer"],
    sortLabels: {
      asc: "PayPal First",
      desc: "Bank First",
    },
  },
  { key: "amount", label: "Amount", align: "right", sortable: true },
];

const statusConfig: Record<string, BadgeVariant> = {
  Paid: "success",
  Pending: "secondary",
  Unpaid: "danger",
};

const invoices = ref([
  { invoice: "INV001", status: "Paid", amount: 250.0, method: "Credit Card" },
  { invoice: "INV002", status: "Pending", amount: 150.0, method: "PayPal" },
  {
    invoice: "INV003",
    status: "Unpaid",
    amount: 350.0,
    method: "Bank Transfer",
  },
  { invoice: "INV004", status: "Paid", amount: 450.0, method: "Credit Card" },
  { invoice: "INV005", status: "Paid", amount: 550.0, method: "PayPal" },
  {
    invoice: "INV006",
    status: "Pending",
    amount: 200.0,
    method: "Bank Transfer",
  },
  { invoice: "INV007", status: "Unpaid", amount: 300.0, method: "Credit Card" },
]);

const search = ref<string>("");
const sortState = ref<{ key: string; dir: "asc" | "desc" | null }>({
  key: "",
  dir: null,
});

const handleSortChange = ({
  key,
  direction,
}: {
  key: string;
  direction: "asc" | "desc" | null;
}) => {
  sortState.value = { key, dir: direction };
};

const processedData = computed(() => {
  let data = [...invoices.value];

  if (search.value) {
    const q = search.value.toLowerCase();
    data = data.filter(
      (i) =>
        i.invoice.toLowerCase().includes(q) ||
        i.status.toLowerCase().includes(q)
    );
  }

  if (sortState.value.key && sortState.value.dir) {
    data.sort((a, b) => {
      const valA = a[sortState.value.key as keyof typeof a];

      const valB = b[sortState.value.key as keyof typeof b];

      if (valA < valB) return sortState.value.dir === "asc" ? -1 : 1;
      if (valA > valB) return sortState.value.dir === "asc" ? 1 : -1;
      return 0;
    });
  }

  return data;
});

const formatCurrency = (val: number) =>
  new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(
    val
  );

const getMethodIcon = (method: string) => {
  if (method.includes("Card")) return "mdi:credit-card";
  if (method.includes("PayPal")) return "mdi:paypal";
  return "mdi:bank";
};
</script>
