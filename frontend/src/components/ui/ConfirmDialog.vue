<template>
  <AppModal :open="open" :title="title" size="sm" @close="$emit('cancel')">
    <p class="confirm__msg">{{ message }}</p>
    <template #footer>
      <AppButton variant="ghost" @click="$emit('cancel')">Cancel</AppButton>
      <AppButton :variant="confirmVariant" @click="$emit('confirm')">
        {{ confirmLabel }}
      </AppButton>
    </template>
  </AppModal>
</template>

<script setup>
import AppModal from './AppModal.vue'
import AppButton from './AppButton.vue'

defineProps({
  open:           { type: Boolean, required: true },
  title:          { type: String, default: 'Are you sure?' },
  message:        { type: String, default: 'This action cannot be undone.' },
  confirmLabel:   { type: String, default: 'Confirm' },
  confirmVariant: { type: String, default: 'danger' },
})
defineEmits(['confirm', 'cancel'])
</script>

<style scoped>
.confirm__msg { color: var(--color-text-muted); line-height: 1.6; }
</style>
