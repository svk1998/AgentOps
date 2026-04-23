<template>
  <div class="page">
    <!-- Header -->
    <div class="page-head">
      <div>
        <div class="page-eyebrow mono faint">registry</div>
        <h1 class="page-title">Agents</h1>
        <div class="page-sub mono">
          <span>{{ agents.length }} agent{{ agents.length === 1 ? '' : 's' }}</span>
          <span class="sep">·</span>
          <span class="text-success">{{ counts.active }} active</span>
          <span class="sep">·</span>
          <span class="text-muted">{{ counts.draft }} draft</span>
          <span class="sep">·</span>
          <span class="text-subtle">{{ counts.archived }} archived</span>
        </div>
      </div>
      <div class="page-actions">
        <div class="search-wrap">
          <svg class="search-icon" width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round">
            <circle cx="7" cy="7" r="4.5" /><path d="M10.5 10.5L14 14" />
          </svg>
          <input v-model="search" class="input search-input" placeholder="Search agents…" />
        </div>
        <select v-model="filters.agent_type" class="input">
          <option value="">All types</option>
          <option v-for="t in AGENT_TYPES" :key="t" :value="t">{{ t }}</option>
        </select>
        <select v-model="filters.status" class="input">
          <option value="">All status</option>
          <option v-for="s in AGENT_STATUSES" :key="s" :value="s">{{ s }}</option>
        </select>
        <button class="btn ghost" :disabled="loading" @click="load">
          <svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" :class="loading ? 'spin' : ''"><path d="M14 8a6 6 0 1 1-6-6c1.9 0 3.6 0.9 4.7 2.3"/><path d="M14 2v3h-3"/></svg>
          Refresh
        </button>
        <button class="btn primary" @click="createNew">
          <svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M8 3v10M3 8h10"/></svg>
          New agent
        </button>
      </div>
    </div>

    <!-- Table -->
    <Panel :padding="false">
      <DataTable
        :columns="cols"
        :rows="filteredAgents"
        :on-row-click="r => $router.push(`/registry/agents/${r.id}`)"
        :empty-text="search ? `no agents match “${search}”` : 'no agents registered yet — click “New agent” to get started'"
      >
        <template #cell-status="{ row }">
          <div class="cell-status">
            <StatusDot :status="statusToDot(row.status)" />
            <span class="mono faint">{{ row.status }}</span>
          </div>
        </template>
        <template #cell-name="{ row }">
          <div class="cell-name">
            <span class="mono" style="color:var(--text)">{{ row.name }}</span>
            <Chip v-if="row.version" style="margin-left:8px">{{ row.version }}</Chip>
          </div>
        </template>
        <template #cell-agent_type="{ value }">
          <span class="mono faint" style="font-size:11px">{{ value }}</span>
        </template>
        <template #cell-model_provider="{ value }">
          <span class="mono faint" style="font-size:11px">{{ value || '—' }}</span>
        </template>
        <template #cell-tags="{ value }">
          <div class="tag-row">
            <Chip v-for="t in (value || []).slice(0, 3)" :key="t" variant="accent" style="height:18px; padding:0 6px; font-size:10px">{{ t }}</Chip>
            <span v-if="(value || []).length > 3" class="mono faint" style="font-size:10px">+{{ value.length - 3 }}</span>
          </div>
        </template>
        <template #cell-owner="{ value }">
          <span class="mono faint" style="font-size:11px">{{ value || '—' }}</span>
        </template>
        <template #cell-updated_at="{ value }">
          <span class="mono faint" style="font-size:11px" :title="formatDateTime(value)">{{ formatRelativeTime(value) }}</span>
        </template>
      </DataTable>
    </Panel>

    <div v-if="error" class="error-banner mono">{{ error }}</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { agentService } from '@/services/agentService'
import { formatRelativeTime, formatDateTime } from '@/utils/format'

import Panel from '@/components/primitives/Panel.vue'
import Chip from '@/components/primitives/Chip.vue'
import StatusDot from '@/components/primitives/StatusDot.vue'
import DataTable from '@/components/primitives/DataTable.vue'

const AGENT_TYPES = ['llm', 'rag', 'vision', 'multi_step_chain', 'tool_use', 'custom']
const AGENT_STATUSES = ['draft', 'active', 'deprecated', 'archived']

const agents = ref([])
const loading = ref(false)
const error = ref('')
const search = ref('')
const filters = ref({ agent_type: '', status: '' })

const cols = [
  { key: 'status',         label: 'Status',  width: '130px' },
  { key: 'name',           label: 'Agent',   width: '2fr' },
  { key: 'agent_type',     label: 'Type',    width: '120px' },
  { key: 'model_provider', label: 'Model',   width: '1fr' },
  { key: 'tags',           label: 'Tags',    width: '1fr' },
  { key: 'owner',          label: 'Owner',   width: '120px' },
  { key: 'updated_at',     label: 'Updated', width: '110px', align: 'right' },
]

const filteredAgents = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return agents.value
  return agents.value.filter(a =>
    a.name?.toLowerCase().includes(q) ||
    a.model_provider?.toLowerCase().includes(q) ||
    a.description?.toLowerCase().includes(q) ||
    (a.tags || []).some(t => t.toLowerCase().includes(q))
  )
})

const counts = computed(() => {
  const c = { active: 0, draft: 0, archived: 0, deprecated: 0 }
  for (const a of agents.value) c[a.status] = (c[a.status] || 0) + 1
  return c
})

function statusToDot(status) {
  return { active: 'ok', draft: 'pending', deprecated: 'warn', archived: 'pending' }[status] || 'pending'
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const params = {}
    if (filters.value.agent_type) params.agent_type = filters.value.agent_type
    if (filters.value.status) params.status = filters.value.status
    const { data } = await agentService.list(params)
    agents.value = Array.isArray(data) ? data : (data?.items ?? [])
  } catch (e) {
    error.value = e?.response?.data?.detail || e?.message || 'Failed to load agents'
    agents.value = []
  } finally {
    loading.value = false
  }
}

function createNew() {
  // Placeholder — full create form lives at /registry/agents/new in future iterations
  error.value = 'Agent creation form coming next iteration'
}

onMounted(load)
</script>

<style scoped>
.page { display: flex; flex-direction: column; gap: 14px; }

.page-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  padding: 2px 2px 6px;
  flex-wrap: wrap;
}
.page-eyebrow { font-size: 10.5px; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 4px; }
.page-title { font-size: 22px; font-weight: 600; letter-spacing: -0.02em; color: var(--text); }
.page-sub { font-size: 11.5px; color: var(--text-dim); display: flex; gap: 6px; align-items: center; margin-top: 2px; }
.page-sub .sep { color: var(--text-faint); }

.page-actions { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }

.search-wrap { position: relative; display: flex; align-items: center; }
.search-icon { position: absolute; left: 10px; color: var(--text-faint); pointer-events: none; }
.search-input { padding-left: 28px; min-width: 200px; }

select.input { cursor: pointer; }

.cell-status { display: flex; align-items: center; gap: 8px; }
.cell-name { display: inline-flex; align-items: center; }

.tag-row { display: flex; gap: 4px; align-items: center; flex-wrap: nowrap; overflow: hidden; }

.error-banner {
  background: var(--err-dim);
  color: var(--err);
  border: 1px solid var(--err);
  border-radius: var(--r);
  padding: 10px 14px;
  font-size: 12px;
}

.spin { animation: spin 1s linear infinite; }
</style>
