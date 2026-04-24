<template>
  <div
    class="relative w-full"
    role="region"
    aria-roledescription="carousel"
    @keydown="onKeyDown"
  >
    <slot />
  </div>
</template>

<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    orientation?: "horizontal" | "vertical";
    loop?: boolean;
  }>(),
  {
    orientation: "horizontal",
    loop: false,
  }
);

const { scrollPrev, scrollNext } = useProvideCarousel({
  orientation: props.orientation,
  loop: props.loop,
});

const onKeyDown = (event: KeyboardEvent) => {
  if (event.key === "ArrowLeft") {
    event.preventDefault();
    scrollPrev();
  } else if (event.key === "ArrowRight") {
    event.preventDefault();
    scrollNext();
  }
};
</script>
