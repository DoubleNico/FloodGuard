<template>
  <div
    class="flex flex-col gap-3 p-3 w-full rounded-[20px] bg-(--surface-primary) border border-(--border-color) shadow-(--shadow-apple) select-none transition-transform"
  >
    <div
      ref="sbAreaRef"
      class="relative h-40 w-full rounded-xl cursor-crosshair overflow-hidden ring-1 ring-black/5 touch-none"
      :style="{ backgroundColor: `hsl(${hsv.h}, 100%, 50%)` }"
      @mousedown="startSbDrag"
      @touchstart.prevent.stop="startSbDrag"
    >
      <div
        class="absolute inset-0 bg-linear-to-r from-white to-transparent pointer-events-none"
      />
      <div
        class="absolute inset-0 bg-linear-to-t from-black to-transparent pointer-events-none"
      />

      <div
        class="absolute w-4 h-4 rounded-full border-2 border-white shadow-sm -translate-x-1/2 -translate-y-1/2 pointer-events-none will-change-[left,top]"
        :style="{
          left: `${hsv.s * 100}%`,
          top: `${(1 - hsv.v) * 100}%`,
          backgroundColor: currentColorCss,
        }"
      />
    </div>

    <div class="flex items-center gap-3">
      <Button
        v-if="isSupported"
        variant="ghost"
        size="sm"
        rounded="full"
        class="p-0! w-8 h-8 shrink-0 text-(--hint-text) hover:border-(--border-color) border border-transparent"
        title="Pick color from screen"
        @click="open()"
      >
        <Icon name="mdi:eyedropper" class="w-4 h-4" />
      </Button>

      <div class="flex-1 flex flex-col gap-1 min-w-0">
        <div
          ref="hueSliderRef"
          class="relative h-8 w-full flex items-center cursor-pointer touch-none select-none group"
          @mousedown="startHueDrag"
          @touchstart.prevent.stop="startHueDrag"
        >
          <div
            class="w-full h-3 rounded-full shadow-inner pointer-events-none"
            style="
              background: linear-gradient(
                to right,
                #f00 0%,
                #ff0 17%,
                #0f0 33%,
                #0ff 50%,
                #00f 67%,
                #f0f 83%,
                #f00 100%
              );
            "
          />
          <div
            class="absolute top-1/2 -translate-y-1/2 w-4 h-4 bg-white rounded-full shadow-md border border-black/10 -translate-x-1/2 pointer-events-none will-change-[left]"
            :style="{ left: `${(hsv.h / 360) * 100}%` }"
          />
        </div>

        <div
          ref="alphaSliderRef"
          class="relative h-8 w-full flex items-center cursor-pointer touch-none select-none group"
          @mousedown="startAlphaDrag"
          @touchstart.prevent.stop="startAlphaDrag"
        >
          <div
            class="relative w-full h-3 rounded-full bg-[url('/checkboard.png')] shadow-inner overflow-hidden pointer-events-none"
          >
            <div
              class="absolute inset-0 w-full h-full"
              :style="{
                background: `linear-gradient(to right, transparent, ${colorNoAlpha})`,
              }"
            />
          </div>
          <div
            class="absolute top-1/2 -translate-y-1/2 w-4 h-4 bg-white rounded-full shadow-md border border-black/10 -translate-x-1/2 pointer-events-none will-change-[left]"
            :style="{ left: `${hsv.a * 100}%` }"
          />
        </div>
      </div>
    </div>

    <div class="flex items-center gap-2">
      <div class="w-[85px] shrink-0">
        <CustomSelect
          v-model="formatOption"
          size="sm"
          :options="formatOptions"
          :clearable="false"
        />
      </div>

      <div class="flex-1 min-w-0">
        <Input
          v-model="textInput"
          type="text"
          size="sm"
          class="text-center px-1! uppercase font-mono text-[13px]"
          @blur="handleInputBlur"
          @keyup.enter="handleInputBlur"
        />
      </div>

      <div class="relative w-14 shrink-0">
        <Input
          :model-value="Math.round(hsv.a * 100)"
          type="number"
          size="sm"
          :min="0"
          :max="100"
          :step="1"
          class="text-right pr-4!"
          @update:model-value="updateAlphaValue"
        />
        <span
          class="absolute right-1.5 top-1/2 -translate-y-1/2 text-[9px] text-(--hint-text) pointer-events-none"
          >%</span
        >
      </div>

      <Button
        variant="ghost"
        size="sm"
        rounded="lg"
        class="p-0! w-8 h-8 shrink-0 text-(--hint-text) hover:border-(--border-color) border border-transparent"
        title="Advanced Color Tools"
        @click="showModal = true"
      >
        <Icon name="mdi:palette" class="w-5 h-5" />
      </Button>
    </div>

    <Modal v-model="showModal" title="Color Studio" size="lg">
      <div class="space-y-6">
        <div class="flex gap-4 items-stretch h-28">
          <div
            class="w-28 rounded-2xl shadow-sm border border-(--border-color) relative overflow-hidden bg-[url('/checkboard.png')]"
          >
            <div
              class="absolute inset-0"
              :style="{ backgroundColor: currentColorCss }"
            />
          </div>
          <div class="flex-1 flex flex-col justify-center gap-1">
            <h3 class="text-3xl font-bold font-mono text-(--label-text)">
              {{ textInput }}
            </h3>
            <p class="text-sm text-(--hint-text) font-mono">
              {{ formatOption.toUpperCase() }} Mode
            </p>
            <div class="mt-2">
              <Button
                size="sm"
                color="primary"
                variant="outline"
                icon-left="mdi:content-save-plus-outline"
                @click="saveColor"
              >
                Add to Collection
              </Button>
            </div>
          </div>
        </div>

        <div v-if="savedColors.length > 0">
          <div class="flex items-center justify-between mb-3">
            <h4
              class="text-xs font-semibold text-(--hint-text) uppercase tracking-wider"
            >
              Collection ({{ savedColors.length }})
            </h4>
            <Button
              variant="ghost"
              size="sm"
              rounded="full"
              class="text-xs text-(--hint-text) hover:text-(--label-text) hover:underline h-auto p-0"
              @click="savedColors = []"
            >
              Clear
            </Button>
          </div>
          <div class="flex flex-wrap gap-2">
            <div
              v-for="color in savedColors"
              :key="color"
              :tabindex="savedColors.indexOf(color) + 1"
              class="group relative w-10 h-10 rounded-full border border-(--border-color) shadow-sm hover:scale-110 active:scale-95 transition-transform bg-[url('/checkboard.png')] overflow-hidden cursor-pointer focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-blue-500 focus:outline-none"
              role="button"
              :aria-label="'Select color ' + color"
              @click="setColorFromString(color)"
              @keydown.enter="setColorFromString(color)"
              @keydown.space.prevent="setColorFromString(color)"
            >
              <div
                class="absolute inset-0"
                :style="{ backgroundColor: color }"
              />
              <div
                class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity"
                @click.stop="removeColor(color)"
              >
                <Icon name="mdi:close" class="w-4 h-4 text-white" />
              </div>
            </div>
          </div>
        </div>

        <Tabs default-value="harmony" class="w-full">
          <TabsList
            class="flex w-full justify-between border-b border-(--border-color)"
          >
            <TabsTrigger value="harmony" class="w-[33%]">Harmony</TabsTrigger>
            <TabsTrigger value="palettes" class="w-[33%]">System</TabsTrigger>
            <TabsTrigger value="generate" class="w-[33%]"
              >Generator</TabsTrigger
            >
          </TabsList>

          <div class="mt-4 min-h-[300px] relative">
            <TabsContent value="harmony" class="space-y-6">
              <div v-for="scheme in harmonies" :key="scheme.name">
                <h4 class="text-xs font-medium text-(--hint-text) mb-2">
                  {{ scheme.name }}
                </h4>
                <div class="grid grid-cols-5 gap-2 h-12">
                  <Button
                    v-for="(color, idx) in scheme.colors"
                    :key="idx"
                    :tabindex="idx + 1"
                    size="sm"
                    variant="ghost"
                    class="h-full rounded-lg border border-(--border-color) relative group hover:scale-[1.02] transition-transform focus-visible:ring-2 focus-visible:ring-offset-1 focus-visible:ring-blue-500"
                    :style="{ backgroundColor: color }"
                    :aria-label="
                      'Select ' + scheme.name + ' color ' + (idx + 1)
                    "
                    @click="setColorFromString(color)"
                  >
                    <div
                      class="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 bg-black/20 text-white rounded-lg transition-opacity"
                    >
                      <Icon name="mdi:eyedropper" class="w-4 h-4" />
                    </div>
                  </Button>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="palettes">
              <div class="grid grid-cols-6 gap-3">
                <Button
                  v-for="color in systemColors"
                  :key="color.value"
                  :tabindex="systemColors.indexOf(color) + 1"
                  size="sm"
                  variant="ghost"
                  class="aspect-square rounded-xl border border-(--border-color) shadow-sm transition-transform hover:scale-105 active:scale-95 group relative focus-visible:ring-2 focus-visible:ring-offset-1 focus-visible:ring-blue-500"
                  :style="{ backgroundColor: color.value }"
                  :aria-label="'Select system color ' + color.name"
                  @click="setColorFromString(color.value)"
                >
                  <div
                    class="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 bg-black/20 text-white rounded-xl transition-opacity"
                  >
                    <span class="text-[10px] font-bold">{{ color.name }}</span>
                  </div>
                </Button>
              </div>
            </TabsContent>

            <TabsContent value="generate" class="space-y-6">
              <div
                class="p-5 rounded-2xl bg-(--surface-secondary)/30 border border-(--border-color)"
              >
                <div class="grid grid-cols-2 gap-6 w-full">
                  <div class="flex flex-col items-center gap-2 w-full">
                    <label
                      class="text-[11px] uppercase tracking-wider font-semibold text-(--hint-text)"
                      >Count</label
                    >
                    <div
                      class="flex items-center w-full shadow-sm rounded-lg isolate"
                    >
                      <Button
                        size="sm"
                        variant="ghost"
                        class="rounded-r-none border border-(--border-color) border-r-0 px-2 h-8 bg-(--surface-primary) hover:bg-(--surface-secondary) z-0 focus:z-10 shrink-0"
                        :disabled="genSettings.count <= 3"
                        @click="
                          genSettings.count = Math.max(3, genSettings.count - 1)
                        "
                      >
                        <Icon name="mdi:minus" class="w-3.5 h-3.5" />
                      </Button>
                      <div class="flex-1 min-w-0">
                        <Input
                          v-model.number="genSettings.count"
                          type="number"
                          size="sm"
                          :min="3"
                          :max="20"
                          class="rounded-none! border-x-0! h-8! text-center! px-0! z-0 focus:z-10 shadow-none! flex-1 w-full min-w-0"
                        />
                      </div>
                      <Button
                        size="sm"
                        variant="ghost"
                        class="rounded-l-none border border-(--border-color) border-l-0 px-2 h-8 bg-(--surface-primary) hover:bg-(--surface-secondary) z-0 focus:z-10 shrink-0"
                        :disabled="genSettings.count >= 20"
                        @click="
                          genSettings.count = Math.min(
                            20,
                            genSettings.count + 1
                          )
                        "
                      >
                        <Icon name="mdi:plus" class="w-3.5 h-3.5" />
                      </Button>
                    </div>
                  </div>
                </div>
              </div>

              <div class="space-y-4">
                <div v-for="row in generatedPalettes" :key="row.title">
                  <h4 class="text-xs font-medium text-(--hint-text) mb-2">
                    {{ row.title }}
                  </h4>
                  <div class="flex flex-wrap gap-2">
                    <Button
                      v-for="(color, idx) in row.colors"
                      :key="idx"
                      :tabindex="idx + 1"
                      size="sm"
                      variant="ghost"
                      class="w-10 h-10 rounded-lg border border-(--border-color) shadow-sm hover:scale-110 active:scale-95 transition-transform relative group focus-visible:ring-2 focus-visible:ring-offset-1 focus-visible:ring-blue-500"
                      :style="{ backgroundColor: color }"
                      @click="setColorFromString(color)"
                      @contextmenu.prevent="saveSpecificColor(color)"
                    >
                      <div
                        class="absolute -top-1 -right-1 w-2 h-2 bg-blue-500 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                      />
                    </Button>
                  </div>
                </div>
              </div>
            </TabsContent>
          </div>
        </Tabs>
      </div>

      <template #footer>
        <Button variant="ghost" color="danger" @click="showModal = false"
          >Close</Button
        >
      </template>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { useEyeDropper } from "@vueuse/core";

const props = defineProps<{ modelValue?: string }>();
const emit = defineEmits(["update:modelValue"]);

const { open, sRGBHex, isSupported } = useEyeDropper();

const sbAreaRef = ref<HTMLElement | null>(null);
const hueSliderRef = ref<HTMLElement | null>(null);
const alphaSliderRef = ref<HTMLElement | null>(null);

const textInput = ref("#FF0000");
const formatOption = ref("hex");
const formatOptions = [
  { label: "HEX", value: "hex" },
  { label: "RGB", value: "rgb" },
  { label: "HSL", value: "hsl" },
];

const hsv = reactive({ h: 0, s: 1, v: 1, a: 1 });
const showModal = ref(false);
const savedColors = ref<string[]>([]);

const genSettings = reactive({
  count: 8,
  hue: 15,
  sat: 10,
  light: 10,
});

const systemColors = [
  { name: "Red", value: "#FF3B30" },
  { name: "Orange", value: "#FF9500" },
  { name: "Yellow", value: "#FFCC00" },
  { name: "Green", value: "#34C759" },
  { name: "Mint", value: "#00C7BE" },
  { name: "Teal", value: "#30B0C7" },
  { name: "Cyan", value: "#32ADE6" },
  { name: "Blue", value: "#007AFF" },
  { name: "Indigo", value: "#5856D6" },
  { name: "Purple", value: "#AF52DE" },
  { name: "Pink", value: "#FF2D55" },
  { name: "Brown", value: "#A2845E" },
];

const getRgbObj = () => {
  const { h, s, v, a } = hsv;
  const f = (n: number, k = (n + h / 60) % 6) =>
    v - v * s * Math.max(Math.min(k, 4 - k, 1), 0);
  return {
    r: Math.round(f(5) * 255),
    g: Math.round(f(3) * 255),
    b: Math.round(f(1) * 255),
    a,
  };
};

const getHslObj = () => {
  const { h, s: sv, v, a } = hsv;
  const l = v * (1 - sv / 2);
  const sl = l === 0 || l === 1 ? 0 : (v - l) / Math.min(l, 1 - l);
  return { h, s: sl, l, a };
};

const rgbToHex = (r: number, g: number, b: number) =>
  "#" +
  [r, g, b]
    .map((x) => x.toString(16).padStart(2, "0"))
    .join("")
    .toUpperCase();

const hexToHsv = (hex: string) => {
  let c = hex.replace("#", "").split("");

  if (c.length === 3 && c[0] && c[1] && c[2] && c[3])
    c = [c[0], c[0], c[1], c[1], c[2], c[2]];
  let a = 1;
  if (c.length === 8) a = parseInt(c.slice(6, 8).join(""), 16) / 255;
  const r = parseInt(c.slice(0, 2).join(""), 16) / 255;
  const g = parseInt(c.slice(2, 4).join(""), 16) / 255;
  const b = parseInt(c.slice(4, 6).join(""), 16) / 255;
  const v = Math.max(r, g, b);
  const diff = v - Math.min(r, g, b);
  const diffc = (c: number) => (v - c) / 6 / diff + 1 / 2;
  let h = 0,
    s = 0;
  if (diff !== 0) {
    s = diff / v;
    const rr = diffc(r),
      gg = diffc(g),
      bb = diffc(b);
    if (r === v) h = bb - gg;
    else if (g === v) h = 1 / 3 + rr - bb;
    else if (b === v) h = 2 / 3 + gg - rr;
    if (h < 0) h += 1;
    else if (h > 1) h -= 1;
  }
  return { h: h * 360, s, v, a };
};

const rgbToHsv = (r: number, g: number, b: number, a = 1) => {
  r /= 255;
  g /= 255;
  b /= 255;
  const max = Math.max(r, g, b),
    min = Math.min(r, g, b),
    d = max - min;
  const s = max === 0 ? 0 : d / max,
    v = max;
  let h = 0;
  if (max !== min) {
    if (max === r) h = (g - b) / d + (g < b ? 6 : 0);
    else if (max === g) h = (b - r) / d + 2;
    else h = (r - g) / d + 4;
    h /= 6;
  }
  return { h: h * 360, s, v, a };
};

const hslToHsv = (h: number, s: number, l: number, a = 1) => {
  const v = l + s * Math.min(l, 1 - l);
  const sv = v === 0 ? 0 : 2 * (1 - l / v);
  return { h, s: sv, v, a };
};

const updateOutput = (triggerEmit = true) => {
  const { r, g, b, a } = getRgbObj();
  let val = "",
    display = "";

  if (formatOption.value === "hex") {
    display = rgbToHex(r, g, b);
    if (a < 1)
      display += Math.round(a * 255)
        .toString(16)
        .padStart(2, "0")
        .toUpperCase();
    val = display;
  } else if (formatOption.value === "rgb") {
    display =
      a === 1
        ? `rgb(${r}, ${g}, ${b})`
        : `rgba(${r}, ${g}, ${b}, ${a.toFixed(2)})`;
    val = display;
  } else if (formatOption.value === "hsl") {
    const { h, s, l } = getHslObj();
    display =
      a === 1
        ? `hsl(${Math.round(h)}, ${Math.round(s * 100)}%, ${Math.round(
            l * 100
          )}%)`
        : `hsla(${Math.round(h)}, ${Math.round(s * 100)}%, ${Math.round(
            l * 100
          )}%, ${a.toFixed(2)})`;
    val = display;
  }

  textInput.value = display;
  if (triggerEmit) emit("update:modelValue", val);
};

const setColorFromString = (str: string) => {
  const s = str.trim();
  if (s.startsWith("#")) {
    Object.assign(hsv, hexToHsv(s));
    return;
  }
  const rgbMatch = s.match(
    /^rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)/i
  );
  if (rgbMatch && rgbMatch[1] && rgbMatch[2] && rgbMatch[3]) {
    Object.assign(
      hsv,
      rgbToHsv(
        +rgbMatch[1],
        +rgbMatch[2],
        +rgbMatch[3],
        rgbMatch[4] ? parseFloat(rgbMatch[4]) : 1
      )
    );
    return;
  }
  const hslMatch = s.match(
    /^hsla?\((\d+),\s*(\d+)%,\s*(\d+)%(?:,\s*([\d.]+))?\)/i
  );
  if (hslMatch && hslMatch[1] && hslMatch[2] && hslMatch[3]) {
    Object.assign(
      hsv,
      hslToHsv(
        +hslMatch[1],
        +hslMatch[2] / 100,
        +hslMatch[3] / 100,
        hslMatch[4] ? parseFloat(hslMatch[4]) : 1
      )
    );
    return;
  }
};

const handleInputBlur = () => {
  setColorFromString(textInput.value);
  updateOutput(true);
};

const currentColorCss = computed(() => {
  const { r, g, b, a } = getRgbObj();
  return `rgba(${r}, ${g}, ${b}, ${a})`;
});
const colorNoAlpha = computed(() => {
  const { r, g, b } = getRgbObj();
  return `rgb(${r}, ${g}, ${b})`;
});

const generateRow = (
  hueMod: number,
  satMod: number,
  lightMod: number,
  flip: boolean = false
) => {
  const colors: string[] = [];
  const { h: baseH, s: baseS, l: baseL } = getHslObj();

  for (let i = 0; i < genSettings.count; i++) {
    let hue = (flip ? baseH + 180 : baseH) + hueMod * i;
    hue = ((hue % 360) + 360) % 360;

    let sat = baseS + ((i * satMod) / 100) * (baseS > 0.65 ? -1 : 1);
    let light = baseL + ((i * lightMod) / 100) * (baseL > 0.65 ? -1 : 1);

    sat = Math.max(0, Math.min(1, sat));
    light = Math.max(0, Math.min(1, light));

    const { h: hNew, s: sNew, v: vNew } = hslToHsv(hue, sat, light);

    const f = (n: number, k = (n + hNew / 60) % 6) =>
      vNew - vNew * sNew * Math.max(Math.min(k, 4 - k, 1), 0);
    const r = Math.round(f(5) * 255);
    const g = Math.round(f(3) * 255);
    const b = Math.round(f(1) * 255);
    colors.push(rgbToHex(r, g, b));
  }
  return colors;
};

const generatedPalettes = computed(() => [
  { title: "Hue Variations", colors: generateRow(genSettings.hue, 0, 0) },
  {
    title: "Saturation Variations",
    colors: generateRow(0, genSettings.sat, 0),
  },
  {
    title: "Lightness Variations",
    colors: generateRow(0, 0, genSettings.light),
  },
  {
    title: "Combined Variations",
    colors: generateRow(
      genSettings.hue / 2,
      genSettings.sat / 2,
      genSettings.light / 2
    ),
  },
  {
    title: "Complementary Hue",
    colors: generateRow(genSettings.hue, 0, 0, true),
  },
]);

const harmonies = computed(() => {
  const { h: baseH } = hsv;
  const toHex = (h: number) => {
    h = ((h % 360) + 360) % 360;
    const { s, v } = hsv;
    const f = (n: number, k = (n + h / 60) % 6) =>
      v - v * s * Math.max(Math.min(k, 4 - k, 1), 0);
    return rgbToHex(
      Math.round(f(5) * 255),
      Math.round(f(3) * 255),
      Math.round(f(1) * 255)
    );
  };
  return [
    {
      name: "Analogous",
      colors: [
        toHex(baseH - 30),
        toHex(baseH - 15),
        toHex(baseH),
        toHex(baseH + 15),
        toHex(baseH + 30),
      ],
    },
    { name: "Complementary", colors: [toHex(baseH), toHex(baseH + 180)] },
    {
      name: "Triadic",
      colors: [toHex(baseH), toHex(baseH + 120), toHex(baseH + 240)],
    },
  ];
});

watch(hsv, () => updateOutput(true));
watch(formatOption, () => updateOutput(true));
watch(
  () => props.modelValue,
  (val) => {
    if (val && val !== textInput.value) {
      setColorFromString(val);
      if (val.startsWith("rgb")) formatOption.value = "rgb";
      else if (val.startsWith("hsl")) formatOption.value = "hsl";
      else formatOption.value = "hex";
      updateOutput(false);
    }
  },
  { immediate: true }
);
watch(sRGBHex, (val) => {
  if (val) {
    setColorFromString(val);
    updateOutput(true);
  }
});

const handleDrag = (
  e: MouseEvent | TouchEvent,
  el: HTMLElement,
  cb: (x: number, y: number) => void
) => {
  const rect = el.getBoundingClientRect();
  let cx, cy;
  if (window.TouchEvent && e instanceof TouchEvent) {
    if (e.touches[0]) {
      cx = e.touches[0].clientX;
      cy = e.touches[0].clientY;
    } else if (e.changedTouches[0]) {
      cx = e.changedTouches[0].clientX;
      cy = e.changedTouches[0].clientY;
    }
  } else {
    cx = (e as MouseEvent).clientX;
    cy = (e as MouseEvent).clientY;
  }
  if (cx === undefined || cy === undefined) return;
  cb(
    Math.max(0, Math.min(1, (cx - rect.left) / rect.width)),
    Math.max(0, Math.min(1, (cy - rect.top) / rect.height))
  );
};

const createDragHandler =
  (elRef: typeof sbAreaRef, cb: (x: number, y: number) => void) =>
  (e: MouseEvent | TouchEvent) => {
    if (!elRef.value) return;
    if (e.cancelable) e.preventDefault();

    const move = (ev: MouseEvent | TouchEvent) => {
      if (ev.cancelable) ev.preventDefault();
      handleDrag(ev, elRef.value!, cb);
    };
    const stop = () => {
      window.removeEventListener("mousemove", move as EventListener);
      window.removeEventListener("mouseup", stop);
      window.removeEventListener("touchmove", move as EventListener);
      window.removeEventListener("touchend", stop);
    };
    move(e);
    if (e instanceof TouchEvent) {
      window.addEventListener("touchmove", move, { passive: false });
      window.addEventListener("touchend", stop);
    } else {
      window.addEventListener("mousemove", move);
      window.addEventListener("mouseup", stop);
    }
  };

const startSbDrag = createDragHandler(sbAreaRef, (x, y) => {
  hsv.s = x;
  hsv.v = 1 - y;
});
const startHueDrag = createDragHandler(hueSliderRef, (x) => {
  hsv.h = x * 360;
});
const startAlphaDrag = createDragHandler(alphaSliderRef, (x) => {
  hsv.a = x;
});
const updateAlphaValue = (val: string | number | Date | null) => {
  if (val === null) return;
  if (val instanceof Date) return;
  const num = Number(val);
  if (!isNaN(num)) hsv.a = Math.max(0, Math.min(100, num)) / 100;
};

const saveColor = () => {
  if (!savedColors.value.includes(textInput.value))
    savedColors.value.unshift(textInput.value);
};
const saveSpecificColor = (c: string) => {
  if (!savedColors.value.includes(c)) savedColors.value.unshift(c);
};
const removeColor = (c: string) => {
  savedColors.value = savedColors.value.filter((x) => x !== c);
};
</script>
