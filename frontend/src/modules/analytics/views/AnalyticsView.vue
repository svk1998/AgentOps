<template>
  <div class="page">
    <div class="page-head">
      <div>
        <div class="page-eyebrow mono faint">observe</div>
        <h1 class="page-title">Analytics</h1>
        <div class="page-sub mono">
          <span>accuracy trends · latency · regressions</span>
        </div>
      </div>
      <div class="page-actions">
        <select v-model="selectedAgentId" class="input" style="min-width:260px">
          <option value="">Pick an agent…</option>
          <option v-for="a in agents" :key="a.id" :value="a.id">{{ a.name }} · {{ a.version }}</option>
        </select>
        <button class="btn ghost" :disabled="!selectedAgentId || loading" @click="loadAll">
          <svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" :class="loading ? 'spin' : ''"><path d="M14 8a6 6 0 1 1-6-6c1.9 0 3.6 0.9 4.7 2.3"/><path d="M14 2v3h-3"/></svg>
          Refresh
        </button>
      </div>
    </div>

    <!-- No agent selected state -->
    <Panel v-if="!selectedAgentId" :padding="false">
      <div class="empty-state">
        <svg width="32" height="32" viewBox="0 0 16 16" fill="none" stroke="var(--accent)" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round" style="opacity:0.8">
          <path d="M2 12l3-4 3 2 4-6"/><path d="M2 14h12"/>
        </svg>
        <p class="empty-title">Pick an agent above to view analytics</p>
        <p class="empty-sub mono">accuracy trend · field-level breakdown · latency · regressions</p>
      </div>
    </Panel>

    <!-- Dashboard -->
    <template v-else>
      <!-- KPI strip (summary) -->
      <div class="kpi-strip">
        <Kpi
          label="Last run pass rate"
          :value="loading ? '—' : lastRun ? lastRun.pass_rate_pct.toFixed(1) + '%' : '—'"
          :tone="lastRunTone"
          :spark="trendData.slice(-24)"
          :delta="trendDelta"
        />
        <Kpi
          label="Runs tracked"
          :value="loading ? '—' : trend.length.toString()"
          tone="neu"
          :spark="trendCountsSpark"
        />
        <Kpi
          label="Avg p95 latency"
          :value="loading ? '—' : avgP95 ? Math.round(avgP95) + 'ms' : '—'"
          tone="neu"
        />
        <Kpi
          label="Regressions"
          :value="loading ? '—' : regressions.filter(r => r.is_regression).length.toString()"
          :tone="regressions.filter(r => r.is_regression).length ? 'neg' : 'pos'"
        />
      </div>

      <!-- Accuracy trend chart -->
      <Panel title="Accuracy trend" subtitle="pass rate over time">
        <template #actions>
          <span class="mono faint" style="font-size:11px">{{ trend.length }} runs</span>
        </template>
        <div v-if="!trend.length" class="empty-state" style="padding:40px">
          <p class="empty-sub mono">no completed runs yet</p>
        </div>
        <div v-else class="trend-chart">
          <svg :viewBox="`0 0 ${chartW} ${chartH}`" preserveAspectRatio="none" class="trend-svg">
            <!-- grid lines -->
            <line v-for="g in gridLines" :key="g.y" :x1="0" :x2="chartW" :y1="g.y" :y2="g.y" stroke="var(--border)" stroke-width="0.5" />
            <!-- area -->
            <path :d="trendAreaPath" fill="var(--accent)" opacity="0.1" />
            <!-- line -->
            <path :d="trendLinePath" stroke="var(--accent)" stroke-width="1.5" fill="none" />
            <!-- points -->
            <circle v-for="(p, i) in trendPoints" :key="i" :cx="p.x" :cy="p.y" r="2" fill="var(--accent)" />
          </svg>
          <div class="trend-axis mono">
            <span>0%</span>
            <span>50%</span>
            <span>100%</span>
          </div>
        </div>
      </Panel>

      <div class="grid-2">
        <!-- Field accuracy -->
        <Panel title="Field accuracy" subtitle="last run — per output field">
          <div v-if="!fieldAccuracy.length" class="empty-state" style="padding:20px">
            <p class="empty-sub mono">no field-level data</p>
          </div>
          <div v-else class="field-list">
            <div v-for="f in fieldAccuracy" :key="f.field + f.run_id" class="field-row">
              <span class="mono field-name">{{ f.field }}</span>
              <div class="field-bar">
                <div
                  class="field-fill"
                  :class="fieldColor(f.accuracy_pct)"
                  :style="{ width: f.accuracy_pct + '%' }"
                ></div>
              </div>
              <span class="mono field-pct" :class="fieldTextColor(f.accuracy_pct)">{{ f.accuracy_pct.toFixed(1) }}%</span>
            </div>
          </div>
        </Panel>

        <!-- Regressions -->
        <Panel title="Regressions" subtitle="version-over-version">
          <div v-if="!regressions.length" class="empty-state" style="padding:20px">
            <p class="empty-sub mono">no comparisons yet</p>
          </div>
          <div v-else class="regression-list">
            <div v-for="r in regressions" :key="r.current_run" class="regression-row" :class="{ 'regression-row--bad': r.is_regression }">
              <div class="regression-head">
                <span class="mono" style="font-size:11.5px">
                  {{ r.previous_version || '—' }} → <span style="color:var(--text)">{{ r.current_version || '—' }}</span>
                </span>
                <span v-if="r.is_regression" class="chip chip--err" style="font-size:10px;height:18px;padding:0 6px;border-radius:999px">regression</span>
              </div>
              <div class="regression-meta mono">
                <span>{{ r.previous_pass_rate != null ? r.previous_pass_rate.toFixed(1) + '%' : '—' }}</span>
                <span class="dim">→</span>
                <span style="color:var(--text)">{{ r.current_pass_rate.toFixed(1) }}%</span>
                <span v-if="r.pass_rate_delta != null" :class="r.pass_rate_delta < 0 ? 'text-danger' : 'text-success'">
                  ({{ r.pass_rate_delta > 0 ? '+' : '' }}{{ r.pass_rate_delta.toFixed(1) }}pts)
                </span>
              </div>
            </div>
          </div>
        </Panel>
      </div>
    </template>

    <div v-if="error" class="error-banner mono">{{ error }}</div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { agentService } from '@/services/agentService'
import { analyticsService } from '@/services/analyticsService'

import Panel from '@/components/primitives/Panel.vue'
import Kpi from '@/components/primitives/Kpi.vue'

const agents = ref([])
const selectedAgentId = ref('')
const trend = ref([])
const fieldAccuracy = ref([])
const latency = ref([])
const regressions = ref([])
const loading = ref(false)
const error = ref('')

// ── Chart geometry ──
const chartW = 800
const chartH = 160

const trendData = computed(() => trend.value.map(p => p.pass_rate_pct / 100))
const trendCountsSpark = computed(() => trend.value.map(p => p.total_items))

const trendPoints = computed(() => {
  if (!trend.value.length) return []
  const pad = 4
  const n = trend.value.length
  const stepX = n > 1 ? (chartW - pad * 2) / (n - 1) : 0
  return trend.value.map((p, i) => ({
    x: pad + i * stepX,
    y: pad + (1 - p.pass_rate_pct / 100) * (chartH - pad * 2),
  }))
})
const trendLinePath = computed(() =>
  trendPoints.value.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x.toFixed(2)},${p.y.toFixed(2)}`).join(' ')
)
const trendAreaPath = computed(() => {
  const pts = trendPoints.value
  if (!pts.length) return ''
  return `M${pts[0].x},${chartH} ` +
    pts.map(p => `L${p.x.toFixed(2)},${p.y.toFixed(2)}`).join(' ') +
    ` L${pts[pts.length - 1].x},${chartH} Z`
})

const gridLines = computed(() => [
  { y: 4 },
  { y: chartH / 2 },
  { y: chartH - 4 },
])

const lastRun = computed(() => trend.value[trend.value.length - 1])
const lastRunTone = computed(() => {
  if (!lastRun.value) return 'neu'
  if (lastRun.value.pass_rate_pct >= 95) return 'pos'
  if (lastRun.value.pass_rate_pct >= 80) return 'warn'
  return 'neg'
})
const trendDelta = computed(() => {
  if (trend.value.length < 2) return null
  const d = trend.value[trend.value.length - 1].pass_rate_pct - trend.value[trend.value.length - 2].pass_rate_pct
  return `${d > 0 ? '+' : ''}${d.toFixed(1)}pts`
})

const avgP95 = computed(() => {
  const vals = trend.value.map(p => p.p95_latency_ms).filter(v => v != null)
  if (!vals.length) return null
  return vals.reduce((s, v) => s + v, 0) / vals.length
})

function fieldColor(pct) {
  if (pct >= 95) return 'field-fill--ok'
  if (pct >= 80) return 'field-fill--warn'
  return 'field-fill--err'
}
function fieldTextColor(pct) {
  if (pct >= 95) return 'text-success'
  if (pct >= 80) return 'text-warning'
  return 'text-danger'
}

async function loadAgents() {
  try {
    const { data } = await agentService.list()
    agents.value = Array.isArray(data) ? data : (data?.items ?? [])
    if (agents.value.length && !selectedAgentId.value) {
      selectedAgentId.value = agents.value[0].id
    }
  } catch (e) {
    error.value = e?.response?.data?.detail || e?.message || 'Failed to load agents'
  }
}

async function loadAll() {
  if (!selectedAgentId.value) return
  loading.value = true
  error.value = ''
  try {
    const [tRes, fRes, lRes, rRes] = await Promise.allSettled([
      analyticsService.accuracyTrend(selectedAgentId.value),
      analyticsService.fieldAccuracy(selectedAgentId.value),
      analyticsService.latency(selectedAgentId.value),
      analyticsService.regressions(selectedAgentId.value),
    ])
    trend.value = tRes.status === 'fulfilled' ? (tRes.value.data || []) : []
    fieldAccuracy.value = fRes.status === 'fulfilled' ? (fRes.value.data || []) : []
    latency.value = lRes.status === 'fulfilled' ? (lRes.value.data || []) : []
    regressions.value = rRes.status === 'fulfilled' ? (rRes.value.data || []) : []
  } catch (e) {
    error.value = e?.response?.data?.detail || e?.message || 'Failed to load analytics'
  } finally {
    loading.value = false
  }
}

watch(selectedAgentId, loadAll)
onMounted(async () => {
  await loadAgents()
  if (selectedAgentId.value) loadAll()
})
</script>

<style scoped>
.page { display: flex; flex-direction: column; gap: 14px; }

.page-head { display: flex; align-items: flex-end; justify-content: space-between; gap: 16px; padding: 2px 2px 6px; flex-wrap: wrap; }
.page-eyebrow { font-size: 10.5px; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 4px; }
.page-title { font-size: 22px; font-weight: 600; letter-spacing: -0.02em; color: var(--text); }
.page-sub { font-size: 11.5px; color: var(--text-dim); display: flex; gap: 6px; align-items: center; margin-top: 2px; }

.page-actions { display: flex; align-items: center; gap: 8px; }
select.input { cursor: pointer; }

.empty-state { padding: 60px 20px; display: flex; flex-direction: column; align-items: center; gap: 10px; }
.empty-title { font-size: 14px; font-weight: 500; color: var(--text-dim); }
.empty-sub { font-size: 11px; color: var(--text-faint); }

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

.trend-chart { display: flex; flex-direction: column; gap: 4px; }
.trend-svg { width: 100%; height: 160px; }
.trend-axis { display: flex; justify-content: space-between; font-size: 10px; color: var(--text-faint); padding: 0 4px; }

.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
@media (max-width: 900px) { .grid-2 { grid-template-columns: 1fr; } }

.field-list { display: flex; flex-direction: column; gap: 8px; }
.field-row { display: grid; grid-template-columns: 180px 1fr 60px; gap: 10px; align-items: center; }
.field-name { font-size: 12px; color: var(--text); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.field-bar { height: 6px; background: var(--bg-elev-2); border-radius: 3px; overflow: hidden; }
.field-fill { height: 100%; transition: width 0.3s; }
.field-fill--ok   { background: var(--ok); }
.field-fill--warn { background: var(--warn); }
.field-fill--err  { background: var(--err); }
.field-pct { font-size: 11.5px; text-align: right; }

.regression-list { display: flex; flex-direction: column; gap: 10px; }
.regression-row {
  padding: 10px 12px;
  border: 1px solid var(--border);
  border-radius: var(--r);
  background: var(--bg-elev);
}
.regression-row--bad { border-color: var(--err); background: var(--err-dim); }
.regression-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px; }
.regression-meta { font-size: 11.5px; color: var(--text-dim); display: flex; gap: 6px; align-items: center; }

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
