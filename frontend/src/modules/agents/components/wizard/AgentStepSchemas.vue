<template>
  <div class="step-card">
    <h2 class="step-title">Schemas</h2>
    <p class="step-sub">Define the JSON shapes your agent expects and returns. Leave as <code>{}</code> if not applicable.</p>

    <div class="schema-list">
      <FormField
        v-for="f in fields"
        :key="f.key"
        :label="f.label"
        :help="f.help"
        :error="errors[f.errorKey]"
      >
        <template #default="{ id }">
          <textarea
            :id="id"
            class="json-editor"
            :class="{ 'json-editor--err': errors[f.errorKey] }"
            :value="form[f.key]"
            rows="8"
            spellcheck="false"
            @input="emit('update', f.key, $event.target.value)"
          />
        </template>
      </FormField>
    </div>
  </div>
</template>

<script setup>
import FormField from '@/components/ui/FormField.vue'

defineProps({
  form:   { type: Object, required: true },
  errors: { type: Object, required: true },
})

const emit = defineEmits(['update'])

const fields = [
  {
    key:      'input_schema_str',
    errorKey: 'input_schema',
    label:    'Input schema',
    help:     'JSON object describing the input this agent accepts',
  },
  {
    key:      'output_schema_str',
    errorKey: 'output_schema',
    label:    'Output schema',
    help:     'JSON object describing what this agent returns',
  },
  {
    key:      'config_str',
    errorKey: 'config',
    label:    'Config',
    help:     'Additional runtime configuration (model params, thresholds, etc.)',
  },
]
</script>

<style scoped>
.step-card {
  background: var(--bg-elev);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 28px 32px;
}
.step-title { font-size: 14px; font-weight: 600; color: var(--text); margin-bottom: 4px; }
.step-sub   { font-size: 12px; color: var(--text-dim); margin-bottom: 20px; }
.step-sub code { font-family: var(--mono, monospace); color: var(--accent); }

.schema-list { display: flex; flex-direction: column; gap: 20px; }

.json-editor {
  width: 100%;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--r-sm, 4px);
  padding: 10px 12px;
  color: var(--text);
  font-family: var(--mono, 'JetBrains Mono', monospace);
  font-size: 12px;
  line-height: 1.6;
  resize: vertical;
  outline: none;
  transition: border-color 0.1s;
}
.json-editor:focus { border-color: var(--accent); }
.json-editor--err  { border-color: var(--err); }
</style>
