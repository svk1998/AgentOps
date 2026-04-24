<template>
  <span class="spinner" :style="{ width: `${size}px`, height: `${size}px` }" />
</template>

<script setup>
defineProps({ size: { type: Number, default: 20 } })
</script>

<style scoped>
.spinner {
  display: inline-block;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  flex-shrink: 0;
}
</style>
