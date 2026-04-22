<template>
  <span class="chip" :class="variant && `chip--${variant}`">
    <span v-if="dot" class="chip__dot" />
    <slot />
  </span>
</template>

<script setup>
defineProps({
  variant: { type: String, default: null }, // ok | warn | err | info | accent
  dot: { type: Boolean, default: false },
})
</script>

<style scoped>
.chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 20px;
  padding: 0 8px;
  border-radius: 999px;
  font-family: var(--mono);
  font-size: 11px;
  letter-spacing: 0.02em;
  border: 1px solid var(--border);
  color: var(--text-dim);
  background: var(--bg-elev);
  white-space: nowrap;
}
.chip__dot { width: 6px; height: 6px; border-radius: 50%; background: currentColor; }
.chip--ok    { color: var(--ok);    background: var(--ok-dim);    border-color: transparent; }
.chip--warn  { color: var(--warn);  background: var(--warn-dim);  border-color: transparent; }
.chip--err   { color: var(--err);   background: var(--err-dim);   border-color: transparent; }
.chip--info  { color: var(--info);  background: var(--info-dim);  border-color: transparent; }
.chip--accent{ color: var(--accent);background: var(--accent-dim);border-color: transparent; }
</style>
