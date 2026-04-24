<template>
  <div class="empty">
    <div v-if="$slots.icon" class="empty__icon"><slot name="icon" /></div>
    <h3 class="empty__title">{{ title }}</h3>
    <p v-if="description" class="empty__desc">{{ description }}</p>
    <AppButton v-if="actionLabel" variant="primary" @click="$emit('action')">
      {{ actionLabel }}
    </AppButton>
  </div>
</template>

<script setup>
import AppButton from './AppButton.vue'
defineProps({
  title:       { type: String, required: true },
  description: { type: String, default: '' },
  actionLabel: { type: String, default: '' },
})
defineEmits(['action'])
</script>

<style scoped>
.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  padding: 3rem 2rem;
  text-align: center;
}
.empty__icon  { font-size: 2.5rem; opacity: 0.5; }
.empty__title { font-size: 1rem; font-weight: 600; }
.empty__desc  { color: var(--color-text-muted); font-size: 0.875rem; max-width: 360px; }
</style>
