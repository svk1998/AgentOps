<template>
  <div class="stepper">
    <template v-for="(s, i) in steps" :key="s.id">
      <div class="step">
        <div class="step-circle" :class="circleClass(i + 1)">
          <Check v-if="i + 1 < current" :size="12" :stroke-width="2.5" />
          <span v-else>{{ i + 1 }}</span>
        </div>
        <span class="step-label" :class="labelClass(i + 1)">{{ s.label }}</span>
      </div>
      <div
        v-if="i < steps.length - 1"
        class="step-connector"
        :class="{ 'step-connector--done': i + 1 < current }"
      />
    </template>
  </div>
</template>

<script setup>
import { Check } from 'lucide-vue-next'

const props = defineProps({
  steps:   { type: Array,  required: true },  // [{ id: string, label: string }]
  current: { type: Number, required: true },  // 1-based active step index
})

function circleClass(n) {
  if (n < props.current)   return 'step-circle--done'
  if (n === props.current) return 'step-circle--active'
  return 'step-circle--todo'
}

function labelClass(n) {
  if (n < props.current)   return 'step-label--done'
  if (n === props.current) return 'step-label--active'
  return 'step-label--todo'
}
</script>

<style scoped>
.stepper {
  display: flex;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 28px;
}

.step { display: flex; align-items: center; gap: 8px; }

.step-circle {
  width: 24px; height: 24px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 600; flex-shrink: 0;
  transition: background 0.15s;
}
.step-circle--done   { background: #22c55e; color: #fff; }
.step-circle--active { background: var(--accent); color: var(--accent-text, #0A0B0D); }
.step-circle--todo   { background: var(--bg-elev); border: 1px solid var(--border); color: var(--text-faint); }

.step-label { font-size: 12px; font-weight: 500; white-space: nowrap; }
.step-label--done   { color: #22c55e; }
.step-label--active { color: var(--accent); }
.step-label--todo   { color: var(--text-faint); }

.step-connector {
  flex: 1; height: 1px;
  min-width: 24px; max-width: 72px;
  margin: 0 6px;
  background: var(--border);
  transition: background 0.15s;
}
.step-connector--done { background: rgba(34, 197, 94, 0.35); }
</style>
