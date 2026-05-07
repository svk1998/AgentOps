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
    </div>

    <!-- Section: Schemas -->
    <div class="review-section">
      <div class="section-header">
        <span class="section-label mono">Schemas</span>
        <button type="button" class="edit-btn" @click="emit('goto', 2)">edit</button>
      </div>
      <div class="review-grid">
        <div class="full">
          <div class="review-label mono">Input schema</div>
          <div class="review-value mono">{{ form.input_schema_str }}</div>
        </div>
        <div class="full">
          <div class="review-label mono">Output schema</div>
          <div class="review-value mono">{{ form.output_schema_str }}</div>
        </div>
        <div class="full">
          <div class="review-label mono">Config</div>
          <div class="review-value mono">{{ form.config_str }}</div>
        </div>
      </div>
    </div>

    <!-- Section: Auth & tags -->
    <div class="review-section">
      <div class="section-header">
        <span class="section-label mono">Auth &amp; tags</span>
        <button type="button" class="edit-btn" @click="emit('goto', 3)">edit</button>
      </div>
      <div class="review-grid">
        <div>
          <div class="review-label mono">Auth method</div>
          <div class="review-value">{{ form.auth_method }}</div>
        </div>
        <template v-if="form.auth_method === 'api_key' || form.auth_method === 'bearer_token'">
          <div>
            <div class="review-label mono">Header name</div>
            <div class="review-value mono">{{ form.auth_header_name }}</div>
          </div>
          <div>
            <div class="review-label mono">Secret ref</div>
            <div class="review-value mono">{{ form.auth_secret_ref || '—' }}</div>
          </div>
        </template>
        <template v-if="form.auth_method === 'oauth'">
          <div class="full">
            <div class="review-label mono">Token URL</div>
            <div class="review-value mono">{{ form.auth_token_url }}</div>
          </div>
          <div>
            <div class="review-label mono">Client ID</div>
            <div class="review-value mono">{{ form.auth_client_id }}</div>
          </div>
          <div>
            <div class="review-label mono">Client secret ref</div>
            <div class="review-value mono">{{ form.auth_client_secret_ref || '—' }}</div>
          </div>
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
.section-header {
  display: flex; align-items: center; justify-content: space-between;
  padding-bottom: 4px;
  border-bottom: 1px solid var(--border);
}
.section-label { font-size: 10px; letter-spacing: 0.08em; text-transform: uppercase; color: var(--accent); }
.edit-btn {
  font-size: 11px; color: var(--accent); background: none;
  border: none; cursor: pointer; padding: 0;
  text-decoration: underline; text-underline-offset: 2px;
  opacity: 0.75; transition: opacity 0.1s;
}
.edit-btn:hover { opacity: 1; }

.review-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px 24px;
  padding: 14px;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--r-sm, 4px);
}
.full { grid-column: span 2; }

.review-label { font-size: 10px; letter-spacing: 0.06em; text-transform: uppercase; color: var(--text-faint); margin-bottom: 3px; }
.review-value { font-size: 12.5px; color: var(--text); word-break: break-all; }
.review-value.mono { font-family: var(--mono, monospace); font-size: 11.5px; white-space: pre-wrap; }
.faint { font-size: 12.5px; color: var(--text-faint); }

.tags-row { display: flex; gap: 5px; flex-wrap: wrap; margin-top: 2px; }
.tag-chip {
  display: inline-flex; align-items: center;
  padding: 2px 8px; border-radius: 999px;
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
