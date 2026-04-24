<template>
  <div class="page">
    <div class="page-head">
      <div>
        <div class="page-eyebrow mono faint">evaluate</div>
        <h1 class="page-title">Datasets</h1>
        <div class="page-sub mono">
          <span>{{ datasets.length }} dataset{{ datasets.length === 1 ? '' : 's' }}</span>
          <span class="sep">·</span>
          <span>{{ totalItems }} items</span>
          <span class="sep">·</span>
          <span class="text-muted">{{ uniqueAgentTypes }} agent types</span>
        </div>
      </div>
      <div class="page-actions">
        <div class="search-wrap">
          <svg class="search-icon" width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round">
            <circle cx="7" cy="7" r="4.5" /><path d="M10.5 10.5L14 14" />
          </svg>
          <input v-model="search" class="input search-input" placeholder="Search datasets…" />
        </div>
        <select v-model="filters.agent_type" class="input">
          <option value="">All types</option>
          <option v-for="t in AGENT_TYPES" :key="t" :value="t">{{ t }}</option>
        </select>
        <button class="btn ghost" :disabled="loading" @click="load">
          <svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" :class="loading ? 'spin' : ''"><path d="M14 8a6 6 0 1 1-6-6c1.9 0 3.6 0.9 4.7 2.3"/><path d="M14 2v3h-3"/></svg>
          Refresh
        </button>
        <button class="btn primary">
          <svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M8 3v10M3 8h10"/></svg>
          New dataset
        </button>
      </div>
    </div>

    <Panel :padding="false">
      <DataTable
        :columns="cols"
        :rows="filtered"
        :on-row-click="r => $router.push(`/evaluate/datasets/${r.id}`)"
        :empty-text="search ? `no datasets match “${search}”` : 'no datasets yet — create one to start evaluating agents'"
      >
        <template #cell-name="{ row }">
          <div class="cell-name">
            <svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="var(--accent)" stroke-width="1.4" stroke-linecap="round" style="flex-shrink:0">
              <ellipse cx="8" cy="4" rx="6" ry="2"/>
              <path d="M2 4v4c0 1.1 2.7 2 6 2s6-.9 6-2V4"/>
              <path d="M2 8v4c0 1.1 2.7 2 6 2s6-.9 6-2V8"/>
            </svg>
            <span class="mono" style="color:var(--text)">{{ row.name }}</span>
            <Chip style="margin-left:6px">v{{ row.current_version }}</Chip>
          </div>
        </template>
        <template #cell-agent_type="{ value }">
          <Chip v-if="value" variant="accent">{{ value }}</Chip>
          <span v-else class="mono faint" style="font-size:11px">—</span>
        </template>
        <template #cell-item_count="{ value }">
          <span class="mono" style="color:var(--text)">{{ value }}</span>
        </template>
        <template #cell-tags="{ value }">
          <div class="tag-row">
            <Chip v-for="t in (value || []).slice(0, 3)" :key="t" style="height:18px; padding:0 6px; font-size:10px">{{ t }}</Chip>
            <span v-if="(value || []).length > 3" class="mono faint" style="font-size:10px">+{{ value.length - 3 }}</span>
          </div>
        </template>
        <template #cell-description="{ value }">
          <span class="dim truncate" style="font-size:11.5px">{{ value || '—' }}</span>
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
import { datasetService } from '@/services/datasetService'
import { formatRelativeTime, formatDateTime } from '@/utils/format'

import Panel from '@/components/ui/Panel.vue'
import Chip from '@/components/ui/Chip.vue'
import DataTable from '@/components/ui/DataTable.vue'

const AGENT_TYPES = ['llm', 'rag', 'vision', 'multi_step_chain', 'tool_use', 'custom']

const datasets = ref([])
const loading = ref(false)
const error = ref('')
const search = ref('')
const filters = ref({ agent_type: '' })

const cols = [
  { key: 'name',        label: 'Dataset',     width: '2fr' },
  { key: 'agent_type',  label: 'Agent Type',  width: '140px' },
  { key: 'item_count',  label: 'Items',       width: '80px', align: 'right' },
  { key: 'tags',        label: 'Tags',        width: '1fr' },
  { key: 'description', label: 'Description', width: '1.5fr' },
  { key: 'updated_at',  label: 'Updated',     width: '110px', align: 'right' },
]

const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return datasets.value
  return datasets.value.filter(d =>
    d.name?.toLowerCase().includes(q) ||
    d.description?.toLowerCase().includes(q) ||
    (d.tags || []).some(t => t.toLowerCase().includes(q))
  )
})

const totalItems = computed(() => datasets.value.reduce((s, d) => s + (d.item_count || 0), 0))
const uniqueAgentTypes = computed(() => new Set(datasets.value.map(d => d.agent_type).filter(Boolean)).size)

async function load() {
  loading.value = true
  error.value = ''
  try {
    const params = {}
    if (filters.value.agent_type) params.agent_type = filters.value.agent_type
    const { data } = await datasetService.list(params)
    datasets.value = Array.isArray(data) ? data : (data?.items ?? [])
  } catch (e) {
    error.value = e?.response?.data?.detail || e?.message || 'Failed to load datasets'
    datasets.value = []
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.page { display: flex; flex-direction: column; gap: 14px; }

.page-head { display: flex; align-items: flex-end; justify-content: space-between; gap: 16px; padding: 2px 2px 6px; flex-wrap: wrap; }
.page-eyebrow { font-size: 10.5px; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 4px; }
.page-title { font-size: 22px; font-weight: 600; letter-spacing: -0.02em; color: var(--text); }
.page-sub { font-size: 11.5px; color: var(--text-dim); display: flex; gap: 6px; align-items: center; margin-top: 2px; }
.page-sub .sep { color: var(--text-faint); }

.page-actions { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }

.search-wrap { position: relative; display: flex; align-items: center; }
.search-icon { position: absolute; left: 10px; color: var(--text-faint); pointer-events: none; }
.search-input { padding-left: 28px; min-width: 200px; }

select.input { cursor: pointer; }

.cell-name { display: inline-flex; align-items: center; gap: 8px; }
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
