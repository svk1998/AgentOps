<template>
  <div class="kpi">
    <div class="kpi__label">{{ label }}</div>
    <div class="kpi__row">
      <div class="kpi__value">{{ value }}</div>
      <div v-if="delta" class="kpi__delta" :class="`kpi__delta--${tone || 'neu'}`">{{ delta }}</div>
    </div>
    <div v-if="spark && spark.length" class="kpi__spark">
      <Sparkline :data="spark" :tone="tone" :width="sparkWidth" :height="28" />
    </div>
    <div v-else-if="$slots.sub" class="kpi__sub">
      <slot name="sub" />
    </div>
  </div>
</template>

<script setup>
import Sparkline from './Sparkline.vue'
defineProps({
  label: { type: String, required: true },
  value: { type: [String, Number], required: true },
  delta: { type: String, default: null },
  tone: { type: String, default: 'neu' },       // pos | neg | neu | accent
  spark: { type: Array, default: null },
  sparkWidth: { type: Number, default: 80 },
})
</script>

<style scoped>
.kpi {
  background: var(--panel);
  padding: 14px 18px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.kpi__label {
  font-size: 10.5px;
  color: var(--text-faint);
  font-family: var(--mono);
  letter-spacing: 0.04em;
  text-transform: uppercase;
}
.kpi__row {
  display: flex;
  align-items: baseline;
  gap: 10px;
}
.kpi__value {
  font-size: 24px;
  font-weight: 500;
  letter-spacing: -0.02em;
  font-feature-settings: "tnum";
  color: var(--text);
}
.kpi__delta {
  font-size: 11px;
  font-family: var(--mono);
}
.kpi__delta--pos { color: var(--ok); }
.kpi__delta--neg { color: var(--err); }
.kpi__delta--neu { color: var(--text-dim); }
.kpi__delta--accent { color: var(--accent); }
.kpi__spark { margin-top: 2px; }
.kpi__sub {
  font-size: 11px;
  color: var(--text-dim);
  font-family: var(--mono);
}
</style>
