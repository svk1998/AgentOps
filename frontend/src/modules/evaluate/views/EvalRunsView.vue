<template>
  <div class="page">
    <div class="page-head">
      <div>
        <div class="page-eyebrow mono faint">evaluate</div>
        <h1 class="page-title">Eval Runs</h1>
        <div class="page-sub mono">
          <span>{{ runs.length }} run{{ runs.length === 1 ? '' : 's' }}</span>
          <span class="sep">·</span>
          <span class="text-info">{{ statusCounts.running }} running</span>
          <span class="sep">·</span>
          <span class="text-success">{{ statusCounts.completed }} completed</span>
          <span class="sep">·</span>
          <span class="text-danger">{{ statusCounts.failed }} failed</span>
        </div>
      </div>
      <div class="page-actions">
        <select v-model="filters.status" class="input">
          <option value="">All status</option>
          <option v-for="s in RUN_STATUSES" :key="s" :value="s">{{ s }}</option>
        </select>
        <button class="btn ghost" :disabled="loading" @click="load">
          <svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" :class="loading ? 'spin' : ''"><path d="M14 8a6 6 0 1 1-6-6c1.9 0 3.6 0.9 4.7 2.3"/><path d="M14 2v3h-3"/></svg>
          Refresh
        </button>
        <button class="btn primary">
          <svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M8 3v10M3 8h10"/></svg>
          New run
        </button>
      </div>
    </div>

    <Panel :padding="false">
      <DataTable
        :columns="cols"
        :rows="runs"
        :on-row-click="r => $router.push(`/evaluate/runs/${r.id}`)"
        empty-text="no evaluation runs yet — create a dataset and register an agent to start"
      >
        <template #cell-status="{ row }">
          <div class="cell-status">
            <StatusDot :status="statusToDot(row.status)" />
            <span class="mono faint">{{ row.status }}</span>
          </div>
        </template>
        <template #cell-agent_id="{ value, row }">
          <span class="mono" style="color:var(--text); font-size:11.5px">
            {{ shortId(value) }}<span v-if="row.agent_version" class="faint"> · {{ row.agent_version }}</span>
          </span>
        </template>
        <template #cell-dataset="{ row }">
          <span class="mono faint" style="font-size:11px">
            {{ row.dataset_id ? shortId(row.dataset_id) : row.rag_dataset_id ? 'rag · ' + shortId(row.rag_dataset_id) : '—' }}
          </span>
        </template>
        <template #cell-progress="{ row }">
          <div class="progress-wrap">
            <div class="progress-bar">
              <div class="progress-fill progress-fill--pass" :style="{ width: pct(row.passed, row.total_items) }"></div>
              <div class="progress-fill progress-fill--fail" :style="{ width: pct(row.failed, row.total_items) }"></div>
              <div class="progress-fill progress-fill--err"  :style="{ width: pct(row.errored, row.total_items) }"></div>
            </div>
            <span class="mono faint progress-label">{{ row.passed + row.failed + row.errored }}/{{ row.total_items || 0 }}</span>
          </div>
        </template>
        <template #cell-pass_rate="{ row }">
          <span class="mono" :class="passRateColor(row)">{{ passRatePct(row) }}</span>
        </template>
        <template #cell-p95="{ value }">
          <span class="mono faint" style="font-size:11px">{{ value != null ? Math.round(value) + 'ms' : '—' }}</span>
        </template>
        <template #cell-cost="{ value }">
          <span class="mono faint" style="font-size:11px">{{ value != null ? '$' + value.toFixed(2) : '—' }}</span>
        </template>
        <template #cell-created_at="{ value }">
          <span class="mono faint" style="font-size:11px" :title="formatDateTime(value)">{{ formatRelativeTime(value) }}</span>
        </template>
      </DataTable>
    </Panel>

    <div v-if="error" class="error-banner mono">{{ error }}</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { evalRunService } from '@/services/evalRunService'
import { formatRelativeTime, formatDateTime } from '@/utils/format'

import Panel from '@/components/primitives/Panel.vue'
import StatusDot from '@/components/primitives/StatusDot.vue'
import DataTable from '@/components/primitives/DataTable.vue'

const RUN_STATUSES = ['pending', 'running', 'completed', 'failed', 'cancelled']

const runs = ref([])
const loading = ref(false)
const error = ref('')
const filters = ref({ status: '' })

const cols = [
  { key: 'status',     label: 'Status',   width: '130px' },
  { key: 'agent_id',   label: 'Agent',    width: '1.5fr' },
  { key: 'dataset',    label: 'Dataset',  width: '1fr' },
  { key: 'progress',   label: 'Progress', width: '2fr' },
  { key: 'pass_rate',  label: 'Pass Rate',width: '90px', align: 'right' },
  { key: 'p95',        label: 'p95',      width: '80px', align: 'right' },
  { key: 'cost',       label: 'Cost',     width: '80px', align: 'right' },
  { key: 'created_at', label: 'Started',  width: '110px', align: 'right' },
]

const statusCounts = computed(() => {
  const c = { running: 0, completed: 0, failed: 0, pending: 0, cancelled: 0 }
  for (const r of runs.value) c[r.status] = (c[r.status] || 0) + 1
  return c
})

function statusToDot(status) {
  return { running: 'info', completed: 'ok', failed: 'err', cancelled: 'pending', pending: 'pending' }[status] || 'pending'
}

function pct(n, total) {
  if (!total) return '0%'
  return `${Math.min(100, (n / total) * 100)}%`
}

function passRatePct(r) {
  const done = r.passed + r.failed + r.errored
  if (!done) return '—'
  return `${Math.round((r.passed / done) * 100)}%`
}

function passRateColor(r) {
  const done = r.passed + r.failed + r.errored
  if (!done) return 'text-subtle'
  const rate = r.passed / done
  if (rate >= 0.95) return 'text-success'
  if (rate >= 0.80) return 'text-warning'
  return 'text-danger'
}

function shortId(id) {
  if (!id) return '—'
  return id.slice(0, 8)
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const params = { limit: 100 }
    if (filters.value.status) params.status = filters.value.status
    const { data } = await evalRunService.list(params)
    runs.value = Array.isArray(data) ? data : (data?.items ?? [])
  } catch (e) {
    error.value = e?.response?.data?.detail || e?.message || 'Failed to load eval runs'
    runs.value = []
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

select.input { cursor: pointer; }

.cell-status { display: flex; align-items: center; gap: 8px; }

.progress-wrap { display: flex; align-items: center; gap: 10px; }
.progress-bar {
  flex: 1;
  height: 6px;
  background: var(--bg-elev-2);
  border-radius: 3px;
  overflow: hidden;
  display: flex;
  min-width: 100px;
}
.progress-fill { height: 100%; }
.progress-fill--pass { background: var(--ok); }
.progress-fill--fail { background: var(--err); }
.progress-fill--err  { background: var(--warn); }
.progress-label { font-size: 10.5px; min-width: 60px; text-align: right; }

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
