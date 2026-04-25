<template>
  <div class="space-y-6 max-w-[1400px] mx-auto">
    <div>
      <h1 class="text-2xl font-bold text-(--label-text) tracking-tight">
        {{ t("industrialPage.title") }}
      </h1>
      <p class="text-sm text-(--hint-text) mt-1">
        {{ t("industrialPage.subtitle") }}
      </p>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard
        icon="mdi:factory"
        :label="t('industrialPage.cards.totalFacilities')"
        :value="factories.length"
        glow-color="primary"
        icon-bg="#0066CC"
        class="animate-fade-up stagger-1"
      />
      <StatCard
        icon="mdi:alert-octagon"
        :label="t('industrialPage.cards.atRiskFacilities')"
        :value="criticalFactories.length"
        glow-color="danger"
        icon-bg="#EF4444"
        class="animate-fade-up stagger-2"
      />
      <StatCard
        icon="mdi:account-hard-hat"
        :label="t('industrialPage.cards.employeesAtRisk')"
        :value="totalEmployeesAtRisk"
        glow-color="warning"
        icon-bg="#F59E0B"
        class="animate-fade-up stagger-3"
      />
      <StatCard
        icon="mdi:access-point"
        :label="t('industrialPage.cards.criticalSensors')"
        :value="criticalSensors.length"
        glow-color="info"
        icon-bg="#3B82F6"
        class="animate-fade-up stagger-4"
      />
    </div>

    <Card class="p-5">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h2 class="text-lg font-semibold text-(--label-text)">
            {{ t("industrialPage.map.title") }}
          </h2>
          <p class="text-xs text-(--hint-text) flex items-center gap-1 mt-0.5">
            <Icon name="mdi:satellite-variant" class="h-3 w-3" />
            {{ t("industrialPage.map.source") }}
          </p>
        </div>
      </div>
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-2 h-[400px] map-container">
          <ClientOnly>
            <LMap
              :zoom="12"
              :center="[45.4353, 28.035]"
              :use-global-leaflet="false"
              :options="{ zoomControl: true, attributionControl: false }"
            >
              <LTileLayer
                url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                layer-type="base"
                name="CartoDB Dark"
              />
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
                        {{ t("industrialPage.map.floodIntensity") }}:
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
              <LMarker
                v-for="factory in factories"
                :key="factory.id"
                :lat-lng="[factory.lat, factory.lng]"
              >
                <LIcon
                  :icon-size="[44, 44]"
                  :icon-anchor="[22, 22]"
                  class-name=""
                >
                  <div class="flex flex-col items-center">
                    <div
                      class="h-11 w-11 rounded-xl flex flex-col items-center justify-center shadow-lg border-2"
                      :style="{
                        background:
                          factory.status === 'critical'
                            ? '#7F1D1D'
                            : factory.status === 'warning'
                              ? '#92400E'
                              : '#14532D',
                        borderColor: factoryStatusColor(factory.status),
                      }"
                    >
                      <Icon name="mdi:factory" class="h-5 w-5 text-white" />
                    </div>
                  </div>
                </LIcon>
                <LPopup>
                  <div class="p-2 min-w-[200px]">
                    <h3 class="font-bold text-sm text-gray-900 mb-1">
                      {{ factory.name }}
                    </h3>
                    <p class="text-xs text-gray-600 mb-2">
                      {{ factory.location }}
                    </p>
                    <div class="space-y-1 text-xs">
                      <div class="flex justify-between">
                        <span class="text-gray-500"
                          >{{ t("industrialPage.fields.status") }}:</span
                        ><span
                          class="font-medium"
                          :style="{ color: factoryStatusColor(factory.status) }"
                          >{{ factoryStatusLabel(factory.status) }}</span
                        >
                      </div>
                      <div class="flex justify-between">
                        <span class="text-gray-500"
                          >{{ t("industrialPage.fields.risk") }}:</span
                        ><span class="font-medium capitalize">{{
                          riskLabel(factory.riskLevel)
                        }}</span>
                      </div>
                      <div class="flex justify-between">
                        <span class="text-gray-500"
                          >{{ t("industrialPage.fields.employees") }}:</span
                        ><span class="font-medium">{{
                          factory.employees
                        }}</span>
                      </div>
                      <div class="flex justify-between">
                        <span class="text-gray-500"
                          >{{ t("industrialPage.fields.waterDistance") }}:</span
                        ><span class="font-medium"
                          >{{ factory.waterProximity
                          }}{{ t("industrialPage.units.meters") }}</span
                        >
                      </div>
                      <div class="flex justify-between">
                        <span class="text-gray-500"
                          >{{ t("industrialPage.fields.sensors") }}:</span
                        ><span class="font-medium">{{
                          factory.sensorCount
                        }}</span>
                      </div>
                    </div>
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
        <div class="space-y-3">
          <div
            v-for="factory in factories"
            :key="factory.id"
            class="p-3 rounded-xl border border-(--border-color) bg-(--surface-secondary)/30 hover:bg-(--surface-secondary)/50 transition-colors cursor-pointer"
            @click="navigateTo('/dashboard/industrial/factories')"
          >
            <div class="flex items-center gap-2 mb-2">
              <div
                class="h-8 w-8 rounded-lg flex items-center justify-center shrink-0"
                :style="{
                  background: `${factoryStatusColor(factory.status)}15`,
                }"
              >
                <Icon
                  name="mdi:factory"
                  class="h-4 w-4"
                  :style="{ color: factoryStatusColor(factory.status) }"
                />
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-(--label-text) truncate">
                  {{ factory.name }}
                </p>
                <p class="text-[10px] text-(--hint-text)">
                  {{ factory.location }}
                </p>
              </div>
              <Badge
                :variant="
                  factory.status === 'operational'
                    ? 'success'
                    : factory.status === 'critical'
                      ? 'danger'
                      : 'secondary'
                "
                class="shrink-0"
              >
                {{ factoryStatusLabel(factory.status) }}
              </Badge>
            </div>
            <div class="grid grid-cols-3 gap-2 text-center">
              <div class="p-1.5 rounded-lg bg-(--surface-secondary)/50">
                <p class="text-sm font-bold text-(--label-text)">
                  {{ factory.sensorCount }}
                </p>
                <p class="text-[9px] text-(--hint-text)">
                  {{ t("industrialPage.fields.sensors") }}
                </p>
              </div>
              <div class="p-1.5 rounded-lg bg-(--surface-secondary)/50">
                <p class="text-sm font-bold text-(--label-text)">
                  {{ factory.employees }}
                </p>
                <p class="text-[9px] text-(--hint-text)">
                  {{ t("industrialPage.people") }}
                </p>
              </div>
              <div class="p-1.5 rounded-lg bg-(--surface-secondary)/50">
                <p
                  class="text-sm font-bold"
                  :class="
                    factory.waterProximity < 100
                      ? 'text-red-500'
                      : factory.waterProximity < 300
                        ? 'text-amber-500'
                        : 'text-green-500'
                  "
                >
                  {{ factory.waterProximity
                  }}{{ t("industrialPage.units.meters") }}
                </p>
                <p class="text-[9px] text-(--hint-text)">
                  {{ t("industrialPage.water") }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Card>
  </div>
</template>

<script setup lang="ts">
import type { FloodHeatmapZone } from "~/composables/useSatelliteData";
import type { Factory } from "~/composables/useIndustrial";
import {
  LIcon,
  LMap,
  LMarker,
  LPolygon,
  LPopup,
  LTileLayer,
} from "@vue-leaflet/vue-leaflet";

definePageMeta({ layout: "dashboard", middleware: "auth" });
const { t } = useI18n();
const {
  factories,
  criticalFactories,
  criticalSensors,
  totalEmployeesAtRisk,
  factoryStatusColor,
} = useIndustrial();
const { floodHeatmap, heatmapIntensityColor } = useSatelliteData();

const riskLabel = (
  risk: FloodHeatmapZone["riskLevel"] | Factory["riskLevel"],
) =>
  ({
    low: t("industrialPage.risk.low"),
    moderate: t("industrialPage.risk.moderate"),
    high: t("industrialPage.risk.high"),
    critical: t("industrialPage.risk.critical"),
  })[risk];

const factoryStatusLabel = (status: Factory["status"]) =>
  ({
    operational: t("industrialPage.status.operational"),
    warning: t("industrialPage.status.warning"),
    critical: t("industrialPage.status.critical"),
    offline: t("industrialPage.status.offline"),
  })[status];
</script>
