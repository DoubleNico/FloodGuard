<template>
  <li>
    <NavigationMenuLink :href="href" :active="active">
      <div class="text-[14px] font-semibold text-(--label-text)">
        {{ title }}
      </div>
      <p
        class="line-clamp-2 mt-1 text-[13px] leading-relaxed text-(--hint-text)"
      >
        <slot />
      </p>
    </NavigationMenuLink>
  </li>
</template>

<script setup lang="ts">
defineProps<{
  title: string;
  href: string;
  active?: boolean;
}>();
</script>
