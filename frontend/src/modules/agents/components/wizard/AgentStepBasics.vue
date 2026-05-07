<template>
  <div class="step-card">
    <h2 class="step-title">Basics</h2>

    <div class="form-grid">
      <!-- Name -->
      <FormField label="Name" hint="required" :error="errors.name">
        <template #default="{ id }">
          <input
            :id="id"
            class="input"
            :class="{ 'input--err': errors.name }"
            :value="form.name"
            placeholder="e.g. wine-recognizer-v2"
            @input="emit('update', 'name', $event.target.value)"
          />
        </template>
      </FormField>

      <!-- Agent type -->
      <FormField label="Agent type" hint="required" :error="errors.agent_type">
        <template #default="{ id }">
          <select
            :id="id"
            class="input"
            :class="{ 'input--err': errors.agent_type }"
            :value="form.agent_type"
            @change="emit('update', 'agent_type', $event.target.value)"
          >
            <option value="" disabled>Select type…</option>
            <option v-for="t in AGENT_TYPES" :key="t" :value="t">{{ AGENT_TYPE_LABELS[t] }}</option>
          </select>
        </template>
      </FormField>

      <!-- Endpoint URL — full width -->
      <FormField
        class="full"
        label="Endpoint URL"
        hint="required"
        help="The HTTP(S) endpoint this agent listens on"
        :error="errors.endpoint_url"
      >
        <template #default="{ id }">
          <input
            :id="id"
            class="input"
            :class="{ 'input--err': errors.endpoint_url }"
            :value="form.endpoint_url"
            placeholder="https://api.example.com/v1/agent"
            @input="emit('update', 'endpoint_url', $event.target.value)"
          />
        </template>
      </FormField>

      <!-- Model provider -->
      <FormField label="Model provider" help="e.g. openai, anthropic, groq">
        <template #default="{ id }">
          <input
            :id="id"
            class="input"
            :value="form.model_provider"
            placeholder="optional"
            @input="emit('update', 'model_provider', $event.target.value)"
          />
        </template>
      </FormField>

      <!-- Owner -->
      <FormField label="Owner" help="Team or person responsible">
        <template #default="{ id }">
          <input
            :id="id"
            class="input"
            :value="form.owner"
            placeholder="optional"
            @input="emit('update', 'owner', $event.target.value)"
          />
        </template>
      </FormField>

      <!-- Version -->
      <FormField label="Version">
        <template #default="{ id }">
          <input
            :id="id"
            class="input"
            :value="form.version"
            placeholder="1.0.0"
            @input="emit('update', 'version', $event.target.value)"
          />
        </template>
      </FormField>

      <!-- Status -->
      <FormField label="Status">
        <template #default="{ id }">
          <select
            :id="id"
            class="input"
            :value="form.status"
            @change="emit('update', 'status', $event.target.value)"
          >
            <option v-for="s in AGENT_STATUSES" :key="s" :value="s">{{ s }}</option>
          </select>
        </template>
      </FormField>

      <!-- Description — full width -->
      <FormField class="full" label="Description">
        <template #default="{ id }">
          <textarea
            :id="id"
            class="input textarea"
            :value="form.description"
            rows="3"
            placeholder="What does this agent do?"
            @input="emit('update', 'description', $event.target.value)"
          />
        </template>
      </FormField>
    </div>
  </div>
</template>

<script setup>
import FormField from '@/components/ui/FormField.vue'
import { AGENT_TYPES, AGENT_TYPE_LABELS, AGENT_STATUSES } from '@/constants/enums'

defineProps({
  form:   { type: Object, required: true },
  errors: { type: Object, required: true },
})

const emit = defineEmits(['update'])
</script>

<style scoped>
.step-card {
  background: var(--bg-elev);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 28px 32px;
}
.step-title { font-size: 14px; font-weight: 600; color: var(--text); margin-bottom: 20px; }

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
.full { grid-column: span 2; }

.input {
  width: 100%;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--r-sm, 4px);
  padding: 8px 10px;
  color: var(--text);
  font-size: 13px;
  font-family: inherit;
  outline: none;
  transition: border-color 0.1s;
}
.input:focus  { border-color: var(--accent); }
.input--err   { border-color: var(--err); }
select.input  { cursor: pointer; appearance: none; }
.textarea     { resize: vertical; line-height: 1.5; }
</style>
