<template>
  <div class="page">
    <!-- Header ------------------------------------------------------------ -->
    <div class="page-header">
      <div>
        <h1 class="page-title">Agents</h1>
        <p class="page-subtitle">
          {{ agentStore.agents.length }}
          agent{{ agentStore.agents.length === 1 ? '' : 's' }} configured
        </p>
      </div>
      <div class="header-actions">
        <IconField icon-position="left" class="search-field">
          <InputIcon class="pi pi-search" />
          <InputText
            v-model="search"
            placeholder="Search agents…"
            class="search-input"
          />
        </IconField>
        <Button
          label="New Agent"
          icon="pi pi-plus"
          severity="primary"
          @click="openCreate"
        />
      </div>
    </div>

    <!-- Table ------------------------------------------------------------- -->
    <DataTable
      :value="filteredAgents"
      :loading="loading"
      data-key="id"
      striped-rows
      :rows="10"
      :rows-per-page-options="[10, 25, 50]"
      paginator
      removable-sort
      class="agents-table"
      row-hover
      @row-click="onRowClick"
    >
      <template #empty>
        <div class="table-empty">
          <i class="pi pi-sparkles empty-icon" />
          <h3>No agents yet</h3>
          <p>Create your first AI agent to start running tasks and workflows.</p>
          <Button
            label="Create Agent"
            icon="pi pi-plus"
            severity="primary"
            @click="openCreate"
          />
        </div>
      </template>

      <template #loading>
        <div class="table-loading">
          <i class="pi pi-spin pi-spinner" />
          <span>Loading agents…</span>
        </div>
      </template>

      <Column field="name" header="Agent" sortable style="min-width: 18rem">
        <template #body="{ data }">
          <div class="agent-cell">
            <Avatar
              :label="data.name[0]?.toUpperCase() || '?'"
              shape="circle"
              class="agent-avatar"
            />
            <div class="agent-meta">
              <div class="agent-name">{{ data.name }}</div>
              <div class="agent-desc">
                {{ data.description || 'No description provided.' }}
              </div>
            </div>
          </div>
        </template>
      </Column>

      <Column field="model" header="Model" sortable style="min-width: 10rem">
        <template #body="{ data }">
          <Tag :value="shortModel(data.model)" severity="secondary" rounded />
        </template>
      </Column>

      <Column
        field="tool_ids"
        header="Tools"
        sortable
        style="width: 7rem"
        :sort-field="(d) => d.tool_ids?.length ?? 0"
      >
        <template #body="{ data }">
          <span class="tools-count">
            <i class="pi pi-wrench" />
            {{ data.tool_ids?.length ?? 0 }}
          </span>
        </template>
      </Column>

      <Column field="created_at" header="Created" sortable style="width: 10rem">
        <template #body="{ data }">
          <span class="text-muted">{{ formatRelativeTime(data.created_at) }}</span>
        </template>
      </Column>

      <Column header="" style="width: 11rem">
        <template #body="{ data }">
          <div class="row-actions" @click.stop>
            <Button
              v-tooltip.top="'Run agent'"
              icon="pi pi-play"
              severity="primary"
              text
              rounded
              @click="openRun(data)"
            />
            <Button
              v-tooltip.top="'Edit agent'"
              icon="pi pi-pencil"
              severity="secondary"
              text
              rounded
              @click="openEdit(data)"
            />
            <Button
              v-tooltip.top="'Delete agent'"
              icon="pi pi-trash"
              severity="danger"
              text
              rounded
              @click="askDelete(data)"
            />
          </div>
        </template>
      </Column>
    </DataTable>

    <!-- Modals ------------------------------------------------------------ -->
    <AgentFormModal
      :open="formOpen"
      :agent="editTarget"
      @close="formOpen = false"
      @saved="onSaved"
    />

    <Dialog
      v-model:visible="runOpen"
      modal
      header="Trigger Run"
      :style="{ width: '32rem' }"
    >
      <div class="run-form">
        <p class="run-form__label">
          Agent:
          <span class="run-form__agent">{{ runTarget?.name }}</span>
        </p>
        <label class="run-form__field">
          <span>User message / input</span>
          <Textarea
            v-model="runInput"
            rows="5"
            placeholder="Enter the prompt or task…"
            auto-resize
          />
        </label>
      </div>
      <template #footer>
        <Button label="Cancel" text @click="runOpen = false" />
        <Button
          label="Trigger Run"
          icon="pi pi-play"
          severity="primary"
          :loading="runLoading"
          @click="triggerRun"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useConfirm } from 'primevue/useconfirm'
import { useAgentStore } from '@/stores/agent'
import { runService } from '@/services/runService'
import { useToast } from '@/composables/useToast'

import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import IconField from 'primevue/iconfield'
import InputIcon from 'primevue/inputicon'
import Avatar from 'primevue/avatar'
import Tag from 'primevue/tag'
import Dialog from 'primevue/dialog'
import Textarea from 'primevue/textarea'

import AgentFormModal from '../components/AgentFormModal.vue'
import { formatRelativeTime } from '@/utils/format'

const router     = useRouter()
const agentStore = useAgentStore()
const toast      = useToast()
const confirm    = useConfirm()

const loading    = ref(false)
const search     = ref('')
const formOpen   = ref(false)
const editTarget = ref(null)
const runOpen    = ref(false)
const runTarget  = ref(null)
const runInput   = ref('')
const runLoading = ref(false)

const filteredAgents = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return agentStore.agents
  return agentStore.agents.filter(
    (a) =>
      a.name.toLowerCase().includes(q) ||
      (a.description || '').toLowerCase().includes(q) ||
      (a.model || '').toLowerCase().includes(q)
  )
})

function shortModel(m) { return m?.split('/').pop() || m }
function openCreate()  { editTarget.value = null; formOpen.value = true }
function openEdit(a)   { editTarget.value = a;    formOpen.value = true }
function openRun(a)    { runTarget.value = a; runInput.value = ''; runOpen.value = true }

function onRowClick(event) {
  router.push(`/agents/${event.data.id}`)
}

async function triggerRun() {
  runLoading.value = true
  try {
    const { data } = await runService.trigger({
      agent_id: runTarget.value.id,
      input: { message: runInput.value },
    })
    runOpen.value = false
    toast.success('Run triggered!')
    router.push(`/runs/${data.id}`)
  } catch {
    toast.error('Failed to trigger run')
  } finally {
    runLoading.value = false
  }
}

function onSaved() {
  formOpen.value = false
  toast.success('Agent saved!')
}

function askDelete(agent) {
  confirm.require({
    message: `Delete '${agent.name}'? This cannot be undone.`,
    header: 'Delete agent',
    icon: 'pi pi-exclamation-triangle',
    rejectProps: { label: 'Cancel', severity: 'secondary', text: true },
    acceptProps: { label: 'Delete', severity: 'danger' },
    accept: async () => {
      try {
        await agentStore.deleteAgent(agent.id)
        toast.success('Agent deleted')
      } catch {
        toast.error('Delete failed')
      }
    },
  })
}

onMounted(async () => {
  loading.value = true
  try {
    await agentStore.loadAgents()
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.page { display: flex; flex-direction: column; gap: 1.5rem; }

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1.5rem;
  flex-wrap: wrap;
}
.page-title {
  font-size: 1.6rem;
  font-weight: 700;
  letter-spacing: -0.01em;
  color: var(--p-text-color, var(--color-text));
}
.page-subtitle {
  color: var(--p-text-muted-color, var(--color-text-muted));
  font-size: 0.875rem;
  margin-top: 0.25rem;
}
.header-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.search-field :deep(.p-inputtext) {
  min-width: 16rem;
}

/* Table surface ------------------------------------------------------------ */
:deep(.agents-table) {
  background: var(--p-surface-900, var(--color-surface));
  border: 1px solid var(--p-surface-800, var(--color-border));
  border-radius: var(--radius-lg);
  overflow: hidden;
}
:deep(.agents-table .p-datatable-tbody > tr) { cursor: pointer; }

/* Agent cell */
.agent-cell {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  min-width: 0;
}
.agent-avatar {
  background: color-mix(in srgb, var(--p-primary-500, #6366f1) 22%, transparent) !important;
  color: var(--p-primary-300, var(--color-primary-light)) !important;
  font-weight: 700;
  flex-shrink: 0;
}
.agent-meta { min-width: 0; flex: 1; }
.agent-name {
  font-weight: 600;
  color: var(--p-text-color, var(--color-text));
  font-size: 0.9rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.agent-desc {
  font-size: 0.78rem;
  color: var(--p-text-muted-color, var(--color-text-muted));
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 36rem;
}

.tools-count {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  color: var(--p-text-muted-color, var(--color-text-muted));
  font-size: 0.82rem;
}

.row-actions {
  display: flex;
  align-items: center;
  gap: 0.1rem;
  justify-content: flex-end;
}

/* Empty + loading states -------------------------------------------------- */
.table-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  padding: 3rem 1rem;
  text-align: center;
}
.empty-icon {
  font-size: 2rem;
  color: var(--p-primary-400, var(--color-primary-light));
  margin-bottom: 0.25rem;
}
.table-empty h3 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--p-text-color, var(--color-text));
}
.table-empty p {
  color: var(--p-text-muted-color, var(--color-text-muted));
  margin-bottom: 0.5rem;
  max-width: 28rem;
}
.table-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 2rem;
  color: var(--p-text-muted-color, var(--color-text-muted));
}

/* Run dialog -------------------------------------------------------------- */
.run-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding-top: 0.5rem;
}
.run-form__label {
  font-size: 0.85rem;
  color: var(--p-text-muted-color, var(--color-text-muted));
}
.run-form__agent {
  color: var(--p-text-color, var(--color-text));
  font-weight: 600;
}
.run-form__field {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  font-size: 0.82rem;
  color: var(--p-text-muted-color, var(--color-text-muted));
}
.run-form__field :deep(textarea) { width: 100%; }
</style>
