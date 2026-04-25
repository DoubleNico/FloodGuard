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

const generateMockLocations = (): SafeLocation[] => [
  {
    id: "SL-001",
    name: "Sala Sporturilor — Dunărea",
    type: "shelter",
    lat: 45.4353,
    lng: 28.0497,
    address: "Str. Stadionului 2, Galați",
    capacity: 500,
    currentOccupancy: 187,
    status: "open",
    contactPhone: "+40 236 412 000",
    accessibilityNotes: "Wheelchair accessible, ground floor entry",
    lastUpdated: new Date(),
  },
  {
    id: "SL-002",
    name: "Liceul Teoretic Dunărea",
    type: "shelter",
    lat: 45.4412,
    lng: 28.0385,
    address: "Str. Brăilei 134, Galați",
    capacity: 300,
    currentOccupancy: 245,
    status: "filling",
    contactPhone: "+40 236 413 100",
    accessibilityNotes: "Ramp access available at south entrance",
    lastUpdated: new Date(),
  },
  {
    id: "SL-003",
    name: "Parcul Rizer — Assembly Point",
    type: "assembly-point",
    lat: 45.4298,
    lng: 28.0542,
    address: "Parcul Rizer, Galați",
    capacity: 1000,
    currentOccupancy: 312,
    status: "open",
    contactPhone: "+40 236 414 200",
    accessibilityNotes: "Open-air area, flat terrain",
    lastUpdated: new Date(),
  },
  {
    id: "SL-004",
    name: "Spitalul Județean de Urgență",
    type: "medical",
    lat: 45.4267,
    lng: 28.0312,
    address: "Str. Brăilei 177, Galați",
    capacity: 150,
    currentOccupancy: 142,
    status: "filling",
    contactPhone: "+40 236 415 300",
    accessibilityNotes: "Full medical facility, emergency department active",
    lastUpdated: new Date(),
  },
  {
    id: "SL-005",
    name: "Centrul Comercial — Zona de Siguranță",
    type: "shelter",
    lat: 45.4489,
    lng: 28.0267,
    address: "Str. Tecuci 2A, Galați",
    capacity: 800,
    currentOccupancy: 89,
    status: "open",
    contactPhone: "+40 236 416 400",
    accessibilityNotes: "Elevator access, indoor parking available",
    lastUpdated: new Date(),
  },
  {
    id: "SL-006",
    name: "Stadionul Oțelul",
    type: "assembly-point",
    lat: 45.4378,
    lng: 28.0198,
    address: "Str. Oțelarilor 4, Galați",
    capacity: 2000,
    currentOccupancy: 0,
    status: "open",
    contactPhone: "+40 236 417 500",
    accessibilityNotes: "Large open venue, designated evacuation area",
    lastUpdated: new Date(),
  },
  {
    id: "SL-007",
    name: "Depozit Aprovizionare ISU",
    type: "supply-depot",
    lat: 45.4445,
    lng: 28.0451,
    address: "Str. Traian 200, Galați",
    capacity: 100,
    currentOccupancy: 34,
    status: "open",
    contactPhone: "+40 236 418 600",
    accessibilityNotes: "Emergency supplies, staff-only distribution",
    lastUpdated: new Date(),
  },
];

export const useSafeLocations = () => {
  const locations = useState<SafeLocation[]>("safe-locations", () =>
    generateMockLocations()
  );

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

  const addLocation = (
    data: Omit<SafeLocation, "id" | "lastUpdated">
  ) => {
    const id = `SL-${String(locations.value.length + 1).padStart(3, "0")}`;
    locations.value.push({
      ...data,
      id,
      lastUpdated: new Date(),
    });
    return id;
  };

  const updateLocation = (id: string, updates: Partial<SafeLocation>) => {
    const loc = locations.value.find((l) => l.id === id);
    if (loc) {
      Object.assign(loc, updates, { lastUpdated: new Date() });
    }
  };

  const removeLocation = (id: string) => {
    locations.value = locations.value.filter((l) => l.id !== id);
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

  return {
    locations,
    openLocations,
    totalCapacity,
    totalOccupancy,
    occupancyPercentage,
    addLocation,
    updateLocation,
    removeLocation,
    statusColor,
    typeIcon,
  };
};
