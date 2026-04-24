<template>
  <div class="form-field">
    <label v-if="label" :for="inputId" class="form-field__label mono">
      <span>{{ label }}</span>
      <span v-if="hint" class="form-field__hint mono">{{ hint }}</span>
    </label>
    <slot :id="inputId" />
    <div v-if="error" class="form-field__error mono">{{ error }}</div>
    <div v-else-if="help" class="form-field__help mono faint">{{ help }}</div>
  </div>
</template>

<script setup>
import { computed, useId } from 'vue'

const props = defineProps({
  label: { type: String, default: null },
  hint:  { type: String, default: null }, // small right-aligned hint e.g. "min 8 chars"
  help:  { type: String, default: null }, // help text below the input
  error: { type: String, default: null }, // error takes priority over help
  id:    { type: String, default: null },
})

const generatedId = useId()
const inputId = computed(() => props.id ?? `ff-${generatedId}`)
</script>

<style scoped>
.form-field { display: flex; flex-direction: column; gap: 6px; }

.form-field__label {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  font-size: 10.5px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--text-faint);
}
.form-field__hint {
  font-size: 9.5px;
  color: var(--text-faint);
  text-transform: none;
  letter-spacing: 0.02em;
}
.form-field__help  { font-size: 10.5px; color: var(--text-faint); }
.form-field__error { font-size: 10.5px; color: var(--err); }
</style>
