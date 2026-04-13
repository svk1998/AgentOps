<template>
  <AppModal :open="open" :title="agent ? 'Edit Agent' : 'New Agent'" size="lg" @close="$emit('close')">
    <div class="form-grid">
      <AppInput v-model="form.name" label="Name" required placeholder="e.g. Customer Support Bot" />
      <AppInput v-model="form.description" label="Description" placeholder="What does this agent do?" />

      <!-- Model select -->
      <div class="field">
        <label class="field-label">Model <span class="required">*</span></label>
        <select v-model="form.model" class="field-select">
          <optgroup v-for="(group, provider) in groupedModels" :key="provider" :label="providerLabel(provider)">
            <option v-for="m in group" :key="m.id" :value="m.id">{{ m.name }}</option>
          </optgroup>
        </select>
      </div>

      <AppTextarea
        v-model="form.system_prompt"
        label="System Prompt"
        :rows="5"
        mono
        placeholder="You are a helpful assistant that..."
      />

      <!-- Parameters -->
      <div class="params-section">
        <p class="section-label">Parameters</p>
        <div class="params-grid">
          <AppInput
            v-model.number="form.parameters.temperature"
            label="Temperature"
            type="number" min="0" max="2" step="0.1"
            placeholder="0.7"
          />
          <AppInput
            v-model.number="form.parameters.max_tokens"
            label="Max Tokens"
            type="number" min="1" max="128000"
            placeholder="4096"
          />
        </div>
      </div>
    </div>

    <template #footer>
      <AppButton variant="ghost" @click="$emit('close')">Cancel</AppButton>
      <AppButton variant="primary" :loading="saving" @click="save">
        {{ agent ? 'Save Changes' : 'Create Agent' }}
      </AppButton>
    </template>
  </AppModal>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useAgentStore } from '@/stores/agent'
import { useModels } from '@/composables/useModels'
import { useToast } from '@/composables/useToast'
import AppModal from '@/components/ui/AppModal.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppTextarea from '@/components/ui/AppTextarea.vue'

const props = defineProps({
  open:  { type: Boolean, required: true },
  agent: { type: Object,  default: null },
})
const emit = defineEmits(['close', 'saved'])

const agentStore = useAgentStore()
const toast      = useToast()
const { groupedModels, providerLabel, loadModels } = useModels()

const saving = ref(false)
const form   = ref(emptyForm())

function emptyForm() {
  return {
    name: '', description: '', model: 'groq/llama-3.3-70b-versatile',
    system_prompt: '', tool_ids: [], parameters: { temperature: 0.7 },
  }
}

watch(() => props.open, (open) => {
  if (open) {
    form.value = props.agent
      ? { ...props.agent, parameters: { ...props.agent.parameters } }
      : emptyForm()
  }
})

async function save() {
  if (!form.value.name || !form.value.model) return
  saving.value = true
  try {
    const payload = { ...form.value }
    // strip empty parameter keys
    Object.keys(payload.parameters).forEach(k => {
      if (payload.parameters[k] === '' || payload.parameters[k] === null) delete payload.parameters[k]
    })
    if (props.agent) {
      await agentStore.updateAgent(props.agent.id, payload)
    } else {
      await agentStore.createAgent(payload)
    }
    emit('saved')
  } catch {
    toast.error('Failed to save agent')
  } finally {
    saving.value = false
  }
}

onMounted(loadModels)
</script>

<style scoped>
.form-grid { display: flex; flex-direction: column; gap: 1.25rem; }
.field { display: flex; flex-direction: column; gap: 0.4rem; }
.field-label { font-size: 0.8rem; font-weight: 500; color: var(--color-text-muted); }
.required { color: var(--color-danger-text); }
.field-select {
  appearance: none;
  padding: 0.55rem 0.75rem;
  background: var(--color-surface-2);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  color: var(--color-text);
  outline: none;
  cursor: pointer;
  width: 100%;
}
.field-select:focus { border-color: var(--color-primary); }
.field-select option { background: var(--color-surface-2); }
.section-label { font-size: 0.8rem; font-weight: 600; color: var(--color-text-muted); margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 0.04em; }
.params-grid   { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
</style>
