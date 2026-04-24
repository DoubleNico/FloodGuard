<template>
  <div
    ref="rootRef"
    :class="[block ? 'flex w-full relative' : 'inline-flex relative']"
  >
    <div
      ref="triggerRef"
      :class="[block ? 'w-full' : 'inline-flex']"
      :aria-expanded="isOpen"
      aria-haspopup="dialog"
      @click="onTriggerClick"
      @keydown.enter.prevent="onTriggerKey"
      @keydown.space.prevent="onTriggerKey"
      @mouseenter="onTriggerEnter"
      @mouseleave="onTriggerLeave"
      @focusin="onTriggerEnter"
      @focusout="onTriggerLeave"
    >
      <slot />
    </div>

    <Teleport v-if="isClient" to="body">
      <div
        v-if="isRendered"
        ref="panelRef"
        :style="panelStyle"
        class="z-50 popover-panel"
        @mouseenter="onPanelEnter"
        @mouseleave="onPanelLeave"
        @click.stop
        @pointerdown.stop
      >
        <div
          class="transition will-change-[opacity]"
          :class="[
            isVisible
              ? 'opacity-100 scale-100 duration-200 ease-out'
              : 'opacity-0 scale-95 duration-150 ease-in',
            isVisible ? 'pointer-events-auto' : 'pointer-events-none',
          ]"
          :style="{ transformOrigin }"
        >
          <slot name="content" :close="close" :is-open="isOpen" />
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import type { PopoverPlacement, PopoverProps } from "~/types/PopoverProps";
import {
  onClickOutside,
  useEventListener,
  useResizeObserver,
} from "@vueuse/core";

const props = withDefaults(defineProps<PopoverProps>(), {
  modelValue: undefined,
  placement: "bottom",
  offset: 8,
  disabled: false,
  trigger: "click",
  hoverDelay: 200,
  block: false,
});

const emit = defineEmits<{
  (e: "update:modelValue", value: boolean): void;
}>();

const isClient = ref(false);
onMounted(() => {
  isClient.value = true;
});

const triggerRef = ref<HTMLElement | null>(null);
const panelRef = ref<HTMLElement | null>(null);

const internalIsOpen = ref(false);

const isOpen = computed<boolean>({
  get() {
    if (props.disabled) return false;
    return props.modelValue ?? internalIsOpen.value;
  },
  set(v) {
    if (props.disabled) return;
    internalIsOpen.value = v;
    emit("update:modelValue", v);
  },
});

const isRendered = ref(false);
const isVisible = ref(false);

const panelStyle = ref<Record<string, string>>({
  position: "fixed",
  top: "-9999px",
  left: "-9999px",
});

const transformOrigin = ref("top center");

const CLOSE_MS = 150;
let unmountTimer: ReturnType<typeof setTimeout> | null = null;

function clearUnmountTimer() {
  if (unmountTimer) {
    clearTimeout(unmountTimer);
    unmountTimer = null;
  }
}

async function mountPositionAndShow() {
  clearUnmountTimer();
  if (!isClient.value) return;

  isRendered.value = true;

  await nextTick();

  updatePosition();

  requestAnimationFrame(() => {
    isVisible.value = true;
  });
}

function hideAndUnmountLater() {
  isVisible.value = false;

  clearUnmountTimer();
  unmountTimer = setTimeout(() => {
    if (!isOpen.value) {
      isRendered.value = false;
      panelStyle.value = { position: "fixed", top: "-9999px", left: "-9999px" };
    }
  }, CLOSE_MS);
}

watch(
  () => isOpen.value,
  (v) => {
    if (v) mountPositionAndShow();
    else hideAndUnmountLater();
  },
  { immediate: true }
);

function clamp(n: number, min: number, max: number) {
  return Math.min(Math.max(n, min), max);
}

type MainSide = "top" | "bottom" | "left" | "right";
type Align = "start" | "end" | "center";

function parsePlacement(p: PopoverPlacement): { side: MainSide; align: Align } {
  const [sideRaw, alignRaw] = p.split("-") as [
    MainSide,
    "start" | "end" | undefined
  ];
  return { side: sideRaw, align: alignRaw ?? "center" };
}

function originFor(side: MainSide, align: Align) {
  const ox = align === "start" ? "left" : align === "end" ? "right" : "center";

  if (side === "bottom") return `top ${ox}`;
  if (side === "top") return `bottom ${ox}`;
  if (side === "right") return `${ox} left`;
  return `${ox} right`;
}

function computeCoords(
  side: MainSide,
  align: Align,
  t: DOMRect,
  cW: number,
  cH: number,
  offset: number
) {
  let top = 0;
  let left = 0;

  if (side === "bottom") top = t.bottom + offset;
  if (side === "top") top = t.top - cH - offset;
  if (side === "right") left = t.right + offset;
  if (side === "left") left = t.left - cW - offset;

  if (side === "top" || side === "bottom") {
    if (align === "start") left = t.left;
    else if (align === "end") left = t.right - cW;
    else left = t.left + t.width / 2 - cW / 2;
  } else {
    if (align === "start") top = t.top;
    else if (align === "end") top = t.bottom - cH;
    else top = t.top + t.height / 2 - cH / 2;
  }

  return { top, left };
}

function overflowScore(
  top: number,
  left: number,
  w: number,
  h: number,
  pad: number
) {
  const vw = window.innerWidth;
  const vh = window.innerHeight;

  const overLeft = Math.max(0, pad - left);
  const overTop = Math.max(0, pad - top);
  const overRight = Math.max(0, left + w + pad - vw);
  const overBottom = Math.max(0, top + h + pad - vh);

  return overLeft + overTop + overRight + overBottom;
}

function updatePosition() {
  if (!isClient.value) return;
  if (!triggerRef.value || !panelRef.value) return;

  const t = triggerRef.value.getBoundingClientRect();
  const contentRect = panelRef.value.getBoundingClientRect();

  const cW = contentRect.width;
  const cH = contentRect.height;

  if (!cW || !cH) return;

  const pad = 8;
  const { side: preferredSide, align } = parsePlacement(props.placement);

  const opposite: Record<MainSide, MainSide> = {
    top: "bottom",
    bottom: "top",
    left: "right",
    right: "left",
  };

  let side: MainSide = preferredSide;
  let { top, left } = computeCoords(side, align, t, cW, cH, props.offset);
  let bestScore = overflowScore(top, left, cW, cH, pad);

  const flippedSide = opposite[preferredSide];
  const flipped = computeCoords(flippedSide, align, t, cW, cH, props.offset);
  const flippedScore = overflowScore(flipped.top, flipped.left, cW, cH, pad);

  if (flippedScore < bestScore) {
    side = flippedSide;
    top = flipped.top;
    left = flipped.left;
    bestScore = flippedScore;
  }

  const vw = window.innerWidth;
  const vh = window.innerHeight;

  top = clamp(top, pad, vh - cH - pad);
  left = clamp(left, pad, vw - cW - pad);

  panelStyle.value = {
    position: "fixed",
    top: `${top}px`,
    left: `${left}px`,
  };

  transformOrigin.value = originFor(side, align);
}

useEventListener(
  window,
  "scroll",
  () => {
    if (isOpen.value) updatePosition();
  },
  { passive: true, capture: true }
);
useEventListener(
  window,
  "resize",
  () => {
    if (isOpen.value) updatePosition();
  },
  { passive: true }
);
useResizeObserver(triggerRef, () => {
  if (isOpen.value) updatePosition();
});
useResizeObserver(panelRef, () => {
  if (isOpen.value) updatePosition();
});

onClickOutside(panelRef, (e) => {
  if (!isOpen.value) return;
  const target = e.target as Node | null;
  if (target && triggerRef.value?.contains(target)) return;

  if (target instanceof Element) {
    const clickedElement = target.closest(".popover-panel, .modal-panel");
    const isModalBackdrop = target.classList.contains("backdrop-blur-md");
    if (clickedElement && clickedElement !== panelRef.value) return;
    if (isModalBackdrop) return;
  }
  close();
});

useEventListener(window, "keydown", (e: KeyboardEvent) => {
  if (e.key === "Escape" && isOpen.value) {
    e.stopPropagation();
    close();
    triggerRef.value?.focus?.();
  }
});

let hoverTimer: ReturnType<typeof setTimeout> | null = null;
function clearHoverTimer() {
  if (hoverTimer) {
    clearTimeout(hoverTimer);
    hoverTimer = null;
  }
}
function scheduleOpen() {
  clearHoverTimer();
  hoverTimer = setTimeout(() => open(), props.hoverDelay);
}
function scheduleClose() {
  clearHoverTimer();
  hoverTimer = setTimeout(() => close(), props.hoverDelay);
}

function onTriggerEnter() {
  if (props.trigger !== "hover") return;
  scheduleOpen();
}
function onTriggerLeave() {
  if (props.trigger !== "hover") return;
  scheduleClose();
}
function onPanelEnter() {
  if (props.trigger !== "hover") return;
  scheduleOpen();
}
function onPanelLeave() {
  if (props.trigger !== "hover") return;
  scheduleClose();
}

function onTriggerClick() {
  if (props.trigger !== "click") return;
  toggle();
}
function onTriggerKey() {
  if (props.trigger !== "click") return;
  toggle();
}

function open() {
  isOpen.value = true;
}
function close() {
  isOpen.value = false;
}
function toggle() {
  isOpen.value = !isOpen.value;
}

defineExpose({ open, close, toggle, isOpen });
</script>
