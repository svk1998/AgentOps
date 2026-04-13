<template>
  <div :class="['card', { 'card--hoverable': hoverable, 'card--no-pad': !padding }]"
       :style="borderAccent ? `border-left: 3px solid ${borderAccent}` : ''">
    <div v-if="$slots.header" class="card__header">
      <slot name="header" />
    </div>
    <div v-if="padding" class="card__body">
      <slot />
    </div>
    <slot v-else />
    <div v-if="$slots.footer" class="card__footer">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup>
defineProps({
  padding:      { type: Boolean, default: true },
  hoverable:    { type: Boolean, default: false },
  borderAccent: { type: String,  default: '' },
})
</script>

<style scoped>
.card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}
.card--hoverable {
  cursor: pointer;
  transition: border-color var(--transition), box-shadow var(--transition);
}
.card--hoverable:hover {
  border-color: var(--color-border-strong);
  box-shadow: var(--shadow-md);
}
.card__header {
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}
.card__body { padding: 1.25rem; }
.card__footer {
  padding: 0.75rem 1.25rem;
  border-top: 1px solid var(--color-border);
  background: var(--color-surface-2);
}
</style>
