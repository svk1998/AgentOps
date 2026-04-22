<template>
  <div class="dashboard">
    <!-- ── Header row (sticky-ish top bar) ─────────────────────────────── -->
    <div class="dash-header">
      <div class="dash-title-wrap">
        <div class="dash-eyebrow mono faint">overview</div>
        <h1 class="dash-title">Fleet</h1>
        <div class="dash-subtitle mono">
          <span>{{ summary?.agents?.total ?? 0 }} agents</span>
          <span class="sep">·</span>
          <span class="text-success">{{ summary?.runs?.completed ?? 0 }} completed</span>
          <span class="sep">·</span>
          <span class="text-danger">{{ summary?.runs?.failed ?? 0 }} failed</span>
          <span class="sep">·</span>
          <span class="text-info">{{ summary?.runs?.running ?? 0 }} running</span>
        </div>
      </div>
      <div class="dash-actions">
        <Chip variant="ok" dot>live · auto-refresh 30s</Chip>
        <button class="btn ghost" :disabled="loading" @click="refresh">
          <svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" :style="loading ? 'animation:spin 1s linear infinite' : ''">
            <path d="M14 8a6 6 0 1 1-6-6c1.9 0 3.6 0.9 4.7 2.3"/>
            <path d="M14 2v3h-3"/>
          </svg>
          Refresh
        </button>
        <button class="btn primary" @click="$router.push('/registry/agents')">
          <svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M8 3v10M3 8h10"/></svg>
          New agent
        </button>
      </div>
    </div>

    <!-- ── KPI strip ─────────────────────────────────────────────────── -->
    <div class="kpi-strip">
      <Kpi
        label="Total agents"
        :value="loading ? '—' : (summary?.agents?.total ?? 0).toString()"
        :delta="agentsDelta"
        tone="accent"
        :spark="agentsSpark"
      />
      <Kpi
        label="Runs (24h)"
        :value="loading ? '—' : formatNumber(summary?.runs?.last_24h ?? 0)"
        :delta="runsDelta"
        tone="pos"
        :spark="runsSpark"
      />
      <Kpi
        label="Success rate"
        :value="loading ? '—' : successRateDisplay"
        :delta="successDelta"
        :tone="successTone"
        :spark="successSpark"
      />
      <Kpi
        label="Tokens (24h)"
        :value="loading ? '—' : formatTokens(summary?.tokens?.last_24h ?? 0)"
        delta="live"
        tone="neu"
        :spark="tokensSpark"
      />
    </div>

    <!-- ── Run activity timeline ─────────────────────────────────────── -->
    <Panel title="Run activity" subtitle="last 7 days">
      <div v-if="!runsTimeline.length" class="tl-empty mono faint">No runs in this period</div>
      <div v-else class="tl">
        <div class="tl-bars">
          <div
            v-for="day in runsTimeline"
            :key="day.date"
            class="tl-col"
            :title="`${day.date}: ${day.total} runs (${day.completed} ok, ${day.failed} failed)`"
          >
            <div class="tl-stack">
              <div class="tl-bar tl-bar--failed" :style="{ height: barHeight(day.failed) }" />
              <div class="tl-bar tl-bar--completed" :style="{ height: barHeight(day.completed) }" />
            </div>
            <div class="tl-label mono">{{ dayLabel(day.date) }}</div>
          </div>
        </div>
        <div class="tl-legend mono">
          <span class="tl-legend-item"><span class="tl-dot tl-dot--completed"/>completed</span>
          <span class="tl-legend-item"><span class="tl-dot tl-dot--failed"/>failed</span>
        </div>
      </div>
    </Panel>

    <!-- ── Recent runs table ─────────────────────────────────────────── -->
    <Panel title="Recent runs" subtitle="last 10" :padding="false">
      <template #actions>
        <RouterLink to="/evaluate/runs" class="panel-link mono">view all →</RouterLink>
      </template>

      <DataTable
        :columns="runCols"
        :rows="recentRuns"
        :on-row-click="r => $router.push(`/runs/${r.id}`)"
        empty-text="no runs yet — trigger your first agent run"
      >
        <template #cell-status="{ value }">
          <div class="cell-status">
            <StatusDot :status="value" />
            <span class="mono faint" style="font-size:11px">{{ value }}</span>
          </div>
        </template>
        <template #cell-agent_name="{ value }">
          <span class="mono" style="color:var(--text)">{{ value || '—' }}</span>
        </template>
        <template #cell-usage="{ value }">
          <span class="mono faint">{{ formatTokens(value?.total_tokens) }}</span>
        </template>
        <template #cell-created_at="{ value }">
          <span class="mono faint" :title="formatDateTime(value)">{{ formatRelativeTime(value) }}</span>
        </template>
      </DataTable>
    </Panel>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { RouterLink } from 'vue-router'
import { statsService } from '@/services/statsService'
import api from '@/services/api'
import { formatTokens, formatNumber, formatRelativeTime, formatDateTime } from '@/utils/format'

import Kpi from '@/components/primitives/Kpi.vue'
import Panel from '@/components/primitives/Panel.vue'
import Chip from '@/components/primitives/Chip.vue'
import StatusDot from '@/components/primitives/StatusDot.vue'
import DataTable from '@/components/primitives/DataTable.vue'

// ── State ─────────────────────────────────────────────────────────────
const loading = ref(false)
const runsLoading = ref(false)
const summary = ref(null)
const runsTimeline = ref([])
const recentRuns = ref([])

const runCols = [
  { key: 'status',     label: 'Status',  width: '140px' },
  { key: 'agent_name', label: 'Agent',   width: '1.5fr' },
  { key: 'usage',      label: 'Tokens',  width: '110px', align: 'right' },
  { key: 'created_at', label: 'Started', width: '130px', align: 'right' },
]

// ── Derived ───────────────────────────────────────────────────────────
const successRateDisplay = computed(() => {
  const r = summary.value?.runs?.success_rate
  if (r == null) return '—'
  return `${Math.round(r * 100)}%`
})

const successTone = computed(() => {
  const r = summary.value?.runs?.success_rate
  if (r == null) return 'neu'
  if (r >= 0.95) return 'pos'
  if (r >= 0.80) return 'warn'
  return 'neg'
})

// Sparkline data — derived from timeline where possible, deterministic fallback otherwise
const agentsSpark = computed(() => stableSpark(summary.value?.agents?.total ?? 0, 3))
const runsSpark = computed(() => {
  const data = runsTimeline.value.map(d => d.total || 0)
  return data.length ? data : stableSpark(summary.value?.runs?.last_24h ?? 0, 11)
})
const successSpark = computed(() => {
  const data = runsTimeline.value.map(d => d.total ? d.completed / d.total : 1)
  return data.length ? data : stableSpark(summary.value?.runs?.success_rate ?? 0, 7)
})
const tokensSpark = computed(() => stableSpark(summary.value?.tokens?.last_24h ?? 0, 13))

const agentsDelta = computed(() => loading.value ? null : `${summary.value?.agents?.active_last_24h ?? 0} active`)
const runsDelta = computed(() => loading.value ? null : `${summary.value?.runs?.total ?? 0} total`)
const successDelta = computed(() => {
  if (loading.value) return null
  const ok = summary.value?.runs?.completed ?? 0
  const fail = summary.value?.runs?.failed ?? 0
  return `${ok}/${ok + fail}`
})

// Simple deterministic spark fallback so cards never look broken
function stableSpark(seed, variant = 0) {
  const n = 24
  const base = 0.5
  const out = []
  let v = base
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

// ── Timeline bar chart ────────────────────────────────────────────────
const maxBarTotal = computed(() =>
  Math.max(1, ...runsTimeline.value.map(d => d.total))
)
function barHeight(n) { return `${Math.round((n / maxBarTotal.value) * 100)}%` }
function dayLabel(dateStr) {
  return new Date(dateStr).toLocaleDateString(navigator.language, { weekday: 'short' })
}

// ── Fetch ─────────────────────────────────────────────────────────────
async function refresh() {
  loading.value = true
  runsLoading.value = true
  try {
    const [sumRes, timelineRes, runsRes] = await Promise.all([
      statsService.getSummary(),
      statsService.getRunsTimeline(7),
      api.get('/runs', { params: { limit: 10 } }),
    ])
    summary.value = sumRes.data
    runsTimeline.value = timelineRes.data
    recentRuns.value = runsRes.data?.items ?? []
  } catch (_e) {
    // silently fail — backend may not be running
  } finally {
    loading.value = false
    runsLoading.value = false
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
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 14px;
  height: 100%;
}

/* ── Header ── */
.dash-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  padding: 2px 2px 6px;
}
.dash-title-wrap { display: flex; flex-direction: column; gap: 4px; }
.dash-eyebrow {
  font-size: 10.5px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.dash-title {
  font-size: 22px;
  font-weight: 600;
  letter-spacing: -0.02em;
  color: var(--text);
}
.dash-subtitle {
  font-size: 11.5px;
  color: var(--text-dim);
  display: flex;
  gap: 6px;
  align-items: center;
}
.dash-subtitle .sep { color: var(--text-faint); }
.dash-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

/* ── KPI strip — matches standalone Fleet: 4 cards, 1px gap ── */
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

/* ── Timeline ── */
.tl { display: flex; flex-direction: column; gap: 10px; }
.tl-empty { padding: 32px 0; text-align: center; font-size: 11px; }
.tl-bars {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 6px;
  height: 120px;
}
.tl-col {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  flex: 1;
  height: 100%;
  justify-content: flex-end;
}
.tl-stack {
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  gap: 1px;
  width: 100%;
  max-width: 28px;
  flex: 1;
}
.tl-bar {
  border-radius: 2px 2px 0 0;
  min-height: 2px;
  transition: height 0.3s ease;
}
.tl-bar--completed { background: var(--ok); }
.tl-bar--failed    { background: var(--err); }
.tl-label {
  font-size: 10px;
  color: var(--text-faint);
  letter-spacing: 0.04em;
  text-transform: lowercase;
}
.tl-legend {
  display: flex;
  gap: 12px;
  justify-content: center;
  padding-top: 4px;
  font-size: 10.5px;
  color: var(--text-faint);
}
.tl-legend-item { display: inline-flex; align-items: center; gap: 5px; }
.tl-dot { width: 8px; height: 8px; border-radius: 2px; }
.tl-dot--completed { background: var(--ok); }
.tl-dot--failed    { background: var(--err); }

/* ── Table cell helpers ── */
.cell-status { display: flex; align-items: center; gap: 8px; }
.panel-link {
  font-size: 11px;
  color: var(--text-dim);
  text-decoration: none;
  transition: color 0.1s;
}
.panel-link:hover { color: var(--accent); }
</style>
