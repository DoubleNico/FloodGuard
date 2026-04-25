<template>
  <div class="min-h-screen bg-(--surface-secondary)">
    <NavigationMenu class="px-6 h-16 max-w-screen fixed top-0 left-0 right-0 z-50 bg-(--nav-bg) backdrop-blur-xl border-b border-(--nav-border)">
      <template #left>
        <a href="/" class="flex items-center gap-2.5 cursor-pointer">
          <div class="h-8 w-8 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-400 flex items-center justify-center shadow-lg shadow-blue-500/20">
            <Icon name="mdi:water-alert" class="h-4.5 w-4.5 text-white" />
          </div>
          <span class="font-bold text-lg tracking-tight text-(--label-text)">Hydralis</span>
        </a>
      </template>

      <div class="hidden md:block">
        <NavigationMenuList>
          <NavigationMenuItem>
            <NavigationMenuLink href="#features" class="text-[13px] font-medium px-3 py-2 text-(--label-text) hover:text-blue-500 transition-colors">
              Features
            </NavigationMenuLink>
          </NavigationMenuItem>
          <NavigationMenuItem>
            <NavigationMenuLink href="#satellite" class="text-[13px] font-medium px-3 py-2 text-(--label-text) hover:text-blue-500 transition-colors">
              Satellite Data
            </NavigationMenuLink>
          </NavigationMenuItem>
          <NavigationMenuItem>
            <NavigationMenuLink href="#pricing" class="text-[13px] font-medium px-3 py-2 text-(--label-text) hover:text-blue-500 transition-colors">
              Pricing
            </NavigationMenuLink>
          </NavigationMenuItem>
        </NavigationMenuList>
      </div>

      <template #right>
        <div class="flex items-center gap-3">
          <ClientOnly>
            <button class="h-8 w-8 flex items-center justify-center rounded-lg hover:bg-(--surface-secondary) text-(--icon-color) transition-colors" @click="changeMode">
              <Icon :name="$colorMode.value === 'dark' ? 'mdi:weather-sunny' : 'mdi:weather-night'" class="h-4.5 w-4.5" />
            </button>
          </ClientOnly>
          <CustomLink to="/auth">
            <Button size="sm" class="rounded-full px-5 bg-gradient-to-r from-blue-500 to-cyan-400 text-white hover:from-blue-600 hover:to-cyan-500 shadow-lg shadow-blue-500/25 border-0">
              Access Dashboard
            </Button>
          </CustomLink>
        </div>
      </template>
    </NavigationMenu>

    <section class="relative pt-32 pb-20 px-6 overflow-hidden">
      <div class="absolute inset-0 overflow-hidden">
        <div class="absolute top-20 -left-32 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl" />
        <div class="absolute top-40 -right-32 w-96 h-96 bg-cyan-400/10 rounded-full blur-3xl" />
        <div class="absolute bottom-0 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-blue-600/5 rounded-full blur-3xl" />
      </div>

      <div class="relative max-w-4xl mx-auto text-center">
        <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-(--surface-primary) border border-(--border-color) shadow-sm mb-8">
          <span class="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
          <span class="text-xs font-semibold text-(--label-text)">CASSINI Hackathon — Space for Water</span>
        </div>

        <h1 class="text-4xl sm:text-5xl lg:text-6xl font-bold text-(--label-text) tracking-tight leading-[1.1] mb-6">
          Flood Early Warning &
          <span class="bg-gradient-to-r from-blue-500 to-cyan-400 bg-clip-text text-transparent">Evacuation Platform</span>
        </h1>

        <p class="text-lg sm:text-xl text-(--hint-text) max-w-2xl mx-auto mb-10 leading-relaxed">
          Real-time flood monitoring, emergency dispatch, and citizen guidance powered by
          <strong class="text-(--label-text)">Copernicus</strong> Earth Observation and
          <strong class="text-(--label-text)">Galileo</strong> GNSS.
        </p>

        <div class="flex flex-col sm:flex-row items-center justify-center gap-4">
          <CustomLink to="/auth">
            <Button size="lg" class="rounded-full px-8 bg-gradient-to-r from-blue-500 to-cyan-400 text-white hover:from-blue-600 hover:to-cyan-500 shadow-xl shadow-blue-500/25 border-0 h-12 text-base">
              <Icon name="mdi:shield-alert" class="h-5 w-5 mr-2" />
              Access Dashboard
            </Button>
          </CustomLink>
          <Button variant="outline" color="primary" size="lg" class="rounded-full px-8 h-12 text-base" @click="scrollToFeatures">
            <Icon name="mdi:arrow-down" class="h-5 w-5 mr-2" />
            Learn More
          </Button>
        </div>

        <div class="flex items-center justify-center gap-8 mt-12 flex-wrap">
          <div class="flex items-center gap-2 text-sm text-(--hint-text)">
            <Icon name="mdi:satellite-variant" class="h-5 w-5 text-blue-500" />
            <span>Copernicus Data</span>
          </div>
          <div class="flex items-center gap-2 text-sm text-(--hint-text)">
            <Icon name="mdi:satellite-uplink" class="h-5 w-5 text-cyan-500" />
            <span>Galileo GNSS</span>
          </div>
          <div class="flex items-center gap-2 text-sm text-(--hint-text)">
            <Icon name="mdi:map-marker-radius" class="h-5 w-5 text-green-500" />
            <span>OpenStreetMap</span>
          </div>
          <div class="flex items-center gap-2 text-sm text-(--hint-text)">
            <Icon name="mdi:cellphone" class="h-5 w-5 text-amber-500" />
            <span>Flutter Mobile</span>
          </div>
        </div>
      </div>
    </section>

    <section id="features" class="py-20 px-6">
      <div class="max-w-6xl mx-auto">
        <div class="text-center mb-16">
          <h2 class="text-3xl sm:text-4xl font-bold text-(--label-text) tracking-tight mb-4">
            Complete Flood Response Platform
          </h2>
          <p class="text-lg text-(--hint-text) max-w-2xl mx-auto">
            From satellite detection to citizen evacuation — everything emergency teams need.
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card class="p-8 hover:shadow-lg transition-all duration-300 group" hover>
            <div class="h-14 w-14 rounded-2xl bg-red-500/10 flex items-center justify-center mb-5 group-hover:scale-110 transition-transform">
              <Icon name="mdi:bell-alert" class="h-7 w-7 text-red-500" />
            </div>
            <h3 class="text-xl font-bold text-(--label-text) mb-2">{{ $t('landing.feature_alerts') }}</h3>
            <p class="text-sm text-(--hint-text) leading-relaxed">{{ $t('landing.feature_alerts_desc') }}</p>
          </Card>

          <Card class="p-8 hover:shadow-lg transition-all duration-300 group" hover>
            <div class="h-14 w-14 rounded-2xl bg-green-500/10 flex items-center justify-center mb-5 group-hover:scale-110 transition-transform">
              <Icon name="mdi:map-marker-check" class="h-7 w-7 text-green-500" />
            </div>
            <h3 class="text-xl font-bold text-(--label-text) mb-2">{{ $t('landing.feature_map') }}</h3>
            <p class="text-sm text-(--hint-text) leading-relaxed">{{ $t('landing.feature_map_desc') }}</p>
          </Card>

          <Card class="p-8 hover:shadow-lg transition-all duration-300 group" hover>
            <div class="h-14 w-14 rounded-2xl bg-blue-500/10 flex items-center justify-center mb-5 group-hover:scale-110 transition-transform">
              <Icon name="mdi:satellite-variant" class="h-7 w-7 text-blue-500" />
            </div>
            <h3 class="text-xl font-bold text-(--label-text) mb-2">{{ $t('landing.feature_satellite') }}</h3>
            <p class="text-sm text-(--hint-text) leading-relaxed">{{ $t('landing.feature_satellite_desc') }}</p>
          </Card>

          <Card class="p-8 hover:shadow-lg transition-all duration-300 group" hover>
            <div class="h-14 w-14 rounded-2xl bg-amber-500/10 flex items-center justify-center mb-5 group-hover:scale-110 transition-transform">
              <Icon name="mdi:factory" class="h-7 w-7 text-amber-500" />
            </div>
            <h3 class="text-xl font-bold text-(--label-text) mb-2">{{ $t('landing.feature_industrial') }}</h3>
            <p class="text-sm text-(--hint-text) leading-relaxed">{{ $t('landing.feature_industrial_desc') }}</p>
          </Card>
        </div>
      </div>
    </section>

    <section id="satellite" class="py-20 px-6 bg-(--surface-primary)">
      <div class="max-w-6xl mx-auto">
        <div class="text-center mb-16">
          <h2 class="text-3xl sm:text-4xl font-bold text-(--label-text) tracking-tight mb-4">
            Powered by Space Technology
          </h2>
          <p class="text-lg text-(--hint-text) max-w-2xl mx-auto">
            Leveraging the EU Space Programme for accurate flood detection and positioning.
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card class="p-6 text-center" hover>
            <div class="h-16 w-16 rounded-2xl bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center mx-auto mb-4 shadow-lg shadow-blue-500/20">
              <Icon name="mdi:satellite-variant" class="h-8 w-8 text-white" />
            </div>
            <h3 class="text-lg font-bold text-(--label-text) mb-2">Copernicus Sentinel</h3>
            <p class="text-sm text-(--hint-text)">Water level monitoring via Sentinel-1 SAR and NDWI analysis via Sentinel-2 MSI imagery.</p>
          </Card>

          <Card class="p-6 text-center" hover>
            <div class="h-16 w-16 rounded-2xl bg-gradient-to-br from-cyan-400 to-cyan-600 flex items-center justify-center mx-auto mb-4 shadow-lg shadow-cyan-500/20">
              <Icon name="mdi:satellite-uplink" class="h-8 w-8 text-white" />
            </div>
            <h3 class="text-lg font-bold text-(--label-text) mb-2">Galileo GNSS</h3>
            <p class="text-sm text-(--hint-text)">High-accuracy positioning for citizen routing and safe location guidance during evacuations.</p>
          </Card>

          <Card class="p-6 text-center" hover>
            <div class="h-16 w-16 rounded-2xl bg-gradient-to-br from-green-400 to-green-600 flex items-center justify-center mx-auto mb-4 shadow-lg shadow-green-500/20">
              <Icon name="mdi:map" class="h-8 w-8 text-white" />
            </div>
            <h3 class="text-lg font-bold text-(--label-text) mb-2">OpenStreetMap</h3>
            <p class="text-sm text-(--hint-text)">Detailed road networks and building data for evacuation routing and safe location management.</p>
          </Card>
        </div>
      </div>
    </section>

    <section id="pricing" class="py-20 px-6">
      <div class="max-w-5xl mx-auto">
        <div class="text-center mb-16">
          <h2 class="text-3xl sm:text-4xl font-bold text-(--label-text) tracking-tight mb-4">
            Plans & Pricing
          </h2>
          <p class="text-lg text-(--hint-text) max-w-2xl mx-auto">
            From municipal pilots to enterprise infrastructure operators.
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card v-for="plan in plans" :key="plan.tier" class="p-6 relative" :class="plan.tier === 'operations' ? 'ring-2 ring-blue-500 shadow-xl shadow-blue-500/10' : ''" hover>
            <div v-if="plan.tier === 'operations'" class="absolute -top-3 left-1/2 -translate-x-1/2">
              <Badge>Most Popular</Badge>
            </div>
            <h3 class="text-lg font-bold text-(--label-text) mb-2">{{ plan.name }}</h3>
            <div class="flex items-baseline gap-1 mb-6">
              <span class="text-4xl font-bold text-(--label-text)">€{{ plan.price }}</span>
              <span class="text-sm text-(--hint-text)">/month</span>
            </div>
            <ul class="space-y-2 mb-6">
              <li v-for="f in plan.features" :key="f" class="flex items-start gap-2 text-sm text-(--label-text)">
                <Icon name="mdi:check-circle" class="h-4 w-4 text-green-500 shrink-0 mt-0.5" />
                <span>{{ f }}</span>
              </li>
            </ul>
            <CustomLink to="/auth">
              <Button :variant="plan.tier === 'operations' ? 'solid' : 'outline'" color="primary" block class="rounded-full">
                Get Started
              </Button>
            </CustomLink>
          </Card>
        </div>
      </div>
    </section>

    <footer class="py-12 px-6 border-t border-(--border-color) bg-(--surface-primary)">
      <div class="max-w-6xl mx-auto">
        <div class="flex flex-col md:flex-row items-center justify-between gap-6">
          <div class="flex items-center gap-2.5">
            <div class="h-8 w-8 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-400 flex items-center justify-center">
              <Icon name="mdi:water-alert" class="h-4.5 w-4.5 text-white" />
            </div>
            <span class="font-bold text-lg tracking-tight text-(--label-text)">Hydralis</span>
          </div>
          <div class="flex items-center gap-6 text-sm text-(--hint-text)">
            <span>CASSINI Hackathon 2026</span>
            <span>•</span>
            <span>Copernicus • Galileo</span>
            <span>•</span>
            <span>Made in Galați, Romania 🇷🇴</span>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
const colorMode = useColorMode();

const changeMode = () => {
  const modes = ["light", "dark"];
  const current = modes.indexOf(colorMode.preference);
  colorMode.preference = modes[(current + 1) % modes.length]!;
};

const { plans } = useSubscription();

const scrollToFeatures = () => {
  document.getElementById("features")?.scrollIntoView({ behavior: "smooth" });
};
</script>
