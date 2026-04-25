export type SafeLocationStatus = "open" | "filling" | "full" | "closed";
export type SafeLocationType =
  | "shelter"
  | "assembly-point"
  | "medical"
  | "supply-depot";

export interface SafeLocation {
  id: string;
  name: string;
  type: SafeLocationType;
  lat: number;
  lng: number;
  address: string;
  capacity: number;
  currentOccupancy: number;
  status: SafeLocationStatus;
  contactPhone: string;
  accessibilityNotes: string;
  lastUpdated: Date;
}

interface LocationApiRow {
  id: string;
  name: string;
  type: SafeLocationType;
  lat: number;
  lng: number;
  address: string;
  capacity: number;
  currentOccupancy: number;
  status: SafeLocationStatus;
  contactPhone: string | null;
  accessibilityNotes: string | null;
  lastUpdated: string;
}

const parseLocation = (raw: LocationApiRow): SafeLocation => ({
  ...raw,
  contactPhone: raw.contactPhone || "",
  accessibilityNotes: raw.accessibilityNotes || "",
  lastUpdated: new Date(raw.lastUpdated),
});

export const useSafeLocations = () => {
  const { get, post, patch, del } = useApi();

  const locations = useState<SafeLocation[]>("safe-locations", () => []);
  const loading = useState("locations-loading", () => false);

  const refreshLocations = async () => {
    loading.value = true;
    try {
      const data = await get<{ locations: LocationApiRow[] }>("/api/v1/locations");
      locations.value = data.locations.map(parseLocation);
    } catch {
      // keep existing data on error
    } finally {
      loading.value = false;
    }
  };

  const openLocations = computed(() =>
    locations.value.filter((l) => l.status === "open" || l.status === "filling")
  );

  const totalCapacity = computed(() =>
    locations.value.reduce((sum, l) => sum + l.capacity, 0)
  );

  const totalOccupancy = computed(() =>
    locations.value.reduce((sum, l) => sum + l.currentOccupancy, 0)
  );

  const occupancyPercentage = computed(() => {
    if (totalCapacity.value === 0) return 0;
    return Math.round((totalOccupancy.value / totalCapacity.value) * 100);
  });

  const addLocation = async (
    data: Omit<SafeLocation, "id" | "lastUpdated">
  ) => {
    await post("/api/v1/locations", {
      name: data.name,
      type: data.type,
      lat: data.lat,
      lng: data.lng,
      address: data.address,
      capacity: data.capacity,
      currentOccupancy: data.currentOccupancy,
      status: data.status,
      contactPhone: data.contactPhone || null,
      accessibilityNotes: data.accessibilityNotes || null,
    });
    await refreshLocations();
  };

  const updateLocation = async (id: string, updates: Partial<SafeLocation>) => {
    const body: Record<string, unknown> = {};
    if (updates.name !== undefined) body.name = updates.name;
    if (updates.type !== undefined) body.type = updates.type;
    if (updates.lat !== undefined) body.lat = updates.lat;
    if (updates.lng !== undefined) body.lng = updates.lng;
    if (updates.address !== undefined) body.address = updates.address;
    if (updates.capacity !== undefined) body.capacity = updates.capacity;
    if (updates.currentOccupancy !== undefined) body.currentOccupancy = updates.currentOccupancy;
    if (updates.status !== undefined) body.status = updates.status;
    if (updates.contactPhone !== undefined) body.contactPhone = updates.contactPhone;
    if (updates.accessibilityNotes !== undefined) body.accessibilityNotes = updates.accessibilityNotes;

    await patch(`/api/v1/locations/${id}`, body);
    await refreshLocations();
  };

  const removeLocation = async (id: string) => {
    await del(`/api/v1/locations/${id}`);
    await refreshLocations();
  };

  const statusColor = (status: SafeLocationStatus) => {
    switch (status) {
      case "open":
        return "#22C55E";
      case "filling":
        return "#F59E0B";
      case "full":
        return "#EF4444";
      case "closed":
        return "#6B7280";
    }
  };

  const typeIcon = (type: SafeLocationType) => {
    switch (type) {
      case "shelter":
        return "mdi:home-flood";
      case "assembly-point":
        return "mdi:account-group";
      case "medical":
        return "mdi:hospital-box";
      case "supply-depot":
        return "mdi:package-variant-closed";
    }
  };

  if (import.meta.client && locations.value.length === 0) {
    refreshLocations();
  }

  return {
    locations,
    loading,
    openLocations,
    totalCapacity,
    totalOccupancy,
    occupancyPercentage,
    addLocation,
    updateLocation,
    removeLocation,
    statusColor,
    typeIcon,
    refreshLocations,
  };
};
