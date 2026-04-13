<template>
  <div class="field">
    <label v-if="label" :for="id" class="field__label">
      {{ label }}
      <span v-if="required" class="field__required">*</span>
    </label>
    <div class="field__select-wrap">
      <select
        :id="id"
        :class="['field__select', { 'field__select--error': error }]"
        :value="modelValue"
        v-bind="$attrs"
        @change="$emit('update:modelValue', $event.target.value)"
      >
        <option v-if="placeholder" value="" disabled>{{ placeholder }}</option>
        <slot />
      </select>
      <svg class="field__arrow" width="12" height="12" viewBox="0 0 12 12" fill="currentColor">
        <path d="M6 8L1 3h10L6 8z"/>
      </svg>
    </div>
    <p v-if="error" class="field__error">{{ error }}</p>
    <p v-else-if="hint" class="field__hint">{{ hint }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

defineProps({
  modelValue:  { type: String, default: '' },
  label:       { type: String, default: '' },
  hint:        { type: String, default: '' },
  error:       { type: String, default: '' },
  required:    { type: Boolean, default: false },
  placeholder: { type: String, default: '' },
})
defineEmits(['update:modelValue'])

const id = computed(() => `select-${Math.random().toString(36).slice(2)}`)
</script>

<style scoped>
.field { display: flex; flex-direction: column; gap: 0.4rem; }
.field__label { font-size: 0.8rem; font-weight: 500; color: var(--color-text-muted); }
.field__required { color: var(--color-danger-text); margin-left: 2px; }
.field__select-wrap { position: relative; }
.field__select {
  appearance: none;
  width: 100%;
  padding: 0.55rem 2rem 0.55rem 0.75rem;
  background: var(--color-surface-2);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  color: var(--color-text);
  outline: none;
  cursor: pointer;
  transition: border-color var(--transition), box-shadow var(--transition);
}
.field__select:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(99,102,241,0.2);
}
.field__select--error { border-color: var(--color-danger); }
.field__select option { background: var(--color-surface-2); }
.field__arrow {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-text-muted);
  pointer-events: none;
}
.field__error { font-size: 0.78rem; color: var(--color-danger-text); }
.field__hint  { font-size: 0.78rem; color: var(--color-text-subtle); }
</style>
