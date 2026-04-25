<template>
  <div class="flex h-screen overflow-hidden bg-(--surface-secondary)">
    <Sidebar>
      <SidebarHeader>
        <template #default>
          <div class="flex items-center gap-2.5">
            <div
              class="h-9 w-9 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-400 flex items-center justify-center shadow-lg shadow-blue-500/25"
            >
              <Icon name="mdi:water-alert" class="h-5 w-5 text-white" />
            </div>
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
          <div
            class="h-9 w-9 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-400 flex items-center justify-center shadow-lg shadow-blue-500/25"
          >
            <Icon name="mdi:water-alert" class="h-5 w-5 text-white" />
          </div>
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
          to="/dashboard/subscription"
          icon="mdi:credit-card"
          :label="$t('nav.subscription')"
        />
        <SidebarItem
          to="/dashboard/settings"
          icon="mdi:cog"
          :label="$t('nav.settings')"
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
const { activeAlerts, globalAlarmActive } = useAlerts();
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
  return "Dashboard";
});
</script>
