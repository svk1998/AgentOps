<template>
  <Loader2 :size="sizePx" :stroke-width="strokeWidth" class="spinner" :style="{ color: toneColor }" :aria-label="label" role="status" />
</template>

<script setup>
import { computed } from 'vue'
import { Loader2 } from 'lucide-vue-next'

const props = defineProps({
  size:        { type: [Number, String], default: 'md' }, // xs | sm | md | lg | xl | number
  tone:        { type: String, default: 'muted' },        // accent | ok | err | info | muted | inherit
  strokeWidth: { type: Number, default: 1.75 },
  label:       { type: String, default: 'Loading' },
})

const SIZE_MAP = { xs: 10, sm: 12, md: 14, lg: 18, xl: 24 }
const sizePx = computed(() => typeof props.size === 'number' ? props.size : (SIZE_MAP[props.size] ?? 14))

const TONE_MAP = {
  accent:  'var(--accent)',
  ok:      'var(--ok)',
  err:     'var(--err)',
  info:    'var(--info)',
  muted:   'var(--text-faint)',
  inherit: 'currentColor',
}
const toneColor = computed(() => TONE_MAP[props.tone] ?? 'currentColor')
</script>

<style scoped>
.spinner {
  display: inline-block;
  animation: spin 0.9s linear infinite;
  flex-shrink: 0;
}
</style>
