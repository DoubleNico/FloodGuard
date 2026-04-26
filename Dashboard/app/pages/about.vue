<template>
  <div>
    <NavigationMenu
      class="about-nav px-6 h-16 max-w-screen fixed top-0 left-0 right-0 z-50 backdrop-blur-xl border-b border-(--nav-border)"
    >
      <template #left>
        <a href="/" class="flex items-center gap-2.5 cursor-pointer">
          <img
            src="/icon.png"
            alt="Hydralis Logo"
            class="h-8 w-8 rounded-xl shadow-lg object-cover"
          />
          <span class="font-bold text-lg tracking-tight text-(--label-text)">
            Hydralis
          </span>
        </a>
      </template>

      <div class="hidden md:block">
        <NavigationMenuList>
          <NavigationMenuItem v-for="link in navLinks" :key="link.label">
            <NavigationMenuLink
              :href="link.href"
              class="text-[13px] font-semibold px-3 py-2 text-(--label-text) hover:text-sky-500 transition-colors"
            >
              {{ link.label }}
            </NavigationMenuLink>
          </NavigationMenuItem>
        </NavigationMenuList>
      </div>

      <template #right>
        <div class="flex items-center gap-3">
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

          <CustomLink to="/auth">
            <Button
              size="sm"
              class="rounded-full px-5 cta-gradient text-white shadow-lg shadow-sky-500/25 border-0"
            >
              Access Dashboard
            </Button>
          </CustomLink>
        </div>
      </template>
    </NavigationMenu>
    <main class="about-shell min-h-screen px-6 py-20 text-(--label-text)">
      <section class="max-w-6xl mx-auto space-y-8">
        <Card class="about-hero p-7 sm:p-9" hover>
          <p
            class="text-xs font-semibold uppercase tracking-[0.12em] text-sky-500 mb-3"
          >
            About Hydralis
          </p>
          <h1
            class="about-title text-3xl sm:text-4xl font-bold tracking-tight mb-4"
          >
            Team behind the flood response platform
          </h1>
          <p
            class="text-base sm:text-lg text-(--hint-text) leading-relaxed max-w-3xl"
          >
            Hydralis started as a mission to connect satellite intelligence,
            dispatcher operations, and citizen safety into one practical command
            workflow for flood events.
          </p>
        </Card>

        <section class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
          <Card
            v-for="member in team"
            :key="member.role"
            class="team-card p-6"
            hover
          >
            <div
              class="h-12 w-12 rounded-xl flex items-center justify-center mb-4"
              :class="member.tone"
            >
              <Icon :name="member.icon" class="h-6 w-6 text-white" />
            </div>
            <p class="text-xs uppercase tracking-[0.12em] text-(--hint-text)">
              {{ member.role }}
            </p>
            <h2 class="about-title text-xl font-bold mt-2">
              {{ member.name }}
            </h2>
            <p class="text-sm text-(--hint-text) mt-3 leading-relaxed">
              {{ member.summary }}
            </p>
          </Card>
        </section>

        <section class="grid grid-cols-1 lg:grid-cols-[1.1fr_0.9fr] gap-6">
          <Card class="about-block p-7" hover>
            <h3 class="about-title text-2xl font-bold mb-4">How we build</h3>
            <div class="space-y-3">
              <p
                v-for="item in developmentNotes"
                :key="item"
                class="text-sm text-(--label-text) leading-relaxed"
              >
                {{ item }}
              </p>
            </div>
          </Card>

          <Card class="about-block p-7" hover>
            <h3 class="about-title text-2xl font-bold mb-4">Work with us</h3>
            <p class="text-sm text-(--hint-text) leading-relaxed mb-5">
              We are currently partnering with organizations that want to pilot
              and scale flood-response capabilities.
            </p>
            <div class="flex flex-col sm:flex-row gap-3">
              <CustomLink to="/contact" class="inline-flex">
                <Button color="primary" class="rounded-full px-6"
                  >Contact Team</Button
                >
              </CustomLink>
              <CustomLink to="/#pricing" class="inline-flex">
                <Button
                  variant="outline"
                  color="primary"
                  class="rounded-full px-6"
                  >View Collaboration Plans</Button
                >
              </CustomLink>
            </div>
          </Card>
        </section>
      </section>
    </main>
    <footer
      class="py-10 px-6 border-t border-(--border-color)/70 bg-(--surface-primary)/80"
    >
      <div
        class="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-5"
      >
        <div class="flex items-center gap-2.5">
          <img
            src="/icon.png"
            alt="Hydralis Logo"
            class="h-8 w-8 rounded-xl object-cover"
          />
          <span
            class="font-bold text-lg tracking-tight text-(--label-text) hero-title"
          >
            Hydralis
          </span>
        </div>

        <div
          class="flex items-center gap-3 sm:gap-5 text-xs sm:text-sm text-(--hint-text) flex-wrap justify-center"
        >
          <span>CASSINI Hackathon 2026</span>
          <span class="hidden sm:inline">|</span>
          <span>Copernicus + Galileo</span>
          <span class="hidden sm:inline">|</span>
          <span>Built in Bucharest, Romania</span>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
const colorMode = useColorMode();

const navLinks = [
  { label: "Features", href: "/#features" },
  { label: "Space Stack", href: "/#satellite" },
  { label: "Pricing", href: "/#pricing" },
  { label: "About", href: "/about" },
  { label: "Contact", href: "/contact" },
];

const changeMode = () => {
  const modes = ["light", "dark"];
  const current = modes.indexOf(colorMode.preference);
  colorMode.preference = modes[(current + 1) % modes.length]!;
};

const team = [
  {
    role: "CEO",
    name: "Gabriel Georgescu",
    icon: "mdi:account-tie",
    tone: "bg-sky-500",
    summary:
      "Leads strategic direction, partnerships, and long-term mission for Hydralis.",
  },
  {
    role: "CTO",
    name: "Tomescu Vlad",
    icon: "mdi:chip",
    tone: "bg-cyan-500",
    summary:
      "Drives architecture, platform reliability, and technical integration across the stack.",
  },
  {
    role: "CFO",
    name: "Delia Voicu",
    icon: "mdi:finance",
    tone: "bg-emerald-500",
    summary:
      "Oversees financial planning, budgeting, and sustainable delivery models.",
  },
  {
    role: "CMO",
    name: "Flavia Alexandra",
    icon: "mdi:bullhorn",
    tone: "bg-indigo-500",
    summary:
      "Shapes communication, market positioning, and stakeholder engagement strategy.",
  },
];

const developmentNotes = [
  "We iterate quickly with dispatcher and field-feedback loops instead of static assumptions.",
  "Our product direction combines Copernicus and Galileo insights with local operational realities.",
  "Each release focuses on practical emergency decisions: detect earlier, coordinate faster, evacuate safer.",
];
</script>

<style scoped>
.about-shell {
  font-family: "Manrope", "Avenir Next", "Segoe UI", sans-serif;
  background:
    radial-gradient(
      780px circle at 14% -10%,
      rgba(14, 165, 233, 0.18),
      transparent 54%
    ),
    radial-gradient(
      760px circle at 88% 0%,
      rgba(34, 211, 238, 0.16),
      transparent 52%
    ),
    linear-gradient(
      180deg,
      var(--surface-secondary) 0%,
      var(--surface-primary) 54%,
      var(--surface-secondary) 100%
    );
}

.about-nav {
  background: color-mix(in srgb, var(--nav-bg) 88%, transparent);
}

.brand-gradient {
  background-image: linear-gradient(135deg, #0ea5e9 0%, #22d3ee 100%);
}

.cta-gradient {
  background-image: linear-gradient(90deg, #0ea5e9 0%, #22d3ee 100%);
}

.cta-gradient:hover {
  background-image: linear-gradient(90deg, #0284c7 0%, #06b6d4 100%);
}

.about-title {
  font-family: "Sora", "Manrope", "Avenir Next", sans-serif;
}

.about-hero,
.team-card,
.about-block {
  border: 1px solid color-mix(in srgb, var(--border-color) 84%, transparent);
  background: color-mix(in srgb, var(--surface-primary) 90%, transparent);
}
</style>
