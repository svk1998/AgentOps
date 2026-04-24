<template>
  <div class="page-head">
    <div class="page-head__title-col">
      <div v-if="eyebrow" class="page-eyebrow mono faint">{{ eyebrow }}</div>
      <h1 class="page-title">{{ title }}</h1>
      <div v-if="$slots.meta || subtitle" class="page-sub mono">
        <slot name="meta">{{ subtitle }}</slot>
      </div>
    </div>
    <div v-if="$slots.actions" class="page-head__actions">
      <slot name="actions" />
    </div>
  </div>
</template>

<script setup>
defineProps({
  eyebrow:  { type: String, default: null },
  title:    { type: String, required: true },
  subtitle: { type: String, default: null },
})
</script>

<style scoped>
.page-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  padding: 2px 2px 6px;
  flex-wrap: wrap;
}
.page-head__title-col { display: flex; flex-direction: column; gap: 4px; }
.page-head__actions { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }

.page-eyebrow {
  font-size: 10.5px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-bottom: 2px;
}
.page-title {
  font-size: 22px;
  font-weight: 600;
  letter-spacing: -0.02em;
  color: var(--text);
}
.page-sub {
  font-size: 11.5px;
  color: var(--text-dim);
  display: flex;
  gap: 6px;
  align-items: center;
  margin-top: 2px;
}
.page-sub :deep(.sep) { color: var(--text-faint); }
</style>
