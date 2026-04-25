<template>
  <div class="space-y-6 max-w-[800px] mx-auto">
    <div>
      <h1 class="text-2xl font-bold text-(--label-text) tracking-tight">Settings</h1>
      <p class="text-sm text-(--hint-text) mt-1">Configure your dashboard preferences</p>
    </div>

    <Card class="p-6">
      <h2 class="text-lg font-semibold text-(--label-text) mb-4">Appearance</h2>
      <div class="space-y-4">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-(--label-text)">Dark Mode</p>
            <p class="text-xs text-(--hint-text)">Toggle dark/light theme</p>
          </div>
          <ClientOnly>
            <Switch v-model="isDarkMode" color="primary" @update:model-value="toggleDark" />
          </ClientOnly>
        </div>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-(--label-text)">Language</p>
            <p class="text-xs text-(--hint-text)">Switch between English and Romanian</p>
          </div>
          <div class="flex gap-2">
            <Button v-for="lang in availableLocales" :key="lang.code" :variant="locale === lang.code ? 'solid' : 'outline'" color="primary" size="sm" @click="setLocale(lang.code)">
              {{ lang.name }}
            </Button>
          </div>
        </div>
      </div>
    </Card>

    <Card class="p-6">
      <h2 class="text-lg font-semibold text-(--label-text) mb-4">Role & Access</h2>
      <div class="space-y-4">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-(--label-text)">Current Role</p>
            <p class="text-xs text-(--hint-text)">Select your dashboard view</p>
          </div>
          <div class="flex gap-2">
            <Button v-for="role in roles" :key="role.value" :variant="currentRole === role.value ? 'solid' : 'outline'" color="primary" size="sm" :icon-left="role.icon" @click="setRole(role.value as any)">
              {{ role.label }}
            </Button>
          </div>
        </div>
      </div>
    </Card>

    <Card class="p-6">
      <h2 class="text-lg font-semibold text-(--label-text) mb-4">Notifications</h2>
      <div class="space-y-4">
        <Switch v-model="notifSettings.pushAlerts" color="primary" label="Push Notifications for Alerts" />
        <Switch v-model="notifSettings.emailDigest" color="primary" label="Daily Email Digest" />
        <Switch v-model="notifSettings.sensorWarnings" color="primary" label="Sensor Warning Notifications" />
        <Switch v-model="notifSettings.soundAlarm" color="danger" label="Audible Alarm on Critical Events" />
      </div>
    </Card>

    <Card class="p-6">
      <h2 class="text-lg font-semibold text-(--label-text) mb-4">About Hydralis</h2>
      <div class="space-y-2 text-sm text-(--hint-text)">
        <p>Version: 1.0.0-mvp</p>
        <p>Built for the CASSINI Hackathon — Space for Water</p>
        <p>Powered by Copernicus Data Space Ecosystem & EU Galileo GNSS</p>
        <div class="flex items-center gap-2 mt-3">
          <Badge variant="outline">Nuxt 4</Badge>
          <Badge variant="outline">Leaflet</Badge>
          <Badge variant="outline">Copernicus</Badge>
          <Badge variant="outline">Galileo</Badge>
        </div>
      </div>
    </Card>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: "dashboard", middleware: "auth" });

const colorMode = useColorMode();
const { locale, locales, setLocale } = useI18n();
const { currentRole, setRole } = useRole();

const availableLocales = computed(() => locales.value.filter((l): l is { code: string; name: string } => typeof l !== "string"));

const isDarkMode = ref(colorMode.preference === "dark");
const toggleDark = (val: boolean) => { colorMode.preference = val ? "dark" : "light"; };

const roles = [
  { value: "dispatcher", label: "Dispatcher", icon: "mdi:shield-alert" },
  { value: "industrial", label: "Industrial", icon: "mdi:factory" },
  { value: "admin", label: "Admin", icon: "mdi:cog" },
];

const notifSettings = reactive({
  pushAlerts: true,
  emailDigest: false,
  sensorWarnings: true,
  soundAlarm: true,
});
</script>
