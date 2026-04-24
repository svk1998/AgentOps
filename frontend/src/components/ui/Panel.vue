<template>
  <div class="panel" :class="{ 'panel--flat': flat }">
    <div v-if="title || $slots.header || $slots.actions" class="panel__head">
      <div class="panel__title-wrap">
        <div v-if="title" class="panel__title">{{ title }}</div>
        <div v-if="subtitle" class="panel__sub">{{ subtitle }}</div>
        <slot name="header" />
      </div>
      <div v-if="$slots.actions" class="panel__actions"><slot name="actions" /></div>
    </div>
    <div class="panel__body" :class="{ 'panel__body--pad': padding !== false, 'panel__body--flush': padding === false }">
      <slot />
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, default: null },
  subtitle: { type: String, default: null },
  padding: { type: Boolean, default: true },
  flat: { type: Boolean, default: false },
})
</script>

<style scoped>
.panel {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
.panel--flat { border: none; border-radius: 0; background: transparent; }

.panel__head {
  padding: 12px 14px;
  display: flex;
  align-items: center;
  gap: 10px;
  border-bottom: 1px solid var(--border);
}
.panel__title-wrap { display: flex; flex-direction: column; gap: 2px; flex: 1; min-width: 0; }
.panel__title {
  font-size: 12.5px;
  font-weight: 600;
  color: var(--text);
  letter-spacing: -0.01em;
}
.panel__sub {
  font-size: 11px;
  color: var(--text-faint);
  font-family: var(--mono);
}
.panel__actions {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}
.panel__body--pad   { padding: 14px; }
.panel__body--flush { padding: 0; }
</style>
