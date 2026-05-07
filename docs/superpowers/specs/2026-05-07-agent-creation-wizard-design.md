# Agent Creation Wizard — Design Spec

## Goal
Replace the existing limited `AgentFormModal.vue` create flow with a full-page, 4-step wizard at `/agents/new` that covers all backend schema fields and matches the amber terminal theme.

## Architecture
Single page (`AgentCreateView.vue`) owns all wizard state (current step + form data). Four step sub-components receive the form object via props and emit field updates. On final submit, the page calls `agentService.create()` and redirects to `/registry/agents`.

## Tech Stack
Vue 3 Composition API, Pinia (`useAgentStore`), existing `agentService.js`, reusable UI components from `components/ui/` (Button, FormField, Select, Panel, Spinner).

---

## Routes

| Route | Name | Component |
|---|---|---|
| `/agents/new` | `AgentCreate` | `modules/agents/views/AgentCreateView.vue` |

Added to `router/routes.js` under the DefaultLayout children block, `requiresAuth: true`.

---

## File Structure

```
frontend/src/modules/agents/
  views/
    AgentCreateView.vue          ← page wrapper, stepper nav, submit
  components/
    wizard/
      AgentStepBasics.vue        ← step 1
      AgentStepSchemas.vue       ← step 2
      AgentStepAuth.vue          ← step 3
      AgentStepReview.vue        ← step 4
    WizardStepper.vue            ← reusable step-indicator bar
```

---

## Steps & Fields

### Step 1 — Basics
| Field | Type | Required | Default |
|---|---|---|---|
| name | text | ✓ | — |
| agent_type | select (enum) | ✓ | — |
| endpoint_url | text (url) | ✓ | — |
| model_provider | text | — | — |
| description | textarea | — | — |
| owner | text | — | — |
| version | text | — | `1.0.0` |
| status | select (enum) | — | `draft` |

`agent_type` options: `llm`, `rag`, `vision`, `multi_step_chain`, `tool_use`, `custom`
`status` options: `draft`, `active`, `deprecated`, `archived`

Validation before advancing: `name`, `agent_type`, `endpoint_url` must be non-empty.

### Step 2 — Schemas
Three JSON textarea fields (monospace, 8-row each):
- `input_schema` — JSON object, default `{}`
- `output_schema` — JSON object, default `{}`
- `config` — JSON object, default `{}`

Validation before advancing: each field must be valid parseable JSON. Show inline error on invalid JSON.

### Step 3 — Auth & tags
**Auth config** — button-group selector for method, then conditional fields:
- `none` → no extra fields, `auth_config = {}`
- `api_key` → header_name (text), secret_ref (text)
- `bearer_token` → header_name (text, default `Authorization`), secret_ref (text)
- `oauth` → token_url (text), client_id (text), client_secret_ref (text), scope (text)

The method + conditional fields are merged into the `auth_config` JSONB object on submit.

**Tags** — chip list; inline text input, Enter/comma to add a tag, × to remove. Stored as `tags: string[]`.

No required fields on this step; advancing is always valid.

### Step 4 — Review
Read-only summary of all entered data, grouped in sections matching the steps. Each section has an "Edit" button that jumps back to that step.
Submit button calls `agentService.create(payload)`. On success, toast "Agent created" + `router.push('/registry/agents')`. On error, toast the error message and stay on review.

---

## WizardStepper Component

Props: `steps: [{id, label}]`, `current: number` (1-based).
Renders the horizontal step bar: completed steps show a green check, the active step shows the amber number badge, future steps are dimmed.
No emits — navigation is controlled by the parent.

---

## Form State Shape

```js
{
  // Basics
  name: '',
  agent_type: '',
  endpoint_url: '',
  model_provider: '',
  description: '',
  owner: '',
  version: '1.0.0',
  status: 'draft',

  // Schemas (stored as strings in the editor, parsed to objects on submit)
  input_schema_str: '{}',
  output_schema_str: '{}',
  config_str: '{}',

  // Auth
  auth_method: 'none',   // ui-only field, not sent to API
  auth_header_name: 'Authorization',
  auth_secret_ref: '',
  auth_token_url: '',
  auth_client_id: '',
  auth_client_secret_ref: '',
  auth_scope: '',

  // Tags
  tags: [],
}
```

On submit, `AgentCreateView` assembles the final API payload:
```js
{
  name, agent_type, endpoint_url, model_provider, description,
  owner, version, status, tags,
  input_schema:  JSON.parse(input_schema_str),
  output_schema: JSON.parse(output_schema_str),
  config:        JSON.parse(config_str),
  auth_config:   buildAuthConfig(auth_method, ...),
  change_summary: 'Initial registration',
}
```

---

## Error Handling

- Per-step validation errors displayed inline below the relevant field using `FormField`'s error slot.
- API errors on submit shown via `useToast().error(msg)`, user stays on Review step to fix and retry.
- JSON parse errors shown inline on the Schemas step.

---

## Styling

- Amber `#F5A524` accent for active step indicator, field labels (uppercase mono), selected auth method chip, tag chips.
- Green `#22c55e` for completed step checkmarks.
- Follows the existing CSS custom property system (`--accent`, `--bg`, `--border`, `--text`, etc.).
- Stepper bar styled identically to the mockup approved by the user.
