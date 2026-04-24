<template>
  <div class="field">
    <label v-if="label" :for="id" class="field__label">
      {{ label }}
      <span v-if="required" class="field__required">*</span>
    </label>
    <input
      :id="id"
      :class="['field__input', { 'field__input--error': error }]"
      :value="modelValue"
      v-bind="$attrs"
      @input="$emit('update:modelValue', $event.target.value)"
    />
    <p v-if="error" class="field__error">{{ error }}</p>
    <p v-else-if="hint" class="field__hint">{{ hint }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: { type: [String, Number], default: '' },
  label:      { type: String, default: '' },
  hint:       { type: String, default: '' },
  error:      { type: String, default: '' },
  required:   { type: Boolean, default: false },
})
defineEmits(['update:modelValue'])

const id = computed(() => `input-${Math.random().toString(36).slice(2)}`)
</script>

<style scoped>
.field { display: flex; flex-direction: column; gap: 0.4rem; }
.field__label {
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--color-text-muted);
}
.field__required { color: var(--color-danger-text); margin-left: 2px; }
.field__input {
  padding: 0.55rem 0.75rem;
  background: var(--color-surface-2);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  color: var(--color-text);
  outline: none;
  transition: border-color var(--transition), box-shadow var(--transition);
  width: 100%;
}
.field__input::placeholder { color: var(--color-text-subtle); }
.field__input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(99,102,241,0.2);
}
.field__input--error { border-color: var(--color-danger); }
.field__input--error:focus { box-shadow: 0 0 0 3px rgba(248,81,73,0.2); }
.field__error { font-size: 0.78rem; color: var(--color-danger-text); }
.field__hint  { font-size: 0.78rem; color: var(--color-text-subtle); }
</style>
