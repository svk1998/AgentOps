<template>
  <!-- Decorative — readers just hear "Loading" from the aria-live region -->
  <span
    class="skeleton"
    :class="[`skeleton--${variant}`, { 'skeleton--block': block }]"
    :style="styleVars"
    aria-hidden="true"
  />
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  /** 'text' | 'line' | 'block' | 'circle' */
  variant: { type: String, default: 'line' },
  width:   { type: [String, Number], default: null },
  height:  { type: [String, Number], default: null },
  block:   { type: Boolean, default: false },
  /** Border-radius override (e.g. '50%' for circular) */
  radius:  { type: String, default: null },
})

function px(v) {
  if (v == null) return null
  return typeof v === 'number' ? `${v}px` : v
}

const styleVars = computed(() => ({
  width:  px(props.width),
  height: px(props.height),
  borderRadius: props.radius || null,
}))
</script>

<style scoped>
.skeleton {
  display: inline-block;
  background:
    linear-gradient(
      90deg,
      var(--bg-elev-2) 0%,
      var(--bg-hover) 50%,
      var(--bg-elev-2) 100%
    );
  background-size: 400% 100%;
  animation: skeleton-shimmer 1.4s ease-in-out infinite;
  border-radius: var(--r-sm);
  vertical-align: middle;
}

.skeleton--block  { display: block; }
.skeleton--text   { height: 0.85em; border-radius: 3px; }
.skeleton--line   { height: 10px; width: 100%; }
.skeleton--block  { height: 80px; width: 100%; border-radius: var(--r); }
.skeleton--circle { border-radius: 50%; }

@keyframes skeleton-shimmer {
  0%   { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
</style>
