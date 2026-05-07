<template>
  <div class="create-page">
    <!-- Page header -->
    <div class="create-header">
      <div>
        <div class="page-eyebrow mono faint">agents</div>
        <h1 class="page-title">Register a new agent</h1>
      </div>
    </div>

    <!-- Stepper -->
    <WizardStepper :steps="STEPS" :current="step" />

    <!-- Step panels -->
    <AgentStepBasics
      v-if="step === 1"
      :form="form"
      :errors="errors"
      @update="onUpdate"
    />
    <AgentStepSchemas
      v-else-if="step === 2"
      :form="form"
      :errors="errors"
      @update="onUpdate"
    />
    <AgentStepAuth
      v-else-if="step === 3"
      :form="form"
      :errors="errors"
      @update="onUpdate"
    />
    <AgentStepReview
      v-else-if="step === 4"
      :form="form"
      :saving="saving"
      @goto="step = $event"
      @submit="submit"
    />

    <!-- Navigation footer (not shown on review — review has its own) -->
    <div v-if="step < 4" class="create-footer">
      <Button variant="ghost" :disabled="step === 1" @click="step--">← Back</Button>
      <div class="footer-right">
        <Button variant="ghost" @click="router.push('/registry/agents')">Cancel</Button>
        <Button variant="primary" @click="advance">
          {{ step === 3 ? 'Review →' : 'Next →' }}
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { agentService } from '@/services/agentService'
import { useToast } from '@/composables/useToast'
import WizardStepper    from '../components/WizardStepper.vue'
import AgentStepBasics  from '../components/wizard/AgentStepBasics.vue'
import AgentStepSchemas from '../components/wizard/AgentStepSchemas.vue'
import AgentStepAuth    from '../components/wizard/AgentStepAuth.vue'
import AgentStepReview  from '../components/wizard/AgentStepReview.vue'
import Button from '@/components/ui/Button.vue'

const router = useRouter()
const toast  = useToast()

const STEPS = [
  { id: 'basics',  label: 'Basics' },
  { id: 'schemas', label: 'Schemas' },
  { id: 'auth',    label: 'Auth & tags' },
  { id: 'review',  label: 'Review' },
]

const step   = ref(1)
const saving = ref(false)
const errors = ref({})

const form = reactive({
  // Step 1 — Basics
  name:           '',
  agent_type:     '',
  endpoint_url:   '',
  model_provider: '',
  description:    '',
  owner:          '',
  version:        '1.0.0',
  status:         'draft',
  // Step 2 — Schemas (raw strings; parsed to objects on submit)
  input_schema_str:  '{}',
  output_schema_str: '{}',
  config_str:        '{}',
  // Step 3 — Auth
  auth_method:            'none',
  auth_header_name:       'Authorization',
  auth_secret_ref:        '',
  auth_token_url:         '',
  auth_client_id:         '',
  auth_client_secret_ref: '',
  auth_scope:             '',
  // Step 3 — Tags
  tags: [],
})

function onUpdate(field, value) {
  form[field] = value
}

function validateStep(n) {
  const e = {}
  if (n === 1) {
    if (!form.name.trim())         e.name = 'Required'
    if (!form.agent_type)          e.agent_type = 'Required'
    if (!form.endpoint_url.trim()) e.endpoint_url = 'Required'
  }
  if (n === 2) {
    for (const [key, label] of [
      ['input_schema_str',  'input_schema'],
      ['output_schema_str', 'output_schema'],
      ['config_str',        'config'],
    ]) {
      try { JSON.parse(form[key]) } catch { e[label] = 'Invalid JSON' }
    }
  }
  errors.value = e
  return Object.keys(e).length === 0
}

function advance() {
  if (validateStep(step.value)) step.value++
}

function buildAuthConfig() {
  const m = form.auth_method
  if (m === 'none') return {}
  if (m === 'api_key' || m === 'bearer_token') {
    return { method: m, header_name: form.auth_header_name, secret_ref: form.auth_secret_ref }
  }
  if (m === 'oauth') {
    return {
      method:            m,
      token_url:         form.auth_token_url,
      client_id:         form.auth_client_id,
      client_secret_ref: form.auth_client_secret_ref,
      scope:             form.auth_scope,
    }
  }
  return {}
}

async function submit() {
  saving.value = true
  try {
    await agentService.create({
      name:           form.name.trim(),
      agent_type:     form.agent_type,
      endpoint_url:   form.endpoint_url.trim(),
      model_provider: form.model_provider || null,
      description:    form.description    || null,
      owner:          form.owner          || null,
      version:        form.version        || '1.0.0',
      status:         form.status,
      tags:           form.tags,
      input_schema:   JSON.parse(form.input_schema_str),
      output_schema:  JSON.parse(form.output_schema_str),
      config:         JSON.parse(form.config_str),
      auth_config:    buildAuthConfig(),
      change_summary: 'Initial registration',
    })
    toast.success('Agent created')
    router.push('/registry/agents')
  } catch (err) {
    toast.error(err?.response?.data?.detail || 'Failed to create agent')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.create-page {
  display: flex;
  flex-direction: column;
  gap: 0;
  max-width: 720px;
}

.create-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  margin-bottom: 24px;
}
.page-eyebrow { font-size: 10.5px; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 4px; }
.page-title   { font-size: 22px; font-weight: 600; letter-spacing: -0.02em; color: var(--text); }

.create-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 20px;
  border-top: 1px solid var(--border);
  margin-top: 8px;
}
.footer-right { display: flex; gap: 8px; }
</style>
