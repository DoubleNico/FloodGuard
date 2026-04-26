<template>
  <div class="flex h-screen overflow-hidden bg-(--surface-secondary)">
    <!-- Mobile Emergency Alerts Overlay -->
    <div
      v-if="mobileEmergencies && mobileEmergencies.length > 0"
      class="fixed inset-x-0 top-0 z-50 flex flex-col gap-2 p-4 md:p-6 pointer-events-none"
    >
      <div
        v-for="sos in mobileEmergencies"
        :key="sos.id"
        class="bg-red-900 border-2 border-red-500 shadow-2xl rounded-2xl p-4 md:p-6 text-white pointer-events-auto max-w-2xl mx-auto w-full"
      >
        <div class="flex items-start gap-4">
          <div
            class="h-12 w-12 rounded-full bg-red-500 flex items-center justify-center shrink-0 alarm-ring"
          >
            <Icon name="mdi:alert-decagram" class="h-8 w-8 text-white" />
          </div>
          <div class="flex-1">
            <h2
              class="text-xl font-bold uppercase tracking-widest text-red-100 flex items-center gap-2"
            >
              <span class="relative flex h-3 w-3">
                <span
                  class="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"
                ></span>
                <span
                  class="relative inline-flex rounded-full h-3 w-3 bg-red-500"
                ></span>
              </span>
              Mobile SOS Alert
            </h2>
            <p class="text-lg font-semibold mt-1">
              {{ sos.userName || "Unknown Worker" }}
            </p>
            <p class="text-red-200 text-sm mt-1 leading-relaxed">
              {{ sos.message }}
            </p>

            <div class="mt-4 grid grid-cols-2 gap-3">
              <div
                class="bg-red-950/50 rounded-lg p-2.5 border border-red-500/20"
              >
                <p
                  class="text-[10px] text-red-300 uppercase tracking-wider font-semibold"
                >
                  Location
                </p>
                <p class="font-medium text-sm mt-0.5 truncate">
                  {{ sos.affectedAreas[0] }}
                </p>
              </div>
              <div
                class="bg-red-950/50 rounded-lg p-2.5 border border-red-500/20"
              >
                <p
                  class="text-[10px] text-red-300 uppercase tracking-wider font-semibold"
                >
                  Mobility Info
                </p>
                <p class="font-medium text-sm mt-0.5">
                  {{
                    sos.mobilityInfo?.has_issues
                      ? `Issues: ${sos.mobilityInfo.gravity}`
                      : "No known issues"
                  }}
                </p>
              </div>
            </div>
          </div>

          <button
            @click="updateAlertStatus(sos.id, 'closed')"
            class="px-4 py-2 bg-red-950/50 border border-red-500/30 hover:bg-red-800 rounded-lg text-sm font-semibold transition-colors"
          >
            Dismiss
          </button>
        </div>
      </div>
    </div>

    <Sidebar>
      <SidebarHeader>
        <template #default>
          <div class="flex items-center gap-2.5">
            <img
              src="/icon.png"
              alt="Hydralis Logo"
              class="h-9 w-9 rounded-xl shadow-lg object-cover"
            />
            <div>
              <span
                class="text-base font-bold text-(--label-text) tracking-tight"
                >Hydralis</span
              >
              <span
                class="block text-[10px] text-(--hint-text) -mt-0.5 font-medium uppercase tracking-wider"
                >Dashboard</span
              >
            </div>
          </div>
        </template>
        <template #icon>
          <img
            src="/icon.png"
            alt="Hydralis Logo"
            class="h-9 w-9 rounded-xl shadow-lg object-cover"
          />
        </template>
      </SidebarHeader>

      <SidebarContent>
        <div v-if="!isCollapsed" class="px-2 mb-1">
          <span
            class="text-[10px] font-semibold text-(--hint-text) uppercase tracking-widest"
            >{{
              isDispatcher
                ? "Dispatcher"
                : isIndustrial
                  ? "Industrial"
                  : "Admin"
            }}</span
          >
        </div>

        <SidebarItem
          to="/dashboard"
          icon="mdi:view-dashboard"
          :label="$t('nav.overview')"
        />

        <template v-if="isDispatcher || isAdmin">
          <SidebarItem
            to="/dashboard/alerts"
            icon="mdi:bell-alert"
            :label="$t('nav.alerts')"
          >
            <template #suffix>
              <span
                v-if="activeAlerts.length > 0"
                class="flex h-5 min-w-5 items-center justify-center rounded-full bg-(--btn-danger-bg) text-[10px] font-bold text-white px-1"
              >
                {{ activeAlerts.length }}
              </span>
            </template>
          </SidebarItem>
          <SidebarItem
            to="/dashboard/map"
            icon="mdi:map-marker-radius"
            :label="$t('nav.map')"
          />
          <SidebarItem
            to="/dashboard/satellite"
            icon="mdi:satellite-variant"
            :label="$t('nav.satellite')"
          />
        </template>

        <template v-if="isIndustrial || isAdmin">
          <SidebarItem
            to="/dashboard/industrial"
            icon="mdi:factory"
            :label="$t('nav.industrial')"
          />
          <SidebarItem
            to="/dashboard/industrial/factories"
            icon="mdi:office-building"
            :label="$t('nav.factories')"
          />
          <SidebarItem
            to="/dashboard/industrial/sensors"
            icon="mdi:access-point"
            :label="$t('nav.sensors')"
          />
        </template>

        <div v-if="!isCollapsed" class="px-2 mt-6 mb-1">
          <span
            class="text-[10px] font-semibold text-(--hint-text) uppercase tracking-widest"
            >System</span
          >
        </div>
        <SidebarItem
          to="/dashboard/settings"
          icon="mdi:cog"
          :label="$t('nav.settings')"
        />
        <SidebarItem
          to="/dashboard/profile"
          icon="mdi:account"
          label="Profile"
        />
      </SidebarContent>

      <SidebarFooter>
        <template #default="{ isCollapsed: collapsed }">
          <div v-if="!collapsed" class="flex items-center gap-2.5">
            <div
              class="h-8 w-8 rounded-full bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center text-white text-xs font-bold shadow"
            >
              {{ sessionCookie?.charAt(0)?.toUpperCase() || "H" }}
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-(--label-text) truncate">
                {{ sessionCookie || "Hydralis" }}
              </p>
              <p class="text-[11px] text-(--hint-text)">{{ roleLabel }}</p>
            </div>
          </div>
          <div v-else class="flex justify-center">
            <div
              class="h-8 w-8 rounded-full bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center text-white text-xs font-bold shadow"
            >
              {{ sessionCookie?.charAt(0)?.toUpperCase() || "H" }}
            </div>
          </div>
        </template>
      </SidebarFooter>
    </Sidebar>

    <div class="flex-1 flex flex-col min-w-0 overflow-hidden">
      <header
        class="h-14 shrink-0 flex items-center justify-between px-4 border-b border-(--border-color) bg-(--surface-primary)"
      >
        <div class="flex items-center gap-3">
          <button
            class="md:hidden h-8 w-8 flex items-center justify-center rounded-lg hover:bg-(--surface-secondary) text-(--icon-color)"
            @click="toggleMobile"
          >
            <Icon name="mdi:menu" class="h-5 w-5" />
          </button>
          <div
            class="hidden md:flex items-center gap-1.5 text-sm text-(--hint-text)"
          >
            <Icon name="mdi:home" class="h-4 w-4" />
            <span>/</span>
            <span class="text-(--label-text) font-medium">{{
              currentPageTitle
            }}</span>
          </div>
        </div>

        <div class="flex items-center gap-3">
          <div
            v-if="globalAlarmActive"
            class="flex items-center gap-2 px-3 py-1.5 rounded-full bg-red-500/10 border border-red-500/20"
          >
            <span class="relative flex h-2.5 w-2.5">
              <span
                class="alarm-pulse absolute inline-flex h-full w-full rounded-full bg-red-500 opacity-75"
              ></span>
              <span
                class="relative inline-flex rounded-full h-2.5 w-2.5 bg-red-500"
              ></span>
            </span>
            <span
              class="text-xs font-bold text-red-500 uppercase tracking-wider"
              >Active Alert</span
            >
          </div>

          <ClientOnly>
            <button
              class="h-8 w-8 flex items-center justify-center rounded-lg hover:bg-(--surface-secondary) text-(--icon-color) transition-colors"
              @click="changeMode"
            >
              <Icon
                :name="
                  $colorMode.value === 'dark'
                    ? 'mdi:weather-sunny'
                    : 'mdi:weather-night'
                "
                class="h-4.5 w-4.5"
              />
            </button>
          </ClientOnly>

          <div
            class="flex items-center gap-1.5 px-2 py-1 rounded-lg bg-(--surface-secondary) cursor-pointer"
            @click="cycleRole"
          >
            <Icon :name="roleIcon" class="h-4 w-4 text-(--icon-color)" />
            <span
              class="text-xs font-medium text-(--label-text) hidden sm:inline"
              >{{ roleLabel }}</span
            >
          </div>
        </div>
      </header>

      <main class="flex-1 overflow-y-auto p-4 md:p-6">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { AUTH_USER_COOKIE } from "~/utils/internalAuth";

const { isCollapsed, toggleMobile } = useSidebar();
const {
  currentRole,
  isDispatcher,
  isIndustrial,
  isAdmin,
  roleLabel,
  roleIcon,
  setRole,
} = useRole();
const {
  activeAlerts,
  globalAlarmActive,
  mobileEmergencies,
  updateAlertStatus,
} = useAlerts();
const { connect: connectStream, disconnect: disconnectStream } = useStream();

const sessionCookie = useCookie<string | null>(AUTH_USER_COOKIE);
const route = useRoute();
const colorMode = useColorMode();
const { t } = useI18n();

onMounted(() => {
  connectStream();
});

onBeforeUnmount(() => {
  disconnectStream();
});

const changeMode = () => {
  const modes = ["light", "dark"];
  const current = modes.indexOf(colorMode.preference);
  colorMode.preference = modes[(current + 1) % modes.length]!;
};

const roleOrder: Array<"dispatcher" | "industrial" | "admin"> = [
  "dispatcher",
  "industrial",
  "admin",
];
const cycleRole = () => {
  const idx = roleOrder.indexOf(currentRole.value);
  setRole(roleOrder[(idx + 1) % roleOrder.length]!);
};

const currentPageTitle = computed(() => {
  const path = route.path;
  if (path === "/dashboard") return t("nav.overview");
  if (path.includes("/alerts")) return t("nav.alerts");
  if (path.includes("/map")) return t("nav.map");
  if (path.includes("/satellite")) return t("nav.satellite");
  if (path.includes("/industrial/factories")) return t("nav.factories");
  if (path.includes("/industrial/sensors")) return t("nav.sensors");
  if (path.includes("/industrial")) return t("nav.industrial");
  if (path.includes("/subscription")) return t("nav.subscription");
  if (path.includes("/settings")) return t("nav.settings");
  if (path.includes("/profile")) return "Profile";
  return "Dashboard";
});
</script>
