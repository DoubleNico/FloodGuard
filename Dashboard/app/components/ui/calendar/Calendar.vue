<template>
  <div class="p-4 w-[400px] select-none flex flex-col gap-2">
    <div class="flex items-center justify-between">
      <Button
        variant="ghost"
        size="sm"
        class="h-8 w-8 rounded-full p-0"
        @click="handlePrev"
      >
        <Icon name="mdi:chevron-left" class="h-5 w-5" />
      </Button>

      <Button
        type="button"
        variant="ghost"
        class="text-sm font-bold text-(--label-text) hover:bg-(--surface-secondary) px-3 py-1.5 rounded-md transition-colors h-auto min-w-[120px]"
        @click="toggleView"
      >
        <span v-if="currentView === 'days'">
          {{ currentMonthName }} {{ currentYear }}
        </span>
        <span v-else-if="currentView === 'months'">
          {{ currentYear }}
        </span>
        <span v-else> {{ yearRangeStart }} - {{ yearRangeEnd }} </span>
      </Button>

      <Button
        variant="ghost"
        size="sm"
        class="h-8 w-8 rounded-full p-0"
        @click="handleNext"
      >
        <Icon name="mdi:chevron-right" class="h-5 w-5" />
      </Button>
    </div>

    <div
      v-if="currentView === 'days'"
      class="animate-in fade-in zoom-in-95 duration-200"
    >
      <div class="grid grid-cols-7 mb-2">
        <span
          v-for="day in weekDays"
          :key="day"
          class="text-[11px] text-center font-semibold text-(--hint-text) uppercase tracking-wide"
        >
          {{ day }}
        </span>
      </div>

      <div class="grid grid-cols-7 gap-1">
        <Button
          v-for="(day, index) in calendarDays"
          :key="index"
          type="button"
          variant="ghost"
          :disabled="!isSameMonth(day, viewDate)"
          class="relative h-9 w-9 rounded-full flex items-center justify-center text-sm transition-all duration-200 p-0"
          :class="getDayClasses(day)"
          @click="selectDate(day)"
        >
          {{ format(day, "d") }}
          <span
            v-if="isToday(day) && !isSameDay(day, selectedDate || new Date(0))"
            class="absolute bottom-1.5 w-1 h-1 rounded-full bg-(--btn-primary-bg)"
          />
        </Button>
      </div>
    </div>

    <div
      v-else-if="currentView === 'months'"
      class="grid grid-cols-3 gap-2 py-4 animate-in fade-in zoom-in-95 duration-200"
    >
      <Button
        v-for="(month, index) in months"
        :key="month"
        variant="ghost"
        class="h-10 rounded-lg text-sm font-medium transition-colors hover:bg-(--surface-secondary) text-(--label-text)"
        :class="{
          'bg-(--btn-primary-bg) text-white hover:bg-(--btn-primary-hover)':
            index === viewDate.getMonth(),
        }"
        @click="setMonth(index)"
      >
        {{ month }}
      </Button>
    </div>

    <div
      v-else
      class="grid grid-cols-4 gap-2 py-4 animate-in fade-in zoom-in-95 duration-200"
    >
      <Button
        v-for="year in yearsList"
        :key="year"
        variant="ghost"
        class="h-10 rounded-lg text-sm font-medium transition-colors hover:bg-(--surface-secondary) text-(--label-text)"
        :class="{
          'bg-(--btn-primary-bg) text-white hover:bg-(--btn-primary-hover)':
            year === viewDate.getFullYear(),
        }"
        @click="setYear(year)"
      >
        {{ year }}
      </Button>
    </div>

    <div
      v-if="enableTime && currentView === 'days'"
      class="border-t border-(--border-color) mt-2 pt-3 flex flex-col gap-3"
    >
      <div class="flex items-center justify-between gap-2">
        <div class="flex items-center gap-1 flex-1">
          <CustomSelect
            v-model="time.hours"
            :options="hoursOptions"
            size="sm"
            searchable
            :clearable="false"
            hide-scrollbar
            class="min-w-[3.5rem] w-[4rem]"
            @update:model-value="updateTime"
          />
          <span class="text-(--hint-text) font-bold px-0.5">:</span>
          <CustomSelect
            v-model="time.minutes"
            :options="minutesOptions"
            size="sm"
            searchable
            hide-scrollbar
            :clearable="false"
            class="min-w-[3.5rem] w-[4rem]"
            @update:model-value="updateTime"
          />

          <div v-if="is12HourMode" class="ml-1">
            <CustomSelect
              v-model="time.period"
              :options="periodOptions"
              size="sm"
              hide-scrollbar
              :clearable="false"
              class="min-w-[4rem]"
              @update:model-value="updateTime"
            />
          </div>

          <Button
            variant="ghost"
            size="xs"
            class="ml-2 text-[10px] uppercase font-bold text-(--hint-text) hover:text-(--label-text) border border-(--border-color) h-7 px-2"
            title="Toggle 12h/24h"
            @click="toggleTimeFormat"
          >
            {{ is12HourMode ? "12H" : "24H" }}
          </Button>
        </div>

        <Button
          size="sm"
          variant="solid"
          color="primary"
          class="shrink-0 px-3 ml-auto"
          @click="selectNow"
        >
          Now
        </Button>
      </div>
    </div>

    <div
      v-else-if="!enableTime && currentView === 'days'"
      class="border-t border-(--border-color) mt-2 pt-3 text-center"
    >
      <Button
        size="sm"
        variant="ghost"
        class="w-full text-xs"
        @click="selectNow"
      >
        Today
      </Button>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  format,
  addMonths,
  addYears,
  startOfWeek,
  endOfWeek,
  startOfMonth,
  endOfMonth,
  eachDayOfInterval,
  isSameMonth,
  isSameDay,
  set,
  isToday,
  getHours,
  getMinutes,
} from "date-fns";
import { usePreferredLanguages, useEventListener } from "@vueuse/core";

const props = withDefaults(
  defineProps<{
    modelValue?: Date | string | null;
    enableTime?: boolean;
  }>(),
  {
    enableTime: false,
  }
);

const emit = defineEmits<{
  (e: "update:modelValue", value: Date): void;
}>();

const viewDate = ref(
  props.modelValue ? new Date(props.modelValue) : new Date()
);
const selectedDate = ref<Date | null>(
  props.modelValue ? new Date(props.modelValue) : null
);

watch(
  () => props.modelValue,
  (val) => {
    if (val) {
      const d = new Date(val);
      if (!isNaN(d.getTime())) {
        selectedDate.value = d;
        syncTimeState(d);

        if (!isSameMonth(d, viewDate.value)) {
          viewDate.value = new Date(d);
        }
      }
    }
  }
);

type ViewMode = "days" | "months" | "years";
const currentView = ref<ViewMode>("days");
const weekDays = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"];
const months = [
  "Jan",
  "Feb",
  "Mar",
  "Apr",
  "May",
  "Jun",
  "Jul",
  "Aug",
  "Sep",
  "Oct",
  "Nov",
  "Dec",
];

const is12HourMode = ref(false);
const preferredLanguages = usePreferredLanguages();
const locale = computed(() => preferredLanguages.value?.[0]);

function detect12HourClock(loc?: string) {
  try {
    const dtf = new Intl.DateTimeFormat(loc, { hour: "numeric" });
    const opts = dtf.resolvedOptions();

    if (typeof opts.hour12 === "boolean") return opts.hour12;

    const hc = opts.hourCycle as "h11" | "h12" | "h23" | "h24" | undefined;
    if (hc) return hc === "h11" || hc === "h12";

    const parts = dtf.formatToParts(new Date("2020-01-01T13:00:00"));
    return parts.some((p) => p.type === "dayPeriod");
  } catch {
    return false;
  }
}

const time = reactive({
  hours: 12,
  minutes: 0,
  period: "AM" as "AM" | "PM",
});

function syncTimeState(date: Date) {
  const h = getHours(date);
  time.minutes = getMinutes(date);

  if (is12HourMode.value) {
    time.period = h >= 12 ? "PM" : "AM";
    time.hours = h % 12 || 12;
  } else {
    time.hours = h;
  }
}

function refreshHourMode() {
  is12HourMode.value = detect12HourClock(locale.value);
  const base = selectedDate.value
    ? new Date(selectedDate.value)
    : props.modelValue
    ? new Date(props.modelValue)
    : new Date();

  if (!isNaN(base.getTime())) syncTimeState(base);
}

onMounted(() => {
  refreshHourMode();
  useEventListener(window, "languagechange", refreshHourMode);
});

watch(
  () => locale.value,
  () => refreshHourMode()
);

function getRealHours(): number {
  if (!is12HourMode.value) return time.hours;

  if (time.period === "PM") {
    return time.hours === 12 ? 12 : time.hours + 12;
  } else {
    return time.hours === 12 ? 0 : time.hours;
  }
}

const hoursOptions = computed(() => {
  if (is12HourMode.value) {
    return [
      { label: "12", value: 12 },
      ...Array.from({ length: 11 }, (_, i) => ({
        label: (i + 1).toString(),
        value: i + 1,
      })),
    ];
  }
  return Array.from({ length: 24 }, (_, i) => ({
    label: i.toString().padStart(2, "0"),
    value: i,
  }));
});

const minutesOptions = Array.from({ length: 60 }, (_, i) => ({
  label: i.toString().padStart(2, "0"),
  value: i,
}));
const periodOptions = [
  { label: "AM", value: "AM" },
  { label: "PM", value: "PM" },
];

const currentMonthName = computed(() => format(viewDate.value, "MMMM"));
const currentYear = computed(() => format(viewDate.value, "yyyy"));

const yearRangeStart = computed(
  () => Math.floor(viewDate.value.getFullYear() / 12) * 12
);
const yearRangeEnd = computed(() => yearRangeStart.value + 11);

const yearsList = computed(() => {
  const arr = [];
  for (let i = yearRangeStart.value; i <= yearRangeEnd.value; i++) arr.push(i);
  return arr;
});

const calendarDays = computed(() => {
  const start = startOfWeek(startOfMonth(viewDate.value));
  const end = endOfWeek(endOfMonth(viewDate.value));
  return eachDayOfInterval({ start, end });
});

function handlePrev() {
  if (currentView.value === "days")
    viewDate.value = addMonths(viewDate.value, -1);
  else if (currentView.value === "months")
    viewDate.value = addYears(viewDate.value, -1);
  else viewDate.value = addYears(viewDate.value, -12);
}

function handleNext() {
  if (currentView.value === "days")
    viewDate.value = addMonths(viewDate.value, 1);
  else if (currentView.value === "months")
    viewDate.value = addYears(viewDate.value, 1);
  else viewDate.value = addYears(viewDate.value, 12);
}

function toggleView() {
  if (currentView.value === "days") currentView.value = "years";
  else if (currentView.value === "years") currentView.value = "months";
  else currentView.value = "days";
}

function setMonth(index: number) {
  viewDate.value = set(viewDate.value, { month: index });
  currentView.value = "days";
}

function setYear(year: number) {
  viewDate.value = set(viewDate.value, { year });
  currentView.value = "months";
}

function selectDate(day: Date) {
  const realHours = getRealHours();
  const newDate = set(day, { hours: realHours, minutes: time.minutes });
  selectedDate.value = newDate;
  emit("update:modelValue", newDate);
}

function updateTime() {
  if (selectedDate.value) {
    const realHours = getRealHours();
    const newDate = set(selectedDate.value, {
      hours: realHours,
      minutes: time.minutes,
    });
    selectedDate.value = newDate;
    emit("update:modelValue", newDate);
  }
}

function selectNow() {
  const now = new Date();
  viewDate.value = now;
  selectedDate.value = now;
  syncTimeState(now);
  emit("update:modelValue", now);
}

function toggleTimeFormat() {
  is12HourMode.value = !is12HourMode.value;

  if (selectedDate.value) {
    syncTimeState(selectedDate.value);
  } else {
    syncTimeState(new Date());
  }
}

function getDayClasses(day: Date) {
  if (!isSameMonth(day, viewDate.value)) {
    return "text-(--input-placeholder) pointer-events-none opacity-50";
  }
  if (selectedDate.value && isSameDay(day, selectedDate.value)) {
    return "bg-(--btn-primary-bg) text-(--btn-primary-text) font-semibold shadow-md hover:opacity-90";
  }
  return "text-(--label-text) hover:bg-(--switch-bg-off) hover:text-(--label-text)";
}
</script>
