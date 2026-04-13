<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Tools</h1>
        <p class="page-subtitle">{{ tools.length }} tools registered</p>
      </div>
      <AppButton v-if="isAdmin" @click="openCreate">+ New Tool</AppButton>
    </div>

    <AppEmptyState
      v-if="!loading && !tools.length"
      title="No tools registered"
      description="Tools extend what your agents can do — file operations, API calls, database queries, and more."
      :action-label="isAdmin ? 'Register Tool' : ''"
      @action="openCreate"
    >
      <template #icon>🔧</template>
    </AppEmptyState>

    <div v-else class="tools-grid">
      <div v-for="tool in tools" :key="tool.id" class="tool-card">
        <div class="tool-card__header">
          <div class="tool-icon">⚙</div>
          <div class="tool-meta">
            <h3 class="tool-name">{{ tool.name }}</h3>
            <AppBadge :variant="tool.is_active ? 'success' : 'neutral'">
              {{ tool.is_active ? 'Active' : 'Inactive' }}
            </AppBadge>
          </div>
          <div v-if="isAdmin" class="tool-actions">
            <AppButton variant="ghost" size="sm" @click="openEdit(tool)">Edit</AppButton>
            <AppButton variant="ghost" size="sm" @click="confirmDelete(tool)">Delete</AppButton>
          </div>
        </div>
        <p class="tool-desc">{{ tool.description || 'No description.' }}</p>
        <div class="tool-handler font-mono">{{ tool.handler }}</div>
        <div v-if="tool.input_schema" class="tool-schema">
          <p class="schema-label">Parameters</p>
          <div class="schema-props">
            <span
              v-for="(prop, key) in tool.input_schema?.properties"
              :key="key"
              class="schema-tag"
              :title="prop.description"
            >
              {{ key }}<span class="schema-type">: {{ prop.type }}</span>
            </span>
          </div>
        </div>
      </div>

      <!-- Loading skeletons -->
      <div v-if="loading" v-for="n in 3" :key="n" class="tool-skeleton" />
    </div>

    <!-- Form modal -->
    <AppModal :open="formOpen" :title="editTarget ? 'Edit Tool' : 'Register Tool'" size="lg" @close="formOpen = false">
      <div class="tool-form">
        <AppInput v-model="form.name" label="Name" required placeholder="web_search" />
        <AppInput v-model="form.description" label="Description" placeholder="Search the web for information" />
        <AppInput v-model="form.handler" label="Handler" required placeholder="app.tools.web.search" hint="Dotted Python path to the handler function" />
        <AppTextarea
          v-model="schemaJson"
          label="Input Schema (JSON)"
          :mono="true"
          :rows="6"
          :error="schemaError"
          placeholder='{"type":"object","properties":{"query":{"type":"string"}}}'
        />
        <div class="form-toggle">
          <label class="toggle-label">
            <input type="checkbox" v-model="form.is_active" />
            Active
          </label>
        </div>
      </div>
      <template #footer>
        <AppButton variant="ghost" @click="formOpen = false">Cancel</AppButton>
        <AppButton variant="primary" :loading="saving" @click="save">
          {{ editTarget ? 'Save Changes' : 'Register Tool' }}
        </AppButton>
      </template>
    </AppModal>

    <ConfirmDialog
      :open="deleteOpen"
      title="Delete Tool"
      :message="`Delete '${deleteTarget?.name}'? Agents using this tool will lose access.`"
      confirm-label="Delete"
      @confirm="doDelete"
      @cancel="deleteOpen = false"
    />
  </div>
</template>

<script setup>
import { ref, watch, onMounted, computed } from 'vue'
import { toolService } from '@/services/toolService'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import AppButton from '@/components/ui/AppButton.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppModal from '@/components/ui/AppModal.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppTextarea from '@/components/ui/AppTextarea.vue'
import AppEmptyState from '@/components/ui/AppEmptyState.vue'
import ConfirmDialog from '@/components/ui/ConfirmDialog.vue'

const auth    = useAuthStore()
const toast   = useToast()
const isAdmin = computed(() => auth.isAdmin)

const tools       = ref([])
const loading     = ref(false)
const formOpen    = ref(false)
const saving      = ref(false)
const editTarget  = ref(null)
const deleteOpen  = ref(false)
const deleteTarget = ref(null)
const schemaJson  = ref('')
const schemaError = ref('')

const form = ref(emptyForm())
function emptyForm() {
  return { name: '', description: '', handler: '', input_schema: null, config: null, is_active: true }
}

watch(schemaJson, (v) => {
  if (!v.trim()) { schemaError.value = ''; form.value.input_schema = null; return }
  try { form.value.input_schema = JSON.parse(v); schemaError.value = '' }
  catch { schemaError.value = 'Invalid JSON' }
})

function openCreate() { editTarget.value = null; form.value = emptyForm(); schemaJson.value = ''; formOpen.value = true }
function openEdit(t)  {
  editTarget.value = t
  form.value = { ...t }
  schemaJson.value = t.input_schema ? JSON.stringify(t.input_schema, null, 2) : ''
  formOpen.value = true
}
function confirmDelete(t) { deleteTarget.value = t; deleteOpen.value = true }

async function save() {
  if (schemaError.value) return
  saving.value = true
  try {
    if (editTarget.value) {
      const updated = await toolService.update(editTarget.value.id, form.value)
      const idx = tools.value.findIndex(t => t.id === editTarget.value.id)
      if (idx !== -1) tools.value[idx] = updated.data
    } else {
      const created = await toolService.create(form.value)
      tools.value.unshift(created.data)
    }
    formOpen.value = false
    toast.success('Tool saved!')
  } catch { toast.error('Failed to save tool') }
  finally  { saving.value = false }
}

async function doDelete() {
  try {
    await toolService.delete(deleteTarget.value.id)
    tools.value = tools.value.filter(t => t.id !== deleteTarget.value.id)
    toast.success('Tool deleted')
  } catch { toast.error('Delete failed') }
  deleteOpen.value = false
}

onMounted(async () => {
  loading.value = true
  try {
    const { data } = await toolService.getAll(isAdmin.value ? { include_inactive: true } : {})
    tools.value = data
  } finally { loading.value = false }
})
</script>

<style scoped>
.page { display: flex; flex-direction: column; gap: 1.5rem; }
.page-header { display: flex; align-items: flex-start; justify-content: space-between; }
.page-title  { font-size: 1.4rem; font-weight: 700; }
.page-subtitle { color: var(--color-text-muted); font-size: 0.875rem; margin-top: 0.2rem; }

.tools-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 1rem; }
.tool-skeleton {
  height: 180px; border-radius: var(--radius-lg); border: 1px solid var(--color-border);
  background: linear-gradient(90deg, var(--color-surface) 25%, var(--color-surface-2) 50%, var(--color-surface) 75%);
  background-size: 200% 100%; animation: shimmer 1.5s infinite;
}
.tool-card {
  background: var(--color-surface); border: 1px solid var(--color-border);
  border-radius: var(--radius-lg); padding: 1.25rem;
  display: flex; flex-direction: column; gap: 0.75rem;
  transition: border-color var(--transition);
}
.tool-card:hover { border-color: var(--color-border-strong); }
.tool-card__header { display: flex; align-items: center; gap: 0.75rem; }
.tool-icon {
  width: 36px; height: 36px; border-radius: var(--radius); background: var(--color-surface-3);
  display: grid; place-items: center; font-size: 1.1rem; flex-shrink: 0;
}
.tool-meta   { flex: 1; min-width: 0; display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; }
.tool-name   { font-weight: 600; font-size: 0.95rem; }
.tool-actions { display: flex; gap: 0.25rem; }
.tool-desc   { font-size: 0.82rem; color: var(--color-text-muted); line-height: 1.5; }
.tool-handler { font-size: 0.75rem; color: var(--color-text-subtle); padding: 0.25rem 0.5rem; background: var(--color-surface-2); border-radius: var(--radius-sm); }
.schema-label { font-size: 0.72rem; font-weight: 600; color: var(--color-text-subtle); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.3rem; }
.schema-props { display: flex; flex-wrap: wrap; gap: 0.3rem; }
.schema-tag   { font-size: 0.72rem; font-family: var(--font-mono); background: var(--color-surface-2); border: 1px solid var(--color-border); border-radius: var(--radius-sm); padding: 0.15rem 0.4rem; }
.schema-type  { color: var(--color-text-muted); }

.tool-form { display: flex; flex-direction: column; gap: 1rem; }
.form-toggle { display: flex; align-items: center; }
.toggle-label { display: flex; align-items: center; gap: 0.5rem; font-size: 0.875rem; cursor: pointer; }
</style>
