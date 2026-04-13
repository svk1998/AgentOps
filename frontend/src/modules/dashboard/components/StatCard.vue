<template>
  <div class="stat-card">
    <div class="stat-icon">{{ icon }}</div>
    <div class="stat-body">
      <p class="stat-label">{{ label }}</p>
      <p class="stat-value">{{ prefix }}{{ value }}</p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  label:  { type: String, required: true },
  value:  { type: [String, Number], required: true },
  icon:   { type: String, default: '📈' },
  prefix: { type: String, default: '' }
})
</script>

<style scoped>
.stat-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  padding: 1.25rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: var(--shadow);
}
.stat-icon  { font-size: 2rem; }
.stat-label { font-size: 0.8rem; color: var(--color-text-muted); margin-bottom: 0.2rem; }
.stat-value { font-size: 1.5rem; font-weight: 700; }
</style>
