<template>
  <div class="space-y-6 max-w-[1400px] mx-auto">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-(--label-text) tracking-tight">Safe Locations Map</h1>
        <p class="text-sm text-(--hint-text) mt-1">Manage evacuation shelters and assembly points — Galați</p>
      </div>
      <div class="flex items-center gap-3">
        <div class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-(--surface-primary) border border-(--border-color)">
          <span class="h-2.5 w-2.5 rounded-full bg-green-500" />
          <span class="text-xs text-(--label-text)">{{ openLocations.length }} Open</span>
        </div>
        <div class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-(--surface-primary) border border-(--border-color)">
          <span class="text-xs text-(--label-text) font-semibold">{{ occupancyPercentage }}%</span>
          <span class="text-xs text-(--hint-text)">Occupied</span>
        </div>
        <Button variant="solid" color="primary" icon-left="mdi:plus" @click="showAddModal = true">Add Location</Button>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <div class="lg:col-span-2">
        <Card class="overflow-hidden">
          <ClientOnly>
            <div class="h-[500px] lg:h-[600px] map-container">
              <LMap ref="mapRef" :zoom="13" :center="[45.4353, 28.0397]" :use-global-leaflet="false" :options="{ zoomControl: true, attributionControl: true }">
                <LTileLayer url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" layer-type="base" name="CartoDB Dark" attribution="&copy; CartoDB" />
                <LMarker v-for="loc in locations" :key="loc.id" :lat-lng="[loc.lat, loc.lng]">
                  <LIcon :icon-size="[32, 32]" :icon-anchor="[16, 32]">
                    <div class="flex flex-col items-center">
                      <div class="h-8 w-8 rounded-full flex items-center justify-center shadow-lg border-2 border-white" :style="{ background: statusColor(loc.status) }">
                        <span class="text-white text-xs font-bold">{{ Math.round((loc.currentOccupancy / loc.capacity) * 100) }}%</span>
                      </div>
                    </div>
                  </LIcon>
                  <LPopup>
                    <div class="p-2 min-w-[200px]">
                      <h3 class="font-bold text-sm text-gray-900 mb-1">{{ loc.name }}</h3>
                      <p class="text-xs text-gray-600 mb-2">{{ loc.address }}</p>
                      <div class="space-y-1 text-xs">
                        <div class="flex justify-between"><span class="text-gray-500">Type:</span><span class="font-medium capitalize">{{ loc.type.replace('-', ' ') }}</span></div>
                        <div class="flex justify-between"><span class="text-gray-500">Status:</span><span class="font-medium capitalize" :style="{ color: statusColor(loc.status) }">{{ loc.status }}</span></div>
                        <div class="flex justify-between"><span class="text-gray-500">Capacity:</span><span class="font-medium">{{ loc.currentOccupancy }}/{{ loc.capacity }}</span></div>
                        <div class="flex justify-between"><span class="text-gray-500">Phone:</span><span class="font-medium">{{ loc.contactPhone }}</span></div>
                      </div>
                    </div>
                  </LPopup>
                </LMarker>
              </LMap>
            </div>
            <template #fallback>
              <div class="h-[500px] lg:h-[600px] flex items-center justify-center bg-(--surface-secondary) rounded-[20px]">
                <div class="text-center">
                  <Icon name="mdi:map" class="h-12 w-12 text-(--hint-text) mx-auto mb-2" />
                  <p class="text-sm text-(--hint-text)">Loading map...</p>
                </div>
              </div>
            </template>
          </ClientOnly>
        </Card>
      </div>

      <div class="space-y-4">
        <Card class="p-4">
          <h3 class="text-sm font-semibold text-(--label-text) mb-3">Location Registry</h3>
          <div class="space-y-2 max-h-[520px] overflow-y-auto pr-1">
            <div v-for="loc in locations" :key="loc.id" class="p-3 rounded-xl border border-(--border-color) hover:bg-(--surface-secondary)/50 transition-colors cursor-pointer" @click="selectedLocation = loc">
              <div class="flex items-center gap-2 mb-1">
                <span class="h-2.5 w-2.5 rounded-full shrink-0" :style="{ background: statusColor(loc.status) }" />
                <p class="text-sm font-medium text-(--label-text) truncate">{{ loc.name }}</p>
              </div>
              <div class="flex items-center justify-between text-xs text-(--hint-text)">
                <span class="capitalize">{{ loc.type.replace('-', ' ') }}</span>
                <span class="font-semibold" :style="{ color: statusColor(loc.status) }">{{ loc.currentOccupancy }}/{{ loc.capacity }}</span>
              </div>
              <div class="water-gauge mt-1.5">
                <div class="water-gauge-fill" :style="{ width: `${(loc.currentOccupancy / loc.capacity) * 100}%`, background: statusColor(loc.status) }" />
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>

    <Modal v-model="showAddModal" title="Add Safe Location" size="lg">
      <Form class="space-y-4" @submit="handleAddLocation">
        <Input v-model="newLocation.name" label="Location Name" placeholder="e.g. School No. 14 — Gymnasium" :required="true" />
        <div class="grid grid-cols-2 gap-4">
          <Input v-model="newLocation.lat" label="Latitude" type="number" placeholder="45.4353" :required="true" />
          <Input v-model="newLocation.lng" label="Longitude" type="number" placeholder="28.0397" :required="true" />
        </div>
        <Input v-model="newLocation.address" label="Address" placeholder="Full address" :required="true" />
        <div class="grid grid-cols-2 gap-4">
          <Input v-model="newLocation.capacity" label="Capacity" type="number" placeholder="100" :required="true" />
          <CustomSelect v-model="newLocation.type" label="Type" :options="typeOptions" :required="true" />
        </div>
        <Input v-model="newLocation.contactPhone" label="Contact Phone" placeholder="+40 236 000 000" />
        <Textarea v-model="newLocation.accessibilityNotes" label="Accessibility Notes" placeholder="Wheelchair access, elevators, etc." :rows="2" />
      </Form>
      <template #footer="{ close }">
        <Button variant="outline" color="secondary" @click="close">Cancel</Button>
        <Button variant="solid" color="primary" @click="handleAddLocation">Add Location</Button>
      </template>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import type { SafeLocation, SafeLocationType } from "~/composables/useSafeLocations";

definePageMeta({ layout: "dashboard", middleware: "auth" });

const { locations, openLocations, occupancyPercentage, statusColor, addLocation } = useSafeLocations();

const showAddModal = ref(false);
const selectedLocation = ref<SafeLocation | null>(null);

const newLocation = reactive({
  name: "", lat: "", lng: "", address: "", capacity: "", type: "", contactPhone: "", accessibilityNotes: "",
});

const typeOptions = [
  { label: "Shelter", value: "shelter" },
  { label: "Assembly Point", value: "assembly-point" },
  { label: "Medical Facility", value: "medical" },
  { label: "Supply Depot", value: "supply-depot" },
];

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
  Object.assign(newLocation, { name: "", lat: "", lng: "", address: "", capacity: "", type: "", contactPhone: "", accessibilityNotes: "" });
};
</script>
