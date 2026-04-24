<template>
  <div
    class="w-full overflow-auto rounded-xl border border-(--border-color) bg-(--surface-primary) shadow-(--shadow-sm)"
  >
    <table class="w-full caption-bottom text-sm text-left">
      <slot />
    </table>
  </div>
</template>

<script setup lang="ts"></script>
