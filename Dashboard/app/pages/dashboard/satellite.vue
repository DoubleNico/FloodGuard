<template>
  <div class="space-y-6 max-w-[1400px] mx-auto">
    <div>
      <h1 class="text-2xl font-bold text-(--label-text) tracking-tight">
        {{ t("satellitePage.title") }}
      </h1>
      <p class="text-sm text-(--hint-text) mt-1">
        {{ t("satellitePage.subtitle") }}
      </p>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard
        icon="mdi:satellite-variant"
        :label="t('satellitePage.cards.galileoSatellites')"
        :value="`${operationalSatellites}/${totalGalileoSatellites}`"
        glow-color="primary"
        icon-bg="#0066CC"
        class="animate-fade-up stagger-1"
      />
      <StatCard
        icon="mdi:signal"
        :label="t('satellitePage.cards.averageSignal')"
        :value="`${averageSignal}%`"
        glow-color="success"
        icon-bg="#22C55E"
        class="animate-fade-up stagger-2"
      />
      <StatCard
        icon="mdi:water"
        :label="t('satellitePage.cards.highestWaterLevel')"
        :value="`${highestWaterLevel}${t('satellitePage.units.cm')}`"
        glow-color="danger"
        icon-bg="#EF4444"
        class="animate-fade-up stagger-3"
      />
      <StatCard
        icon="mdi:earth"
        :label="t('satellitePage.cards.ndwiZonesMonitored')"
        :value="ndwiReadings.length"
        glow-color="info"
        icon-bg="#3B82F6"
        class="animate-fade-up stagger-4"
      />
    </div>

    <Card class="p-5">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h2 class="text-lg font-semibold text-(--label-text)">
            {{ t("satellitePage.waterForecast.title") }}
          </h2>
          <p class="text-xs text-(--hint-text) flex items-center gap-1 mt-0.5">
            <Icon name="mdi:satellite-variant" class="h-3 w-3" />
            {{ t("satellitePage.waterForecast.source") }}
          </p>
        </div>
        <Badge variant="outline" class="alarm-pulse">{{
          t("satellitePage.liveFeed")
        }}</Badge>
      </div>
      <div class="grid grid-cols-1 lg:grid-cols-5 gap-6">
        <div class="lg:col-span-3 h-[400px] map-container">
          <ClientOnly>
            <LMap
              :zoom="12"
              :center="[45.4353, 28.0397]"
              :use-global-leaflet="false"
              :options="{ zoomControl: true, attributionControl: false }"
            >
              <LTileLayer
                url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                layer-type="base"
                name="CartoDB Dark"
              />
              <LMarker
                v-for="wl in waterLevels"
                :key="wl.station"
                :lat-lng="[wl.lat, wl.lng]"
              >
                <LIcon
                  :icon-size="[48, 48]"
                  :icon-anchor="[24, 24]"
                  class-name=""
                >
                  <div class="flex flex-col items-center">
                    <div
                      class="h-12 w-12 rounded-xl flex flex-col items-center justify-center shadow-lg border-2"
                      :style="{
                        background:
                          wl.level >= wl.criticalLevel
                            ? '#7F1D1D'
                            : wl.level >= wl.warningLevel
                              ? '#92400E'
                              : '#14532D',
                        borderColor:
                          wl.level >= wl.criticalLevel
                            ? '#EF4444'
                            : wl.level >= wl.warningLevel
                              ? '#F59E0B'
                              : '#22C55E',
                      }"
                    >
                      <span class="text-white text-xs font-bold leading-none">{{
                        Math.round(wl.level)
                      }}</span>
                      <span class="text-white/60 text-[8px]">cm</span>
                    </div>
                  </div>
                </LIcon>
                <LPopup>
                  <div class="p-2 min-w-[180px]">
                    <h3 class="font-bold text-sm text-gray-900 mb-1">
                      {{ wl.station }}
                    </h3>
                    <div class="space-y-1 text-xs">
                      <div class="flex justify-between">
                        <span class="text-gray-500"
                          >{{ t("satellitePage.fields.level") }}:</span
                        ><span
                          class="font-bold"
                          :style="{
                            color:
                              wl.level >= wl.criticalLevel
                                ? '#EF4444'
                                : wl.level >= wl.warningLevel
                                  ? '#F59E0B'
                                  : '#22C55E',
                          }"
                          >{{ Math.round(wl.level)
                          }}{{ t("satellitePage.units.cm") }}</span
                        >
                      </div>
                      <div class="flex justify-between">
                        <span class="text-gray-500"
                          >{{ t("satellitePage.fields.warning") }}:</span
                        ><span
                          >{{ wl.warningLevel
                          }}{{ t("satellitePage.units.cm") }}</span
                        >
                      </div>
                      <div class="flex justify-between">
                        <span class="text-gray-500"
                          >{{ t("satellitePage.fields.critical") }}:</span
                        ><span
                          >{{ wl.criticalLevel
                          }}{{ t("satellitePage.units.cm") }}</span
                        >
                      </div>
                      <div class="flex justify-between">
                        <span class="text-gray-500"
                          >{{ t("satellitePage.fields.trend") }}:</span
                        ><span class="capitalize font-medium">{{
                          trendLabel(wl.trend)
                        }}</span>
                      </div>
                    </div>
                  </div>
                </LPopup>
              </LMarker>
              <template v-for="hz in floodHeatmap" :key="hz.id">
                <LPolygon
                  :lat-lngs="hz.polygon"
                  :color="heatmapIntensityColor(hz.intensity)"
                  :fill-color="heatmapIntensityColor(hz.intensity)"
                  :fill-opacity="0.28"
                  :weight="1"
                >
                  <LPopup>
                    <div class="p-2 min-w-[180px]">
                      <h3 class="font-bold text-sm text-gray-900 mb-1">
                        {{ hz.zone }}
                      </h3>
                      <p class="text-xs text-gray-600 mb-1">
                        {{ t("satellitePage.floodIntensity") }}:
                        <strong
                          :style="{
                            color: heatmapIntensityColor(hz.intensity),
                          }"
                          >{{ Math.round(hz.intensity * 100) }}%</strong
                        >
                      </p>
                      <p
                        class="text-xs text-gray-500 uppercase font-semibold"
                        :style="{ color: heatmapIntensityColor(hz.intensity) }"
                      >
                        {{ riskLabel(hz.riskLevel) }}
                      </p>
                    </div>
                  </LPopup>
                </LPolygon>
              </template>
            </LMap>
            <template #fallback>
              <div
                class="h-full flex items-center justify-center bg-(--surface-secondary) rounded-[20px]"
              >
                <Icon name="mdi:map" class="h-8 w-8 text-(--hint-text)" />
              </div>
            </template>
          </ClientOnly>
        </div>
        <div class="lg:col-span-2 space-y-4">
          <div
            v-for="wl in waterLevels"
            :key="wl.station"
            class="space-y-2 p-3 rounded-xl border border-(--border-color) bg-(--surface-secondary)/30"
          >
            <div class="flex items-center justify-between">
              <span class="text-sm font-medium text-(--label-text)">{{
                wl.station.replace("Galați — ", "")
              }}</span>
              <div class="flex items-center gap-2">
                <Icon
                  :name="
                    wl.trend === 'rising'
                      ? 'mdi:trending-up'
                      : wl.trend === 'falling'
                        ? 'mdi:trending-down'
                        : 'mdi:trending-neutral'
                  "
                  class="h-4 w-4"
                  :class="
                    wl.trend === 'rising'
                      ? 'text-red-500'
                      : wl.trend === 'falling'
                        ? 'text-green-500'
                        : 'text-(--hint-text)'
                  "
                />
                <span
                  class="text-xl font-bold"
                  :class="
                    wl.level >= wl.criticalLevel
                      ? 'text-red-500'
                      : wl.level >= wl.warningLevel
                        ? 'text-amber-500'
                        : 'text-green-500'
                  "
                >
                  {{ Math.round(wl.level)
                  }}<span class="text-sm font-normal text-(--hint-text)">{{
                    t("satellitePage.units.cm")
                  }}</span>
                </span>
              </div>
            </div>
            <div class="relative">
              <div class="water-gauge h-3 rounded-lg">
                <div
                  class="water-gauge-fill rounded-lg"
                  :style="{
                    width: `${Math.min(100, (wl.level / wl.criticalLevel) * 100)}%`,
                    background:
                      wl.level >= wl.criticalLevel
                        ? 'linear-gradient(90deg, #EF4444, #DC2626)'
                        : wl.level >= wl.warningLevel
                          ? 'linear-gradient(90deg, #F59E0B, #D97706)'
                          : 'linear-gradient(90deg, #22C55E, #16A34A)',
                  }"
                />
              </div>
              <div
                class="absolute top-0 h-3 w-0.5 bg-(--label-text)/30"
                :style="{
                  left: `${(wl.warningLevel / wl.criticalLevel) * 100}%`,
                }"
              />
            </div>
            <div class="flex justify-between text-[10px] text-(--hint-text)">
              <span>{{ t("satellitePage.levelBands.normal") }}</span>
              <span
                >{{ t("satellitePage.levelBands.warning") }} ({{
                  wl.warningLevel
                }}{{ t("satellitePage.units.cm") }})</span
              >
              <span
                >{{ t("satellitePage.levelBands.critical") }} ({{
                  wl.criticalLevel
                }}{{ t("satellitePage.units.cm") }})</span
              >
            </div>
          </div>
        </div>
      </div>
    </Card>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <Card class="p-5">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h2 class="text-lg font-semibold text-(--label-text)">
              {{ t("satellitePage.precipitation.title") }}
            </h2>
            <p
              class="text-xs text-(--hint-text) flex items-center gap-1 mt-0.5"
            >
              <Icon name="mdi:satellite-variant" class="h-3 w-3" />
              {{ t("satellitePage.precipitation.source") }}
            </p>
          </div>
        </div>
        <div class="h-[280px]">
          <ClientOnly>
            <Bar v-if="chartData" :data="chartData" :options="chartOptions" />
            <template #fallback>
              <div class="h-full flex items-center justify-center">
                <p class="text-sm text-(--hint-text)">
                  {{ t("satellitePage.loadingChart") }}
                </p>
              </div>
            </template>
          </ClientOnly>
        </div>
      </Card>

      <Card class="p-5">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h2 class="text-lg font-semibold text-(--label-text)">
              {{ t("satellitePage.galileoStatus.title") }}
            </h2>
            <p
              class="text-xs text-(--hint-text) flex items-center gap-1 mt-0.5"
            >
              <Icon name="mdi:satellite-uplink" class="h-3 w-3" /> EU Galileo
              GNSS
            </p>
          </div>
          <Badge variant="success"
            >{{ operationalSatellites }}/{{ galileoSatellites.length }}
            {{ t("satellitePage.active") }}</Badge
          >
        </div>
        <div class="space-y-3">
          <div
            v-for="sat in galileoSatellites"
            :key="sat.id"
            class="flex items-center gap-3 p-3 rounded-xl bg-(--surface-secondary)/30"
          >
            <div
              class="h-9 w-9 rounded-lg flex items-center justify-center"
              :style="{
                background:
                  sat.status === 'operational'
                    ? '#22C55E15'
                    : sat.status === 'testing'
                      ? '#F59E0B15'
                      : '#EF444415',
              }"
            >
              <Icon
                name="mdi:satellite-variant"
                class="h-4.5 w-4.5"
                :style="{
                  color:
                    sat.status === 'operational'
                      ? '#22C55E'
                      : sat.status === 'testing'
                        ? '#F59E0B'
                        : '#EF4444',
                }"
              />
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2">
                <span class="text-sm font-medium text-(--label-text)">{{
                  sat.id
                }}</span>
                <span class="text-xs text-(--hint-text)">{{ sat.name }}</span>
              </div>
              <div
                v-if="sat.status === 'operational'"
                class="water-gauge mt-1.5"
              >
                <div
                  class="water-gauge-fill"
                  :style="{
                    width: `${sat.signal}%`,
                    background:
                      sat.signal > 85
                        ? '#22C55E'
                        : sat.signal > 70
                          ? '#F59E0B'
                          : '#EF4444',
                  }"
                />
              </div>
            </div>
            <div class="flex items-center gap-2 shrink-0">
              <span
                v-if="sat.status === 'operational'"
                class="text-sm font-bold text-(--label-text)"
                >{{ Math.round(sat.signal) }}%</span
              >
              <Badge
                :variant="
                  sat.status === 'operational'
                    ? 'success'
                    : sat.status === 'testing'
                      ? 'secondary'
                      : 'danger'
                "
              >
                {{ satelliteStatusLabel(sat.status) }}
              </Badge>
            </div>
          </div>
        </div>
      </Card>
    </div>

    <Card class="p-5">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h2 class="text-lg font-semibold text-(--label-text)">
            {{ t("satellitePage.ndwi.title") }}
          </h2>
          <p class="text-xs text-(--hint-text) flex items-center gap-1 mt-0.5">
            <Icon name="mdi:satellite-variant" class="h-3 w-3" />
            {{ t("satellitePage.ndwi.source") }}
          </p>
        </div>
      </div>
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="grid grid-cols-2 gap-3 lg:col-span-1 h-fit">
          <div
            v-for="nr in ndwiReadings"
            :key="nr.zone"
            class="p-3 rounded-xl border border-(--border-color) bg-(--surface-secondary)/30 hover:bg-(--surface-secondary)/60 transition-colors"
          >
            <div class="flex items-center justify-between mb-2">
              <span class="text-xs font-medium text-(--label-text) truncate">{{
                nr.zone
              }}</span>
              <span
                class="text-[10px] font-bold uppercase px-1.5 py-0.5 rounded-full"
                :style="{
                  background: `${ndwiRiskColor(nr.risk)}20`,
                  color: ndwiRiskColor(nr.risk),
                }"
                >{{ riskLabel(nr.risk) }}</span
              >
            </div>
            <p
              class="text-2xl font-bold tracking-tight"
              :style="{ color: ndwiRiskColor(nr.risk) }"
            >
              {{ nr.value.toFixed(2) }}
            </p>
            <div class="water-gauge mt-2">
              <div
                class="water-gauge-fill"
                :style="{
                  width: `${nr.value * 100}%`,
                  background: ndwiRiskColor(nr.risk),
                }"
              />
            </div>
          </div>
        </div>
        <div class="lg:col-span-2 h-[400px] map-container">
          <ClientOnly>
            <LMap
              :zoom="13"
              :center="[45.4353, 28.0397]"
              :use-global-leaflet="false"
              :options="{ zoomControl: true, attributionControl: false }"
            >
              <LTileLayer
                url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                layer-type="base"
                name="CartoDB Dark"
              />
              <LMarker
                v-for="nr in ndwiReadings"
                :key="nr.zone"
                :lat-lng="[nr.lat, nr.lng]"
              >
                <LIcon
                  :icon-size="[32, 32]"
                  :icon-anchor="[16, 32]"
                  class-name=""
                >
                  <div class="flex flex-col items-center">
                    <div
                      class="h-8 w-8 rounded-full flex items-center justify-center shadow-lg border-2 border-white"
                      :style="{ background: ndwiRiskColor(nr.risk) }"
                    >
                      <span class="text-white text-xs font-bold">{{
                        Math.round(nr.value * 100)
                      }}</span>
                    </div>
                  </div>
                </LIcon>
                <LPopup>
                  <div class="p-2 min-w-[150px]">
                    <h3 class="font-bold text-sm text-gray-900 mb-1">
                      {{ nr.zone }}
                    </h3>
                    <p class="text-xs text-gray-600 mb-1">
                      {{ t("satellitePage.ndwi.value") }}:
                      <strong :style="{ color: ndwiRiskColor(nr.risk) }">{{
                        nr.value.toFixed(2)
                      }}</strong>
                    </p>
                    <p class="text-xs text-gray-500 uppercase font-semibold">
                      {{ riskLabel(nr.risk) }}
                    </p>
                  </div>
                </LPopup>
              </LMarker>
            </LMap>
            <template #fallback>
              <div
                class="h-full flex items-center justify-center bg-(--surface-secondary) rounded-[20px]"
              >
                <Icon name="mdi:map" class="h-8 w-8 text-(--hint-text)" />
              </div>
            </template>
          </ClientOnly>
        </div>
      </div>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { Bar } from "vue-chartjs";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
  Legend,
} from "chart.js";
import type {
  FloodHeatmapZone,
  GalileoSatellite,
  NDWIReading,
  WaterLevelReading,
} from "~/composables/useSatelliteData";
import {
  LIcon,
  LMap,
  LMarker,
  LPolygon,
  LPopup,
  LTileLayer,
} from "@vue-leaflet/vue-leaflet";

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

definePageMeta({ layout: "dashboard", middleware: "auth" });

const { t } = useI18n();
const {
  waterLevels,
  precipitation,
  galileoSatellites,
  ndwiReadings,
  floodHeatmap,
  operationalSatellites,
  averageSignal,
  ndwiRiskColor,
  heatmapIntensityColor,
  startSimulation,
  stopSimulation,
} = useSatelliteData();

const totalGalileoSatellites = computed(() =>
  Math.max(8, galileoSatellites.value.length),
);
const highestWaterLevel = computed(() =>
  waterLevels.value.length > 0
    ? Math.round(Math.max(...waterLevels.value.map((w) => w.level)))
    : 0,
);

const trendLabel = (trend: WaterLevelReading["trend"]) =>
  ({
    rising: t("satellitePage.trends.rising"),
    stable: t("satellitePage.trends.stable"),
    falling: t("satellitePage.trends.falling"),
  })[trend];

const riskLabel = (risk: NDWIReading["risk"] | FloodHeatmapZone["riskLevel"]) =>
  ({
    low: t("satellitePage.risk.low"),
    moderate: t("satellitePage.risk.moderate"),
    high: t("satellitePage.risk.high"),
    critical: t("satellitePage.risk.critical"),
  })[risk];

const satelliteStatusLabel = (status: GalileoSatellite["status"]) =>
  ({
    operational: t("satellitePage.galileoStatus.operational"),
    testing: t("satellitePage.galileoStatus.testing"),
    unavailable: t("satellitePage.galileoStatus.unavailable"),
  })[status];

const chartData = computed(() => ({
  labels: precipitation.value.map((p) => p.date),
  datasets: [
    {
      label: t("satellitePage.precipitation.actual"),
      data: precipitation.value.map((p) => p.actual),
      backgroundColor: "rgba(34, 197, 94, 0.7)",
      borderRadius: 6,
      barThickness: 16,
    },
    {
      label: t("satellitePage.precipitation.forecast"),
      data: precipitation.value.map((p) => p.forecast),
      backgroundColor: "rgba(59, 130, 246, 0.5)",
      borderRadius: 6,
      barThickness: 16,
    },
  ],
}));

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: "top" as const,
      labels: {
        boxWidth: 12,
        usePointStyle: true,
        padding: 16,
        font: { size: 11 },
      },
    },
  },
  scales: {
    x: { grid: { display: false }, ticks: { font: { size: 10 } } },
    y: {
      grid: { color: "rgba(128,128,128,0.1)" },
      ticks: { font: { size: 10 } },
      title: {
        display: true,
        text: t("satellitePage.precipitation.unit"),
        font: { size: 10 },
      },
    },
  },
}));

onMounted(() => startSimulation());
onBeforeUnmount(() => stopSimulation());
</script>
