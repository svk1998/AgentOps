# Agent Creation Wizard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a 4-step wizard at `/agents/new` that lets users register a new agent, covering every backend schema field with proper per-step validation and the amber terminal visual design.

**Architecture:** `AgentCreateView.vue` owns all wizard state (current step number + a single reactive `form` object). Four step sub-components receive the form via props and emit field-level updates. On final submit, the view builds the API payload, calls `agentService.create()`, and redirects to `/registry/agents`.

**Tech Stack:** Vue 3 Composition API (`<script setup>`, `reactive`, `ref`, `computed`), Vue Router 4, existing `agentService.js`, reusable UI components from `src/components/ui/` (Button, FormField, Panel), `AGENT_TYPES`/`AGENT_STATUSES` from `src/constants/enums.js`.

---

## File Map

| Action | Path | Purpose |
|---|---|---|
| Create | `src/modules/agents/views/AgentCreateView.vue` | Page wrapper — stepper state, per-step validation, submit |
| Create | `src/modules/agents/components/WizardStepper.vue` | Horizontal step indicator bar |
| Create | `src/modules/agents/components/wizard/AgentStepBasics.vue` | Step 1 — core identity fields |
| Create | `src/modules/agents/components/wizard/AgentStepSchemas.vue` | Step 2 — JSON schema editors |
| Create | `src/modules/agents/components/wizard/AgentStepAuth.vue` | Step 3 — auth method + tags |
| Create | `src/modules/agents/components/wizard/AgentStepReview.vue` | Step 4 — read-only summary + submit |
| Modify | `src/router/routes.js` | Add `/agents/new` route |
| Modify | `src/modules/registry/views/AgentsView.vue` | Wire "New agent" button to route |

---

## Task 1: WizardStepper component

**Files:**
- Create: `frontend/src/modules/agents/components/WizardStepper.vue`

- [ ] **Step 1.1: Create the component**

```vue
<!-- frontend/src/modules/agents/components/WizardStepper.vue -->
<template>
  <div class="stepper">
    <template v-for="(s, i) in steps" :key="s.id">
      <div class="step">
        <div class="step-circle" :class="circleClass(i + 1)">
          <Check v-if="i + 1 < current" :size="12" :stroke-width="2.5" />
          <span v-else>{{ i + 1 }}</span>
        </div>
        <span class="step-label" :class="labelClass(i + 1)">{{ s.label }}</span>
      </div>
      <div
        v-if="i < steps.length - 1"
        class="step-connector"
        :class="{ 'step-connector--done': i + 1 < current }"
      />
    </template>
  </div>
</template>

<script setup>
import { Check } from 'lucide-vue-next'

const props = defineProps({
  steps:   { type: Array,  required: true },  // [{ id: string, label: string }]
  current: { type: Number, required: true },  // 1-based active step index
})

function circleClass(n) {
  if (n < props.current)  return 'step-circle--done'
  if (n === props.current) return 'step-circle--active'
  return 'step-circle--todo'
}

function labelClass(n) {
  if (n < props.current)  return 'step-label--done'
  if (n === props.current) return 'step-label--active'
  return 'step-label--todo'
}
</script>

<style scoped>
.stepper {
  display: flex;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 28px;
}

.step { display: flex; align-items: center; gap: 8px; }

.step-circle {
  width: 24px; height: 24px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 600; flex-shrink: 0;
  transition: background 0.15s;
}
.step-circle--done   { background: #22c55e; color: #fff; }
.step-circle--active { background: var(--accent); color: var(--accent-text, #0A0B0D); }
.step-circle--todo   { background: var(--bg-elev); border: 1px solid var(--border); color: var(--text-faint); }

.step-label { font-size: 12px; font-weight: 500; white-space: nowrap; }
.step-label--done   { color: #22c55e; }
.step-label--active { color: var(--accent); }
.step-label--todo   { color: var(--text-faint); }

.step-connector {
  flex: 1; height: 1px;
  min-width: 24px; max-width: 72px;
  margin: 0 6px;
  background: var(--border);
  transition: background 0.15s;
}
.step-connector--done { background: rgba(34, 197, 94, 0.35); }
</style>
```

- [ ] **Step 1.2: Commit**

```bash
git add frontend/src/modules/agents/components/WizardStepper.vue
git commit -m "feat(agents): add WizardStepper component"
```

---

## Task 2: AgentCreateView — skeleton + form state

**Files:**
- Create: `frontend/src/modules/agents/views/AgentCreateView.vue`

- [ ] **Step 2.1: Create the view with form state, step navigation, and step slot**

```vue
<!-- frontend/src/modules/agents/views/AgentCreateView.vue -->
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
import WizardStepper from '../components/WizardStepper.vue'
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
  name:          '',
  agent_type:    '',
  endpoint_url:  '',
  model_provider: '',
  description:   '',
  owner:         '',
  version:       '1.0.0',
  status:        'draft',
  // Step 2 — Schemas (raw strings; parsed to objects on submit)
  input_schema_str:  '{}',
  output_schema_str: '{}',
  config_str:        '{}',
  // Step 3 — Auth
  auth_method:          'none',
  auth_header_name:     'Authorization',
  auth_secret_ref:      '',
  auth_token_url:       '',
  auth_client_id:       '',
  auth_client_secret_ref: '',
  auth_scope:           '',
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
      method: m,
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
.create-page { display: flex; flex-direction: column; gap: 0; max-width: 720px; }

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
```

- [ ] **Step 2.2: Commit**

```bash
git add frontend/src/modules/agents/views/AgentCreateView.vue
git commit -m "feat(agents): add AgentCreateView skeleton with form state"
```

---

## Task 3: Route + "New agent" button

**Files:**
- Modify: `frontend/src/router/routes.js`
- Modify: `frontend/src/modules/registry/views/AgentsView.vue`

- [ ] **Step 3.1: Add the route**

In `frontend/src/router/routes.js`, inside the DefaultLayout children array, add after the `RegistryAgents` entry:

```js
{
  path: 'agents/new',
  name: 'AgentCreate',
  component: () => import('@/modules/agents/views/AgentCreateView.vue'),
  meta: { requiresAuth: true, title: 'New Agent' }
},
```

The full block after editing (just the relevant section):
```js
// Registry
{
  path: 'registry/agents',
  name: 'RegistryAgents',
  component: () => import('@/modules/registry/views/AgentsView.vue'),
  meta: { requiresAuth: true, title: 'Agents' }
},
{
  path: 'agents/new',
  name: 'AgentCreate',
  component: () => import('@/modules/agents/views/AgentCreateView.vue'),
  meta: { requiresAuth: true, title: 'New Agent' }
},
```

- [ ] **Step 3.2: Wire the "New agent" button in AgentsView**

In `frontend/src/modules/registry/views/AgentsView.vue`, the script setup block imports `useRouter` at the top (add if not present):

```js
import { useRouter } from 'vue-router'
const router = useRouter()
```

Replace the `createNew` function (currently at ~line 156):

```js
// Before:
function createNew() {
  // Placeholder — full create form lives at /registry/agents/new in future iterations
  error.value = 'Agent creation form coming next iteration'
}

// After:
function createNew() {
  router.push('/agents/new')
}
```

- [ ] **Step 3.3: Commit**

```bash
git add frontend/src/router/routes.js frontend/src/modules/registry/views/AgentsView.vue
git commit -m "feat(agents): add /agents/new route and wire New Agent button"
```

---

## Task 4: AgentStepBasics

**Files:**
- Create: `frontend/src/modules/agents/components/wizard/AgentStepBasics.vue`

- [ ] **Step 4.1: Create the component**

```vue
<!-- frontend/src/modules/agents/components/wizard/AgentStepBasics.vue -->
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
.input:focus { border-color: var(--accent); }
.input--err  { border-color: var(--err); }
select.input { cursor: pointer; appearance: none; }
.textarea { resize: vertical; line-height: 1.5; }
</style>
```

- [ ] **Step 4.2: Commit**

```bash
git add frontend/src/modules/agents/components/wizard/AgentStepBasics.vue
git commit -m "feat(agents): add wizard step 1 — Basics"
```

---

## Task 5: AgentStepSchemas

**Files:**
- Create: `frontend/src/modules/agents/components/wizard/AgentStepSchemas.vue`

- [ ] **Step 5.1: Create the component**

```vue
<!-- frontend/src/modules/agents/components/wizard/AgentStepSchemas.vue -->
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
    key: 'input_schema_str',
    errorKey: 'input_schema',
    label: 'Input schema',
    help: 'JSON object describing the input this agent accepts',
  },
  {
    key: 'output_schema_str',
    errorKey: 'output_schema',
    label: 'Output schema',
    help: 'JSON object describing what this agent returns',
  },
  {
    key: 'config_str',
    errorKey: 'config',
    label: 'Config',
    help: 'Additional runtime configuration (model params, thresholds, etc.)',
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
.json-editor:focus  { border-color: var(--accent); }
.json-editor--err   { border-color: var(--err); }
</style>
```

- [ ] **Step 5.2: Commit**

```bash
git add frontend/src/modules/agents/components/wizard/AgentStepSchemas.vue
git commit -m "feat(agents): add wizard step 2 — Schemas"
```

---

## Task 6: AgentStepAuth

**Files:**
- Create: `frontend/src/modules/agents/components/wizard/AgentStepAuth.vue`

- [ ] **Step 6.1: Create the component**

```vue
<!-- frontend/src/modules/agents/components/wizard/AgentStepAuth.vue -->
<template>
  <div class="step-card">
    <h2 class="step-title">Auth &amp; tags</h2>

    <!-- Auth method selector -->
    <FormField label="Auth method" class="field">
      <template #default>
        <div class="method-group">
          <button
            v-for="m in AUTH_METHODS"
            :key="m"
            type="button"
            class="method-chip"
            :class="{ 'method-chip--active': form.auth_method === m }"
            @click="emit('update', 'auth_method', m)"
          >{{ m }}</button>
        </div>
      </template>
    </FormField>

    <!-- api_key / bearer_token conditional fields -->
    <template v-if="form.auth_method === 'api_key' || form.auth_method === 'bearer_token'">
      <FormField label="Header name" class="field">
        <template #default="{ id }">
          <input
            :id="id"
            class="input"
            :value="form.auth_header_name"
            placeholder="Authorization"
            @input="emit('update', 'auth_header_name', $event.target.value)"
          />
        </template>
      </FormField>

      <FormField
        label="Secret reference"
        help="Stored encrypted; resolved at eval-time"
        class="field"
      >
        <template #default="{ id }">
          <input
            :id="id"
            class="input"
            :value="form.auth_secret_ref"
            placeholder="secrets://my-agent/token"
            @input="emit('update', 'auth_secret_ref', $event.target.value)"
          />
        </template>
      </FormField>
    </template>

    <!-- oauth conditional fields -->
    <template v-if="form.auth_method === 'oauth'">
      <FormField label="Token URL" class="field">
        <template #default="{ id }">
          <input
            :id="id"
            class="input"
            :value="form.auth_token_url"
            placeholder="https://auth.example.com/oauth/token"
            @input="emit('update', 'auth_token_url', $event.target.value)"
          />
        </template>
      </FormField>

      <div class="two-col">
        <FormField label="Client ID">
          <template #default="{ id }">
            <input
              :id="id"
              class="input"
              :value="form.auth_client_id"
              placeholder="client-id"
              @input="emit('update', 'auth_client_id', $event.target.value)"
            />
          </template>
        </FormField>

        <FormField label="Client secret ref" help="Stored encrypted">
          <template #default="{ id }">
            <input
              :id="id"
              class="input"
              :value="form.auth_client_secret_ref"
              placeholder="secrets://my-agent/oauth-secret"
              @input="emit('update', 'auth_client_secret_ref', $event.target.value)"
            />
          </template>
        </FormField>
      </div>

      <FormField label="Scope" help="Space-separated OAuth scopes" class="field">
        <template #default="{ id }">
          <input
            :id="id"
            class="input"
            :value="form.auth_scope"
            placeholder="read write"
            @input="emit('update', 'auth_scope', $event.target.value)"
          />
        </template>
      </FormField>
    </template>

    <!-- Tags -->
    <FormField label="Tags" help="Press Enter or comma to add" class="field tags-field">
      <template #default>
        <div class="tags-wrap">
          <span
            v-for="tag in form.tags"
            :key="tag"
            class="tag-chip"
          >
            <Tag :size="10" :stroke-width="1.8" />
            {{ tag }}
            <button type="button" class="tag-rm" @click="removeTag(tag)">×</button>
          </span>
          <input
            v-model="tagInput"
            class="tag-input"
            placeholder="+ add tag"
            @keydown.enter.prevent="addTag"
            @keydown.comma.prevent="addTag"
          />
        </div>
      </template>
    </FormField>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Tag } from 'lucide-vue-next'
import FormField from '@/components/ui/FormField.vue'

const AUTH_METHODS = ['none', 'api_key', 'bearer_token', 'oauth']

const props = defineProps({
  form:   { type: Object, required: true },
  errors: { type: Object, required: true },
})

const emit = defineEmits(['update'])

const tagInput = ref('')

function addTag() {
  const val = tagInput.value.trim().replace(/,$/, '')
  if (val && !props.form.tags.includes(val)) {
    emit('update', 'tags', [...props.form.tags, val])
  }
  tagInput.value = ''
}

function removeTag(tag) {
  emit('update', 'tags', props.form.tags.filter(t => t !== tag))
}
</script>

<style scoped>
.step-card {
  background: var(--bg-elev);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 28px 32px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}
.step-title { font-size: 14px; font-weight: 600; color: var(--text); }

.field { /* inherits flex-col from FormField */ }

.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }

.method-group { display: flex; gap: 6px; flex-wrap: wrap; }
.method-chip {
  padding: 5px 12px; border-radius: 4px;
  font-size: 12px; font-family: var(--mono, monospace);
  border: 1px solid var(--border); background: var(--bg); color: var(--text-dim);
  cursor: pointer; transition: border-color 0.1s, color 0.1s, background 0.1s;
}
.method-chip:hover { border-color: var(--accent); color: var(--text); }
.method-chip--active {
  border-color: var(--accent);
  background: rgba(245, 165, 36, 0.1);
  color: var(--accent);
}

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
.input:focus { border-color: var(--accent); }

/* Tags */
.tags-wrap {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  min-height: 36px;
  padding: 5px 8px;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--r-sm, 4px);
  transition: border-color 0.1s;
}
.tags-wrap:focus-within { border-color: var(--accent); }

.tag-chip {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 2px 7px 2px 6px; border-radius: 999px;
  background: rgba(245, 165, 36, 0.12);
  border: 1px solid rgba(245, 165, 36, 0.3);
  color: var(--accent); font-size: 11px;
  font-family: var(--mono, monospace);
}
.tag-rm {
  background: none; border: none; color: var(--accent); opacity: 0.7;
  font-size: 13px; line-height: 1; cursor: pointer; padding: 0 1px;
}
.tag-rm:hover { opacity: 1; }

.tag-input {
  border: none; outline: none; background: transparent;
  color: var(--text); font-size: 12px; min-width: 80px; flex: 1;
}
</style>
```

- [ ] **Step 6.2: Commit**

```bash
git add frontend/src/modules/agents/components/wizard/AgentStepAuth.vue
git commit -m "feat(agents): add wizard step 3 — Auth & tags"
```

---

## Task 7: AgentStepReview

**Files:**
- Create: `frontend/src/modules/agents/components/wizard/AgentStepReview.vue`

- [ ] **Step 7.1: Create the component**

```vue
<!-- frontend/src/modules/agents/components/wizard/AgentStepReview.vue -->
<template>
  <div class="review-card">
    <h2 class="step-title">Review &amp; create</h2>
    <p class="step-sub">Check everything looks right, then create the agent.</p>

    <!-- Section: Basics -->
    <div class="review-section">
      <div class="section-header">
        <span class="section-label mono">Basics</span>
        <button type="button" class="edit-btn" @click="emit('goto', 1)">edit</button>
      </div>
      <div class="review-grid">
        <ReviewRow label="Name"           :value="form.name" />
        <ReviewRow label="Type"           :value="form.agent_type" />
        <ReviewRow label="Endpoint URL"   :value="form.endpoint_url" mono />
        <ReviewRow label="Model provider" :value="form.model_provider || '—'" />
        <ReviewRow label="Owner"          :value="form.owner || '—'" />
        <ReviewRow label="Version"        :value="form.version" />
        <ReviewRow label="Status"         :value="form.status" />
        <ReviewRow v-if="form.description" label="Description" :value="form.description" class="full" />
      </div>
    </div>

    <!-- Section: Schemas -->
    <div class="review-section">
      <div class="section-header">
        <span class="section-label mono">Schemas</span>
        <button type="button" class="edit-btn" @click="emit('goto', 2)">edit</button>
      </div>
      <div class="review-grid">
        <ReviewRow label="Input schema"  :value="form.input_schema_str"  mono class="full" />
        <ReviewRow label="Output schema" :value="form.output_schema_str" mono class="full" />
        <ReviewRow label="Config"        :value="form.config_str"        mono class="full" />
      </div>
    </div>

    <!-- Section: Auth & tags -->
    <div class="review-section">
      <div class="section-header">
        <span class="section-label mono">Auth &amp; tags</span>
        <button type="button" class="edit-btn" @click="emit('goto', 3)">edit</button>
      </div>
      <div class="review-grid">
        <ReviewRow label="Auth method" :value="form.auth_method" />
        <template v-if="form.auth_method !== 'none'">
          <ReviewRow v-if="form.auth_method === 'oauth'" label="Token URL"   :value="form.auth_token_url"   mono />
          <ReviewRow v-if="form.auth_method === 'oauth'" label="Client ID"   :value="form.auth_client_id"   mono />
          <ReviewRow v-if="form.auth_method !== 'oauth'" label="Header name" :value="form.auth_header_name" mono />
          <ReviewRow v-if="form.auth_method !== 'oauth'" label="Secret ref"  :value="form.auth_secret_ref || '—'" mono />
        </template>
        <div class="full">
          <div class="review-label mono">Tags</div>
          <div v-if="form.tags.length" class="tags-row">
            <span v-for="t in form.tags" :key="t" class="tag-chip">{{ t }}</span>
          </div>
          <span v-else class="review-value faint">—</span>
        </div>
      </div>
    </div>

    <!-- Submit footer -->
    <div class="review-footer">
      <button type="button" class="btn-ghost" @click="emit('goto', 3)">← Back</button>
      <Button variant="primary" :loading="saving" @click="emit('submit')">
        Create agent
      </Button>
    </div>
  </div>
</template>

<script setup>
import Button from '@/components/ui/Button.vue'

defineProps({
  form:   { type: Object,  required: true },
  saving: { type: Boolean, default: false },
})

const emit = defineEmits(['goto', 'submit'])
</script>

<!-- ReviewRow used inline as a local sub-component pattern isn't available in SFC,
     so we define a tiny helper via a second script block trick — instead use a simple
     template-level helper div rendered inline below -->

<style scoped>
.review-card {
  background: var(--bg-elev);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 28px 32px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.step-title { font-size: 14px; font-weight: 600; color: var(--text); }
.step-sub   { font-size: 12px; color: var(--text-dim); margin-top: -18px; }

.review-section { display: flex; flex-direction: column; gap: 10px; }
.section-header { display: flex; align-items: center; justify-content: space-between; }
.section-label  { font-size: 10px; letter-spacing: 0.08em; text-transform: uppercase; color: var(--accent); }
.edit-btn {
  font-size: 11px; color: var(--accent); background: none;
  border: none; cursor: pointer; padding: 0;
  text-decoration: underline; text-underline-offset: 2px;
}

.review-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px 20px;
  padding: 14px;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--r-sm, 4px);
}
.full { grid-column: span 2; }

.review-label { font-size: 10px; letter-spacing: 0.06em; text-transform: uppercase; color: var(--text-faint); margin-bottom: 3px; }
.review-value { font-size: 12.5px; color: var(--text); word-break: break-all; }
.review-value.mono { font-family: var(--mono, monospace); font-size: 11.5px; white-space: pre-wrap; }
.faint { color: var(--text-faint); }

.tags-row { display: flex; gap: 5px; flex-wrap: wrap; }
.tag-chip {
  display: inline-flex; align-items: center;
  padding: 2px 7px; border-radius: 999px;
  background: rgba(245, 165, 36, 0.12);
  border: 1px solid rgba(245, 165, 36, 0.3);
  color: var(--accent); font-size: 11px;
  font-family: var(--mono, monospace);
}

.review-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid var(--border);
}
.btn-ghost {
  padding: 7px 14px; border-radius: 5px;
  font-size: 12.5px; font-weight: 500;
  background: transparent; border: 1px solid var(--border);
  color: var(--text-dim); cursor: pointer;
  transition: color 0.1s, border-color 0.1s;
}
.btn-ghost:hover { color: var(--text); border-color: var(--text-dim); }
</style>
```

**Note:** `ReviewRow` references in the template above render a two-div block. Replace each `<ReviewRow label="X" :value="Y" />` with the following inline pattern:

```html
<div>
  <div class="review-label mono">X</div>
  <div class="review-value">Y</div>
</div>
```

For the `mono` variant add class `mono` to `.review-value`. For `full`, add class `full` to the outer `<div>`.

- [ ] **Step 7.2: Replace `<ReviewRow>` shorthand with inline divs**

Edit the template in `AgentStepReview.vue` and replace every `<ReviewRow ... />` call with the inline pattern. Full expanded template for the Basics section (repeat pattern for Schemas / Auth):

```html
<!-- Basics grid -->
<div class="review-grid">
  <div>
    <div class="review-label mono">Name</div>
    <div class="review-value">{{ form.name }}</div>
  </div>
  <div>
    <div class="review-label mono">Type</div>
    <div class="review-value">{{ form.agent_type }}</div>
  </div>
  <div class="full">
    <div class="review-label mono">Endpoint URL</div>
    <div class="review-value mono">{{ form.endpoint_url }}</div>
  </div>
  <div>
    <div class="review-label mono">Model provider</div>
    <div class="review-value">{{ form.model_provider || '—' }}</div>
  </div>
  <div>
    <div class="review-label mono">Owner</div>
    <div class="review-value">{{ form.owner || '—' }}</div>
  </div>
  <div>
    <div class="review-label mono">Version</div>
    <div class="review-value">{{ form.version }}</div>
  </div>
  <div>
    <div class="review-label mono">Status</div>
    <div class="review-value">{{ form.status }}</div>
  </div>
  <div v-if="form.description" class="full">
    <div class="review-label mono">Description</div>
    <div class="review-value">{{ form.description }}</div>
  </div>
</div>
```

Apply the same pattern for the Schemas grid and Auth grid rows.

- [ ] **Step 7.3: Commit**

```bash
git add frontend/src/modules/agents/components/wizard/AgentStepReview.vue
git commit -m "feat(agents): add wizard step 4 — Review & submit"
```

---

## Task 8: Smoke-test in browser

The dev server must be running (`npm run dev` from `frontend/`). Backend must be running (`uvicorn main:app --reload` from `backend/`).

- [ ] **Step 8.1: Navigate to `/agents/new` and verify the stepper renders**

Expected: page title "Register a new agent", four-step bar with "Basics" active in amber, steps 2-4 dimmed.

- [ ] **Step 8.2: Test Basics validation**

Click "Next →" without filling anything. Expected: three inline errors — "Required" under Name, Agent type, and Endpoint URL. Stepper does NOT advance.

- [ ] **Step 8.3: Fill Basics and advance**

Fill Name = `test-agent`, pick any type from the dropdown, Endpoint URL = `http://localhost:9000`. Click "Next →". Expected: stepper moves to step 2 (Schemas), Basics circle turns green.

- [ ] **Step 8.4: Test Schemas validation**

Clear the `input_schema` textarea and type `not json`. Click "Next →". Expected: "Invalid JSON" error appears under input_schema. Fix it back to `{}`, all three fields valid, advance to step 3.

- [ ] **Step 8.5: Test Auth method switching**

Click through `api_key`, `bearer_token`, `oauth` chips. Expected: conditional fields appear/disappear correctly. Add two tags (type name, press Enter). Advance to Review.

- [ ] **Step 8.6: Verify Review step**

All three sections display correct values. Edit buttons jump back to the correct step. "Create agent" button is visible.

- [ ] **Step 8.7: Submit (requires live backend)**

Fill valid data and submit. Expected: toast "Agent created", redirect to `/registry/agents`, agent appears in the list.

- [ ] **Step 8.8: Commit final verification note**

```bash
git add -A
git commit -m "feat(agents): complete 4-step agent creation wizard"
```

---

## Self-Review

**Spec coverage check:**
- ✅ Route `/agents/new` → Task 3
- ✅ WizardStepper component → Task 1
- ✅ Step 1 Basics — all 8 fields → Task 4
- ✅ Step 2 Schemas — 3 JSON editors with validation → Task 5
- ✅ Step 3 Auth — 4 methods + conditional fields + tags → Task 6
- ✅ Step 4 Review — read-only summary + goto buttons + submit → Task 7
- ✅ Per-step validation before advancing → AgentCreateView `validateStep()`
- ✅ `buildAuthConfig()` assembles `auth_config` correctly → AgentCreateView
- ✅ `buildPayload()` / submit calls `agentService.create()` → AgentCreateView
- ✅ Toast on success/error → AgentCreateView
- ✅ Redirect to `/registry/agents` on success → AgentCreateView
- ✅ "New agent" button in AgentsView wired to route → Task 3

**Placeholder scan:** None found.

**Type consistency:** `form` object keys in `AgentCreateView` match every `form[field]` access in step components. `emit('update', field, value)` pattern is consistent across all step components.
