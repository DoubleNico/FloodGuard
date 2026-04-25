<template>
  <div class="space-y-6 max-w-[1400px] mx-auto">
    <div
      class="flex flex-col sm:flex-row sm:items-center justify-between gap-4"
    >
      <div>
        <h1 class="text-2xl font-bold text-(--label-text) tracking-tight">
          {{ t("mapPage.title") }}
        </h1>
        <p class="text-sm text-(--hint-text) mt-1">
          {{ t("mapPage.subtitle") }}
        </p>
      </div>
      <div class="flex items-center gap-3">
        <div
          class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-(--surface-primary) border border-(--border-color)"
        >
          <span class="h-2.5 w-2.5 rounded-full bg-green-500" />
          <span class="text-xs text-(--label-text)"
            >{{ openLocations.length }} {{ t("mapPage.open") }}</span
          >
        </div>
        <div
          class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-(--surface-primary) border border-(--border-color)"
        >
          <span class="text-xs text-(--label-text) font-semibold"
            >{{ occupancyPercentage }}%</span
          >
          <span class="text-xs text-(--hint-text)">{{
            t("mapPage.occupied")
          }}</span>
        </div>
        <Button
          variant="solid"
          color="primary"
          icon-left="mdi:plus"
          @click="showAddModal = true"
          >{{ t("mapPage.addLocation") }}</Button
        >
      </div>
    </div>

    <Tabs v-model="activeMapTab" default-value="locations">
      <TabsList>
        <TabsTrigger value="locations">
          <Icon name="mdi:map-marker-check" class="h-4 w-4 mr-1.5" />{{
            t("mapPage.safeLocations")
          }}
        </TabsTrigger>
        <TabsTrigger value="heatmap">
          <Icon name="mdi:thermometer-alert" class="h-4 w-4 mr-1.5" />{{
            t("mapPage.floodHeatmap")
          }}
        </TabsTrigger>
      </TabsList>

      <TabsContent value="locations">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 mt-4">
          <div class="lg:col-span-2">
            <Card class="overflow-hidden">
              <ClientOnly>
                <div class="h-[500px] lg:h-[600px] map-container">
                  <LMap
                    v-if="activeMapTab === 'locations'"
                    ref="mapRef"
                    :zoom="13"
                    :center="[45.4353, 28.0397]"
                    :use-global-leaflet="false"
                    :options="{ zoomControl: true, attributionControl: true }"
                  >
                    <LTileLayer
                      url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                      layer-type="base"
                      name="CartoDB Dark"
                      attribution="&copy; CartoDB"
                    />
                    <LMarker
                      v-for="loc in locations"
                      :key="loc.id"
                      :lat-lng="[loc.lat, loc.lng]"
                    >
                      <LIcon
                        :icon-size="[32, 32]"
                        :icon-anchor="[16, 32]"
                        class-name=""
                      >
                        <div class="flex flex-col items-center">
                          <div
                            class="h-8 w-8 rounded-full flex items-center justify-center shadow-lg border-2 border-white"
                            :style="{ background: statusColor(loc.status) }"
                          >
                            <span class="text-white text-xs font-bold"
                              >{{
                                Math.round(
                                  (loc.currentOccupancy / loc.capacity) * 100,
                                )
                              }}%</span
                            >
                          </div>
                        </div>
                      </LIcon>
                      <LPopup>
                        <div class="p-2 min-w-[200px]">
                          <h3 class="font-bold text-sm text-gray-900 mb-1">
                            {{ loc.name }}
                          </h3>
                          <p class="text-xs text-gray-600 mb-2">
                            {{ loc.address }}
                          </p>
                          <div class="space-y-1 text-xs">
                            <div class="flex justify-between">
                              <span class="text-gray-500"
                                >{{ t("mapPage.fields.type") }}:</span
                              ><span class="font-medium">{{
                                locationTypeLabel(loc.type)
                              }}</span>
                            </div>
                            <div class="flex justify-between">
                              <span class="text-gray-500"
                                >{{ t("mapPage.fields.status") }}:</span
                              ><span
                                class="font-medium"
                                :style="{ color: statusColor(loc.status) }"
                                >{{ locationStatusLabel(loc.status) }}</span
                              >
                            </div>
                            <div class="flex justify-between">
                              <span class="text-gray-500"
                                >{{ t("mapPage.fields.capacity") }}:</span
                              ><span class="font-medium"
                                >{{ loc.currentOccupancy }}/{{
                                  loc.capacity
                                }}</span
                              >
                            </div>
                            <div class="flex justify-between">
                              <span class="text-gray-500"
                                >{{ t("mapPage.fields.phone") }}:</span
                              ><span class="font-medium">{{
                                loc.contactPhone || t("mapPage.notAvailable")
                              }}</span>
                            </div>
                          </div>
                        </div>
                      </LPopup>
                    </LMarker>
                  </LMap>
                </div>
                <template #fallback>
                  <div
                    class="h-[500px] lg:h-[600px] flex items-center justify-center bg-(--surface-secondary) rounded-[20px]"
                  >
                    <div class="text-center">
                      <Icon
                        name="mdi:map"
                        class="h-12 w-12 text-(--hint-text) mx-auto mb-2"
                      />
                      <p class="text-sm text-(--hint-text)">
                        {{ t("mapPage.loadingMap") }}
                      </p>
                    </div>
                  </div>
                </template>
              </ClientOnly>
            </Card>
          </div>

          <div class="space-y-4">
            <Card class="p-4">
              <h3 class="text-sm font-semibold text-(--label-text) mb-3">
                {{ t("mapPage.locationRegistry") }}
              </h3>
              <div class="space-y-2 max-h-[520px] overflow-y-auto pr-1">
                <div
                  v-for="loc in locations"
                  :key="loc.id"
                  class="p-3 rounded-xl border border-(--border-color) hover:bg-(--surface-secondary)/50 transition-colors cursor-pointer"
                >
                  <div class="flex items-center gap-2 mb-1">
                    <span
                      class="h-2.5 w-2.5 rounded-full shrink-0"
                      :style="{ background: statusColor(loc.status) }"
                    />
                    <p class="text-sm font-medium text-(--label-text) truncate">
                      {{ loc.name }}
                    </p>
                  </div>
                  <div
                    class="flex items-center justify-between text-xs text-(--hint-text)"
                  >
                    <span>{{ locationTypeLabel(loc.type) }}</span>
                    <span
                      class="font-semibold"
                      :style="{ color: statusColor(loc.status) }"
                      >{{ loc.currentOccupancy }}/{{ loc.capacity }}</span
                    >
                  </div>
                  <div class="water-gauge mt-1.5">
                    <div
                      class="water-gauge-fill"
                      :style="{
                        width: `${(loc.currentOccupancy / loc.capacity) * 100}%`,
                        background: statusColor(loc.status),
                      }"
                    />
                  </div>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </TabsContent>

      <TabsContent value="heatmap">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 mt-4">
          <div class="lg:col-span-2">
            <Card class="overflow-hidden">
              <ClientOnly>
                <div class="h-[500px] lg:h-[600px] map-container">
                  <LMap
                    v-if="activeMapTab === 'heatmap'"
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
                    <template v-for="hz in floodHeatmap" :key="hz.id">
                      <LPolygon
                        :lat-lngs="hz.polygon"
                        :color="heatmapIntensityColor(hz.intensity)"
                        :fill-color="heatmapIntensityColor(hz.intensity)"
                        :fill-opacity="0.3"
                        :weight="1"
                      >
                        <LPopup>
                          <div class="p-2 min-w-[180px]">
                            <h3 class="font-bold text-sm text-gray-900 mb-1">
                              {{ hz.zone }}
                            </h3>
                            <p class="text-xs text-gray-600 mb-1">
                              {{ t("mapPage.floodIntensity") }}:
                              <strong
                                :style="{
                                  color: heatmapIntensityColor(hz.intensity),
                                }"
                                >{{ Math.round(hz.intensity * 100) }}%</strong
                              >
                            </p>
                            <p
                              class="text-xs text-gray-500 uppercase font-semibold"
                              :style="{
                                color: heatmapIntensityColor(hz.intensity),
                              }"
                            >
                              {{ riskLabel(hz.riskLevel) }}
                            </p>
                          </div>
                        </LPopup>
                      </LPolygon>
                    </template>
                  </LMap>
                </div>
                <template #fallback>
                  <div
                    class="h-[500px] lg:h-[600px] flex items-center justify-center bg-(--surface-secondary) rounded-[20px]"
                  >
                    <div class="text-center">
                      <Icon
                        name="mdi:map"
                        class="h-12 w-12 text-(--hint-text) mx-auto mb-2"
                      />
                      <p class="text-sm text-(--hint-text)">
                        {{ t("mapPage.loadingHeatmap") }}
                      </p>
                    </div>
                  </div>
                </template>
              </ClientOnly>
            </Card>
          </div>

          <div class="space-y-4">
            <Card class="p-4">
              <div class="flex items-center justify-between mb-3">
                <h3 class="text-sm font-semibold text-(--label-text)">
                  {{ t("mapPage.floodRiskZones") }}
                </h3>
                <Badge variant="outline"
                  >{{ floodHeatmap.length }} {{ t("mapPage.zones") }}</Badge
                >
              </div>
              <div class="space-y-2 max-h-[520px] overflow-y-auto pr-1">
                <div
                  v-for="hz in sortedHeatmap"
                  :key="hz.id"
                  class="p-3 rounded-xl border border-(--border-color) bg-(--surface-secondary)/30"
                >
                  <div class="flex items-center justify-between mb-1">
                    <p class="text-sm font-medium text-(--label-text) truncate">
                      {{ hz.zone }}
                    </p>
                    <span
                      class="text-[10px] font-bold uppercase px-1.5 py-0.5 rounded-full"
                      :style="{
                        background: `${heatmapIntensityColor(hz.intensity)}20`,
                        color: heatmapIntensityColor(hz.intensity),
                      }"
                      >{{ riskLabel(hz.riskLevel) }}</span
                    >
                  </div>
                  <div
                    class="flex items-center justify-between text-xs text-(--hint-text) mb-1.5"
                  >
                    <span>{{ t("mapPage.intensity") }}</span>
                    <span
                      class="font-bold"
                      :style="{ color: heatmapIntensityColor(hz.intensity) }"
                      >{{ Math.round(hz.intensity * 100) }}%</span
                    >
                  </div>
                  <div class="water-gauge">
                    <div
                      class="water-gauge-fill"
                      :style="{
                        width: `${hz.intensity * 100}%`,
                        background: heatmapIntensityColor(hz.intensity),
                      }"
                    />
                  </div>
                </div>
              </div>
            </Card>

            <Card class="p-4">
              <h3 class="text-sm font-semibold text-(--label-text) mb-3">
                {{ t("mapPage.legend") }}
              </h3>
              <div class="space-y-2">
                <div class="flex items-center gap-2">
                  <span class="h-3 w-3 bg-[#EF4444] border border-black/10" />
                  <span class="text-xs text-(--label-text)">{{
                    t("mapPage.legendLabels.critical")
                  }}</span>
                </div>
                <div class="flex items-center gap-2">
                  <span class="h-3 w-3 bg-[#F97316] border border-black/10" />
                  <span class="text-xs text-(--label-text)">{{
                    t("mapPage.legendLabels.high")
                  }}</span>
                </div>
                <div class="flex items-center gap-2">
                  <span class="h-3 w-3 bg-[#FFFF00] border border-black/10" />
                  <span class="text-xs text-(--label-text)">{{
                    t("mapPage.legendLabels.moderate")
                  }}</span>
                </div>
                <div class="flex items-center gap-2">
                  <span class="h-3 w-3 bg-[#22C55E] border border-black/10" />
                  <span class="text-xs text-(--label-text)">{{
                    t("mapPage.legendLabels.low")
                  }}</span>
                </div>
              </div>
              <p
                class="text-[10px] text-(--hint-text) mt-3 flex items-center gap-1"
              >
                <Icon name="mdi:satellite-variant" class="h-3 w-3" />
                {{ t("mapPage.source") }}: Copernicus Sentinel-1 SAR +
                {{ t("mapPage.hydrologicalModel") }}
              </p>
            </Card>
          </div>
        </div>
      </TabsContent>
    </Tabs>

    <Modal
      v-model="showAddModal"
      :title="t('mapPage.addSafeLocation')"
      size="lg"
    >
      <Form class="space-y-4" @submit="handleAddLocation">
        <Input
          v-model="newLocation.name"
          :label="t('mapPage.form.locationName')"
          :placeholder="t('mapPage.form.locationNamePlaceholder')"
          :required="true"
        />
        <div class="grid grid-cols-2 gap-4">
          <Input
            v-model="newLocation.lat"
            :label="t('mapPage.form.latitude')"
            type="number"
            placeholder="45.4353"
            :required="true"
          />
          <Input
            v-model="newLocation.lng"
            :label="t('mapPage.form.longitude')"
            type="number"
            placeholder="28.0397"
            :required="true"
          />
        </div>
        <Input
          v-model="newLocation.address"
          :label="t('mapPage.form.address')"
          :placeholder="t('mapPage.form.addressPlaceholder')"
          :required="true"
        />
        <div class="grid grid-cols-2 gap-4">
          <Input
            v-model="newLocation.capacity"
            :label="t('mapPage.form.capacity')"
            type="number"
            placeholder="100"
            :required="true"
          />
          <CustomSelect
            v-model="newLocation.type"
            :label="t('mapPage.form.type')"
            :options="typeOptions"
            :required="true"
          />
        </div>
        <Input
          v-model="newLocation.contactPhone"
          :label="t('mapPage.form.contactPhone')"
          placeholder="+40 236 000 000"
        />
        <Textarea
          v-model="newLocation.accessibilityNotes"
          :label="t('mapPage.form.accessibilityNotes')"
          :placeholder="t('mapPage.form.accessibilityNotesPlaceholder')"
          :rows="2"
        />
      </Form>
      <template #footer="{ close }">
        <Button variant="outline" color="secondary" @click="close">{{
          t("mapPage.cancel")
        }}</Button>
        <Button variant="solid" color="primary" @click="handleAddLocation">{{
          t("mapPage.addLocation")
        }}</Button>
      </template>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import type { FloodHeatmapZone } from "~/composables/useSatelliteData";
import {
  LIcon,
  LMap,
  LMarker,
  LPolygon,
  LPopup,
  LTileLayer,
} from "@vue-leaflet/vue-leaflet";
import type {
  SafeLocationStatus,
  SafeLocationType,
} from "~/composables/useSafeLocations";

definePageMeta({ layout: "dashboard", middleware: "auth" });

const { t } = useI18n();
const {
  locations,
  openLocations,
  occupancyPercentage,
  statusColor,
  addLocation,
} = useSafeLocations();
const { floodHeatmap, heatmapIntensityColor } = useSatelliteData();

const activeMapTab = ref("locations");
const showAddModal = ref(false);

const sortedHeatmap = computed(() =>
  [...floodHeatmap.value].sort((a, b) => b.intensity - a.intensity),
);

const locationTypeLabel = (type: SafeLocationType) =>
  ({
    shelter: t("mapPage.locationTypes.shelter"),
    "assembly-point": t("mapPage.locationTypes.assemblyPoint"),
    medical: t("mapPage.locationTypes.medical"),
    "supply-depot": t("mapPage.locationTypes.supplyDepot"),
  })[type];

const locationStatusLabel = (status: SafeLocationStatus) =>
  ({
    open: t("mapPage.locationStatus.open"),
    filling: t("mapPage.locationStatus.filling"),
    full: t("mapPage.locationStatus.full"),
    closed: t("mapPage.locationStatus.closed"),
  })[status];

const riskLabel = (risk: FloodHeatmapZone["riskLevel"]) =>
  ({
    low: t("mapPage.riskLevel.low"),
    moderate: t("mapPage.riskLevel.moderate"),
    high: t("mapPage.riskLevel.high"),
    critical: t("mapPage.riskLevel.critical"),
  })[risk];

const newLocation = reactive({
  name: "",
  lat: "",
  lng: "",
  address: "",
  capacity: "",
  type: "",
  contactPhone: "",
  accessibilityNotes: "",
});

const typeOptions = computed(() => [
  { label: t("mapPage.locationTypes.shelter"), value: "shelter" },
  { label: t("mapPage.locationTypes.assemblyPoint"), value: "assembly-point" },
  { label: t("mapPage.locationTypes.medical"), value: "medical" },
  { label: t("mapPage.locationTypes.supplyDepot"), value: "supply-depot" },
]);

const handleAddLocation = () => {
  if (!newLocation.name || !newLocation.lat || !newLocation.lng) return;
  addLocation({
    name: newLocation.name,
    lat: parseFloat(newLocation.lat),
    lng: parseFloat(newLocation.lng),
    address: newLocation.address,
    capacity: parseInt(newLocation.capacity) || 100,
    currentOccupancy: 0,
    status: "open",
    type: (newLocation.type || "shelter") as SafeLocationType,
    contactPhone: newLocation.contactPhone,
    accessibilityNotes: newLocation.accessibilityNotes,
  });
  showAddModal.value = false;
  Object.assign(newLocation, {
    name: "",
    lat: "",
    lng: "",
    address: "",
    capacity: "",
    type: "",
    contactPhone: "",
    accessibilityNotes: "",
  });
};
</script>
