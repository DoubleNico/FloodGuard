<template>
  <div class="landing-shell min-h-screen text-(--label-text)">
    <NavigationMenu
      class="landing-nav px-6 h-16 max-w-screen fixed top-0 left-0 right-0 z-50 backdrop-blur-xl border-b border-(--nav-border)"
    >
      <template #left>
        <a href="/" class="flex items-center gap-2.5 cursor-pointer">
          <div
            class="h-8 w-8 rounded-xl brand-gradient flex items-center justify-center shadow-lg shadow-sky-500/25"
          >
            <Icon name="mdi:water-alert" class="h-4.5 w-4.5 text-white" />
          </div>
          <span class="font-bold text-lg tracking-tight text-(--label-text)">
            Hydralis
          </span>
        </a>
      </template>

      <div class="hidden md:block">
        <NavigationMenuList>
          <NavigationMenuItem v-for="link in navLinks" :key="link.id">
            <NavigationMenuLink
              :href="`#${link.id}`"
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

    <section
      ref="heroSection"
      class="hero-zone relative pt-16 pb-16 sm:pb-20 px-6 overflow-hidden"
      @mousemove="onHeroMouseMove"
      @mouseleave="onHeroMouseLeave"
    >
      <div
        ref="heroGridContainer"
        class="hero-grid-bg absolute inset-0 overflow-hidden"
      >
        <div
          class="hero-grid-inner absolute inset-0"
          :style="{
            gridTemplateColumns: `repeat(${gridCols}, 1fr)`,
            gridTemplateRows: `repeat(${gridRows}, 1fr)`,
          }"
        >
          <div
            v-for="(cell, cellIndex) in gridCells"
            :key="cellIndex"
            class="hero-grid-cell"
            :style="{
              opacity: cell.opacity,
              backgroundColor: cell.color,
              transition: `opacity ${cell.fadeOut ? '3s' : '0.35s'} ease`,
            }"
          />
        </div>
      </div>

      <div class="hero-grid-lines pointer-events-none absolute inset-0" />

      <div
        class="hero-spotlight pointer-events-none absolute inset-0 transition-opacity"
        :class="heroMouseActive ? 'opacity-100' : 'opacity-0'"
        :style="heroGlowStyle"
      />

      <div
        class="relative z-10 max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-[1.05fr_0.95fr] gap-10 items-center"
      >
        <div>
          <div class="eyebrow reveal-up">
            <span class="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
            <span>CASSINI Hackathon | Space for Water</span>
          </div>

          <h1
            class="hero-title text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight leading-[1.08] pb-1 mt-6 reveal-up"
            style="--delay: 80ms"
          >
            Flood Early Warning
            <span class="hero-highlight">Command System</span>
          </h1>

          <p
            class="text-base sm:text-lg lg:text-xl text-(--hint-text) max-w-2xl mt-6 leading-relaxed reveal-up"
            style="--delay: 140ms"
          >
            Real-time flood monitoring, coordinated dispatch, and citizen
            routing built on
            <strong class="text-(--label-text)">Copernicus</strong>
            Earth Observation and
            <strong class="text-(--label-text)">Galileo</strong> GNSS.
          </p>

          <div
            class="flex flex-col sm:flex-row items-start sm:items-center gap-4 mt-8 reveal-up"
            style="--delay: 200ms"
          >
            <CustomLink to="/auth">
              <Button
                size="lg"
                class="rounded-full px-8 cta-gradient text-white shadow-xl shadow-sky-500/25 border-0 h-12 text-base"
              >
                <Icon name="mdi:shield-alert" class="h-5 w-5 mr-2" />
                Access Dashboard
              </Button>
            </CustomLink>

            <Button
              variant="outline"
              color="primary"
              size="lg"
              class="rounded-full px-8 h-12 text-base"
              @click="scrollToSection('features')"
            >
              <Icon name="mdi:arrow-down" class="h-5 w-5 mr-2" />
              Explore Platform
            </Button>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-8">
            <Card
              v-for="(stat, index) in quickStats"
              :key="stat.label"
              class="stat-card p-4 reveal-up"
              :style="{ '--delay': `${260 + index * 80}ms` }"
            >
              <div class="flex items-center justify-between gap-3">
                <div>
                  <p class="text-xl font-extrabold text-(--label-text)">
                    {{ stat.value }}
                  </p>
                  <p class="text-xs text-(--hint-text) mt-1">
                    {{ stat.label }}
                  </p>
                </div>
                <div
                  class="h-10 w-10 rounded-xl bg-sky-500/10 flex items-center justify-center"
                >
                  <Icon :name="stat.icon" class="h-5 w-5 text-sky-500" />
                </div>
              </div>
            </Card>
          </div>
        </div>

        <Card
          class="hero-command-card p-6 sm:p-7 relative overflow-hidden reveal-up"
          style="--delay: 160ms"
          hover
        >
          <div class="flex items-start justify-between gap-4 mb-6">
            <div>
              <p
                class="text-xs font-semibold uppercase tracking-[0.12em] text-sky-500"
              >
                Live command preview
              </p>
              <h2 class="text-2xl font-bold hero-title mt-2">
                Response Snapshot
              </h2>
            </div>
            <Badge
              class="bg-emerald-500/10 text-emerald-600 border-emerald-500/30"
            >
              Active
            </Badge>
          </div>

          <div class="mission-map mb-6">
            <svg
              class="mission-routes"
              viewBox="0 0 100 100"
              preserveAspectRatio="none"
              aria-hidden="true"
            >
              <line
                class="mission-route-main"
                x1="20"
                y1="28"
                x2="52"
                y2="58"
              />
              <line class="mission-route-alt" x1="52" y1="58" x2="85" y2="38" />
            </svg>
            <span class="mission-dot mission-dot-a" />
            <span class="mission-dot mission-dot-b" />
            <span class="mission-dot mission-dot-c" />
          </div>

          <div class="space-y-3">
            <p class="text-xs uppercase tracking-[0.14em] text-(--hint-text)">
              Live event feed
            </p>
            <div
              v-for="event in liveEvents"
              :key="event.label"
              class="event-row flex items-center justify-between gap-3"
            >
              <div class="flex items-center gap-2.5">
                <span class="event-dot" :class="event.dotClass" />
                <p class="text-sm text-(--label-text)">{{ event.label }}</p>
              </div>
              <span class="text-xs text-(--hint-text)">{{ event.time }}</span>
            </div>
          </div>
        </Card>
      </div>
    </section>

    <section class="px-6 pb-10 sm:pb-12">
      <div class="max-w-6xl mx-auto">
        <Card class="flow-strip p-5 sm:p-6 md:p-7" hover>
          <div class="flow-grid grid grid-cols-1 md:grid-cols-3 gap-4">
            <article
              v-for="(step, index) in responseFlow"
              :key="step.title"
              class="flow-step p-4 sm:p-5 reveal-up"
              :style="{ '--delay': `${120 + index * 80}ms` }"
            >
              <div class="flow-step-head flex items-center gap-3 mb-3">
                <div class="flow-number">{{ index + 1 }}</div>
                <div
                  class="flow-step-icon h-9 w-9 rounded-xl bg-sky-500/10 flex items-center justify-center"
                >
                  <Icon :name="step.icon" class="h-4.5 w-4.5 text-sky-500" />
                </div>
                <h3 class="text-lg font-bold hero-title">{{ step.title }}</h3>
              </div>
              <p
                class="flow-step-copy text-sm leading-relaxed text-(--hint-text)"
              >
                {{ step.description }}
              </p>
            </article>
          </div>
        </Card>
      </div>
    </section>

    <section id="features" class="py-16 sm:py-20 px-6">
      <div class="max-w-6xl mx-auto">
        <div class="text-center mb-12 sm:mb-14 reveal-up">
          <h2 class="hero-title text-3xl sm:text-4xl font-bold tracking-tight">
            Complete Flood Response Platform
          </h2>
          <p
            class="text-base sm:text-lg text-(--hint-text) max-w-2xl mx-auto mt-4"
          >
            One clean control layer, from first anomaly detection to safe-route
            guidance.
          </p>
        </div>

        <div
          ref="featureGridRef"
          class="grid grid-cols-1 md:grid-cols-6 gap-5"
          @mousemove="onFeatureGridMouseMove"
          @mouseleave="onFeatureGridMouseLeave"
        >
          <div
            v-for="(feature, index) in featureCards"
            :key="feature.titleKey"
            class="card-spotlight-shell reveal-up h-full"
            :class="feature.spanClass"
            :style="{ '--delay': `${100 + index * 90}ms` }"
            @mouseenter="featureHoveredIndex = index"
            @mouseleave="featureHoveredIndex = -1"
          >
            <div
              class="card-spotlight-outer"
              :class="isFeatureGridHovered ? 'opacity-100' : 'opacity-0'"
              :style="getFeatureOuterGlowStyle(index)"
            />

            <div
              class="card-spotlight-rest"
              :class="isFeatureGridHovered ? 'opacity-0' : 'opacity-100'"
            />

            <div class="card-spotlight-inner-wrap">
              <Card
                class="feature-card p-6 sm:p-7 relative overflow-hidden h-full"
                hover
              >
                <div
                  class="card-spotlight-inner"
                  :class="
                    featureHoveredIndex === index ? 'opacity-100' : 'opacity-0'
                  "
                  :style="getFeatureInnerGlowStyle(index)"
                />
                <div class="card-hover-shine" />

                <div class="relative z-10">
                  <div class="feature-icon" :class="feature.iconTone">
                    <Icon :name="feature.icon" class="h-6 w-6" />
                  </div>
                  <h3
                    class="text-xl font-bold text-(--label-text) mt-5 mb-2 hero-title"
                  >
                    {{ t(feature.titleKey) }}
                  </h3>
                  <p class="text-sm text-(--hint-text) leading-relaxed">
                    {{ t(feature.descriptionKey) }}
                  </p>
                </div>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section id="satellite" class="py-16 sm:py-20 px-6">
      <div
        class="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-[0.92fr_1.08fr] gap-6 sm:gap-8"
      >
        <Card class="p-7 sm:p-8 space-y-6 reveal-up" hover>
          <div>
            <p
              class="text-xs font-semibold uppercase tracking-[0.12em] text-cyan-500 mb-3"
            >
              Space-enabled reliability
            </p>
            <h2
              class="hero-title text-3xl sm:text-4xl font-bold tracking-tight mb-4"
            >
              Powered by the EU Space Stack
            </h2>
            <p class="text-base sm:text-lg text-(--hint-text) leading-relaxed">
              Hydralis combines satellite observation, high-precision
              positioning, and local cartography so teams can move from
              detection to evacuation with confidence.
            </p>
          </div>

          <div class="space-y-3">
            <div
              v-for="point in spacePoints"
              :key="point"
              class="space-point flex items-start gap-3"
            >
              <Icon
                name="mdi:check-decagram"
                class="h-5 w-5 text-emerald-500 mt-0.5"
              />
              <p class="text-sm text-(--label-text) leading-relaxed">
                {{ point }}
              </p>
            </div>
          </div>
        </Card>

        <div
          ref="spaceGridRef"
          class="grid grid-cols-1 sm:grid-cols-2 gap-5"
          @mousemove="onSpaceGridMouseMove"
          @mouseleave="onSpaceGridMouseLeave"
        >
          <div
            v-for="(item, index) in spaceStack"
            :key="item.title"
            class="card-spotlight-shell reveal-up h-full"
            :class="item.spanClass"
            :style="{ '--delay': `${120 + index * 80}ms` }"
            @mouseenter="spaceHoveredIndex = index"
            @mouseleave="spaceHoveredIndex = -1"
          >
            <div
              class="card-spotlight-outer"
              :class="isSpaceGridHovered ? 'opacity-100' : 'opacity-0'"
              :style="getSpaceOuterGlowStyle(index)"
            />

            <div
              class="card-spotlight-rest"
              :class="isSpaceGridHovered ? 'opacity-0' : 'opacity-100'"
            />

            <div class="card-spotlight-inner-wrap">
              <Card class="p-6 relative overflow-hidden h-full" hover>
                <div
                  class="card-spotlight-inner"
                  :class="
                    spaceHoveredIndex === index ? 'opacity-100' : 'opacity-0'
                  "
                  :style="getSpaceInnerGlowStyle(index)"
                />
                <div class="card-hover-shine" />

                <div class="relative z-10">
                  <div
                    class="h-14 w-14 rounded-2xl flex items-center justify-center shadow-lg mb-4"
                    :class="[item.gradientClass, item.shadowClass]"
                  >
                    <Icon :name="item.icon" class="h-7 w-7 text-white" />
                  </div>
                  <h3
                    class="text-lg font-bold text-(--label-text) mb-2 hero-title"
                  >
                    {{ item.title }}
                  </h3>
                  <p class="text-sm text-(--hint-text) leading-relaxed">
                    {{ item.description }}
                  </p>
                </div>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section id="pricing" class="py-16 sm:py-20 px-6">
      <div class="max-w-5xl mx-auto">
        <div class="text-center mb-12 sm:mb-14 reveal-up">
          <h2 class="hero-title text-3xl sm:text-4xl font-bold tracking-tight">
            Plans & Pricing
          </h2>
          <p
            class="text-base sm:text-lg text-(--hint-text) max-w-2xl mx-auto mt-4"
          >
            Flexible for municipalities, emergency operations centers, and
            infrastructure operators.
          </p>
        </div>

        <div
          ref="pricingGridRef"
          class="grid grid-cols-1 md:grid-cols-3 gap-6"
          @mousemove="onPricingGridMouseMove"
          @mouseleave="onPricingGridMouseLeave"
        >
          <div
            v-for="(plan, index) in plans"
            :key="plan.tier"
            class="card-spotlight-shell reveal-up h-full"
            :class="
              plan.tier === 'operations'
                ? 'ring-2 ring-sky-500 shadow-2xl shadow-sky-500/15'
                : ''
            "
            :style="{ '--delay': `${120 + index * 90}ms` }"
            @mouseenter="pricingHoveredIndex = index"
            @mouseleave="pricingHoveredIndex = -1"
          >
            <div
              class="card-spotlight-outer"
              :class="isPricingGridHovered ? 'opacity-100' : 'opacity-0'"
              :style="getPricingOuterGlowStyle(index)"
            />

            <div
              class="card-spotlight-rest"
              :class="isPricingGridHovered ? 'opacity-0' : 'opacity-100'"
            />

            <div class="card-spotlight-inner-wrap">
              <Card
                class="pricing-card p-6 relative overflow-hidden flex flex-col h-full"
                hover
              >
                <div
                  class="card-spotlight-inner"
                  :class="
                    pricingHoveredIndex === index ? 'opacity-100' : 'opacity-0'
                  "
                  :style="getPricingInnerGlowStyle(index)"
                />
                <div class="card-hover-shine" />

                <div
                  v-if="plan.tier === 'operations'"
                  class="absolute -top-1 left-1/2 -translate-x-1/2 z-20"
                >
                  <Badge class="bg-sky-500 text-white border-sky-400"
                    >Most Popular</Badge
                  >
                </div>

                <div class="relative z-10 flex flex-col h-full">
                  <h3
                    class="text-lg font-bold text-(--label-text) mb-2 hero-title"
                  >
                    {{ plan.name }}
                  </h3>

                  <div class="flex items-baseline gap-1 mb-6">
                    <span class="text-4xl font-extrabold text-(--label-text)">
                      EUR {{ plan.price }}
                    </span>
                    <span class="text-sm text-(--hint-text)">/month</span>
                  </div>

                  <ul class="space-y-2.5 mb-6 flex-1">
                    <li
                      v-for="feature in plan.features"
                      :key="feature"
                      class="flex items-start gap-2 text-sm text-(--label-text)"
                    >
                      <Icon
                        name="mdi:check-circle"
                        class="h-4.5 w-4.5 text-emerald-500 shrink-0 mt-0.5"
                      />
                      <span>{{ feature }}</span>
                    </li>
                  </ul>

                  <CustomLink to="/auth" class="mt-auto block">
                    <Button
                      :variant="
                        plan.tier === 'operations' ? 'solid' : 'outline'
                      "
                      color="primary"
                      block
                      class="rounded-full"
                    >
                      Get Started
                    </Button>
                  </CustomLink>
                </div>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </section>

    <footer
      class="py-10 px-6 border-t border-(--border-color)/70 bg-(--surface-primary)/80"
    >
      <div
        class="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-5"
      >
        <div class="flex items-center gap-2.5">
          <div
            class="h-8 w-8 rounded-xl brand-gradient flex items-center justify-center"
          >
            <Icon name="mdi:water-alert" class="h-4.5 w-4.5 text-white" />
          </div>
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
const { t } = useI18n();
const { plans } = useSubscription();

const heroSection = ref<HTMLElement | null>(null);
const heroGridContainer = ref<HTMLElement | null>(null);

const featureGridRef = ref<HTMLElement | null>(null);
const spaceGridRef = ref<HTMLElement | null>(null);
const pricingGridRef = ref<HTMLElement | null>(null);

interface CardMousePosition {
  x: number;
  y: number;
}

const featureHoveredIndex = ref(-1);
const spaceHoveredIndex = ref(-1);
const pricingHoveredIndex = ref(-1);

const isFeatureGridHovered = computed(() => featureHoveredIndex.value !== -1);
const isSpaceGridHovered = computed(() => spaceHoveredIndex.value !== -1);
const isPricingGridHovered = computed(() => pricingHoveredIndex.value !== -1);

const featureCardPositions = ref<CardMousePosition[]>([]);
const spaceCardPositions = ref<CardMousePosition[]>([]);
const pricingCardPositions = ref<CardMousePosition[]>([]);

const CARD_GLOW_SMOOTHING = 0.14;

const GRID_CELL_SIZE = 96;
const gridCols = ref(1);
const gridRows = ref(1);

interface GridCell {
  opacity: number;
  color: string;
  fadeOut: boolean;
}

const gridCells = ref<GridCell[]>([]);
const lastHoverCell = ref<number | null>(null);

const heroMouseActive = ref(false);
const heroMouseX = ref(0);
const heroMouseY = ref(0);

const heroGlowStyle = computed(() => ({
  background: `
    radial-gradient(760px circle at ${heroMouseX.value}px ${heroMouseY.value}px,
      color-mix(in srgb, var(--color-primary) 7%, transparent),
      transparent 72%),
    radial-gradient(360px circle at ${heroMouseX.value}px ${heroMouseY.value}px,
      color-mix(in srgb, var(--color-secondary) 5%, transparent),
      transparent 68%)
  `,
}));

const computeHeroGrid = () => {
  const width = heroSection.value?.clientWidth ?? window.innerWidth;
  const height =
    heroSection.value?.clientHeight ?? Math.round(window.innerHeight * 0.8);

  gridCols.value = Math.max(1, Math.ceil(width / GRID_CELL_SIZE));
  gridRows.value = Math.max(1, Math.ceil(height / GRID_CELL_SIZE));

  const total = gridCols.value * gridRows.value;
  gridCells.value = Array.from({ length: total }, () => ({
    opacity: 0,
    color: "var(--color-primary)",
    fadeOut: false,
  }));
};

const onGridMouseMove = (event: MouseEvent) => {
  if (!heroGridContainer.value) return;

  const rect = heroGridContainer.value.getBoundingClientRect();
  const x = event.clientX - rect.left;
  const y = event.clientY - rect.top;
  const col = Math.floor(x / GRID_CELL_SIZE);
  const row = Math.floor(y / GRID_CELL_SIZE);
  const cellIndex = row * gridCols.value + col;

  if (lastHoverCell.value === cellIndex) return;
  lastHoverCell.value = cellIndex;

  const rippleRadius = 2;

  for (let rowOffset = -rippleRadius; rowOffset <= rippleRadius; rowOffset++) {
    for (
      let colOffset = -rippleRadius;
      colOffset <= rippleRadius;
      colOffset++
    ) {
      const targetRow = row + rowOffset;
      const targetCol = col + colOffset;

      if (
        targetRow < 0 ||
        targetRow >= gridRows.value ||
        targetCol < 0 ||
        targetCol >= gridCols.value
      ) {
        continue;
      }

      const distance = Math.sqrt(rowOffset * rowOffset + colOffset * colOffset);
      if (distance > rippleRadius) continue;

      const targetIndex = targetRow * gridCols.value + targetCol;
      const targetCell = gridCells.value[targetIndex];
      if (!targetCell) continue;

      const intensity = Math.max(0, 1 - distance / rippleRadius);
      targetCell.opacity = intensity * 0.08;
      targetCell.color =
        (targetRow + targetCol) % 2 === 0
          ? "var(--color-primary)"
          : "var(--color-secondary)";
      targetCell.fadeOut = false;

      const delay = distance * 140;
      setTimeout(() => {
        targetCell.fadeOut = true;
        targetCell.opacity = 0;
      }, 240 + delay);
    }
  }
};

const onHeroMouseMove = (event: MouseEvent) => {
  if (!heroSection.value) return;

  const rect = heroSection.value.getBoundingClientRect();
  heroMouseX.value = event.clientX - rect.left;
  heroMouseY.value = event.clientY - rect.top;
  heroMouseActive.value = true;

  onGridMouseMove(event);
};

const onHeroMouseLeave = () => {
  heroMouseActive.value = false;
  lastHoverCell.value = null;
};

const updateGridMousePositions = (
  event: MouseEvent,
  gridElement: HTMLElement | null,
  positions: { value: CardMousePosition[] },
) => {
  if (!gridElement) return;

  const cards = Array.from(gridElement.children) as HTMLElement[];
  const nextPositions = cards.map((card) => {
    const rect = card.getBoundingClientRect();
    return {
      x: event.clientX - rect.left,
      y: event.clientY - rect.top,
    };
  });

  if (positions.value.length !== nextPositions.length) {
    positions.value = nextPositions;
    return;
  }

  const currentPositions = positions.value;
  positions.value = nextPositions.map((next, index) => {
    const current = currentPositions[index] ?? next;
    return {
      x: current.x + (next.x - current.x) * CARD_GLOW_SMOOTHING,
      y: current.y + (next.y - current.y) * CARD_GLOW_SMOOTHING,
    };
  });
};

const getSpotlightOuterStyle = (
  positions: CardMousePosition[],
  index: number,
  tone: "blue" | "teal" | "cyan",
) => {
  const position = positions[index];
  if (!position) return {};

  const tones = {
    blue: "radial-gradient(320px circle at __X__px __Y__px, rgba(14, 165, 233, 0.32), rgba(59, 130, 246, 0.16), transparent 76%)",
    teal: "radial-gradient(320px circle at __X__px __Y__px, rgba(20, 184, 166, 0.3), rgba(34, 211, 238, 0.15), transparent 76%)",
    cyan: "radial-gradient(320px circle at __X__px __Y__px, rgba(56, 189, 248, 0.3), rgba(6, 182, 212, 0.15), transparent 76%)",
  };

  return {
    background: tones[tone]
      .replace("__X__", String(position.x))
      .replace("__Y__", String(position.y)),
  };
};

const getSpotlightInnerStyle = (
  positions: CardMousePosition[],
  index: number,
  tone: "blue" | "teal" | "cyan",
) => {
  const position = positions[index];
  if (!position) return {};

  const tones = {
    blue: "radial-gradient(420px circle at __X__px __Y__px, rgba(14, 165, 233, 0.11), rgba(59, 130, 246, 0.06), transparent 78%)",
    teal: "radial-gradient(420px circle at __X__px __Y__px, rgba(20, 184, 166, 0.1), rgba(34, 211, 238, 0.06), transparent 78%)",
    cyan: "radial-gradient(420px circle at __X__px __Y__px, rgba(56, 189, 248, 0.11), rgba(6, 182, 212, 0.06), transparent 78%)",
  };

  return {
    background: tones[tone]
      .replace("__X__", String(position.x))
      .replace("__Y__", String(position.y)),
  };
};

const getFeatureOuterGlowStyle = (index: number) =>
  getSpotlightOuterStyle(featureCardPositions.value, index, "blue");

const getFeatureInnerGlowStyle = (index: number) =>
  getSpotlightInnerStyle(featureCardPositions.value, index, "blue");

const getSpaceOuterGlowStyle = (index: number) =>
  getSpotlightOuterStyle(spaceCardPositions.value, index, "teal");

const getSpaceInnerGlowStyle = (index: number) =>
  getSpotlightInnerStyle(spaceCardPositions.value, index, "teal");

const getPricingOuterGlowStyle = (index: number) =>
  getSpotlightOuterStyle(pricingCardPositions.value, index, "cyan");

const getPricingInnerGlowStyle = (index: number) =>
  getSpotlightInnerStyle(pricingCardPositions.value, index, "cyan");

const onFeatureGridMouseMove = (event: MouseEvent) => {
  updateGridMousePositions(event, featureGridRef.value, featureCardPositions);
};

const onFeatureGridMouseLeave = () => {
  featureHoveredIndex.value = -1;
};

const onSpaceGridMouseMove = (event: MouseEvent) => {
  updateGridMousePositions(event, spaceGridRef.value, spaceCardPositions);
};

const onSpaceGridMouseLeave = () => {
  spaceHoveredIndex.value = -1;
};

const onPricingGridMouseMove = (event: MouseEvent) => {
  updateGridMousePositions(event, pricingGridRef.value, pricingCardPositions);
};

const onPricingGridMouseLeave = () => {
  pricingHoveredIndex.value = -1;
};

const navLinks = [
  { id: "features", label: "Features" },
  { id: "satellite", label: "Space Stack" },
  { id: "pricing", label: "Pricing" },
];

const quickStats = [
  { value: "<4 min", label: "Alert latency", icon: "mdi:clock-fast" },
  { value: "24/7", label: "Command readiness", icon: "mdi:shield-check" },
  { value: "EU", label: "Space-powered coverage", icon: "mdi:earth" },
];

const liveEvents = [
  {
    label: "Siret river threshold exceeded",
    time: "2m ago",
    dotClass: "bg-rose-500",
  },
  {
    label: "Safe route refreshed for district north",
    time: "5m ago",
    dotClass: "bg-cyan-500",
  },
  {
    label: "Industrial sensor cluster synced",
    time: "9m ago",
    dotClass: "bg-emerald-500",
  },
];

const responseFlow = [
  {
    title: "Detect",
    description:
      "Sentinel imagery and IoT river sensors surface anomalies before critical flooding.",
    icon: "mdi:satellite-variant",
  },
  {
    title: "Coordinate",
    description:
      "Emergency teams align alerts, priorities, and dispatch decisions from one command view.",
    icon: "mdi:account-group",
  },
  {
    title: "Evacuate",
    description:
      "Citizens receive routing to safe locations with Galileo-powered geolocation.",
    icon: "mdi:map-marker-path",
  },
];

const featureCards = [
  {
    titleKey: "landing.feature_alerts",
    descriptionKey: "landing.feature_alerts_desc",
    icon: "mdi:bell-alert",
    spanClass: "md:col-span-3",
    iconTone: "text-rose-500 bg-rose-500/12",
  },
  {
    titleKey: "landing.feature_map",
    descriptionKey: "landing.feature_map_desc",
    icon: "mdi:map-marker-check",
    spanClass: "md:col-span-3",
    iconTone: "text-emerald-500 bg-emerald-500/12",
  },
  {
    titleKey: "landing.feature_satellite",
    descriptionKey: "landing.feature_satellite_desc",
    icon: "mdi:satellite-variant",
    spanClass: "md:col-span-4",
    iconTone: "text-sky-500 bg-sky-500/12",
  },
  {
    titleKey: "landing.feature_industrial",
    descriptionKey: "landing.feature_industrial_desc",
    icon: "mdi:factory",
    spanClass: "md:col-span-2",
    iconTone: "text-amber-500 bg-amber-500/12",
  },
];

const spacePoints = [
  "Sentinel-1 SAR for flood contour detection during cloud cover.",
  "Sentinel-2 MSI for NDWI-based water body classification.",
  "Galileo GNSS for high-confidence citizen guidance and dispatch tracking.",
];

const spaceStack = [
  {
    title: "Copernicus Sentinel",
    description:
      "Continuous EO data for flood surveillance, trend analysis, and anomaly detection.",
    icon: "mdi:satellite-variant",
    gradientClass: "stack-gradient-sentinel",
    shadowClass: "shadow-sky-500/20",
    spanClass: "",
  },
  {
    title: "Galileo GNSS",
    description:
      "Accurate geolocation for routing vulnerable citizens and field responders safely.",
    icon: "mdi:satellite-uplink",
    gradientClass: "stack-gradient-galileo",
    shadowClass: "shadow-cyan-500/25",
    spanClass: "",
  },
  {
    title: "OpenStreetMap",
    description:
      "Detailed street and building context for evacuation corridors and safe zones.",
    icon: "mdi:map",
    gradientClass: "stack-gradient-osm",
    shadowClass: "shadow-emerald-500/20",
    spanClass: "sm:col-span-2",
  },
];

const changeMode = () => {
  const modes = ["light", "dark"];
  const current = modes.indexOf(colorMode.preference);
  colorMode.preference = modes[(current + 1) % modes.length]!;
};

const scrollToSection = (sectionId: string) => {
  document.getElementById(sectionId)?.scrollIntoView({ behavior: "smooth" });
};

onMounted(() => {
  requestAnimationFrame(() => {
    computeHeroGrid();
  });

  window.addEventListener("resize", computeHeroGrid);
});

onUnmounted(() => {
  window.removeEventListener("resize", computeHeroGrid);
});
</script>

<style>
.hero-zone {
  isolation: isolate;
}

.hero-grid-bg {
  z-index: 0;
  pointer-events: none;
}

.hero-grid-inner {
  display: grid;
}

.hero-grid-cell {
  opacity: 0;
  will-change: opacity;
}

.hero-grid-lines {
  z-index: 1;
  background-image:
    linear-gradient(
      color-mix(in srgb, var(--hint-text) 14%, transparent) 1px,
      transparent 1px
    ),
    linear-gradient(
      90deg,
      color-mix(in srgb, var(--hint-text) 14%, transparent) 1px,
      transparent 1px
    );
  background-size: 96px 96px;
  opacity: 0.34;
  mask-image: linear-gradient(180deg, black 0%, black 70%, transparent 100%);
}

.hero-spotlight {
  z-index: 2;
  transition: opacity 1.2s ease;
}

.card-spotlight-shell {
  position: relative;
  border-radius: 1rem;
  overflow: hidden;
}

.card-spotlight-shell::before {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: inherit;
  pointer-events: none;
  box-shadow: 0 22px 40px -34px rgba(2, 132, 199, 0.46);
  opacity: 0;
  transition: opacity 780ms cubic-bezier(0.16, 1, 0.3, 1);
}

.card-spotlight-shell:hover::before {
  opacity: 1;
}

.card-spotlight-outer {
  position: absolute;
  inset: 0;
  border-radius: inherit;
  transition:
    opacity 620ms cubic-bezier(0.16, 1, 0.3, 1),
    background 460ms ease-out;
}

.card-spotlight-rest {
  position: absolute;
  inset: 0;
  border-radius: inherit;
  border: 1px solid color-mix(in srgb, var(--border-color) 76%, transparent);
  transition: opacity 520ms ease;
}

.card-spotlight-inner-wrap {
  position: relative;
  margin: 1px;
  border-radius: calc(1rem - 1px);
  height: calc(100% - 2px);
  overflow: hidden;
}

.card-spotlight-inner {
  pointer-events: none;
  position: absolute;
  inset: 0;
  border-radius: inherit;
  opacity: 0;
  transition:
    opacity 700ms cubic-bezier(0.16, 1, 0.3, 1),
    background 500ms ease-out;
}

.card-hover-shine {
  pointer-events: none;
  position: absolute;
  inset: 0;
  transform: translateX(-120%);
  background: linear-gradient(
    100deg,
    transparent 0%,
    rgba(255, 255, 255, 0.05) 42%,
    rgba(255, 255, 255, 0.025) 52%,
    transparent 70%
  );
  transition: transform 1450ms cubic-bezier(0.16, 1, 0.3, 1);
}

.card-spotlight-shell:hover .card-hover-shine {
  transform: translateX(120%);
}

.landing-shell {
  position: relative;
  overflow-x: clip;
  font-family: "Manrope", "Avenir Next", "Segoe UI", sans-serif;
  background:
    radial-gradient(
      900px circle at 12% -10%,
      rgba(14, 165, 233, 0.2),
      transparent 56%
    ),
    radial-gradient(
      780px circle at 88% 0%,
      rgba(34, 211, 238, 0.2),
      transparent 52%
    ),
    linear-gradient(
      180deg,
      var(--surface-secondary) 0%,
      var(--surface-primary) 48%,
      var(--surface-secondary) 100%
    );
}

.landing-shell::before {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background-image:
    linear-gradient(rgba(148, 163, 184, 0.1) 1px, transparent 1px),
    linear-gradient(90deg, rgba(148, 163, 184, 0.1) 1px, transparent 1px);
  background-size: 36px 36px;
  mask-image: radial-gradient(circle at 50% 12%, black 24%, transparent 74%);
}

.dark .landing-shell {
  background:
    radial-gradient(
      920px circle at 12% -10%,
      rgba(56, 189, 248, 0.28),
      transparent 56%
    ),
    radial-gradient(
      780px circle at 88% 0%,
      rgba(45, 212, 191, 0.24),
      transparent 52%
    ),
    linear-gradient(
      180deg,
      #111827 0%,
      var(--surface-primary) 45%,
      #101420 100%
    );
}

.dark .landing-shell::before {
  background-image:
    linear-gradient(rgba(148, 163, 184, 0.16) 1px, transparent 1px),
    linear-gradient(90deg, rgba(148, 163, 184, 0.16) 1px, transparent 1px);
}

.landing-nav {
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

.stack-gradient-sentinel {
  background-image: linear-gradient(135deg, #0ea5e9 0%, #1d4ed8 100%);
}

.stack-gradient-galileo {
  background-image: linear-gradient(135deg, #22d3ee 0%, #0891b2 100%);
}

.stack-gradient-osm {
  background-image: linear-gradient(135deg, #34d399 0%, #059669 100%);
}

.hero-title {
  font-family: "Sora", "Manrope", "Avenir Next", sans-serif;
}

.hero-highlight {
  display: block;
  margin-top: 0.2em;
  width: fit-content;
  background-image: linear-gradient(
    90deg,
    #0284c7 0%,
    #06b6d4 55%,
    #0d9488 100%
  );
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.eyebrow {
  width: fit-content;
  display: inline-flex;
  align-items: center;
  gap: 0.55rem;
  padding: 0.55rem 0.95rem;
  border-radius: 999px;
  border: 1px solid color-mix(in srgb, var(--border-color) 76%, transparent);
  background: color-mix(in srgb, var(--surface-primary) 84%, transparent);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.hero-command-card {
  border: 1px solid color-mix(in srgb, var(--border-color) 82%, transparent);
  background: linear-gradient(
    145deg,
    color-mix(in srgb, var(--surface-primary) 92%, #ffffff 8%) 0%,
    color-mix(in srgb, var(--surface-primary) 96%, transparent) 100%
  );
  box-shadow: 0 22px 60px -34px rgba(2, 132, 199, 0.34);
}

.mission-map {
  position: relative;
  height: 220px;
  border-radius: 1rem;
  border: 1px dashed color-mix(in srgb, var(--border-color) 86%, transparent);
  background:
    radial-gradient(
      circle at 18% 75%,
      rgba(14, 165, 233, 0.2) 0%,
      transparent 32%
    ),
    radial-gradient(
      circle at 78% 30%,
      rgba(20, 184, 166, 0.2) 0%,
      transparent 36%
    ),
    linear-gradient(
      130deg,
      color-mix(in srgb, var(--surface-secondary) 70%, transparent) 0%,
      var(--surface-primary) 100%
    );
}

.mission-dot {
  position: absolute;
  z-index: 2;
  height: 0.85rem;
  width: 0.85rem;
  border-radius: 999px;
  box-shadow: 0 0 0 4px rgba(2, 132, 199, 0.14);
}

.mission-dot-a {
  top: 24%;
  left: 16%;
  background: #0ea5e9;
}

.mission-dot-b {
  top: 55%;
  left: 49%;
  background: #22d3ee;
}

.mission-dot-c {
  top: 35%;
  right: 16%;
  background: #14b8a6;
}

.mission-routes {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}

.mission-routes line {
  fill: none;
  stroke-width: 1.3;
  stroke-linecap: round;
  stroke-dasharray: 3.6 3.6;
}

.mission-route-main {
  stroke: rgba(56, 189, 248, 0.68);
  animation: route-dash 6s linear infinite;
}

.mission-route-alt {
  stroke: rgba(45, 212, 191, 0.62);
  animation: route-dash 7s linear infinite reverse;
}

@keyframes route-dash {
  to {
    stroke-dashoffset: -45;
  }
}

.event-row {
  border: 1px solid color-mix(in srgb, var(--border-color) 84%, transparent);
  border-radius: 0.85rem;
  padding: 0.65rem 0.85rem;
  background: color-mix(in srgb, var(--surface-primary) 90%, transparent);
}

.event-dot {
  height: 0.48rem;
  width: 0.48rem;
  border-radius: 999px;
}

.flow-strip {
  border: 1px solid color-mix(in srgb, var(--border-color) 84%, transparent);
  background: linear-gradient(
    130deg,
    color-mix(in srgb, var(--surface-primary) 96%, #ffffff 4%) 0%,
    color-mix(in srgb, var(--surface-secondary) 94%, transparent) 100%
  );
}

.flow-grid {
  position: relative;
}

.flow-step {
  position: relative;
  overflow: hidden;
  isolation: isolate;
  border-radius: 1rem;
  border: 1px solid color-mix(in srgb, var(--border-color) 84%, transparent);
  background: color-mix(in srgb, var(--surface-primary) 88%, transparent);
  transition:
    transform 450ms cubic-bezier(0.16, 1, 0.3, 1),
    box-shadow 450ms cubic-bezier(0.16, 1, 0.3, 1),
    border-color 450ms ease;
}

.flow-step::before,
.flow-step::after {
  content: "";
  position: absolute;
  pointer-events: none;
  transition:
    opacity 700ms ease,
    transform 900ms cubic-bezier(0.16, 1, 0.3, 1);
}

.flow-step::before {
  top: -3.6rem;
  right: -3rem;
  width: 9.4rem;
  height: 9.4rem;
  border-radius: 999px;
  opacity: 0.26;
  transform: scale(0.86);
}

.flow-step::after {
  left: -2.4rem;
  bottom: -4.2rem;
  width: 7.8rem;
  height: 7.8rem;
  border-radius: 999px;
  opacity: 0.14;
}

.flow-step:nth-child(1)::before {
  background: radial-gradient(
    circle,
    rgba(14, 165, 233, 0.34),
    transparent 72%
  );
}

.flow-step:nth-child(2)::before {
  background: radial-gradient(
    circle,
    rgba(34, 211, 238, 0.34),
    transparent 72%
  );
}

.flow-step:nth-child(3)::before {
  background: radial-gradient(
    circle,
    rgba(16, 185, 129, 0.34),
    transparent 72%
  );
}

.flow-step:nth-child(1)::after {
  background: radial-gradient(
    circle,
    rgba(56, 189, 248, 0.26),
    transparent 70%
  );
}

.flow-step:nth-child(2)::after {
  background: radial-gradient(
    circle,
    rgba(45, 212, 191, 0.24),
    transparent 70%
  );
}

.flow-step:nth-child(3)::after {
  background: radial-gradient(
    circle,
    rgba(52, 211, 153, 0.24),
    transparent 70%
  );
}

.flow-step:hover {
  transform: translateY(-6px);
  border-color: color-mix(
    in srgb,
    var(--color-primary) 42%,
    var(--border-color)
  );
  box-shadow: 0 24px 45px -34px rgba(2, 132, 199, 0.48);
}

.flow-step:hover::before {
  opacity: 0.42;
  transform: scale(1.08);
}

.flow-step:hover::after {
  opacity: 0.24;
  transform: translateY(-0.35rem);
}

.flow-step-head,
.flow-step-copy {
  position: relative;
  z-index: 1;
}

.flow-step-icon {
  transition:
    transform 420ms cubic-bezier(0.16, 1, 0.3, 1),
    box-shadow 420ms ease;
  animation: flow-icon-drift 4.4s ease-in-out infinite;
}

.flow-step:nth-child(2) .flow-step-icon {
  animation-delay: 360ms;
}

.flow-step:nth-child(3) .flow-step-icon {
  animation-delay: 720ms;
}

.flow-step:hover .flow-step-icon {
  transform: translateY(-2px) scale(1.05) rotate(-3deg);
  box-shadow: 0 12px 22px -18px rgba(2, 132, 199, 0.75);
}

.flow-number {
  display: grid;
  place-items: center;
  position: relative;
  z-index: 1;
  width: 1.85rem;
  height: 1.85rem;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 700;
  color: #0f172a;
  background: linear-gradient(145deg, #7dd3fc 0%, #22d3ee 100%);
  box-shadow: 0 8px 20px -16px rgba(14, 116, 144, 0.9);
  transition:
    transform 450ms cubic-bezier(0.16, 1, 0.3, 1),
    box-shadow 450ms ease;
}

.flow-step:nth-child(1) .flow-number {
  background: linear-gradient(145deg, #7dd3fc 0%, #38bdf8 100%);
}

.flow-step:nth-child(2) .flow-number {
  background: linear-gradient(145deg, #67e8f9 0%, #2dd4bf 100%);
}

.flow-step:nth-child(3) .flow-number {
  background: linear-gradient(145deg, #86efac 0%, #34d399 100%);
}

.flow-step:hover .flow-number {
  transform: scale(1.1) rotate(-10deg);
  box-shadow: 0 12px 24px -15px rgba(14, 116, 144, 0.95);
}

@keyframes flow-icon-drift {
  0%,
  100% {
    transform: translateY(0);
  }

  50% {
    transform: translateY(-2px);
  }
}

.feature-card {
  border: 1px solid color-mix(in srgb, var(--border-color) 84%, transparent);
  background: color-mix(in srgb, var(--surface-primary) 92%, transparent);
  transition:
    transform 280ms ease,
    box-shadow 280ms ease;
}

.card-spotlight-shell:hover .feature-card {
  transform: translateY(-4px);
  box-shadow: 0 20px 34px -28px rgba(2, 132, 199, 0.44);
}

.feature-icon {
  height: 3rem;
  width: 3rem;
  border-radius: 0.95rem;
  display: grid;
  place-items: center;
}

.stat-card,
.pricing-card,
.space-point {
  border: 1px solid color-mix(in srgb, var(--border-color) 84%, transparent);
  background: color-mix(in srgb, var(--surface-primary) 90%, transparent);
}

.pricing-card {
  transition:
    transform 280ms ease,
    box-shadow 280ms ease;
}

.card-spotlight-shell:hover .pricing-card {
  transform: translateY(-4px);
}

.reveal-up {
  opacity: 0;
  transform: translateY(16px);
  animation: reveal-up 700ms cubic-bezier(0.22, 1, 0.36, 1) forwards;
  animation-delay: var(--delay, 0ms);
}

@keyframes reveal-up {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 640px) {
  .hero-highlight {
    width: 100%;
  }

  .mission-map {
    height: 185px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .reveal-up {
    opacity: 1;
    transform: none;
    animation: none;
  }

  .feature-card,
  .pricing-card {
    transition: none;
  }

  .flow-step,
  .flow-step-icon,
  .flow-number {
    transition: none;
    animation: none;
  }

  .flow-step::before,
  .flow-step::after {
    transition: none;
    animation: none;
  }

  .card-hover-shine {
    transition: none;
    transform: none;
  }

  .card-spotlight-shell:hover .feature-card,
  .card-spotlight-shell:hover .pricing-card {
    transform: none;
    box-shadow: none;
  }

  .flow-step:hover,
  .flow-step:hover .flow-number,
  .flow-step:hover .flow-step-icon {
    transform: none;
    box-shadow: none;
  }
}
</style>
