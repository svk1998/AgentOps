<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Runs</h1>
        <p class="page-subtitle">{{ total }} total runs</p>
      </div>
      <div class="header-right">
        <AppButton variant="ghost" size="sm" @click="load">Refresh</AppButton>
      </div>
    </div>

    <!-- Status filter tabs -->
    <div class="filter-tabs">
      <button
        v-for="tab in statusTabs"
        :key="tab.value"
        :class="['tab', { 'tab--active': activeStatus === tab.value }]"
        @click="setStatus(tab.value)"
      >
        {{ tab.label }}
        <span v-if="tab.value === 'running' && runningCount" class="tab-dot" />
      </button>
    </div>

    <AppCard :padding="false">
      <AppTable
        :columns="cols"
        :rows="runs"
        :loading="loading"
        empty-text="No runs found"
        :on-row-click="r => $router.push(`/runs/${r.id}`)"
      >
        <template #cell-status="{ value }">
          <AppBadge :variant="value" :dot="value === 'running'">{{ value }}</AppBadge>
        </template>
        <template #cell-agent_name="{ row }">
          <span class="font-semibold">{{ row.agent_name || '—' }}</span>
        </template>
        <template #cell-input="{ value }">
          <span class="text-muted font-mono" style="font-size:0.78rem">{{ truncate(JSON.stringify(value), 60) }}</span>
        </template>
        <template #cell-usage="{ value }">
          <span class="font-mono text-muted">{{ formatTokens(value?.total_tokens) }}</span>
        </template>
        <template #cell-created_at="{ value, row }">
          <div style="text-align:right">
            <div class="text-muted" style="font-size:0.78rem">{{ formatRelativeTime(value) }}</div>
            <div v-if="row.finished_at" class="text-subtle" style="font-size:0.72rem">{{ formatDuration(value, row.finished_at) }}</div>
          </div>
        </template>
      </AppTable>
    </AppCard>

    <!-- Pagination -->
    <div v-if="total > limit" class="pagination">
      <AppButton variant="secondary" size="sm" :disabled="offset === 0" @click="prev">← Prev</AppButton>
      <span class="page-info">{{ Math.floor(offset/limit) + 1 }} / {{ Math.ceil(total/limit) }}</span>
      <AppButton variant="secondary" size="sm" :disabled="offset + limit >= total" @click="next">Next →</AppButton>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { runService } from '@/services/runService'
import AppButton from '@/components/ui/AppButton.vue'
import AppCard from '@/components/ui/AppCard.vue'
import AppTable from '@/components/ui/AppTable.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import { formatTokens, formatRelativeTime, formatDuration, truncate } from '@/utils/format'

const runs    = ref([])
const total   = ref(0)
const loading = ref(false)
const offset  = ref(0)
const limit   = 20
const activeStatus = ref('')

const statusTabs = [
  { label: 'All',       value: '' },
  { label: 'Running',   value: 'running' },
  { label: 'Pending',   value: 'pending' },
  { label: 'Completed', value: 'completed' },
  { label: 'Failed',    value: 'failed' },
]

const runningCount = computed(() => runs.value.filter(r => r.status === 'running').length)

const cols = [
  { key: 'status',     label: 'Status',  width: '110px' },
  { key: 'agent_name', label: 'Agent' },
  { key: 'input',      label: 'Input' },
  { key: 'usage',      label: 'Tokens',  width: '90px', align: 'right' },
  { key: 'created_at', label: 'Started', width: '130px', align: 'right' },
]

async function load() {
  loading.value = true
  try {
    const params = { limit, offset: offset.value }
    if (activeStatus.value) params.status = activeStatus.value
    const { data } = await runService.getAll(params)
    runs.value  = data.items
    total.value = data.total
  } finally { loading.value = false }
}

function setStatus(s) { activeStatus.value = s; offset.value = 0; load() }
function prev() { offset.value = Math.max(0, offset.value - limit); load() }
function next() { offset.value += limit; load() }

let interval = null
onMounted(() => { load(); interval = setInterval(load, 15_000) })
onUnmounted(() => clearInterval(interval))
</script>

<style scoped>
.page { display: flex; flex-direction: column; gap: 1.25rem; }
.page-header { display: flex; align-items: flex-start; justify-content: space-between; }
.page-title  { font-size: 1.4rem; font-weight: 700; }
.page-subtitle { color: var(--color-text-muted); font-size: 0.875rem; margin-top: 0.2rem; }
.header-right { display: flex; gap: 0.5rem; align-items: center; }

.filter-tabs { display: flex; gap: 0.25rem; border-bottom: 1px solid var(--color-border); }
.tab {
  padding: 0.5rem 1rem;
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--color-text-muted);
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  transition: color var(--transition), border-color var(--transition);
  display: flex; align-items: center; gap: 0.4rem;
}
.tab:hover { color: var(--color-text); }
.tab--active { color: var(--color-primary-light); border-bottom-color: var(--color-primary); }
.tab-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--color-running); animation: pulse-dot 1.5s infinite; }

.pagination { display: flex; align-items: center; justify-content: center; gap: 1rem; }
.page-info { font-size: 0.85rem; color: var(--color-text-muted); }
</style>
