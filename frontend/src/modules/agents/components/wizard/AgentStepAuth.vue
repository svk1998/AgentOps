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
    <FormField label="Tags" help="Press Enter or comma to add" class="field">
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
            @keydown.exact.prevent.capture="onKeydown"
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

function onKeydown(e) {
  if (e.key === ',') {
    e.preventDefault()
    addTag()
  }
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
