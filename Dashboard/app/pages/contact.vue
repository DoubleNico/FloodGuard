<template>
  <div>
    <NavigationMenu
      class="landing-nav px-6 h-16 max-w-screen fixed top-0 left-0 right-0 z-50 backdrop-blur-xl border-b border-(--nav-border)"
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
          <NavigationMenuItem v-for="link in navLinks" :key="link.id">
            <template v-if="link.href">
              <NavigationMenuLink
                :href="link.href"
                class="text-[13px] font-semibold px-3 py-2 text-(--label-text) hover:text-sky-500 transition-colors"
              >
                {{ link.label }}
              </NavigationMenuLink>
            </template>
            <template v-else>
              <NavigationMenuLink
                :href="`#${link.id}`"
                class="text-[13px] font-semibold px-3 py-2 text-(--label-text) hover:text-sky-500 transition-colors"
              >
                {{ link.label }}
              </NavigationMenuLink>
            </template>
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
    <main class="contact-shell min-h-screen px-6 py-20 text-(--label-text)">
      <section
        class="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-[0.95fr_1.05fr] gap-6 sm:gap-8"
      >
        <Card class="contact-overview p-7 sm:p-8" hover>
          <p
            class="text-xs font-semibold uppercase tracking-[0.12em] text-cyan-500 mb-3"
          >
            Contact Hydralis
          </p>
          <h1
            class="contact-title text-3xl sm:text-4xl font-bold tracking-tight mb-4"
          >
            Let us build your flood-response setup together
          </h1>
          <p
            class="text-base sm:text-lg text-(--hint-text) leading-relaxed mb-6"
          >
            Pricing and deployment are currently tailored during discovery
            calls. Share your operational context and our team will reply with a
            fitting plan.
          </p>

          <div class="space-y-3">
            <div
              v-for="item in contactHighlights"
              :key="item"
              class="contact-point flex items-start gap-3"
            >
              <Icon
                name="mdi:check-decagram"
                class="h-5 w-5 text-emerald-500 mt-0.5"
              />
              <p class="text-sm text-(--label-text) leading-relaxed">
                {{ item }}
              </p>
            </div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-7">
            <Card class="contact-mini p-4" hover>
              <p class="text-xs text-(--hint-text)">Business inquiries</p>
              <p class="font-semibold mt-1">hello@hydralis.eu</p>
            </Card>
            <Card class="contact-mini p-4" hover>
              <p class="text-xs text-(--hint-text)">Response target</p>
              <p class="font-semibold mt-1">within 1 business day</p>
            </Card>
          </div>
        </Card>

        <Card class="contact-form p-7 sm:p-8" hover>
          <h2 class="contact-title text-2xl font-bold tracking-tight mb-5">
            Tell us about your organization
          </h2>

          <form class="space-y-4" @submit.prevent="submitInquiry">
            <Input
              v-model="form.company"
              label="Company / Institution"
              :required="true"
              placeholder="e.g. Galati Emergency Authority"
            />
            <Input
              v-model="form.name"
              label="Your Name"
              :required="true"
              placeholder="e.g. Andrei Ionescu"
            />
            <Input
              v-model="form.email"
              type="email"
              label="Work Email"
              :required="true"
              placeholder="name@company.com"
            />
            <Input
              v-model="form.phone"
              label="Phone (optional)"
              placeholder="+40 ..."
            />

            <CustomSelect
              v-model="form.organizationType"
              label="Organization Type"
              :options="organizationTypes"
              :required="true"
            />

            <CustomSelect
              v-model="form.timeline"
              label="Preferred Timeline"
              :options="timelineOptions"
              :required="true"
            />

            <Textarea
              v-model="form.notes"
              label="Project Notes"
              :rows="5"
              :required="true"
              placeholder="Share flood risk context, area size, integration needs, and team size..."
            />

            <div class="pt-2 flex flex-col sm:flex-row gap-3">
              <Button
                type="submit"
                color="primary"
                class="rounded-full px-7"
                :disabled="submitting"
              >
                {{ submitting ? "Sending..." : "Send Inquiry" }}
              </Button>
              <CustomLink to="/about" class="inline-flex">
                <Button
                  variant="outline"
                  color="primary"
                  class="rounded-full px-7"
                >
                  Meet Our Team
                </Button>
              </CustomLink>
            </div>
          </form>
        </Card>
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

const form = reactive({
  company: "",
  name: "",
  email: "",
  phone: "",
  organizationType: "",
  timeline: "",
  notes: "",
});

const submitting = ref(false);

const contactHighlights = [
  "Discovery calls for municipalities, industrial operators, and emergency units.",
  "Scope-based proposal instead of fixed pricing tables.",
  "Guidance from platform, satellite, and operations leadership.",
];

const organizationTypes = [
  { label: "Municipality", value: "municipality" },
  { label: "Emergency Operations Center", value: "eoc" },
  { label: "Industrial Operator", value: "industrial" },
  { label: "Other", value: "other" },
];

const timelineOptions = [
  { label: "Immediate (0-1 month)", value: "immediate" },
  { label: "Short term (1-3 months)", value: "short-term" },
  { label: "Planning phase (3+ months)", value: "planning" },
];

const submitInquiry = async () => {
  submitting.value = true;
  await new Promise((resolve) => setTimeout(resolve, 700));
  submitting.value = false;
  alert("Thanks. Your inquiry was captured for follow-up.");
};
</script>

<style scoped>
.contact-shell {
  font-family: "Manrope", "Avenir Next", "Segoe UI", sans-serif;
  background:
    radial-gradient(
      780px circle at 10% -10%,
      rgba(14, 165, 233, 0.18),
      transparent 55%
    ),
    radial-gradient(
      760px circle at 90% 0%,
      rgba(34, 211, 238, 0.16),
      transparent 52%
    ),
    linear-gradient(
      180deg,
      var(--surface-secondary) 0%,
      var(--surface-primary) 55%,
      var(--surface-secondary) 100%
    );
}

.contact-nav {
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

.contact-title {
  font-family: "Sora", "Manrope", "Avenir Next", sans-serif;
}

.contact-overview,
.contact-form,
.contact-mini,
.contact-point {
  border: 1px solid color-mix(in srgb, var(--border-color) 84%, transparent);
  background: color-mix(in srgb, var(--surface-primary) 90%, transparent);
}
</style>
