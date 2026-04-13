<template>
  <div class="dashboard">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">Dashboard</h1>
        <p class="page-subtitle">Platform overview and live metrics</p>
      </div>
      <div class="header-actions">
        <AppButton variant="ghost" size="sm" :loading="loading" @click="refresh">
          <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor" :style="loading ? 'animation:spin 1s linear infinite' : ''">
            <path d="M11.534 7h3.932a.25.25 0 0 1 .192.41l-1.966 2.36a.25.25 0 0 1-.384 0l-1.966-2.36a.25.25 0 0 1 .192-.41zm-11 2h3.932a.25.25 0 0 0 .192-.41L2.692 6.23a.25.25 0 0 0-.384 0L.342 8.59A.25.25 0 0 0 .534 9z"/>
            <path fill-rule="evenodd" d="M8 3c-1.552 0-2.94.707-3.857 1.818a.5.5 0 1 1-.771-.636A6.002 6.002 0 0 1 13.917 7H12.9A5.002 5.002 0 0 0 8 3zM3.1 9a5.002 5.002 0 0 0 8.757 2.182.5.5 0 1 1 .771.636A6.002 6.002 0 0 1 2.083 9H3.1z"/>
          </svg>
          Refresh
        </AppButton>
      </div>
    </div>

    <!-- Stat cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-card__icon stat-card__icon--blue">
          <svg width="20" height="20" viewBox="0 0 16 16" fill="currentColor">
            <path d="M6 1a2 2 0 1 0 4 0A2 2 0 0 0 6 1zM1 6a7 7 0 0 1 14 0v1H1V6zM0 9h16v1a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V9zm5 3v3h2v-3H5zm4 0v3h2v-3H9z"/>
          </svg>
        </div>
        <div class="stat-card__body">
          <p class="stat-card__label">Total Agents</p>
          <p class="stat-card__value">{{ loading ? '—' : summary?.agents?.total ?? 0 }}</p>
          <p class="stat-card__sub">
            <span class="text-info">{{ summary?.agents?.active_last_24h ?? 0 }}</span> active in 24h
          </p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-card__icon stat-card__icon--purple">
          <svg width="20" height="20" viewBox="0 0 16 16" fill="currentColor">
            <path d="M2 1a1 1 0 0 0-1 1v12a1 1 0 0 0 1.5.87l11-6a1 1 0 0 0 0-1.74l-11-6A1 1 0 0 0 2 1z"/>
          </svg>
        </div>
        <div class="stat-card__body">
          <p class="stat-card__label">Total Runs</p>
          <p class="stat-card__value">{{ loading ? '—' : formatNumber(summary?.runs?.total ?? 0) }}</p>
          <p class="stat-card__sub">
            <span class="text-success">{{ summary?.runs?.last_24h ?? 0 }}</span> in last 24h
          </p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-card__icon stat-card__icon--green">
          <svg width="20" height="20" viewBox="0 0 16 16" fill="currentColor">
            <path d="M10.97 4.97a.75.75 0 0 1 1.07 1.05l-3.99 4.99a.75.75 0 0 1-1.08.02L4.324 8.384a.75.75 0 1 1 1.06-1.06l2.094 2.093 3.473-4.425a.267.267 0 0 1 .02-.022z"/>
            <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>
          </svg>
        </div>
        <div class="stat-card__body">
          <p class="stat-card__label">Success Rate</p>
          <p class="stat-card__value">{{ loading ? '—' : successRateDisplay }}</p>
          <p class="stat-card__sub">
            <span class="text-success">{{ summary?.runs?.completed ?? 0 }}</span> completed /
            <span class="text-danger">{{ summary?.runs?.failed ?? 0 }}</span> failed
          </p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-card__icon stat-card__icon--amber">
          <svg width="20" height="20" viewBox="0 0 16 16" fill="currentColor">
            <path d="M8.97 4.97a.75.75 0 0 1 1.07 1.05l-3.99 4.99a.75.75 0 0 1-1.08.02L2.324 8.384a.75.75 0 1 1 1.06-1.06l2.094 2.093L8.95 4.992a.252.252 0 0 1 .02-.022zm-.92 5.14.92.92a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 1 0-1.091-1.028L9.477 9.417l-.485-.486-.943 1.179z"/>
          </svg>
        </div>
        <div class="stat-card__body">
          <p class="stat-card__label">Tokens Used</p>
          <p class="stat-card__value">{{ loading ? '—' : formatTokens(summary?.tokens?.total ?? 0) }}</p>
          <p class="stat-card__sub">
            <span class="text-warning">{{ formatTokens(summary?.tokens?.last_24h ?? 0) }}</span> in last 24h
          </p>
        </div>
      </div>
    </div>

    <!-- Charts row -->
    <div class="charts-row">
      <!-- Runs timeline -->
      <AppCard class="chart-card">
        <template #header>
          <span class="card-title">Run Activity <span class="text-subtle">— last 7 days</span></span>
        </template>
        <div class="chart-area">
          <div v-if="!runsTimeline.length" class="chart-empty">No runs in this period</div>
          <div v-else class="bar-chart">
            <div
              v-for="day in runsTimeline"
              :key="day.date"
              class="bar-group"
              :title="`${day.date}: ${day.total} runs`"
            >
              <div class="bar-stack">
                <div
                  class="bar bar--completed"
                  :style="{ height: barHeight(day.completed) }"
                />
                <div
                  class="bar bar--failed"
                  :style="{ height: barHeight(day.failed) }"
                />
              </div>
              <span class="bar-label">{{ dayLabel(day.date) }}</span>
            </div>
          </div>
          <div class="chart-legend">
            <span class="legend-item"><span class="legend-dot legend-dot--completed"/>Completed</span>
            <span class="legend-item"><span class="legend-dot legend-dot--failed"/>Failed</span>
          </div>
        </div>
      </AppCard>

      <!-- Run status donut -->
      <AppCard class="chart-card chart-card--sm">
        <template #header>
          <span class="card-title">Run Status</span>
        </template>
        <div class="donut-wrap">
          <svg v-if="summary" class="donut" viewBox="0 0 120 120">
            <circle cx="60" cy="60" r="48" fill="none" stroke="var(--color-surface-3)" stroke-width="14"/>
            <circle
              v-for="seg in donutSegments"
              :key="seg.label"
              cx="60" cy="60" r="48"
              fill="none"
              :stroke="seg.color"
              stroke-width="14"
              :stroke-dasharray="`${seg.dash} ${seg.gap}`"
              :stroke-dashoffset="seg.offset"
              stroke-linecap="butt"
              style="transition: stroke-dasharray 0.5s ease;"
            />
            <text x="60" y="56" text-anchor="middle" fill="var(--color-text)" font-size="18" font-weight="700">
              {{ summary?.runs?.total ?? 0 }}
            </text>
            <text x="60" y="71" text-anchor="middle" fill="var(--color-text-muted)" font-size="9">
              total runs
            </text>
          </svg>
          <div class="donut-legend">
            <div v-for="seg in donutSegments" :key="seg.label" class="donut-legend-row">
              <span class="donut-dot" :style="{ background: seg.color }" />
              <span class="donut-label">{{ seg.label }}</span>
              <span class="donut-count">{{ seg.count }}</span>
            </div>
          </div>
        </div>
      </AppCard>
    </div>

    <!-- Recent runs -->
    <AppCard>
      <template #header>
        <span class="card-title">Recent Runs</span>
        <RouterLink to="/runs" class="card-link">View all →</RouterLink>
      </template>
      <AppTable
        :columns="runCols"
        :rows="recentRuns"
        :loading="runsLoading"
        empty-text="No runs yet — trigger your first agent run"
        :on-row-click="r => $router.push(`/runs/${r.id}`)"
      >
        <template #cell-status="{ value }">
          <AppBadge :variant="value" :dot="value === 'running'">{{ value }}</AppBadge>
        </template>
        <template #cell-agent_name="{ value }">
          <span class="font-semibold">{{ value || '—' }}</span>
        </template>
        <template #cell-created_at="{ value }">
          <span class="text-muted" :title="formatDateTime(value)">{{ formatRelativeTime(value) }}</span>
        </template>
        <template #cell-usage="{ value }">
          <span class="font-mono text-muted">{{ formatTokens(value?.total_tokens) }}</span>
        </template>
      </AppTable>
    </AppCard>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { RouterLink } from 'vue-router'
import { statsService } from '@/services/statsService'
import api from '@/services/api'
import AppCard from '@/components/ui/AppCard.vue'
import AppTable from '@/components/ui/AppTable.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppButton from '@/components/ui/AppButton.vue'
import { formatTokens, formatNumber, formatRelativeTime, formatDateTime } from '@/utils/format'

const loading     = ref(false)
const runsLoading = ref(false)
const summary     = ref(null)
const runsTimeline = ref([])
const recentRuns   = ref([])

const runCols = [
  { key: 'status',     label: 'Status',  width: '110px' },
  { key: 'agent_name', label: 'Agent'                   },
  { key: 'usage',      label: 'Tokens',  width: '90px', align: 'right' },
  { key: 'created_at', label: 'Started', width: '120px', align: 'right' },
]

const successRateDisplay = computed(() => {
  const r = summary.value?.runs?.success_rate
  if (r == null) return '—'
  return `${Math.round(r * 100)}%`
})

const maxBarTotal = computed(() =>
  Math.max(1, ...runsTimeline.value.map(d => d.total))
)

function barHeight(n) {
  return `${Math.round((n / maxBarTotal.value) * 100)}%`
}

function dayLabel(dateStr) {
  return new Date(dateStr).toLocaleDateString(navigator.language, { weekday: 'short' })
}

const CIRCUMFERENCE = 2 * Math.PI * 48  // ≈ 301.6

const donutSegments = computed(() => {
  const r = summary.value?.runs
  if (!r) return []
  const items = [
    { label: 'Completed', count: r.completed, color: 'var(--color-success)' },
    { label: 'Failed',    count: r.failed,    color: 'var(--color-danger)'  },
    { label: 'Running',   count: r.running,   color: 'var(--color-running)' },
    { label: 'Pending',   count: r.pending,   color: 'var(--color-pending)' },
    { label: 'Cancelled', count: r.cancelled, color: 'var(--color-cancelled)'},
  ]
  const total = r.total || 1
  let offset = CIRCUMFERENCE * 0.25  // start at top (12 o'clock)
  return items.map(item => {
    const dash = (item.count / total) * CIRCUMFERENCE
    const seg = { ...item, dash, gap: CIRCUMFERENCE - dash, offset: -offset + CIRCUMFERENCE }
    offset += dash
    return seg
  })
})

async function refresh() {
  loading.value = true
  runsLoading.value = true
  try {
    const [sumRes, timelineRes, runsRes] = await Promise.all([
      statsService.getSummary(),
      statsService.getRunsTimeline(7),
      api.get('/runs', { params: { limit: 10 } }),
    ])
    summary.value      = sumRes.data
    runsTimeline.value = timelineRes.data
    recentRuns.value   = runsRes.data?.items ?? []
  } catch (e) {
    // silently fail — backend may not be running
  } finally {
    loading.value     = false
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
.dashboard { display: flex; flex-direction: column; gap: 1.5rem; }

/* Header */
.page-header   { display: flex; align-items: flex-start; justify-content: space-between; }
.page-title    { font-size: 1.4rem; font-weight: 700; }
.page-subtitle { color: var(--color-text-muted); font-size: 0.875rem; margin-top: 0.2rem; }
.header-actions { display: flex; gap: 0.5rem; }

/* Stat cards */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}
.stat-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 1.25rem;
  display: flex;
  gap: 1rem;
  align-items: flex-start;
  transition: border-color var(--transition);
}
.stat-card:hover { border-color: var(--color-border-strong); }
.stat-card__icon {
  width: 42px; height: 42px;
  border-radius: var(--radius);
  display: grid; place-items: center;
  flex-shrink: 0;
}
.stat-card__icon--blue   { background: rgba(88,166,255,0.15); color: var(--color-info); }
.stat-card__icon--purple { background: var(--color-primary-subtle); color: var(--color-primary-light); }
.stat-card__icon--green  { background: var(--color-success-subtle); color: var(--color-success-text); }
.stat-card__icon--amber  { background: var(--color-warning-subtle); color: var(--color-warning-text); }
.stat-card__label  { font-size: 0.75rem; color: var(--color-text-muted); font-weight: 500; text-transform: uppercase; letter-spacing: 0.04em; }
.stat-card__value  { font-size: 1.75rem; font-weight: 700; line-height: 1.2; margin: 0.2rem 0; }
.stat-card__sub    { font-size: 0.78rem; color: var(--color-text-muted); }

/* Charts row */
.charts-row { display: grid; grid-template-columns: 1fr 280px; gap: 1rem; }
@media (max-width: 900px) { .charts-row { grid-template-columns: 1fr; } }

.chart-card { min-height: 220px; }
.card-title  { font-size: 0.9rem; font-weight: 600; }
.card-link   { font-size: 0.8rem; color: var(--color-primary-light); }
.card-link:hover { text-decoration: underline; }

.chart-area  { padding: 1.25rem; height: 180px; display: flex; flex-direction: column; }
.chart-empty { display: grid; place-items: center; flex: 1; color: var(--color-text-subtle); font-size: 0.85rem; }

/* Bar chart */
.bar-chart {
  display: flex;
  align-items: flex-end;
  justify-content: space-around;
  gap: 6px;
  flex: 1;
  padding-bottom: 0.5rem;
}
.bar-group   { display: flex; flex-direction: column; align-items: center; gap: 4px; flex: 1; height: 100%; justify-content: flex-end; }
.bar-stack   { display: flex; flex-direction: column; justify-content: flex-end; gap: 1px; width: 100%; max-width: 32px; min-height: 4px; }
.bar         { border-radius: 2px 2px 0 0; min-height: 2px; transition: height 0.4s ease; width: 100%; }
.bar--completed { background: var(--color-success); }
.bar--failed    { background: var(--color-danger); }
.bar-label   { font-size: 0.65rem; color: var(--color-text-subtle); }

.chart-legend { display: flex; gap: 1rem; justify-content: center; padding-top: 0.5rem; }
.legend-item  { display: flex; align-items: center; gap: 0.35rem; font-size: 0.75rem; color: var(--color-text-muted); }
.legend-dot   { width: 8px; height: 8px; border-radius: 2px; }
.legend-dot--completed { background: var(--color-success); }
.legend-dot--failed    { background: var(--color-danger); }

/* Donut */
.donut-wrap   { display: flex; flex-direction: column; align-items: center; gap: 1rem; padding: 1.25rem; }
.donut        { width: 120px; height: 120px; transform: rotate(-90deg); }
.donut-legend { width: 100%; display: flex; flex-direction: column; gap: 0.4rem; }
.donut-legend-row { display: flex; align-items: center; gap: 0.5rem; font-size: 0.78rem; }
.donut-dot    { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.donut-label  { flex: 1; color: var(--color-text-muted); }
.donut-count  { font-weight: 600; color: var(--color-text); }
</style>
