<template>
  <svg
    class="sparkline"
    :viewBox="`0 0 ${width} ${height}`"
    :width="width"
    :height="height"
    preserveAspectRatio="none"
  >
    <path v-if="points.length" :d="areaPath" :fill="toneColor" opacity="0.15" />
    <path v-if="points.length" :d="linePath" :stroke="toneColor" :stroke-width="strokeWidth" fill="none" stroke-linecap="round" stroke-linejoin="round" />
    <circle v-if="showDot && lastPoint" :cx="lastPoint[0]" :cy="lastPoint[1]" :r="dotR" :fill="toneColor" />
  </svg>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: { type: Array, required: true },       // array of numbers in [0..1] or raw numbers
  width: { type: Number, default: 120 },
  height: { type: Number, default: 30 },
  tone: { type: String, default: 'neu' },       // pos | neg | neu | accent
  strokeWidth: { type: Number, default: 1.25 },
  showDot: { type: Boolean, default: true },
  dotR: { type: Number, default: 1.5 },
})

const TONE_COLORS = {
  pos: 'var(--ok)',
  neg: 'var(--err)',
  neu: 'var(--text-dim)',
  accent: 'var(--accent)',
  info: 'var(--info)',
  warn: 'var(--warn)',
}
const toneColor = computed(() => TONE_COLORS[props.tone] || TONE_COLORS.neu)

// Normalize data to [0..1] range
const points = computed(() => {
  const d = props.data || []
  if (!d.length) return []
  const min = Math.min(...d)
  const max = Math.max(...d)
  const span = max - min || 1
  const stepX = props.width / Math.max(1, d.length - 1)
  const padY = 2
  const h = props.height - padY * 2
  return d.map((v, i) => [i * stepX, padY + (1 - (v - min) / span) * h])
})

const linePath = computed(() =>
  points.value.map((p, i) => `${i === 0 ? 'M' : 'L'}${p[0].toFixed(2)},${p[1].toFixed(2)}`).join(' ')
)

const areaPath = computed(() => {
  if (!points.value.length) return ''
  const first = points.value[0]
  const last = points.value[points.value.length - 1]
  return (
    `M${first[0]},${props.height} ` +
    points.value.map(p => `L${p[0].toFixed(2)},${p[1].toFixed(2)}`).join(' ') +
    ` L${last[0]},${props.height} Z`
  )
})

const lastPoint = computed(() => points.value[points.value.length - 1])
</script>

<style scoped>
.sparkline { display: inline-block; overflow: visible; }
</style>
