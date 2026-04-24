<template>
  <div class="empty-state" :class="`empty-state--${size}`">
    <component
      :is="icon"
      v-if="icon"
      :size="iconSize"
      :stroke-width="1.4"
      class="empty-state__icon"
      :style="{ color: iconColor, opacity: 0.8 }"
    />
    <p v-if="title" class="empty-state__title">{{ title }}</p>
    <p v-if="subtitle" class="empty-state__sub mono">{{ subtitle }}</p>
    <div v-if="$slots.actions" class="empty-state__actions"><slot name="actions" /></div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  icon:      { type: [Object, Function], default: null }, // Lucide component
  title:     { type: String, default: null },
  subtitle:  { type: String, default: null },
  tone:      { type: String, default: 'accent' }, // accent | ok | err | warn | info | muted
  size:      { type: String, default: 'md' },     // sm | md | lg
})

const iconColor = computed(() => ({
  accent: 'var(--accent)',
  ok:     'var(--ok)',
  err:    'var(--err)',
  warn:   'var(--warn)',
  info:   'var(--info)',
  muted:  'var(--text-faint)',
}[props.tone] || 'var(--accent)'))

const iconSize = computed(() => ({ sm: 20, md: 32, lg: 48 }[props.size] ?? 32))
</script>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  text-align: center;
}
.empty-state--sm { padding: 20px 12px; }
.empty-state--md { padding: 48px 20px; }
.empty-state--lg { padding: 80px 20px; }

.empty-state__icon { flex-shrink: 0; }
.empty-state__title {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-dim);
}
.empty-state__sub {
  font-size: 11px;
  color: var(--text-faint);
}
.empty-state__actions { margin-top: 8px; display: flex; gap: 6px; }
</style>
