<template>
  <div class="page">
    <div v-if="loading && !agentStore.current" class="loading-state">
      <AppSpinner :size="32" />
    </div>

    <template v-else-if="agentStore.current">
      <div class="page-header">
        <div class="agent-title">
          <div class="agent-avatar-lg">{{ agentStore.current.name[0].toUpperCase() }}</div>
          <div>
            <h1 class="page-title">{{ agentStore.current.name }}</h1>
            <AppBadge variant="neutral">{{ agentStore.current.model }}</AppBadge>
          </div>
        </div>
        <div class="header-actions">
          <AppButton variant="secondary" size="sm" @click="editOpen = true">Edit</AppButton>
          <AppButton variant="primary"   size="sm" @click="openRun">&#9654; Run</AppButton>
          <AppButton variant="danger"    size="sm" @click="deleteOpen = true">Delete</AppButton>
        </div>
      </div>

      <div class="detail-grid">
        <div class="detail-left">
          <AppCard>
            <template #header><span class="card-title">Configuration</span></template>
            <div class="config-rows">
              <div class="config-row">
                <span class="config-key">Description</span>
                <span class="config-val">{{ agentStore.current.description || '—' }}</span>
              </div>
              <div class="config-row">
                <span class="config-key">Model</span>
                <code class="config-val font-mono">{{ agentStore.current.model }}</code>
              </div>
              <div v-for="(val, key) in agentStore.current.parameters" :key="key" class="config-row">
                <span class="config-key">{{ key }}</span>
                <code class="config-val font-mono">{{ val }}</code>
              </div>
            </div>
          </AppCard>

          <AppCard v-if="agentStore.current.system_prompt">
            <template #header><span class="card-title">System Prompt</span></template>
            <AppCode :content="agentStore.current.system_prompt" />
          </AppCard>
        </div>

        <div class="detail-right">
          <AppCard :padding="false">
            <template #header>
              <span class="card-title">Recent Runs</span>
              <RouterLink to="/runs" class="card-link">View all &rarr;</RouterLink>
            </template>
            <AppTable
              :columns="runCols"
              :rows="runs"
              :loading="runsLoading"
              empty-text="No runs yet"
              :on-row-click="r => $router.push(`/runs/${r.id}`)"
            >
              <template #cell-status="{ value }">
                <AppBadge :variant="value" :dot="value === 'running'">{{ value }}</AppBadge>
              </template>
              <template #cell-created_at="{ value }">
                <span class="text-muted">{{ formatRelativeTime(value) }}</span>
              </template>
              <template #cell-usage="{ value }">
                <span class="font-mono text-muted">{{ formatTokens(value?.total_tokens) }}</span>
              </template>
            </AppTable>
          </AppCard>
        </div>
      </div>
    </template>

    <AgentFormModal
      :open="editOpen"
      :agent="agentStore.current"
      @close="editOpen = false"
      @saved="editOpen = false"
    />

    <AppModal :open="runOpen" title="Trigger Run" @close="runOpen = false">
      <AppTextarea v-model="runInput" label="User message" :rows="4" placeholder="Enter task for agent..." />
      <template #footer>
        <AppButton variant="ghost"   @click="runOpen = false">Cancel</AppButton>
        <AppButton variant="primary" :loading="runLoading" @click="triggerRun">&#9654; Trigger Run</AppButton>
      </template>
    </AppModal>

    <ConfirmDialog
      :open="deleteOpen"
      title="Delete Agent"
      :message="`Delete '${agentStore.current?.name}'? This cannot be undone.`"
      confirm-label="Delete"
      @confirm="doDelete"
      @cancel="deleteOpen = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { useAgentStore } from '@/stores/agent'
import { runService } from '@/services/runService'
import { useToast } from '@/composables/useToast'
import AppCard from '@/components/ui/AppCard.vue'
import AppTable from '@/components/ui/AppTable.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import AppCode from '@/components/ui/AppCode.vue'
import AppModal from '@/components/ui/AppModal.vue'
import AppTextarea from '@/components/ui/AppTextarea.vue'
import ConfirmDialog from '@/components/ui/ConfirmDialog.vue'
import AgentFormModal from '../components/AgentFormModal.vue'
import { formatRelativeTime, formatTokens } from '@/utils/format'

const route      = useRoute()
const router     = useRouter()
const agentStore = useAgentStore()
const toast      = useToast()

const loading     = ref(false)
const runsLoading = ref(false)
const runs        = ref([])
const editOpen    = ref(false)
const runOpen     = ref(false)
const runInput    = ref('')
const runLoading  = ref(false)
const deleteOpen  = ref(false)

const runCols = [
  { key: 'status',     label: 'Status',  width: '110px' },
  { key: 'usage',      label: 'Tokens',  width: '90px', align: 'right' },
  { key: 'created_at', label: 'Started', width: '120px', align: 'right' },
]

function openRun() { runInput.value = ''; runOpen.value = true }

async function triggerRun() {
  runLoading.value = true
  try {
    const { data } = await runService.trigger({
      agent_id: route.params.id,
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

async function doDelete() {
  try {
    await agentStore.deleteAgent(route.params.id)
    toast.success('Agent deleted')
    router.push('/agents')
  } catch {
    toast.error('Delete failed')
  }
  deleteOpen.value = false
}

onMounted(async () => {
  loading.value = true
  runsLoading.value = true
  try {
    await agentStore.loadById(route.params.id)
    const { data } = await runService.getAll({ agent_id: route.params.id, limit: 10 })
    runs.value = data.items
  } finally {
    loading.value = false
    runsLoading.value = false
  }
})
</script>

<style scoped>
.page { display: flex; flex-direction: column; gap: 1.5rem; }
.loading-state { display: grid; place-items: center; height: 300px; }
.page-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem; flex-wrap: wrap; }
.agent-title { display: flex; align-items: center; gap: 1rem; }
.agent-avatar-lg {
  width: 52px; height: 52px; border-radius: var(--radius-lg);
  background: var(--color-primary-subtle); color: var(--color-primary-light);
  display: grid; place-items: center; font-weight: 700; font-size: 1.4rem;
  border: 1px solid var(--color-primary); flex-shrink: 0;
}
.page-title { font-size: 1.4rem; font-weight: 700; }
.header-actions { display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap; }
.detail-grid { display: grid; grid-template-columns: 1fr 380px; gap: 1rem; align-items: start; }
@media (max-width: 900px) { .detail-grid { grid-template-columns: 1fr; } }
.detail-left, .detail-right { display: flex; flex-direction: column; gap: 1rem; }
.card-title { font-size: 0.9rem; font-weight: 600; }
.card-link  { font-size: 0.8rem; color: var(--color-primary-light); }
.card-link:hover { text-decoration: underline; }
.config-rows { display: flex; flex-direction: column; gap: 0.75rem; }
.config-row  { display: flex; gap: 1rem; align-items: baseline; }
.config-key  { font-size: 0.78rem; font-weight: 500; color: var(--color-text-muted); width: 100px; flex-shrink: 0; text-transform: capitalize; }
.config-val  { font-size: 0.875rem; color: var(--color-text); }
</style>
