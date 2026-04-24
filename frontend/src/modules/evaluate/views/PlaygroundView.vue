<template>
  <div class="page">
    <div class="page-head">
      <div>
        <div class="page-eyebrow mono faint">evaluate</div>
        <h1 class="page-title">Playground</h1>
        <div class="page-sub mono">
          <template v-if="session">
            <span>{{ session.name || 'Unnamed session' }}</span>
            <span class="sep">·</span>
            <span>{{ session.reviewed_count }}/{{ session.total_items }} reviewed</span>
            <span class="sep">·</span>
            <span :class="session.status === 'completed' ? 'text-success' : 'text-info'">{{ session.status }}</span>
          </template>
          <template v-else>
            <span>Human-in-the-loop manual review</span>
          </template>
        </div>
      </div>
      <div class="page-actions">
        <div class="search-wrap">
          <svg class="search-icon" width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round">
            <circle cx="7" cy="7" r="4.5" /><path d="M10.5 10.5L14 14" />
          </svg>
          <input
            v-model="sessionId"
            class="input search-input"
            placeholder="Enter session ID…"
            @keyup.enter="loadSession"
          />
        </div>
        <button class="btn" :disabled="!sessionId || loading" @click="loadSession">Load</button>
      </div>
    </div>

    <!-- No session state -->
    <Panel v-if="!session" :padding="false">
      <div class="empty-state">
        <svg width="32" height="32" viewBox="0 0 16 16" fill="none" stroke="var(--accent)" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round" style="opacity:0.8">
          <path d="M1 8s2.5-5 7-5 7 5 7 5-2.5 5-7 5-7-5-7-5z"/>
          <circle cx="8" cy="8" r="2"/>
        </svg>
        <p class="empty-title">Paste a session ID above to start reviewing</p>
        <p class="empty-sub mono">or create one via POST /api/v1/manual-eval/sessions</p>
      </div>
    </Panel>

    <!-- Review workspace -->
    <div v-else-if="currentItem" class="workspace">
      <!-- Session progress bar -->
      <div class="progress-strip">
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: sessionProgressPct }"></div>
        </div>
        <div class="progress-meta mono">
          <span>item {{ (currentItem.item_index ?? 0) + 1 }}</span>
          <span class="sep">·</span>
          <span>{{ session.reviewed_count }}/{{ session.total_items }} reviewed</span>
        </div>
      </div>

      <div class="review-grid">
        <!-- Input panel -->
        <Panel title="Input" subtitle="agent input payload">
          <pre class="json-block">{{ formatJSON(currentItem.agent_input) }}</pre>
        </Panel>

        <!-- Output panel -->
        <Panel title="Agent output" subtitle="what the agent returned">
          <pre class="json-block">{{ formatJSON(currentItem.agent_output) }}</pre>
        </Panel>

        <!-- Review form -->
        <Panel title="Review" subtitle="your verdict">
          <div class="review-form">
            <div class="field">
              <label class="field-label mono">Verdict</label>
              <div class="verdict-row">
                <button
                  v-for="v in VERDICTS"
                  :key="v.value"
                  class="verdict-btn"
                  :class="[`verdict-btn--${v.value}`, { 'verdict-btn--active': review.verdict === v.value }]"
                  @click="review.verdict = v.value"
                >
                  <kbd class="verdict-key">{{ v.key }}</kbd>
                  {{ v.label }}
                </button>
              </div>
            </div>

            <div v-if="review.verdict === 'fail' || review.verdict === 'partial'" class="field">
              <label class="field-label mono">Severity</label>
              <div class="verdict-row">
                <button
                  v-for="s in SEVERITIES"
                  :key="s"
                  class="btn"
                  :class="{ 'btn primary': review.severity === s }"
                  style="height:26px; font-size:11px"
                  @click="review.severity = s"
                >{{ s }}</button>
              </div>
            </div>

            <div class="field">
              <label class="field-label mono">Notes</label>
              <textarea
                v-model="review.reviewer_notes"
                class="input textarea"
                rows="3"
                placeholder="Why pass/fail? What was wrong?"
              />
            </div>

            <div class="review-actions">
              <button class="btn ghost" :disabled="submitting" @click="skip">Skip →</button>
              <button class="btn primary" :disabled="!review.verdict || submitting" @click="submitReview">
                {{ submitting ? 'Submitting…' : 'Submit & next' }}
              </button>
            </div>
          </div>
        </Panel>
      </div>
    </div>

    <!-- All reviewed state -->
    <Panel v-else-if="session.status === 'completed' || !currentItem" :padding="false">
      <div class="empty-state">
        <svg width="32" height="32" viewBox="0 0 16 16" fill="none" stroke="var(--ok)" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round">
          <path d="M3 8l3 3 7-7"/>
        </svg>
        <p class="empty-title">All items reviewed</p>
        <p class="empty-sub mono">{{ session.reviewed_count }}/{{ session.total_items }} complete</p>
      </div>
    </Panel>

    <div v-if="error" class="error-banner mono">{{ error }}</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { manualEvalService } from '@/services/manualEvalService'

import Panel from '@/components/ui/Panel.vue'

const route = useRoute()

const VERDICTS = [
  { value: 'pass',    label: 'Pass',    key: 'P' },
  { value: 'partial', label: 'Partial', key: 'R' },
  { value: 'fail',    label: 'Fail',    key: 'F' },
]
const SEVERITIES = ['critical', 'major', 'minor']

const sessionId = ref(route.query.session || '')
const session = ref(null)
const currentItem = ref(null)
const loading = ref(false)
const submitting = ref(false)
const error = ref('')

const review = ref({ verdict: null, severity: null, reviewer_notes: '' })

const sessionProgressPct = computed(() => {
  if (!session.value?.total_items) return '0%'
  return `${(session.value.reviewed_count / session.value.total_items) * 100}%`
})

async function loadSession() {
  if (!sessionId.value) return
  loading.value = true
  error.value = ''
  session.value = null
  currentItem.value = null
  try {
    const { data } = await manualEvalService.getSession(sessionId.value)
    session.value = data
    await loadNextItem()
  } catch (e) {
    error.value = e?.response?.data?.detail || e?.message || 'Failed to load session'
  } finally {
    loading.value = false
  }
}

async function loadNextItem() {
  try {
    const { data } = await manualEvalService.nextItem(sessionId.value)
    currentItem.value = data
    resetReviewForm()
  } catch (e) {
    // 404 likely means no more items
    if (e?.response?.status === 404) currentItem.value = null
    else error.value = e?.response?.data?.detail || e?.message || 'Failed to load next item'
  }
}

function resetReviewForm() {
  review.value = { verdict: null, severity: null, reviewer_notes: '' }
}

async function submitReview() {
  if (!review.value.verdict || !currentItem.value) return
  submitting.value = true
  error.value = ''
  try {
    await manualEvalService.submitReview(sessionId.value, currentItem.value.id, {
      verdict: review.value.verdict,
      severity: review.value.severity,
      reviewer_notes: review.value.reviewer_notes,
      field_verdicts: {},
    })
    // reload session for counters, then load next
    const { data } = await manualEvalService.getSession(sessionId.value)
    session.value = data
    await loadNextItem()
  } catch (e) {
    error.value = e?.response?.data?.detail || e?.message || 'Failed to submit review'
  } finally {
    submitting.value = false
  }
}

async function skip() { await loadNextItem() }

function formatJSON(obj) {
  try { return JSON.stringify(obj ?? {}, null, 2) } catch { return String(obj) }
}

// Keyboard shortcuts
function onKey(e) {
  if (!currentItem.value || submitting.value) return
  if (document.activeElement?.tagName === 'TEXTAREA' || document.activeElement?.tagName === 'INPUT') return
  const k = e.key.toLowerCase()
  if (k === 'p')      { review.value.verdict = 'pass';    submitReview() }
  else if (k === 'f') { review.value.verdict = 'fail'     }
  else if (k === 'r') { review.value.verdict = 'partial'  }
  else if (k === 'arrowright') skip()
}

onMounted(() => {
  window.addEventListener('keydown', onKey)
  if (sessionId.value) loadSession()
})
onUnmounted(() => window.removeEventListener('keydown', onKey))
</script>

<style scoped>
.page { display: flex; flex-direction: column; gap: 14px; height: 100%; }

.page-head { display: flex; align-items: flex-end; justify-content: space-between; gap: 16px; padding: 2px 2px 6px; flex-wrap: wrap; }
.page-eyebrow { font-size: 10.5px; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 4px; }
.page-title { font-size: 22px; font-weight: 600; letter-spacing: -0.02em; color: var(--text); }
.page-sub { font-size: 11.5px; color: var(--text-dim); display: flex; gap: 6px; align-items: center; margin-top: 2px; }
.page-sub .sep { color: var(--text-faint); }

.page-actions { display: flex; align-items: center; gap: 8px; }
.search-wrap { position: relative; display: flex; align-items: center; }
.search-icon { position: absolute; left: 10px; color: var(--text-faint); pointer-events: none; }
.search-input { padding-left: 28px; min-width: 280px; font-family: var(--mono); font-size: 11px; }

.empty-state {
  padding: 60px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}
.empty-title { font-size: 14px; font-weight: 500; color: var(--text-dim); }
.empty-sub   { font-size: 11px; color: var(--text-faint); }

.workspace { display: flex; flex-direction: column; gap: 12px; }

.progress-strip {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 2px;
}
.progress-bar {
  flex: 1;
  height: 4px;
  background: var(--bg-elev-2);
  border-radius: 2px;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  background: var(--accent);
  transition: width 0.3s ease;
}
.progress-meta {
  font-size: 10.5px;
  color: var(--text-faint);
  display: flex;
  gap: 6px;
}
.progress-meta .sep { color: var(--text-faint); }

.review-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 12px;
}
@media (max-width: 1100px) { .review-grid { grid-template-columns: 1fr; } }

.json-block {
  font-family: var(--mono);
  font-size: 11.5px;
  color: var(--text);
  background: var(--bg-elev-2);
  padding: 10px;
  border-radius: var(--r-sm);
  overflow: auto;
  max-height: 320px;
  white-space: pre;
  margin: 0;
}

.review-form { display: flex; flex-direction: column; gap: 12px; }
.field { display: flex; flex-direction: column; gap: 6px; }
.field-label {
  font-size: 10px;
  color: var(--text-faint);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
.verdict-row { display: flex; gap: 6px; }
.verdict-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border-radius: var(--r);
  background: var(--bg-elev);
  border: 1px solid var(--border);
  color: var(--text-dim);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.1s;
}
.verdict-btn:hover { border-color: var(--border-strong); color: var(--text); }
.verdict-btn--active.verdict-btn--pass    { background: var(--ok-dim);   border-color: var(--ok);   color: var(--ok);   }
.verdict-btn--active.verdict-btn--partial { background: var(--warn-dim); border-color: var(--warn); color: var(--warn); }
.verdict-btn--active.verdict-btn--fail    { background: var(--err-dim);  border-color: var(--err);  color: var(--err);  }
.verdict-key {
  font-family: var(--mono);
  font-size: 9.5px;
  padding: 1px 4px;
  border: 1px solid currentColor;
  border-radius: 3px;
  opacity: 0.7;
  line-height: 1;
}

.textarea { min-height: 72px; padding: 8px 10px; resize: vertical; font-family: var(--sans); font-size: 12px; }

.review-actions { display: flex; justify-content: flex-end; gap: 6px; margin-top: 4px; }

.error-banner {
  background: var(--err-dim);
  color: var(--err);
  border: 1px solid var(--err);
  border-radius: var(--r);
  padding: 10px 14px;
  font-size: 12px;
}
</style>
