<template>
  <div class="dashboard">
    <!-- Header -->
    <div class="dash-header">
      <div class="dash-title-wrap">
        <div class="dash-eyebrow mono faint">overview</div>
        <h1 class="dash-title">Fleet</h1>
        <div class="dash-subtitle mono">
          <span>{{ agents.length }} agent{{ agents.length === 1 ? '' : 's' }}</span>
          <span class="sep">·</span>
          <span class="text-success">{{ agentCounts.active }} active</span>
          <span class="sep">·</span>
          <span class="text-warning">{{ agentCounts.deprecated }} deprecated</span>
          <span class="sep">·</span>
          <span class="text-muted">{{ agentCounts.draft }} draft</span>
        </div>
      </div>
      <div class="dash-actions">
        <Chip variant="ok" dot>live · auto-refresh 30s</Chip>
        <button class="btn ghost" :disabled="loading" @click="refresh">
          <svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" :class="loading ? 'spin' : ''">
            <path d="M14 8a6 6 0 1 1-6-6c1.9 0 3.6 0.9 4.7 2.3"/><path d="M14 2v3h-3"/>
          </svg>
          Refresh
        </button>
        <button class="btn primary" @click="$router.push('/registry/agents')">
          <svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round">
            <path d="M8 3v10M3 8h10"/>
          </svg>
          New agent
        </button>
      </div>
    </div>

    <!-- KPI strip -->
    <div class="kpi-strip">
      <Kpi
        label="Agents"
        :value="loading ? '—' : agents.length.toString()"
        :delta="`${agentCounts.active} active`"
        tone="accent"
        :spark="agentsSpark"
      />
      <Kpi
        label="Datasets"
        :value="loading ? '—' : datasets.length.toString()"
        :delta="`${totalDatasetItems} items`"
        tone="neu"
        :spark="datasetsSpark"
      />
      <Kpi
        label="Eval runs"
        :value="loading ? '—' : runs.length.toString()"
        :delta="`${runCounts.running} running`"
        tone="pos"
        :spark="runsSpark"
      />
      <Kpi
        label="Pass rate"
        :value="loading ? '—' : avgPassRatePct"
        :delta="`${runCounts.completed}/${runs.length}`"
        :tone="passRateTone"
        :spark="passRateSpark"
      />
    </div>

    <!-- Agents table — Fleet style -->
    <Panel title="Registered agents" subtitle="click to view details" :padding="false">
      <template #actions>
        <RouterLink to="/registry/agents" class="panel-link mono">view all →</RouterLink>
      </template>

      <DataTable
        :columns="agentCols"
        :rows="agents.slice(0, 10)"
        :on-row-click="r => $router.push(`/registry/agents/${r.id}`)"
        empty-text="no agents yet — register one to start"
      >
        <template #cell-status="{ row }">
          <div class="cell-status">
            <StatusDot :status="statusToDot(row.status)" />
            <span class="mono faint" style="font-size:11px">{{ row.status }}</span>
          </div>
        </template>
        <template #cell-name="{ row }">
          <div class="cell-name">
            <span class="mono" style="color:var(--text)">{{ row.name }}</span>
            <Chip v-if="row.version" style="margin-left:6px">{{ row.version }}</Chip>
          </div>
        </template>
        <template #cell-agent_type="{ value }">
          <span class="mono faint" style="font-size:11px">{{ value }}</span>
        </template>
        <template #cell-model_provider="{ value }">
          <span class="mono faint" style="font-size:11px">{{ value || '—' }}</span>
        </template>
        <template #cell-updated_at="{ value }">
          <span class="mono faint" style="font-size:11px" :title="formatDateTime(value)">{{ formatRelativeTime(value) }}</span>
        </template>
      </DataTable>
    </Panel>

    <!-- Recent eval runs -->
    <Panel title="Recent eval runs" subtitle="last 10" :padding="false">
      <template #actions>
        <RouterLink to="/evaluate/runs" class="panel-link mono">view all →</RouterLink>
      </template>

      <DataTable
        :columns="runCols"
        :rows="runs.slice(0, 10)"
        :on-row-click="r => $router.push(`/evaluate/runs/${r.id}`)"
        empty-text="no evaluation runs yet"
      >
        <template #cell-status="{ row }">
          <div class="cell-status">
            <StatusDot :status="runStatusToDot(row.status)" />
            <span class="mono faint" style="font-size:11px">{{ row.status }}</span>
          </div>
        </template>
        <template #cell-agent_id="{ value, row }">
          <span class="mono" style="color:var(--text); font-size:11.5px">
            {{ (value || '').slice(0, 8) }}<span v-if="row.agent_version" class="faint"> · {{ row.agent_version }}</span>
          </span>
        </template>
        <template #cell-pass_rate="{ row }">
          <span class="mono" :class="passRateRowColor(row)">{{ passRateRowPct(row) }}</span>
        </template>
        <template #cell-items="{ row }">
          <span class="mono faint" style="font-size:11px">{{ row.passed + row.failed + row.errored }}/{{ row.total_items || 0 }}</span>
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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { RouterLink } from 'vue-router'

import { agentService } from '@/services/agentService'
import { datasetService } from '@/services/datasetService'
import { evalRunService } from '@/services/evalRunService'
import { formatRelativeTime, formatDateTime } from '@/utils/format'

import Kpi from '@/components/primitives/Kpi.vue'
import Panel from '@/components/primitives/Panel.vue'
import Chip from '@/components/primitives/Chip.vue'
import StatusDot from '@/components/primitives/StatusDot.vue'
import DataTable from '@/components/primitives/DataTable.vue'

// ── State ─────────────────────────────────────────────────────────────
const loading = ref(false)
const error = ref('')

const agents = ref([])
const datasets = ref([])
const runs = ref([])

// ── Columns ───────────────────────────────────────────────────────────
const agentCols = [
  { key: 'status',         label: 'Status',  width: '130px' },
  { key: 'name',           label: 'Agent',   width: '2fr' },
  { key: 'agent_type',     label: 'Type',    width: '110px' },
  { key: 'model_provider', label: 'Model',   width: '1fr' },
  { key: 'updated_at',     label: 'Updated', width: '110px', align: 'right' },
]

const runCols = [
  { key: 'status',     label: 'Status',    width: '130px' },
  { key: 'agent_id',   label: 'Agent',     width: '1.5fr' },
  { key: 'pass_rate',  label: 'Pass Rate', width: '100px', align: 'right' },
  { key: 'items',      label: 'Items',     width: '100px', align: 'right' },
  { key: 'created_at', label: 'Started',   width: '110px', align: 'right' },
]

// ── Derived ───────────────────────────────────────────────────────────
const agentCounts = computed(() => {
  const c = { active: 0, draft: 0, deprecated: 0, archived: 0 }
  for (const a of agents.value) c[a.status] = (c[a.status] || 0) + 1
  return c
})

const runCounts = computed(() => {
  const c = { running: 0, completed: 0, failed: 0, pending: 0, cancelled: 0 }
  for (const r of runs.value) c[r.status] = (c[r.status] || 0) + 1
  return c
})

const totalDatasetItems = computed(() => datasets.value.reduce((s, d) => s + (d.item_count || 0), 0))

const avgPassRatePct = computed(() => {
  const completed = runs.value.filter(r => r.status === 'completed' && r.total_items > 0)
  if (!completed.length) return '—'
  const avg = completed.reduce((s, r) => s + (r.passed / r.total_items), 0) / completed.length
  return `${Math.round(avg * 100)}%`
})

const passRateTone = computed(() => {
  const completed = runs.value.filter(r => r.status === 'completed' && r.total_items > 0)
  if (!completed.length) return 'neu'
  const avg = completed.reduce((s, r) => s + (r.passed / r.total_items), 0) / completed.length
  if (avg >= 0.95) return 'pos'
  if (avg >= 0.80) return 'warn'
  return 'neg'
})

// Sparkline-friendly data
const agentsSpark = computed(() => stableSpark(agents.value.length || 1, 3))
const datasetsSpark = computed(() => stableSpark(datasets.value.length || 1, 7))
const runsSpark = computed(() => {
  // group runs by day and return daily counts
  const buckets = {}
  for (const r of runs.value) {
    if (!r.created_at) continue
    const d = r.created_at.slice(0, 10)
    buckets[d] = (buckets[d] || 0) + 1
  }
  const vals = Object.values(buckets)
  return vals.length >= 2 ? vals : stableSpark(runs.value.length || 1, 11)
})
const passRateSpark = computed(() => {
  const completed = runs.value
    .filter(r => r.status === 'completed' && r.total_items > 0)
    .sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
    .map(r => r.passed / r.total_items)
  return completed.length >= 2 ? completed : stableSpark(runs.value.length || 1, 13)
})

function stableSpark(seed, variant = 0) {
  const n = 24
  let v = 0.5
  const out = []
  let x = (Number(seed) || 1) * 9301 + 49297 + variant * 131
  for (let i = 0; i < n; i++) {
    x = (x * 9301 + 49297) % 233280
    const rnd = x / 233280
    v += (rnd - 0.5) * 0.25
    v = Math.max(0.1, Math.min(0.95, v))
    out.push(v)
  }
  return out
}

function statusToDot(status) {
  return { active: 'ok', draft: 'pending', deprecated: 'warn', archived: 'pending' }[status] || 'pending'
}

function runStatusToDot(status) {
  return { running: 'info', completed: 'ok', failed: 'err', cancelled: 'pending', pending: 'pending' }[status] || 'pending'
}

function passRateRowPct(r) {
  const done = r.passed + r.failed + r.errored
  if (!done) return '—'
  return `${Math.round((r.passed / done) * 100)}%`
}

function passRateRowColor(r) {
  const done = r.passed + r.failed + r.errored
  if (!done) return 'text-subtle'
  const rate = r.passed / done
  if (rate >= 0.95) return 'text-success'
  if (rate >= 0.80) return 'text-warning'
  return 'text-danger'
}

// ── Fetch ─────────────────────────────────────────────────────────────
async function refresh() {
  loading.value = true
  error.value = ''
  try {
    const [aRes, dRes, rRes] = await Promise.allSettled([
      agentService.list(),
      datasetService.list(),
      evalRunService.list({ limit: 50 }),
    ])
    agents.value = aRes.status === 'fulfilled' ? (aRes.value.data ?? []) : []
    datasets.value = dRes.status === 'fulfilled' ? (dRes.value.data ?? []) : []
    runs.value = rRes.status === 'fulfilled' ? (rRes.value.data ?? []) : []
  } catch (e) {
    error.value = e?.response?.data?.detail || e?.message || 'Failed to load dashboard data'
  } finally {
    loading.value = false
  }
}

let pollInterval = null
onMounted(() => {
  refresh()
  pollInterval = setInterval(refresh, 30_000)
})
onUnmounted(() => clearInterval(pollInterval))
</script>

<style scoped>
.dashboard { display: flex; flex-direction: column; gap: 14px; height: 100%; }

/* Header */
.dash-header { display: flex; align-items: flex-end; justify-content: space-between; gap: 16px; padding: 2px 2px 6px; flex-wrap: wrap; }
.dash-title-wrap { display: flex; flex-direction: column; gap: 4px; }
.dash-eyebrow { font-size: 10.5px; letter-spacing: 0.08em; text-transform: uppercase; }
.dash-title { font-size: 22px; font-weight: 600; letter-spacing: -0.02em; color: var(--text); }
.dash-subtitle { font-size: 11.5px; color: var(--text-dim); display: flex; gap: 6px; align-items: center; }
.dash-subtitle .sep { color: var(--text-faint); }
.dash-actions { display: flex; align-items: center; gap: 8px; flex-shrink: 0; }

/* KPI strip */
.kpi-strip {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1px;
  background: var(--border);
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  overflow: hidden;
}
@media (max-width: 900px) { .kpi-strip { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 540px) { .kpi-strip { grid-template-columns: 1fr; } }

/* Cell styles */
.cell-status { display: flex; align-items: center; gap: 8px; }
.cell-name { display: inline-flex; align-items: center; }

/* Shared */
.panel-link {
  font-size: 11px;
  color: var(--text-dim);
  text-decoration: none;
  transition: color 0.1s;
  font-family: var(--mono);
}
.panel-link:hover { color: var(--accent); }

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
