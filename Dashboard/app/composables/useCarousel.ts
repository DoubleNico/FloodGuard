import { createInjectionState } from "@vueuse/core";

const [useProvideCarousel, useInjectCarousel] = createInjectionState(
  (
    options: { orientation: "horizontal" | "vertical"; loop?: boolean } = {
      orientation: "horizontal",
      loop: false,
    }
  ) => {
    const carouselRef = ref<HTMLElement | null>(null);
    const canScrollPrev = ref(false);
    const canScrollNext = ref(false);
    let scrollTimeout: ReturnType<typeof setTimeout> | null = null;

    const withoutSmoothScroll = (
      element: HTMLElement,
      callback: () => void
    ) => {
      const originalBehavior = element.style.scrollBehavior;
      element.style.scrollBehavior = "auto";
      callback();
      // eslint-disable-next-line @typescript-eslint/no-unused-expressions
      element.offsetHeight; // Force reflow
      requestAnimationFrame(() => {
        element.style.scrollBehavior = originalBehavior;
      });
    };

    const calculateSetWidth = (el: HTMLElement) => {
      return el.scrollWidth / 3;
    };

    const resetScrollPosition = () => {
      if (!options.loop || !carouselRef.value) return;
      const el = carouselRef.value;
      const setWidth = calculateSetWidth(el);

      if (el.scrollLeft < setWidth * 0.5) {
        withoutSmoothScroll(el, () => {
          el.scrollLeft += setWidth;
        });
      } else if (el.scrollLeft > setWidth * 1.9) {
        withoutSmoothScroll(el, () => {
          el.scrollLeft -= setWidth;
        });
      }
    };

    const handleScroll = () => {
      checkScrollability();
      if (options.loop) {
        if (scrollTimeout) clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(() => {
          resetScrollPosition();
        }, 150);
      }
    };

    const initInfiniteScroll = () => {
      if (!options.loop || !carouselRef.value) return;
      const el = carouselRef.value;

      const setWidth = calculateSetWidth(el);
      withoutSmoothScroll(el, () => {
        el.scrollLeft = setWidth;
      });
    };

    const checkScrollability = () => {
      const element = carouselRef.value;
      if (!element) return;

      if (options.loop) {
        canScrollPrev.value = true;
        canScrollNext.value = true;
        return;
      }

      const { scrollLeft, scrollWidth, clientWidth } = element;
      canScrollPrev.value = scrollLeft > 1;
      canScrollNext.value = scrollLeft + clientWidth < scrollWidth - 1;
    };

    const scroll = (direction: "prev" | "next") => {
      const element = carouselRef.value;
      if (!element) return;

      const firstChild = element.firstElementChild as HTMLElement;
      const itemWidth = firstChild
        ? firstChild.offsetWidth
        : element.clientWidth;

      const scrollAmount = itemWidth;
      const currentScroll = element.scrollLeft;

      let target =
        direction === "next"
          ? currentScroll + scrollAmount
          : currentScroll - scrollAmount;

      if (!options.loop) {
        const maxScroll = element.scrollWidth - element.clientWidth;
        target = Math.max(0, Math.min(target, maxScroll));
      }

      element.scrollTo({
        left: target,
        behavior: "smooth",
      });
    };

    onMounted(() => {
      checkScrollability();
    });

    return {
      carouselRef,
      orientation: options.orientation,
      loop: options.loop,
      scrollPrev: () => scroll("prev"),
      scrollNext: () => scroll("next"),
      canScrollPrev,
      canScrollNext,
      checkScrollability: handleScroll,
      initInfiniteScroll,
    };
  }
);

export { useProvideCarousel };

export const useCarousel = () => {
  const carousel = useInjectCarousel();
  if (!carousel)
    throw new Error("useCarousel must be used within a <Carousel />");
  return carousel;
};
